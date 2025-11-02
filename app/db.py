"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database URL - modify this based on your database
# Examples:
# PostgreSQL: "postgresql+asyncpg://user:password@localhost/dbname"
# SQLite: "sqlite+aiosqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Set to False in production
)

# Create async SessionLocal class
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create Base class for models
Base = declarative_base()


async def get_db():
    """
    Async dependency function to get database session.
    
    Usage in FastAPI endpoints:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def generate_uuid() -> str:
    """Generate a UUID string for use as default in models."""
    return str(uuid.uuid4())
