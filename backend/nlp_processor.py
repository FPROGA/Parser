import spacy
from pdfminer.high_level import extract_text
from docx import Document
import io
import re

# Загружаю модель Spacy для русского языка
nlp = spacy.load("ru_core_news_lg")

# Список хард скилов из таблицы
HARD_SKILLS = [
    # ИИ и методологии
    "Искусственный интеллект", "AI", "Machine Learning", "ML", 
    "Deep Learning", "нейросети", "Computer Vision", "NLP",
    "Prompt Engineering", "Промпт-инжиниринг", "CitizenDS",
    "Этика ИИ", "Безопасность ИИ", "Цифровые двойники",
    
    # Инфраструктура
    "Docker", "Kubernetes", "Linux", "Bash", "Git",
    "Hadoop", "Spark", "Kafka", "Hive", "GPU",
    
    # Языки и библиотеки
    "Python", "C++", "TensorFlow", "PyTorch", "Scikit-learn",
    "OpenCV", "NLTK", "spaCy", "Pandas", "NumPy",
    
    # Базы данных
    "SQL", "PostgreSQL", "GreenPlum", "Oracle", 
    "NoSQL", "MongoDB", "Cassandra", "ElasticSearch", "Neo4j", "HBase",
    
    # Обработка данных
    "Data Mining", "Data Streaming", "ETL", 
    "OLAP", "Data Warehousing", "Graph Processing",
    
    # Специализированные методы
    "Reinforcement Learning", "Обучение с подкреплением",
    "Recommendation Systems", "Рекомендательные системы",
    "Knowledge Graphs", "Графы знаний", "Ontologies", "Онтологии",
    "Geospatial Analysis", "Анализ геоданных"
]

SOFT_SKILLS_KEYWORDS = [
    "коммуникабельность", "общительность", "работа в команде",
    "лидерство", "креативность", "адаптивность", "стрессоустойчивость",
    "тайм-менеджмент", "управление временем", "организованность",
    "критическое мышление", "аналитические способности", 
    "решение проблем", "пунктуальность", "ответственность",
    "эмоциональный интеллект", "умение убеждать", "публичные выступления",
    "наставничество", "обучаемость", "инициативность"
]

def extract_text_from_file(file_content, filename):
    if filename.endswith('.pdf'):
        return extract_text(io.BytesIO(file_content))
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(file_content))
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

def find_skill_level(text, skill):
    """Ищет уровень владения навыком в тексте"""
    patterns = [
        rf"{skill}\s*[—-]\s*(\d)",      # "SQL - 3" или "SQL — 3"
        rf"{skill}\s*(\d)\b",           # "SQL 3"
        rf"уровень\s*{skill}\s*(\d)",   # "уровень SQL 3"
        rf"знание\s*{skill}\s*(\d)"     # "знание SQL 3"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                level = int(match.group(1))
                return max(1, min(3, level))  # Ограничиваею уровень 1-3
            except (ValueError, IndexError):
                continue
    return 2  # Значение по умолчанию

def process_resume(file_content, filename):
    # Извлекаю текст
    text = extract_text_from_file(file_content, filename)
    doc = nlp(text)
    
    # Извлекаю имя и фамилию
    names = [ent.text for ent in doc.ents if ent.label_ == "PER"]
    first_name, last_name = (names[0].split() + [""]*2)[:2] if names else ("", "")
    
    # Извлекаю хард скилы с уровнями
    found_hard_skills = {}
    for skill in HARD_SKILLS:
        if skill.lower() in text.lower():
            level = find_skill_level(text, skill)
            found_hard_skills[skill] = level
    
    # Извлекаю софт скилы 
    found_soft_skills = list(set(
        skill for skill in SOFT_SKILLS_KEYWORDS 
        if skill.lower() in text.lower()
    ))
    return {
        "first_name": first_name,
        "last_name": last_name,
        "hard_skills": found_hard_skills,
        "soft_skills": found_soft_skills
    }