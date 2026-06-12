from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db, Ticket, Classification, AuditLog
from app.models import (
    TicketIngest, 
    TicketResponse, 
    AuditLogResponse, 
    ClassificationResponse
)
from app.ml.classifier import classify_ticket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("/ingest", response_model=TicketResponse)
async def ingest_ticket(ticket: TicketIngest, db: Session = Depends(get_db)):
    """Ingest a new IT support ticket."""
    ticket_id = str(uuid.uuid4())
    
    db_ticket = Ticket(
        ticket_id=ticket_id,
        subject=ticket.subject,
        description=ticket.description,
        reporter=ticket.reporter
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Log action
    audit = AuditLog(
        ticket_id=ticket_id,
        action="ingested",
        details=f"Ticket created: {ticket.subject}"
    )
    db.add(audit)
    db.commit()
    
    return TicketResponse.model_validate(db_ticket)

@router.get("/", response_model=List[TicketResponse])
async def list_tickets(db: Session = Depends(get_db)):
    """List all tickets."""
    tickets = db.query(Ticket).all()
    return [TicketResponse.model_validate(t) for t in tickets]

@router.get("/audit", response_model=List[AuditLogResponse])
async def list_all_audit_logs(db: Session = Depends(get_db)):
    """Retrieve all audit logs across all tickets."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return [AuditLogResponse.model_validate(log) for log in logs]

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

@router.get("/{ticket_id}/audit", response_model=List[AuditLogResponse])
async def get_audit_trail(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve audit trail for a specific ticket."""
    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).all()
    if not logs:
        # Check if ticket exists to decide between 404 and empty list
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
    return [AuditLogResponse.model_validate(log) for log in logs]

@router.post("/classify/{ticket_id}", response_model=ClassificationResponse)
async def classify(ticket_id: str, db: Session = Depends(get_db)):
    """Classify a ticket using ML model."""
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Classify
    category, priority, cat_conf, pri_conf = classify_ticket(
        ticket.subject, 
        ticket.description
    )
    
    # Save classification
    classification = Classification(
        ticket_id=ticket_id,
        category=category,
        priority=priority,
        category_confidence=cat_conf,
        priority_confidence=pri_conf
    )
    db.add(classification)
    
    # Update ticket
    ticket.category = category
    ticket.priority = priority
    ticket.status = "classified"
    db.commit()
    
    # Log action
    audit = AuditLog(
        ticket_id=ticket_id,
        action="classified",
        details=f"Category: {category}, Priority: {priority}, Confidence: {cat_conf:.2f}"
    )
    db.add(audit)
    db.commit()
    
    return ClassificationResponse(
        ticket_id=ticket_id,
        category=category,
        priority=priority,
        category_confidence=cat_conf,
        priority_confidence=pri_conf,
        created_at=classification.created_at
    )
