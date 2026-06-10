import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

# Ensure database is initialized for tests
init_db()

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ingest_ticket():
    """Test ticket ingestion."""
    payload = {
        "subject": "Network connectivity issue",
        "description": "Cannot connect to corporate network",
        "reporter": "john.doe@company.com"
    }
    response = client.post("/api/tickets/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Network connectivity issue"
    assert data["ticket_id"] is not None
    assert data["status"] == "created"

def test_get_ticket():
    """Test retrieving a ticket."""
    # First ingest
    payload = {
        "subject": "Test ticket",
        "description": "Test description",
        "reporter": "test@company.com"
    }
    ingest_response = client.post("/api/tickets/ingest", json=payload)
    ticket_id = ingest_response.json()["ticket_id"]
    
    # Then retrieve
    response = client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["ticket_id"] == ticket_id

def test_get_audit_trail():
    """Test audit trail retrieval."""
    payload = {
        "subject": "Test ticket",
        "description": "Test description",
        "reporter": "test@company.com"
    }
    ingest_response = client.post("/api/tickets/ingest", json=payload)
    ticket_id = ingest_response.json()["ticket_id"]
    
    response = client.get(f"/api/tickets/{ticket_id}/audit")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["action"] == "ingested"
