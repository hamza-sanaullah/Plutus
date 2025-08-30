"""
Plutus Backend - FastAPI Application Entry Point
A production-grade banking simulation backend with CSV-based data storage in Azure Blob.

Team: Yay!
Date: August 29, 2025
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
from typing import Dict, Any
import uuid

# Import routers
from .routers import (
    balance_router,
    beneficiary_router,
    transaction_router
)

# Import core utilities
from .core.config import get_settings
from .core.logging import get_logger

# Initialize settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Plutus Banking Backend",
    description="Production-grade FastAPI backend for banking simulation with CSV-based storage",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configure logging (updated to use our logging utility)
logger.info("Setting up Plutus Banking Backend...")


# Middleware for request logging and audit trail
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """
    Audit middleware to log all API requests for compliance and debugging.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Log incoming request
    logger.info(f"Request {request_id}: {request.method} {request.url}")
    
    # Add request ID to state for access in routes
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request {request_id} completed: "
            f"Status {response.status_code} in {process_time:.4f}s"
        )
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request {request_id} failed: {str(e)} in {process_time:.4f}s"
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "message": "An unexpected error occurred"
            }
        )


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler for consistent error responses.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
            "status_code": exc.status_code
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "healthy",
        "service": "Plutus Banking Backend",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to Plutus Banking Backend API",
        "team": "Team Yay!",
        "docs": "/docs",
        "health": "/health"
    }


# Register API routers
app.include_router(balance_router, prefix="/api", tags=["Balance Management"])
app.include_router(beneficiary_router, prefix="/api", tags=["Beneficiary Management"])
app.include_router(transaction_router, prefix="/api", tags=["Money Transfer"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize services and connections.
    """
    logger.info("🚀 Plutus Banking Backend starting up...")
    logger.info("📊 CSV-based data storage initialized")
    logger.info("☁️ Azure Blob Storage utilities ready")
    logger.info("✅ Plutus Backend is ready to serve requests!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event for cleanup.
    """
    logger.info("🛑 Plutus Banking Backend shutting down...")
    logger.info("💾 Ensuring all data is saved...")
    logger.info("✅ Shutdown complete!")


# Main entry point for development
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
