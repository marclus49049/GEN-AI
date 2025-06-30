# Task Manager API

A REST API built with FastAPI for managing tasks with user authentication.

## Features

- User registration and login
- Cookie-based session authentication with middleware
- Secure session management with automatic expiry
- CRUD operations for tasks
- MongoDB database with Beanie ODM
- Each user can only access their own tasks
- Automatic cleanup of expired sessions
- Middleware-based authentication for cleaner code
- Mixed public and protected endpoints

## Prerequisites

- MongoDB installed and running (default: localhost:27017)
- Python 3.8+

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MongoDB (optional):
```bash
export MONGODB_URL="mongodb://localhost:27017"
export DATABASE_NAME="task_manager"
```

3. Run the application:
```bash
cd task_manager_api
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user (public)
- `POST /api/auth/login` - Login (sets session cookie) (public)
- `POST /api/auth/logout` - Logout (clears session) (protected)
- `GET /api/auth/me` - Get current user info (protected)
- `GET /api/auth/session` - Get current session info (protected)

### Public Endpoints
- `GET /api/public/stats` - Get public statistics
- `GET /api/public/whoami` - Check authentication status

### Tasks
- `GET /api/tasks` - Get all tasks for the logged-in user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

## Usage Example

1. Register a user:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

2. Login (saves session cookie):
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123" \
  -c cookies.txt
```

3. Create a task (uses session cookie):
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "This is a test task"}' \
  -b cookies.txt
```

4. Logout:
```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -b cookies.txt
```