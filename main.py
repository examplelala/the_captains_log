from fastapi import FastAPI
from routes import register_routes
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import create_db_and_tables
from contextlib import asynccontextmanager
from utils.logger import logger, InterceptHandler
from service.embedding import load_model_sentence_transformers
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False
    
    logger.info("🚀 Starting FastAPI application...")
    await create_db_and_tables()
    load_model_sentence_transformers()
    yield
    logger.info("🛑 Shutting down FastAPI application...")

app=FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routes(app)
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(
        'main:app', 
        host="0.0.0.0", 
        port=18080,
        reload=True,
        log_config=None,
        access_log=True  # Explicitly enable access log
    )