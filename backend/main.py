"""
EcoWatt AI - Main Application
FastAPI application for AI-powered energy management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import routers
from routers import auth, energy, appliances, alerts, predictions, recommendations, dashboard, chatbot, reports, settings

# Import database initialization
from database import init_db

# Create FastAPI app
app = FastAPI(
    title="EcoWatt AI",
    description="AI-Powered Energy Leak & Efficiency Advisor",
    version="1.0.0"
)

# Initialize database tables early so the auth endpoints have a working schema.
init_db()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(energy.router)
app.include_router(appliances.router)
app.include_router(alerts.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)
app.include_router(chatbot.router)
app.include_router(reports.router)
app.include_router(settings.router)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "EcoWatt AI is running"}


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Welcome to EcoWatt AI - AI-Powered Energy Management"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
