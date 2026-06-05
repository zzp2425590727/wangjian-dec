import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db, SessionLocal
from app.models.user import User
from app.models.task import DetectionTask
from app.models.detection import DetectionResult
from app.core.security import hash_password
from app.api import routes_auth, routes_tasks, routes_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_demo_user():
    """Create a demo user if it doesn't exist."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "demo").first()
        if not existing:
            demo_user = User(
                id="user_001",
                username="demo",
                password_hash=hash_password("123456"),
            )
            db.add(demo_user)
            db.commit()
            logger.info("Demo user created: demo / 123456")
        else:
            logger.info("Demo user already exists")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting up: initializing database...")
    init_db()
    seed_demo_user()
    logger.info("Database initialized and demo user ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Simple Object Detection System",
    description="A simple image recognition system using Baidu AI API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allowed origins configurable via environment variable
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(routes_auth.router)
app.include_router(routes_tasks.router)
app.include_router(routes_files.router)


@app.get("/")
def root():
    return {"message": "Simple Object Detection System API", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
