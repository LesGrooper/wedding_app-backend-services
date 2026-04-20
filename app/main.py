from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import auth, guests, checkin, rsvp, comments

settings = get_settings()

app = FastAPI(
    title="Wedding Invitation System",
    description="Backend API for wedding guest management, QR check-in, RSVP, and comments.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1")
app.include_router(guests.router, prefix="/api/v1")
app.include_router(checkin.router, prefix="/api/v1")
app.include_router(rsvp.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "app": settings.app_name}
