from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

# Inicializa o banco de dados
init_db()


app = FastAPI(
    title="API de Gestão de Projetos Imobiliários",
    description="API para gerenciamento de projetos e imóveis para construtoras",
    version="0.1.0",
)


app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Gestão de Projetos Imobiliários"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/print")
async def print_message():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, timeout_keep_alive=65) 