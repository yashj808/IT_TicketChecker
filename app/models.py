from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketCategory(str, Enum):
    NETWORK = "network"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    ACCESS = "access"
    OTHER = "other"

class TicketPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TicketStatus(str, Enum):
    CREATED = "created"
    CLASSIFIED = "classified"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class TicketIngest(BaseModel):
    subject: str
    description: str
    reporter: str

class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    subject: str
    description: str
    reporter: str
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: TicketStatus
    created_at: datetime

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    action: str
    details: str
    timestamp: datetime

class ClassificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    category: TicketCategory
    priority: TicketPriority
    category_confidence: float
    priority_confidence: float
    created_at: datetime

