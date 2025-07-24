from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import json
from typing import List
from ..schemas import FormCreate, FormResponse
from ..database import get_db

router = APIRouter(prefix="/forms", tags=["forms"])

@router.post("/", response_model=FormResponse, summary="Создать новую форму")
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
            
            return await get_form_response(conn, form_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create form: {str(e)}")

@router.get("/", response_model=List[FormResponse], summary="Получить все формы")
async def get_forms(conn=Depends(get_db)):
    try:
        forms = await conn.fetch("SELECT id, title, description FROM forms ORDER BY created_at DESC")
        return [await get_form_response(conn, form["id"]) for form in forms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forms: {str(e)}")

@router.get("/{form_id}", response_model=FormResponse, summary="Получить форму по ID")
async def get_form(form_id: int, conn=Depends(get_db)):
    try:
        return await get_form_response(conn, form_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch form: {str(e)}")

@router.put("/{form_id}", response_model=FormResponse, summary="Обновить форму")
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
            
            return await get_form_response(conn, form_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update form: {str(e)}")

@router.delete("/{form_id}", summary="Удалить форму")
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
        raise HTTPException(status_code=500, detail=f"Failed to delete form: {str(e)}")

async def get_form_response(conn, form_id: int):
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