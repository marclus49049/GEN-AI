from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from app.routers import auth, tasks, public
from app.db.database import init_db
from app.models.session import Session
from app.middleware.auth import AuthMiddleware
from app.core.exceptions import APIException
import uvicorn


async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    while True:
        try:
            await Session.cleanup_expired()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Start background task for session cleanup
    cleanup_task = asyncio.create_task(cleanup_expired_sessions())
    yield
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Task Manager API", version="1.0.0", lifespan=lifespan)

# Configure CORS (must be added before AuthMiddleware due to middleware execution order)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware (will execute before CORS due to add_middleware order)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Task Manager API"}

# Global exception handler for APIException
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code
        }
    )

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )