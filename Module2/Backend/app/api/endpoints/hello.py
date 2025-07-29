from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/hello")
async def hello_world() -> Dict[str, str]:
    """
    Simple hello world endpoint
    
    Returns:
        Dict containing a hello world message
    """
    return {"message": "Hello, World!"}

@router.get("/hello/{name}")
async def hello_name(name: str) -> Dict[str, str]:
    """
    Personalized hello endpoint
    
    Args:
        name: The name to greet
        
    Returns:
        Dict containing a personalized greeting
    """
    return {"message": f"Hello, {name}!"}