from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import hello, auth, todos, public, websocket, notifications
from app.database import engine, Base
from app.models import User, Todo, Notification

# Initialize database tables on startup
# SQLAlchemy will create tables if they don't exist, skip if they do
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="A Todo API with public and private todos, featuring JWT authentication",
    version="2.0.0",
    docs_url="/docs",     # Swagger UI at /docs
    redoc_url="/redoc"    # ReDoc at /redoc
)

# CORS configuration for frontend development
# Allows React dev server at :5173 and common alternative ports
# In production, restrict to specific domains for security
origins = [
    "http://localhost",       # Basic localhost
    "http://localhost:3000",  # Common React port
    "http://localhost:8080",  # Common dev server port
    "http://localhost:5173"   # Vite default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Specific allowed origins (not wildcard for security)
    allow_credentials=True,         # Required for JWT cookies/headers
    allow_methods=["*"],            # Allow all HTTP methods
    allow_headers=["*"],            # Allow all headers including Authorization
)

# API routing organization
# RESTful design with versioned endpoints under /api/v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(public.router, prefix="/api/v1/public/todos", tags=["public todos"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["private todos"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])           # WebSocket for real-time features
app.include_router(hello.router, prefix="/api/v1", tags=["hello"])             # Example/test endpoints

@app.get("/")
async def root():
    """Root endpoint providing API welcome message."""
    return {"message": "Welcome to Todo API - Public and Private Todos with Authentication"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancer probes."""
    return {"status": "healthy"}