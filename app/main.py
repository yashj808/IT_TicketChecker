from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, get_db, Ticket, AuditLog
from app.models import TicketIngest, TicketResponse, AuditLogResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield

app = FastAPI(
    title="IT Ticket Classifier API",
    description="Intelligent ticket classification system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    return TicketResponse.model_validate(db_ticket)

# Get ticket
@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)

# Get audit trail
@app.get("/api/tickets/{ticket_id}/audit", response_model=list[AuditLogResponse])
async def get_audit_trail(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve audit trail for a ticket."""
    logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).all()
    return [AuditLogResponse.model_validate(log) for log in logs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
