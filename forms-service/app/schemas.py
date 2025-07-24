from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

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