# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from app.core.config import settings
# from app.core.logging import logger

# engine = create_async_engine(
#     settings.database_url,
#     echo=not settings.is_production,
#     pool_size=10,
#     max_overflow=20,
#     pool_pre_ping=True,
# )

# AsyncSessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )


# async def get_db() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.logging import logger
import uuid

engine = create_async_engine(
    settings.database_url,
    # SQL echo can include bound values such as signed storage URLs. Keep SQL
    # diagnostics in structured application logs, never raw driver output.
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    # Required for Supabase transaction pooler (PgBouncer)
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        # Supabase transaction pooler may hand a backend connection that has
        # statement names from another client. Unique names avoid asyncpg's
        # DuplicatePreparedStatementError while retaining real DB writes.
        "prepared_statement_name_func": lambda: f"__fasalsetu_{uuid.uuid4().hex}__",
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
