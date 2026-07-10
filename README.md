# Report2Resolve Backend

## Overview

This repository contains the backend service for Report2Resolve. The backend is a FastAPI application that handles user authentication, department approval workflows, issue reporting, and Supabase integration.

The backend exposes REST endpoints for the frontend to authenticate users, submit and manage issues, and approve department accounts. It uses environment variables to connect to Supabase and supports email notifications via Gmail SMTP.

## Architecture

- Backend: `app/app`
- FastAPI web framework
- Supabase client for database operations
- User and department registration
- Role-based access flows for citizens, departments, and admins
- CORS enabled for frontend communication
- Email notifications via Gmail SMTP

## Features

### Authentication and Users

- Citizen signup with password hashing
- Department signup requiring admin approval
- Login with role-based access control
- Password verification using bcrypt

### Admin Workflows

- View pending department approval requests
- Approve department accounts
- Simple admin endpoints for user management

### Issue Reporting

- Submit new issues with category, department, and location
- Store reports to Supabase tables
- Status tracking with predefined status IDs

### Integrations

- Supabase database client for data access
- Gmail SMTP for email notifications
- dotenv for environment configuration
- CORS middleware for frontend access

## Project Structure

```
app/app/
  .env
  app/
    auth.py
    config.py
    database.py
    dependencies.py
    main.py
    models.py
    routers/
      admin.py
      auth.py
      authority.py
      issue.py
    schemas.py
    services/
      notification_service.py
      supabase_service.py
  requirements.txt
  README.md
```

## Setup

### Backend Setup

1. Open a terminal and navigate to the backend folder:

```bash
cd d:\LOCAL R2R\app\app\app
```

2. Create and activate a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r ..\requirements.txt
```

4. Create a `.env` file with the required environment variables:

```text
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>
GMAIL_USER=<your_gmail_address>
GMAIL_PASS=<your_gmail_app_password>
```

5. Start the backend server:

```bash
uvicorn main:app --reload
```

6. Default backend URL:

- `http://127.0.0.1:8000`

## API Endpoints

### Authentication

- `POST /signup` — citizen registration
- `POST /dept-signup` — department registration with approval request
- `POST /login` — login for citizens and departments

### Admin

- `GET /admin/pending-approvals` — list department accounts awaiting approval
- `POST /admin/approve/{user_id}` — approve a pending department account

### Health

- `GET /` — basic health check endpoint

## Data Models

### Environment Variables

- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase service role key or API key
- `GMAIL_USER` — Gmail email address for sending notifications
- `GMAIL_PASS` — Gmail app password for SMTP login

### Supabase Tables

The backend expects Supabase tables such as:

- `app_user` — stores user accounts, roles, approval flags, and department info
- `role` — stores role metadata such as `citizen` and `department`
- status tables / identifiers for issue tracking

## Notes

- Keep the frontend and backend running together during development.
- Update allowed origins in `main.py` CORS middleware if your frontend runs on a different host.
- Ensure Supabase credentials are secured and not committed to source control.

## Dependencies

- `fastapi`
- `uvicorn`
- `supabase`
- `python-jose[cryptography]`
- `passlib[bcrypt]`
- `python-multipart`
- `python-dotenv`
