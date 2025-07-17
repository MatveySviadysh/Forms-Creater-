from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
import json

class FormCreate(BaseModel):
    title: str
    description: str | None = None
    fields: List[str]

class FormResponse(FormCreate):
    id: int

DATABASE_URL = "postgresql://admin:1234@db_forms:5432/auth_db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    await create_tables(app.state.pool)
    yield
    await app.state.pool.close()

app = FastAPI(
    title="Forms API",
    description="API для управления формами",
    version="1.0.0",
    root_path="/api/forms",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

async def get_db():
    async with app.state.pool.acquire() as connection:
        yield connection

async def create_tables(pool: Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS forms (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            fields JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

def format_form_response(form):
    if form is None:
        return None
    
    fields = form['fields']
    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except json.JSONDecodeError:
            fields = []
    
    return {
        "id": form['id'],
        "title": form['title'],
        "description": form['description'],
        "fields": fields
    }

@app.post("/", response_model=FormResponse)
async def create_form(form: FormCreate, conn=Depends(get_db)):
    try:
        fields_json = json.dumps(form.fields)
        
        form_id = await conn.fetchval(
            """
            INSERT INTO forms (title, description, fields)
            VALUES ($1, $2, $3::jsonb)
            RETURNING id
            """,
            form.title, form.description, fields_json
        )
        return {
            "id": form_id,
            "title": form.title,
            "description": form.description,
            "fields": form.fields
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create form: {str(e)}")

@app.get("/", response_model=List[FormResponse])
async def get_forms(conn=Depends(get_db)):
    try:
        forms = await conn.fetch(
            "SELECT id, title, description, fields FROM forms ORDER BY created_at DESC"
        )
        return [format_form_response(form) for form in forms if form is not None]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forms: {str(e)}")

@app.get("/{form_id}", response_model=FormResponse)
async def get_form(form_id: int, conn=Depends(get_db)):
    try:
        form = await conn.fetchrow(
            "SELECT id, title, description, fields FROM forms WHERE id = $1", form_id
        )
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        return format_form_response(form)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch form: {str(e)}")

@app.put("/{form_id}", response_model=FormResponse)
async def update_form(form_id: int, form: FormCreate, conn=Depends(get_db)):
    try:
        fields_json = json.dumps(form.fields)
        updated = await conn.fetchrow(
            """
            UPDATE forms
            SET title = $1, description = $2, fields = $3::jsonb
            WHERE id = $4
            RETURNING id, title, description, fields
            """,
            form.title, form.description, fields_json, form_id
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Form not found")
        return format_form_response(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update form: {str(e)}")

@app.delete("/{form_id}")
async def delete_form(form_id: int, conn=Depends(get_db)):
    try:
        deleted = await conn.execute(
            "DELETE FROM forms WHERE id = $1 RETURNING id", form_id
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Form not found")
        return {"message": "Form deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete form: {str(e)}")