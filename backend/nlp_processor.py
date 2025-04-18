import spacy
from pdfminer.high_level import extract_text
from docx import Document
import re
import io
from collections import defaultdict

try:
    nlp = spacy.load("ru_core_news_lg")
except OSError:
    print("Модель 'ru_core_news_lg' не найдена. Установите: python -m spacy download ru_core_news_lg")
    raise

HARD_SKILLS = [ 
    "Определения, история развития и главные тренды ИИ",
    "Процесс, стадии и методологии разработки решений на основе ИИ",
    "Статистические методы и первичный анализ данных",
    "Промпт-инжиниринг",
    "Инструменты CitizenDS",
    "Оценка качества работы методов ИИ",
    "Языки программирования и библиотеки",
    "Этика ИИ",
    "Безопасность ИИ",
    "Цифровые двойники",
    "Методы машинного обучения",
    "Методы оптимизации",
    "Информационный поиск",
    "Рекомендательные системы",
    "Анализ изображений и видео",
    "Анализ естественного языка",
    "Основы глубокого обучения",
    "Глубокое обучение для анализа и генерации изображений, видео",
    "Глубокое обучение для анализа и генерации естественного языка",
    "Обучение с подкреплением",
    "Гибридные модели и PIML",
    "Анализ геоданных",
    "Массово параллельные вычисления для ускорения машинного обучения (GPU)",
    "Работа с распределенной кластерной системой",
    "Машинное обучение на больших данных",
    "Потоковая обработка данных (data streaming, event processing)",
    "Графовые нейросети",
    "SQL базы данных (GreenPlum, Postgres, Oracle)",
    "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, NEO4J, Hbase)",
    "Массово параллельная обработка и анализ данных",
    "Hadoop, SPARK, Hive",
    "Шины данных (kafka)",
    "Качество и предобработка данных, подходы и инструменты",
    "Графы знаний и онтологии"
]

SKILL_SYNONYMS = {
    "Определения, история развития и главные тренды ИИ": ["ai trends", "история ИИ", "тренды ИИ"],
    "Процесс, стадии и методологии разработки решений на основе ИИ": ["ai development", "методологии ИИ", "разработка ИИ"],
    "Статистические методы и первичный анализ данных": ["статистика", "statistical analysis", "анализ данных"],
    "Промпт-инжиниринг": ["prompt engineering", "генерация промптов"],
    "Инструменты CitizenDS": ["citizen data science", "low-code ai"],
    "Оценка качества работы методов ИИ": ["ai evaluation", "качество ИИ"],
    "Языки программирования и библиотеки": ["python", "r", "программирование", "pandas", "numpy"],
    "Этика ИИ": ["ai ethics", "этика искусственного интеллекта"],
    "Безопасность ИИ": ["ai security", "безопасность данных"],
    "Цифровые двойники": ["digital twins", "виртуальные модели"],
    "Методы машинного обучения": ["machine learning", "ml", "нейросети"],
    "Методы оптимизации": ["optimization", "оптимизация моделей"],
    "Информационный поиск": ["information retrieval", "поиск данных"],
    "Рекомендательные системы": ["recommendation systems", "рекомендации"],
    "Анализ изображений и видео": ["computer vision", "обработка изображений"],
    "Анализ естественного языка": ["nlp", "natural language processing"],
    "Основы глубокого обучения": ["deep learning basics", "основы нейросетей"],
    "Глубокое обучение для анализа и генерации изображений, видео": ["deep learning vision", "генерация видео"],
    "Глубокое обучение для анализа и генерации естественного языка": ["deep learning nlp", "генерация текста"],
    "Обучение с подкреплением": ["reinforcement learning", "rl"],
    "Гибридные модели и PIML": ["hybrid models", "physics-informed ml"],
    "Анализ геоданных": ["geospatial analysis", "gis"],
    "Массово параллельные вычисления для ускорения машинного обучения (GPU)": ["gpu computing", "параллельные вычисления"],
    "Работа с распределенной кластерной системой": ["distributed systems", "кластеры"],
    "Машинное обучение на больших данных": ["big data ml", "обработка больших данных"],
    "Потоковая обработка данных (data streaming, event processing)": ["data streaming", "потоковая аналитика"],
    "Графовые нейросети": ["graph neural networks", "gnn"],
    "SQL базы данных (GreenPlum, Postgres, Oracle)": ["sql", "реляционные бд", "postgres", "oracle"],
    "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, NEO4J, Hbase)": ["nosql", "mongodb", "elasticsearch"],
    "Массово параллельная обработка и анализ данных": ["parallel processing", "распределенная аналитика"],
    "Hadoop, SPARK, Hive": ["hadoop", "spark", "hive", "big data"],
    "Шины данных (kafka)": ["kafka", "data buses"],
    "Качество и предобработка данных, подходы и инструменты": ["data preprocessing", "качество данных"],
    "Графы знаний и онтологии": ["knowledge graphs", "онтологии"]
}

SOFT_SKILLS_KEYWORDS = [
    "коммуникабельность", 
    "работа в команде", 
    "лидерство",
    "креативность", 
    "стрессоустойчивость",
    "аналитическое мышление",
    "тайм-менеджмент",
    "умение работать в многозадачном режиме",
    "пунктуальность",
    "ориентация на результат",
    "внимательность к деталям",
    "усидчивость", 
    "продуктивность",
    "работа с большими объемами данных",
    "навыки презентации",
    "техническое документирование",
    "кросс-функциональное взаимодействие",
    "управление требованиями"
]

STOP_WORDS = [
    "бизнес", "аналитик", "данные", "контактные", "адрес", "опыт", "работа", "стажировка", "возраст", "город", "должность", "зарплата", "обо", "мне", "навыки", "проекты", "образование", "языки", "специальность", "университет", "институт"
]

def extract_text_from_file(file_content, filename):
    """Извлекает текст из файла (PDF/DOCX)"""
    try:
        if filename.endswith('.pdf'):
            return extract_text(io.BytesIO(file_content))
        elif filename.endswith('.docx'):
            doc = Document(io.BytesIO(file_content))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ValueError(f"Неподдерживаемый формат: {filename}")
    except Exception as e:
        print(f"Ошибка чтения файла: {str(e)}")
        return ""

def preprocess_text(text):
    text = re.sub(r'\r\n|\r|\n', ' ', text)
    text = re.sub(r'•|\u2022|\d+\.', ' ', text)
    text = re.sub(r'[^\w\s.,-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def extract_name(raw_text):
    doc = nlp(raw_text)
    candidates = []


    first_lines = raw_text.split('\n')[:5]
    for line in first_lines:
        line = line.strip()
        if re.match(r'^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+$', line):
            return line
        if re.match(r'^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+$', line):
            return line

    patterns = [
        r"ФИО[:\-—]*\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)",
        r"Имя[:\-—]*\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)",
        r"Кандидат[:\-—]*\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)",
        r"Соискатель[:\-—]*\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)",
        r"Резюме[:\-—]*\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)"
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()


    for ent in doc.ents:
        if ent.label_ == "PER":
            parts = ent.text.split()
            if len(parts) >= 2 and len(parts) <= 3:
                if all(part[0].isupper() for part in parts):
                    if not any(stop_word in part.lower() for part in parts for stop_word in STOP_WORDS):
                        return ent.text.strip()


    patterns = [
        r"^([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)",
        r"^([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return "Не указано"

def extract_sections(text, section_names):
    sections = []
    for name in section_names:
        pattern = rf'(?i){re.escape(name)}[\s:-]+(.*?)(?=\n\s*[A-ZА-Я]|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections.append(match.group(1).strip())
    return sections

def find_skill_level(text, keyword):
    patterns = [
        (rf'\b{re.escape(keyword)}\b.*?(\d)\s*[—-]', lambda m: int(m.group(1))),
        (rf'\b(\d+)\s*(?:года|лет).*?{re.escape(keyword)}\b', lambda m: min(int(m.group(1)), 3)),
        (rf'\b{re.escape(keyword)}\b.*?(базов|начальн)', 1),
        (rf'\b{re.escape(keyword)}\b.*?(средн|опыт|реализовывал)', 2),
        (rf'\b{re.escape(keyword)}\b.*?(продвинут|эксперт|руководил)', 3),
    ]
    
    max_level = 0
    for pattern, level_func in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if callable(level_func):
                level = level_func(match)
            else:
                level = level_func
            max_level = max(max_level, level)
    return max_level if max_level > 0 else 2

def map_skills(text):
    found_skills = defaultdict(int)
    
    for skill in HARD_SKILLS:
        main_key = re.split(r'[,(]', skill)[0].strip().lower()
        
        if re.search(rf'\b{re.escape(main_key)}\b', text, re.IGNORECASE):
            level = find_skill_level(text, main_key)
            found_skills[skill] = max(found_skills[skill], level)
            
        if skill in SKILL_SYNONYMS:
            for variant in SKILL_SYNONYMS[skill]:
                if re.search(rf'\b{re.escape(variant)}\b', text, re.IGNORECASE):
                    level = find_skill_level(text, variant)
                    found_skills[skill] = max(found_skills.get(skill, 0), level)
                    
    return found_skills

def process_resume(file_content, filename):
    try:
        raw_text = extract_text_from_file(file_content, filename)
        if not raw_text:
            return {"error": "Не удалось извлечь текст"}
        
        text = preprocess_text(raw_text)
        full_name = extract_name(raw_text)
        
        sections = extract_sections(raw_text, [
            "Навыки", "Профессиональные навыки", 
            "Компетенции", "Технические навыки",
            "Опыт работы", "Проекты",
            "Дополнительные сведения"
        ])
        sections.append(text)  
        
        combined_skills = defaultdict(int)
        for section in sections:
            skills = map_skills(preprocess_text(section))
            for skill, level in skills.items():
                combined_skills[skill] = max(combined_skills[skill], level)

        soft_skills = list({
            skill
            for skill in SOFT_SKILLS_KEYWORDS
            if re.search(rf'\b{re.escape(skill.lower())}\b', text)
        })

        return {
            "full_name": full_name,
            "hard_skills": dict(combined_skills),
            "soft_skills": soft_skills
        }
        
    except Exception as e:
        print(f"Ошибка обработки резюме: {str(e)}")
        return {
            "full_name": "Не указано",
            "hard_skills": {},
            "soft_skills": []
        }