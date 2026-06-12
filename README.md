# IT Ticket Checker

A tool to monitor and check IT support tickets.

## Features
- [ ] Ticket status monitoring
- [ ] Notification system
- [ ] Reporting

## Setup

### Prerequisites
- Python 3.12+
- Pipenv (recommended)

### Installation

Using Pipenv:
```bash
pipenv install
```

### Running the Application

To start the FastAPI server:
```bash
python -m app.main
```
The API will be available at `http://localhost:8001`.

### Quick Start Examples

1. **Ingest a Ticket**:
   ```bash
   curl -X POST "http://localhost:8001/api/tickets/ingest" \
        -H "Content-Type: application/json" \
        -d '{"subject": "Network issue", "description": "WiFi is down", "reporter": "user@example.com"}'
   ```
   *Note: This will return a `ticket_id` (a long UUID).*

2. **Retrieve the Ticket**:
   Use the `ticket_id` returned from the ingest step:
   ```bash
   curl "http://localhost:8001/api/tickets/<YOUR_TICKET_ID>"
   ```

3. **View Audit Trail**:
   ```bash
   curl "http://localhost:8001/api/tickets/<YOUR_TICKET_ID>/audit"
   ```

### API Documentation
Once the server is running, you can access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Available Endpoints

#### Tickets
- `POST /api/tickets/ingest`: Create a new IT support ticket.
- `GET /api/tickets/`: Retrieve a list of all tickets.
- `GET /api/tickets/{ticket_id}`: Get details for a specific ticket.
- `POST /api/tickets/classify/{ticket_id}`: Run the ML classifier on a ticket to assign category and priority.

#### Audit Trail
- `GET /api/tickets/audit`: Retrieve all audit logs for all tickets (most recent first).
- `GET /api/tickets/{ticket_id}/audit`: Retrieve the audit trail for a specific ticket.

#### System
- `GET /health`: Check the API health status.

Create a `.env` file in the root directory and add the following:
- `DATABASE_URL`: Connection string for the database (defaults to SQLite).
- `API_PORT`: Port to run the API on (defaults to 8000).
