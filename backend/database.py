from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://waf_user:waf_password@localhost:5432/waf_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String(255), unique=True, index=True, nullable=False)
    target_url = Column(String(500), nullable=False)
    security_level = Column(String(20), default="moderate")  # strict, moderate, relaxed
    rate_limit = Column(Integer, default=1000)  # requests per hour
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_ip = Column(String(45), index=True, nullable=False)
    request_path = Column(String(500), nullable=False)
    request_method = Column(String(10), nullable=False)
    reason = Column(String(100), nullable=False)  # blocked reason or "allowed"
    details = Column(Text)  # JSON string with additional details
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_agent = Column(String(500))
    referer = Column(String(500))

class AttackPattern(Base):
    __tablename__ = "attack_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(100), nullable=False)
    pattern_regex = Column(String(1000), nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
