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
The API will be available at `http://localhost:8000`.

### Environment Variables
Create a `.env` file in the root directory and add the following:
- `DATABASE_URL`: Connection string for the database (defaults to SQLite).
- `API_PORT`: Port to run the API on (defaults to 8000).
