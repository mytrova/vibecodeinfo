import asyncio
from vibecodeinfo.db.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os


engine = create_async_engine(os.getenv('DATABASE_URL', ''))
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession)  # type: ignore


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
