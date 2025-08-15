from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import game_routes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sword World 2.5 AI GM API",
    description="API for the Sword World 2.5 AI Game Master",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_routes.router, prefix="/api/game", tags=["game"])

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"message": "Sword World 2.5 AI GM API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running normally"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sword World 2.5 AI GM API server...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
