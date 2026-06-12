from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from app.config import settings
from app.database import init_db, get_db, Ticket, AuditLog
from app.models import TicketIngest, TicketResponse, AuditLogResponse
from fastapi.responses import RedirectResponse
from app.api.tickets import router as tickets_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="IT Ticket Classifier API",
    description="Intelligent ticket classification system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets_router)

# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
