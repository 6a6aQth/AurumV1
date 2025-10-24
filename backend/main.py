from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import redis
import json

from database import get_db, engine
from database import Base, Domain, SecurityLog, AttackPattern
from schemas import (
    DomainCreate, DomainResponse, DomainUpdate,
    SecurityLogResponse, DashboardStats, LoginRequest,
    AttackPatternResponse
)
from security import SecurityInspector
from rate_limiter import RateLimiter
from auth import verify_password, create_access_token, get_current_admin
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="WAF Platform",
    description="Web Application Firewall Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis
redis_client = redis.from_url(settings.REDIS_URL)

# Initialize security inspector
security_inspector = SecurityInspector()
rate_limiter = RateLimiter(redis_client)

# Security scheme
security = HTTPBearer()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/waf.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    """Main WAF middleware that inspects all requests"""
    start_time = datetime.utcnow()
    
    # Skip WAF inspection for admin endpoints
    if request.url.path.startswith("/admin") or request.url.path.startswith("/docs"):
        response = await call_next(request)
        return response
    
    # Get client IP
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Rate limiting check
    if not await rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    # Security inspection
    inspection_result = await security_inspector.inspect_request(request)
    
    if not inspection_result["allowed"]:
        # Log the blocked request
        await log_security_event(
            client_ip=client_ip,
            request_path=request.url.path,
            request_method=request.method,
            reason=inspection_result["reason"],
            details=inspection_result["details"]
        )
        
        logger.warning(f"Blocked request from {client_ip}: {inspection_result['reason']}")
        return JSONResponse(
            status_code=403,
            content={"error": "Request blocked by WAF", "reason": inspection_result["reason"]}
        )
    
    # Process the request
    response = await call_next(request)
    
    # Log successful request
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Request processed: {request.method} {request.url.path} - {response.status_code} - {processing_time}s")
    
    return response

async def log_security_event(client_ip: str, request_path: str, request_method: str, reason: str, details: dict):
    """Log security events to database"""
    try:
        db = next(get_db())
        security_log = SecurityLog(
            client_ip=client_ip,
            request_path=request_path,
            request_method=request_method,
            reason=reason,
            details=json.dumps(details),
            timestamp=datetime.utcnow()
        )
        db.add(security_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

# Authentication endpoints (disabled for direct access)
# @app.post("/admin/login")
# async def login(login_data: LoginRequest):
#     """Admin login endpoint"""
#     if login_data.password != settings.ADMIN_PASSWORD:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid password"
#         )
#     
#     access_token = create_access_token(data={"sub": "admin"})
#     return {"access_token": access_token, "token_type": "bearer"}

# Domain management endpoints
@app.get("/admin/domains", response_model=List[DomainResponse])
async def get_domains():
    """Get all protected domains"""
    db = next(get_db())
    domains = db.query(Domain).all()
    return domains

@app.post("/admin/domains", response_model=DomainResponse)
async def create_domain(domain_data: DomainCreate):
    """Create a new protected domain"""
    db = next(get_db())
    
    # Check if domain already exists
    existing_domain = db.query(Domain).filter(Domain.domain_name == domain_data.domain_name).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain already exists"
        )
    
    domain = Domain(
        domain_name=domain_data.domain_name,
        target_url=domain_data.target_url,
        security_level=domain_data.security_level,
        rate_limit=domain_data.rate_limit,
        is_active=domain_data.is_active
    )
    
    db.add(domain)
    db.commit()
    db.refresh(domain)
    
    logger.info(f"New domain added: {domain_data.domain_name}")
    return domain

@app.put("/admin/domains/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    domain_data: DomainUpdate
):
    """Update a domain configuration"""
    db = next(get_db())
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    for field, value in domain_data.dict(exclude_unset=True).items():
        setattr(domain, field, value)
    
    db.commit()
    db.refresh(domain)
    
    logger.info(f"Domain updated: {domain.domain_name}")
    return domain

@app.delete("/admin/domains/{domain_id}")
async def delete_domain(domain_id: int):
    """Delete a domain"""
    db = next(get_db())
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    db.delete(domain)
    db.commit()
    
    logger.info(f"Domain deleted: {domain.domain_name}")
    return {"message": "Domain deleted successfully"}

# Security logs endpoints
@app.get("/admin/logs", response_model=List[SecurityLogResponse])
async def get_security_logs(
    limit: int = 100,
    offset: int = 0
):
    """Get security logs"""
    db = next(get_db())
    logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).offset(offset).limit(limit).all()
    return logs

@app.get("/admin/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    db = next(get_db())
    
    # Total domains
    total_domains = db.query(Domain).count()
    active_domains = db.query(Domain).filter(Domain.is_active == True).count()
    
    # Security logs stats
    total_requests = db.query(SecurityLog).count()
    blocked_requests = db.query(SecurityLog).filter(SecurityLog.reason != "allowed").count()
    
    # Recent attacks (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_attacks = db.query(SecurityLog).filter(
        SecurityLog.timestamp >= yesterday,
        SecurityLog.reason != "allowed"
    ).count()
    
    # Top attack types
    attack_types = db.query(SecurityLog.reason, db.func.count(SecurityLog.id)).filter(
        SecurityLog.reason != "allowed"
    ).group_by(SecurityLog.reason).order_by(db.func.count(SecurityLog.id).desc()).limit(5).all()
    
    return DashboardStats(
        total_domains=total_domains,
        active_domains=active_domains,
        total_requests=total_requests,
        blocked_requests=blocked_requests,
        recent_attacks=recent_attacks,
        top_attack_types=[{"type": attack[0], "count": attack[1]} for attack in attack_types]
    )

@app.get("/admin/logs/export")
async def export_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export security logs to CSV"""
    db = next(get_db())
    
    query = db.query(SecurityLog)
    
    if start_date:
        query = query.filter(SecurityLog.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(SecurityLog.timestamp <= datetime.fromisoformat(end_date))
    
    logs = query.order_by(SecurityLog.timestamp.desc()).all()
    
    # Convert to CSV format
    csv_data = "timestamp,client_ip,request_path,request_method,reason,details\n"
    for log in logs:
        csv_data += f"{log.timestamp},{log.client_ip},{log.request_path},{log.request_method},{log.reason},{log.details}\n"
    
    return JSONResponse(
        content={"csv_data": csv_data},
        headers={"Content-Disposition": "attachment; filename=security_logs.csv"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
