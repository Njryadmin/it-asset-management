from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    # Import all models to ensure their tables are created
    from app.models import User, Category, Supplier, Department, Asset  # noqa: F401
    from app.models import SystemSettings  # noqa: F401 - ensures table is created
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.approval_flow import ApprovalFlow  # noqa: F401
    from app.models.approval_instance import ApprovalInstance  # noqa: F401
    
    # First, drop existing enum types if they exist (fixes PostgreSQL enum conflict)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("DROP TYPE IF EXISTS assetstatus"))
        except Exception:
            pass
        try:
            await conn.execute(text("DROP TYPE IF EXISTS purchaserequeststatus"))
        except Exception:
            pass
    
    # Then create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
