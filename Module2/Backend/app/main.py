from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import hello, auth, todos, public
from app.database import engine, Base
from app.models import User, Todo

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="A Todo API with public and private todos, featuring JWT authentication",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(public.router, prefix="/api/v1/public/todos", tags=["public todos"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["private todos"])
app.include_router(hello.router, prefix="/api/v1", tags=["hello"])

@app.get("/")
async def root():
    return {"message": "Welcome to Todo API - Public and Private Todos with Authentication"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}