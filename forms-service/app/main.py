from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .database import lifespan
from .routers import forms

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

app.include_router(forms.router, prefix="/forms")