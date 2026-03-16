from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check() -> Dict:
    """
    Health check endpoint for monitoring service availability.
    
    Returns:
        Dict with status information including service name and version.
    """
    return {
        "status": "healthy",
        "service": "Adaptive Grid Trading Bot",
        "version": "1.0.0"
    }


@router.get("/status")
def status() -> Dict:
    """
    Get current system status and timestamp.
    
    Returns:
        Dict with running status and current server timestamp.
    """
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }
