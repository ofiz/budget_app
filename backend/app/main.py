"""Main FastAPI application.

Security: Implements OWASP security headers, CORS, rate limiting ready.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import router as auth_router
from .database import db
from .transactions import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title="Budget App",
    description="Secure financial expense tracking application",
    version="1.0.0",
    lifespan=lifespan,
)

# Health check endpoint for Docker healthcheck
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "budget-tracker"}

# Security: CORS configuration (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses.
    
    Security: Implements OWASP A05 - Security Misconfiguration mitigations.
    """
    response = await call_next(request)
    
    # Security: Prevent XSS attacks (OWASP A03)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Security: HSTS for HTTPS enforcement (OWASP A02)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Security: Content Security Policy (OWASP A03)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:;"
    )
    
    return response


# Include routers
app.include_router(auth_router)
app.include_router(transactions_router)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page."""
    with open("frontend/templates/index.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
