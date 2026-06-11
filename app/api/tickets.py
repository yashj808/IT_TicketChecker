from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Ticket, Classification, AuditLog
from app.models import ClassificationResponse
from app.ml.classifier import classify_ticket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

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
