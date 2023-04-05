from typing import AsyncGenerator
import os
import databases
import sqlalchemy
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

# ASYNC_DB_URL = "sqlite+aiosqlite:///./test.db"
# TODO: AWS Secrets Manager
if os.environ.get("ENV", "DEV") == "DEV":
    BASE_URL = "admin:Y4eOI6fL6ASu$7YVwqeET:S83.kX@retain.cngfeig7wcxn.us-east-1.rds.amazonaws.com:3306/yretain"
    ASYNC_DB_URL = f"mysql+aiomysql://{BASE_URL}"
    SYNC_DB_URL = f"mysql+pymysql://{BASE_URL}"
else:
    # Only when Production env or staging env - We AWS
    from yretain.app.aws.secret import get_secret

    secret = get_secret("rds!db-53413df9-246b-4e13-9606-77f6412295af")
    db = "yretain"  # secret['dbInstanceIdentifier']
    engine = "mysql"  # secret['engine']
    username = secret['username']
    password = secret['password']
    BASE_URL = f"{username}:{password}@database-1.cngfeig7wcxn.us-east-1.rds.amazonaws.com:3306/{db}"
    ASYNC_DB_URL = f"{engine}+aiomysql://{BASE_URL}"
    SYNC_DB_URL = f"{engine}+pymysql://{BASE_URL}"

database = databases.Database(ASYNC_DB_URL)
engine = create_async_engine(
    ASYNC_DB_URL, pool_recycle=3600
)
sync_engine = sqlalchemy.create_engine(
    SYNC_DB_URL
)
metadata = sqlalchemy.MetaData()
# engine = create_async_engine(ASYNC_DB_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


async def create_sync_db_tables():
    # Establish the connection pool in AWS RDS MySQL
    # await database.connect()
    metadata.create_all(bind=sync_engine)
    await database.disconnect()


async def disconnect_db():
    # Close all connections in the connection pool in AWS RDS MySQL
    await database.disconnect()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
