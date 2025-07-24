import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
import logging
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

db_pool: Optional[Pool] = None

async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        min_size=int(os.getenv('DB_POOL_MIN_SIZE', 1)),
        max_size=int(os.getenv('DB_POOL_MAX_SIZE', 10)),
        timeout=int(os.getenv('DB_POOL_TIMEOUT', 30))
    )
    logger.info("Database connection pool created successfully")

async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")

async def create_tables(conn):
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS forms (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)
    
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        form_id INTEGER REFERENCES forms(id) ON DELETE CASCADE,
        question_id TEXT NOT NULL,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        required BOOLEAN NOT NULL DEFAULT FALSE,
        options JSONB,
        min_value INTEGER,
        max_value INTEGER,
        min_label TEXT,
        max_label TEXT
    )
    """)
    logger.info("Database tables created/verified")

@asynccontextmanager
async def lifespan(app):
    try:
        await create_db_pool()
        async with db_pool.acquire() as conn:
            await create_tables(conn)
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        await close_db_pool()

async def get_db():
    if not db_pool:
        raise RuntimeError("Database connection not available")
    async with db_pool.acquire() as connection:
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise