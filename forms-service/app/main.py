from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
import json
from enum import Enum
import logging
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionType(str, Enum):
    TEXT = "text"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    LINEAR_SCALE = "linear_scale"

class QuestionOption(BaseModel):
    id: str
    value: str

    def dict(self, **kwargs):
        return {"id": self.id, "value": self.value}

class FormQuestion(BaseModel):
    id: str
    title: str
    type: QuestionType
    required: bool = False
    options: Optional[List[QuestionOption]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_label: Optional[str] = None
    max_label: Optional[str] = None

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if self.options is not None:
            data["options"] = [opt.dict() for opt in self.options]
        return data

class FormCreate(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[FormQuestion]

class FormResponse(FormCreate):
    id: int



DATABASE_URL = "postgresql://admin:1234@db_forms:5432/forms_db"

db_pool: Optional[Pool] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            timeout=30
        )
        logger.info("Database connection pool created successfully")
        
        async with db_pool.acquire() as conn:
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
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        if db_pool:
            await db_pool.close()
            logger.info("Database connection pool closed")

app = FastAPI(
    title="Forms API",
    description="API для управления формами с вопросами",
    version="1.0.0",
    root_path="/api/forms",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    async with db_pool.acquire() as connection:
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

@app.post("/", response_model=FormResponse, summary="Создать новую форму")
async def create_form(form: FormCreate, conn=Depends(get_db)):
    try:
        async with conn.transaction():
            form_id = await conn.fetchval(
                "INSERT INTO forms (title, description) VALUES ($1, $2) RETURNING id",
                form.title, form.description
            )
            
            for question in form.questions:
                options_json = None
                if question.options:
                    options_json = json.dumps([opt.dict() for opt in question.options])
                
                await conn.execute(
                    """
                    INSERT INTO questions (
                        form_id, question_id, title, type, required,
                        options, min_value, max_value, min_label, max_label
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    form_id, question.id, question.title, question.type.value,
                    question.required, options_json,
                    question.min_value, question.max_value, 
                    question.min_label, question.max_label
                )
            
            form_data = await conn.fetchrow(
                "SELECT id, title, description FROM forms WHERE id = $1", 
                form_id
            )
            
            questions = await conn.fetch(
                """
                SELECT 
                    question_id as id, 
                    title, 
                    type, 
                    required,
                    options,
                    min_value,
                    max_value,
                    min_label,
                    max_label
                FROM questions WHERE form_id = $1
                """,
                form_id
            )
            
            return {
                "id": form_data["id"],
                "title": form_data["title"],
                "description": form_data["description"],
                "questions": [{
                    "id": q["id"],
                    "title": q["title"],
                    "type": q["type"],
                    "required": q["required"],
                    "options": json.loads(q["options"]) if q["options"] else None,
                    "min_value": q["min_value"],
                    "max_value": q["max_value"],
                    "min_label": q["min_label"],
                    "max_label": q["max_label"]
                } for q in questions]
            }
    except Exception as e:
        logger.error(f"Error creating form: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create form: {str(e)}")

@app.get("/", response_model=List[FormResponse], summary="Получить все формы")
async def get_forms(conn=Depends(get_db)):
    try:
        forms = await conn.fetch("SELECT id, title, description FROM forms ORDER BY created_at DESC")
        result = []
        
        for form in forms:
            questions = await conn.fetch(
                """
                SELECT 
                    question_id as id, 
                    title, 
                    type, 
                    required,
                    options,
                    min_value,
                    max_value,
                    min_label,
                    max_label
                FROM questions WHERE form_id = $1
                """,
                form["id"]
            )
            
            result.append({
                "id": form["id"],
                "title": form["title"],
                "description": form["description"],
                "questions": [{
                    "id": q["id"],
                    "title": q["title"],
                    "type": q["type"],
                    "required": q["required"],
                    "options": json.loads(q["options"]) if q["options"] else None,
                    "min_value": q["min_value"],
                    "max_value": q["max_value"],
                    "min_label": q["min_label"],
                    "max_label": q["max_label"]
                } for q in questions]
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch forms: {str(e)}")

@app.get("/{form_id}", response_model=FormResponse, summary="Получить форму по ID")
async def get_form(form_id: int, conn=Depends(get_db)):
    try:
        form = await conn.fetchrow(
            "SELECT id, title, description FROM forms WHERE id = $1", 
            form_id
        )
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
            
        questions = await conn.fetch(
            """
            SELECT 
                question_id as id, 
                title, 
                type, 
                required,
                options,
                min_value,
                max_value,
                min_label,
                max_label
            FROM questions WHERE form_id = $1
            """,
            form_id
        )
        
        return {
            "id": form["id"],
            "title": form["title"],
            "description": form["description"],
            "questions": [{
                "id": q["id"],
                "title": q["title"],
                "type": q["type"],
                "required": q["required"],
                "options": json.loads(q["options"]) if q["options"] else None,
                "min_value": q["min_value"],
                "max_value": q["max_value"],
                "min_label": q["min_label"],
                "max_label": q["max_label"]
            } for q in questions]
        }
    except Exception as e:
        logger.error(f"Error fetching form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch form: {str(e)}")

@app.put("/{form_id}", response_model=FormResponse, summary="Обновить форму")
async def update_form(form_id: int, form: FormCreate, conn=Depends(get_db)):
    try:
        async with conn.transaction():
            updated_form = await conn.fetchrow(
                "UPDATE forms SET title = $1, description = $2 WHERE id = $3 RETURNING id, title, description",
                form.title, form.description, form_id
            )
            
            if not updated_form:
                raise HTTPException(status_code=404, detail="Form not found")
            
            await conn.execute("DELETE FROM questions WHERE form_id = $1", form_id)
            
            for question in form.questions:
                await conn.execute(
                    """
                    INSERT INTO questions (
                        form_id, question_id, title, type, required,
                        options, min_value, max_value, min_label, max_label
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    form_id, question.id, question.title, question.type.value,
                    question.required, json.dumps(question.options) if question.options else None,
                    question.min_value, question.max_value, question.min_label, question.max_label
                )
            
            questions = await conn.fetch(
                """
                SELECT 
                    question_id as id, 
                    title, 
                    type, 
                    required,
                    options,
                    min_value,
                    max_value,
                    min_label,
                    max_label
                FROM questions WHERE form_id = $1
                """,
                form_id
            )
            
            return {
                "id": updated_form["id"],
                "title": updated_form["title"],
                "description": updated_form["description"],
                "questions": [{
                    "id": q["id"],
                    "title": q["title"],
                    "type": q["type"],
                    "required": q["required"],
                    "options": json.loads(q["options"]) if q["options"] else None,
                    "min_value": q["min_value"],
                    "max_value": q["max_value"],
                    "min_label": q["min_label"],
                    "max_label": q["max_label"]
                } for q in questions]
            }
    except Exception as e:
        logger.error(f"Error updating form: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update form: {str(e)}")

@app.delete("/{form_id}", summary="Удалить форму")
async def delete_form(form_id: int, conn=Depends(get_db)):
    try:
        async with conn.transaction():
            deleted = await conn.execute(
                "DELETE FROM forms WHERE id = $1 RETURNING id", 
                form_id
            )
            if not deleted:
                raise HTTPException(status_code=404, detail="Form not found")
            return {"message": "Form deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete form: {str(e)}")

