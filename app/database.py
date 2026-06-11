from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
import enum
import os
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class TicketCategory(str, enum.Enum):
    NETWORK = "network"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    ACCESS = "access"
    OTHER = "other"

class TicketPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TicketStatus(str, enum.Enum):
    CREATED = "created"
    CLASSIFIED = "classified"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Models
class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    subject = Column(String, index=True)
    description = Column(Text)
    reporter = Column(String)
    category = Column(Enum(TicketCategory), nullable=True)
    priority = Column(Enum(TicketPriority), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.CREATED)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, index=True)
    action = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Classification(Base):
    __tablename__ = "classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, index=True)
    category = Column(Enum(TicketCategory))
    priority = Column(Enum(TicketPriority))
    category_confidence = Column(Float)
    priority_confidence = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

