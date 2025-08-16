from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .database.database import engine, Base
from .auth.routes import router as auth_router
from .calculators.routes import router as calculator_router
from .middleware.usage_tracker import UsageTrackerMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reliability Calculator",
    description="A comprehensive tool for reliability calculations with usage tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(UsageTrackerMiddleware)  # Disabled for now

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(calculator_router, prefix="/api/calculators", tags=["calculators"])

@app.get("/")
async def root():
    return {"message": "Reliability Calculator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)