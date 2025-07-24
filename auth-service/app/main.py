from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.api.endpoints.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service",
    description="Authentication service API",
    version="1.0.0",
    openapi_url="/api/auth/openapi.json",
    docs_url="/api/auth/docs",
    redoc_url="/api/auth/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/api/auth/health")
def health_check():
    return {"status": "OK"}