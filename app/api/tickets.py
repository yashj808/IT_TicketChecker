from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db, Ticket, Classification, AuditLog, TicketStatus
from app.models import TicketIngest, TicketResponse, ClassificationResponse, AuditLogResponse
from app.ml.classifier import classifier
from datetime import datetime

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("/ingest", response_model=TicketResponse)
async def ingest_ticket(payload: TicketIngest, db: Session = Depends(get_db)):
    """Create a new IT support ticket."""
    ticket_uuid = str(uuid.uuid4())
    
    ticket = Ticket(
        ticket_id=ticket_uuid,
        subject=payload.subject,
        description=payload.description,
        reporter=payload.reporter,
        status=TicketStatus.CREATED
    )
    db.add(ticket)
    
    # Log action
    audit = AuditLog(
        ticket_id=ticket_uuid,
        action="ingested",
        details=f"Ticket created by {payload.reporter}"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(ticket)
    
    return TicketResponse.model_validate(ticket)

@router.get("/", response_model=List[TicketResponse])
async def list_tickets(db: Session = Depends(get_db)):
    """Retrieve all tickets."""
    tickets = db.query(Ticket).all()
    return [TicketResponse.model_validate(t) for t in tickets]

@router.get("/audit", response_model=List[AuditLogResponse])
async def list_all_audit_logs(db: Session = Depends(get_db)):
    """Retrieve all audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return [AuditLogResponse.model_validate(l) for l in logs]

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get details for a specific ticket."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

@router.get("/{ticket_id}/audit", response_model=List[AuditLogResponse])
async def get_audit_trail(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve the audit trail for a specific ticket."""
    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.timestamp.desc()).all()
    return [AuditLogResponse.model_validate(l) for l in logs]

@router.post("/classify/{ticket_id}", response_model=ClassificationResponse)
async def classify_ticket_api(ticket_id: str, db: Session = Depends(get_db)):
    """Classify a ticket using pre-trained AI model."""
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Classify using available model (handles fallback automatically)
    result = classifier.classify(ticket.subject, ticket.description)
    
    # Save classification to database
    classification = Classification(
        ticket_id=ticket_id,
        category=result["category"],
        priority=result["priority"],
        category_confidence=result["category_confidence"],
        priority_confidence=result["priority_confidence"]
    )
    db.add(classification)
    
    # Update ticket
    ticket.category = result["category"]
    ticket.priority = result["priority"]
    ticket.status = TicketStatus.CLASSIFIED
    
    # Log action
    audit = AuditLog(
        ticket_id=ticket_id,
        action="classified",
        details=f"Category: {result['category']}, Priority: {result['priority']}"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(classification)
    
    return ClassificationResponse.model_validate(classification)
