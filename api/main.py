"""
Vercel-optimized FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import routes and database
from backend.app.auth.routes import router as auth_router
from backend.app.calculators.routes import router as calculator_router

app = FastAPI(
    title="Semiconductor Reliability Calculator API",
    description="API for reliability calculations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(calculator_router, prefix="/api/calculators", tags=["calculators"])

@app.get("/")
async def root():
    return {"message": "Semiconductor Reliability Calculator API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# For Vercel
handler = app