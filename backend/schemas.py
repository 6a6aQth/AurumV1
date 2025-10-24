from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class LoginRequest(BaseModel):
    password: str

class DomainCreate(BaseModel):
    domain_name: str
    target_url: HttpUrl
    security_level: str = "moderate"
    rate_limit: int = 1000
    is_active: bool = True

class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    target_url: Optional[HttpUrl] = None
    security_level: Optional[str] = None
    rate_limit: Optional[int] = None
    is_active: Optional[bool] = None

class DomainResponse(BaseModel):
    id: int
    domain_name: str
    target_url: str
    security_level: str
    rate_limit: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SecurityLogResponse(BaseModel):
    id: int
    client_ip: str
    request_path: str
    request_method: str
    reason: str
    details: Optional[str] = None
    timestamp: datetime
    user_agent: Optional[str] = None
    referer: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_domains: int
    active_domains: int
    total_requests: int
    blocked_requests: int
    recent_attacks: int
    top_attack_types: List[Dict[str, Any]]

class AttackPatternResponse(BaseModel):
    id: int
    pattern_name: str
    pattern_regex: str
    severity: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
