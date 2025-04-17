from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import nlp_processor
import database
import recommendations
import logging
from collections import Counter
import requests
import time
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    logger.info(f"Загрузка файла: {file.filename}")
    
    db = database.Database()
    
    try:
        content = await file.read()
        print("Начало обработки резюме")
        candidate_data = nlp_processor.process_resume(content, file.filename)
        print("Резюме обработано:", candidate_data)
        
        candidate_id = db.insert_candidate(candidate_data)
        print("Кандидат сохранен, ID:", candidate_id)
        
        recommendation_data = recommendations.get_recommendations({"id": candidate_id}, db)
        if recommendation_data["roles"]:
            best_profession = recommendation_data["roles"][0]
            db.update_candidate_profession(
                candidate_id,
                best_profession["name"],
                best_profession["match_percent"]
            )
        return {
            "candidate": {
                "id": candidate_id,
                "full_name": candidate_data["full_name"],
                "hard_skills": candidate_data["hard_skills"],
                "soft_skills": candidate_data["soft_skills"]
            },
            "recommendation": recommendation_data
        }
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке резюме: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.get("/get-recommendations/{candidate_id}")
async def get_recommendations_endpoint(candidate_id: int):
    try:
        db = database.Database()
        recommendations_data = recommendations.get_recommendations({"id": candidate_id}, db)
        return recommendations_data
        
    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    
@app.get("/get-analytics/")
async def get_analytics():
    """Возвращает аналитику по резюме из базы данных"""
    try:
        db = database.Database()
        
        with db.conn.cursor() as cur:

            cur.execute("SELECT COUNT(*) FROM candidates")
            total_resumes = cur.fetchone()[0]

            cur.execute("SELECT hard_skills FROM candidates WHERE hard_skills IS NOT NULL")
            resumes = cur.fetchall()

        if total_resumes == 0:
            return {"message": "В базе нет данных о резюме"}

        hard_skills_counter = Counter()
        for resume in resumes:
            if resume[0]:  
                for skill in resume[0].keys():
                    hard_skills_counter[skill] += 1

        # Формируем топ-5 навыков
        top_hard_skills = [
            {"skill": skill, "count": count} 
            for skill, count in hard_skills_counter.most_common(5)
        ]
        
        return {
            "total_resumes": total_resumes,
            "top_hard_skills": top_hard_skills
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении аналитики: {str(e)}"
        )
@app.get("/get-vacancies-analytics/")
async def get_vacancies_analytics():
    """Анализирует вакансии с HeadHunter API"""
    try:
        professions = {
            "Аналитик данных": '(аналитик данных OR data scientist OR ml engineer) NOT "SEO"',
            "Инженер данных": '(инженер данных OR data engineer) NOT "web"',
            "Тех. аналитик в ИИ": '(технический аналитик OR technical analyst OR AI analyst)',
            "Менеджер в ИИ": '(менеджер OR manager) AND (AI OR "искусственный интеллект")'
        }

        results = []
        
        for profession_name, search_query in professions.items():
            print(f"Анализируем вакансии для: {profession_name}...")
            params = {
                "text": search_query,
                "area": 1, 
                "per_page": 100,
                "search_field": "name"
            }

            response = requests.get("https://api.hh.ru/vacancies", params=params)
            data = response.json()
            df = pd.DataFrame(data['items'])

            all_skills = []
            for vacancy_id in df['id'][:20]:  
                try:
                    response = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')
                    vacancy_data = response.json()
                    skills = [skill['name'] for skill in vacancy_data.get('key_skills', [])]
                    all_skills.extend(skills)
                    time.sleep(0.1)  
                except Exception as e:
                    print(f"Ошибка при получении вакансии {vacancy_id}: {e}")
                    continue

            skill_counter = Counter(all_skills)
            top_skills = [{"skill": skill, "count": count} for skill, count in skill_counter.most_common(10)]
            
            results.append({
                "profession": profession_name,
                "vacancies_count": len(df),
                "top_skills": top_skills,
                "total_skills": len(all_skills),
                "unique_skills": len(skill_counter)
            })

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе вакансий: {str(e)}"
        )
@app.get("/get-top-candidates/")
async def get_top_candidates():
    try:
        db = database.Database()
        
        with db.conn.cursor() as cur:
            professions =[
            "Аналитик данных",
            "Инженер данных",
            "Технический аналитик в ИИ",
            "Менеджер в ИИ"
            ]
            top_candidates = {}
            print("Starting get_top_candidates")
            print("Professions to check:", professions)
            for profession in professions:
                cur.execute("""
                    SELECT id, full_name, percent 
                    FROM candidates 
                    WHERE profession = %s 
                    ORDER BY percent DESC 
                    LIMIT 1
                """, (profession,))
                result = cur.fetchone()
                
                if result:  
                    top_candidates[profession] = {
                        "id": result[0],
                        "full_name": result[1],
                        "percent": result[2]
                    }
            
            return top_candidates
            
    except Exception as e:
        print(f"Ошибка в get_top_candidates: {str(e)}")  
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении топ кандидатов: {str(e)}"
        )