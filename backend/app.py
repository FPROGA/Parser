from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import nlp_processor
import database
import logging
from typing import Dict
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandidateData(BaseModel):
    first_name: str
    last_name: str
    hard_skills: Dict[str, int] # это же теперь словарь
    soft_skills: List[str]

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    logger.info(f"Получен файл: {file.filename}, тип: {file.content_type}")
    
    try:
        contents = await file.read()
        logger.info("Файл успешно прочитан")
        
        candidate_data = nlp_processor.process_resume(contents, file.filename)
        logger.info(f"Данные извлечены: {candidate_data}")
        
        db = database.Database()
        db.insert_candidate(candidate_data)
        logger.info("Данные сохранены в БД")
        
        return candidate_data
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        raise HTTPException(500, f"Internal server error: {str(e)}")