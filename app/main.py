from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from app.config import settings
from app.database import init_db, get_db, Ticket, AuditLog
from app.models import TicketIngest, TicketResponse, AuditLogResponse

app = FastAPI(
    title="IT Ticket Classifier API",
    description="Intelligent ticket classification system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Ingest ticket endpoint
@app.post("/api/tickets/ingest", response_model=TicketResponse)
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
    
    return TicketResponse.from_orm(db_ticket)

# Get ticket
@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.from_orm(ticket)

# Get audit trail
@app.get("/api/tickets/{ticket_id}/audit", response_model=list[AuditLogResponse])
async def get_audit_trail(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve audit trail for a ticket."""
    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).all()
    return [AuditLogResponse.from_orm(log) for log in logs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
