from fastapi import Depends, HTTPException
from .database import get_db
import asyncpg

async def get_db_connection(db=Depends(get_db)):
    try:
        yield db
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")