import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.classifier import classify_ticket

client = TestClient(app)

def test_classify_network_issue():
    """Test classification of network issue."""
    category, priority, cat_conf, pri_conf = classify_ticket(
        "Network down",
        "Cannot connect to corporate network"
    )
    assert category == "network"
    assert priority in ["high", "critical"]
    assert cat_conf > 0.4
    assert pri_conf > 0.4

def test_classify_software_issue():
    """Test classification of software issue."""
    category, priority, cat_conf, pri_conf = classify_ticket(
        "Application crash",
        "Software crashes on startup"
    )
    assert category == "software"
    assert cat_conf > 0.4

def test_classify_hardware_issue():
    """Test classification of hardware issue."""
    category, priority, cat_conf, pri_conf = classify_ticket(
        "Monitor not working",
        "Monitor is offline"
    )
    assert category == "hardware"
    assert cat_conf > 0.4

def test_classify_access_issue():
    """Test classification of access issue."""
    category, priority, cat_conf, pri_conf = classify_ticket(
        "Cannot access file share",
        "Permission denied on shared drive"
    )
    assert category == "access"
    assert cat_conf > 0.4

def test_classify_endpoint():
    """Test classification API endpoint."""
    # Ingest a ticket
    payload = {
        "subject": "Network connectivity issue",
        "description": "Cannot connect to corporate network",
        "reporter": "john.doe@company.com"
    }
    ingest_response = client.post("/api/tickets/ingest", json=payload)
    ticket_id = ingest_response.json()["ticket_id"]
    
    # Classify it
    response = client.post(f"/api/tickets/classify/{ticket_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket_id
    assert data["category"] == "network"
    assert "category_confidence" in data
    assert "priority_confidence" in data

def test_classify_nonexistent_ticket():
    """Test classification of non-existent ticket."""
    response = client.post("/api/tickets/classify/nonexistent-id")
    assert response.status_code == 404
