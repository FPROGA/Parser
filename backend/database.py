import psycopg2
import psycopg2.extras
import json
import pandas as pd
from psycopg2 import sql

SKILLS_MAPPING = {
    "Определения, история развития и главные тренды ИИ": "ai_definitions_history_trends",
    "Процесс, стадии и методологии разработки решений на основе ИИ": "ai_development_process",
    "Статистические методы и первичный анализ данных": "statistical_methods",
    "Промпт-инжиниринг": "prompt_engineering",
    "Инструменты CitizenDS": "citizen_ds_tools",
    "Оценка качества работы методов ИИ": "ai_methods_quality_assessment",
    "Языки программирования и библиотеки": "programming_languages",
    "Этика ИИ": "ai_ethics",
    "Безопасность ИИ": "ai_security",
    "Цифровые двойники": "digital_twins",
    "Методы машинного обучения": "machine_learning_methods",
    "Методы оптимизации": "optimization_methods",
    "Информационный поиск": "information_retrieval",
    "Рекомендательные системы": "recommendation_systems",
    "Анализ изображений и видео": "image_video_analysis",
    "Анализ естественного языка": "natural_language_analysis",
    "Основы глубокого обучения": "deep_learning_basics",
    "Глубокое обучение для анализа и генерации изображений, видео": "deep_learning_image_video",
    "Глубокое обучение для анализа и генерации естественного языка": "deep_learning_nlp",
    "Обучение с подкреплением": "reinforcement_learning",
    "Гибридные модели и PIML": "hybrid_models_piml",
    "Анализ геоданных": "geodata_analysis",
    "Массово параллельные вычисления для ускорения машинного обучения (GPU)": "gpu_computing",
    "Работа с распределенной кластерной системой": "distributed_cluster_systems",
    "Машинное обучение на больших данных": "big_data_ml",
    "Потоковая обработка данных (data streaming, event processing)": "data_streaming",
    "Графовые нейросети": "graph_neural_networks",
    "SQL базы данных (GreenPlum, Postgres, Oracle)": "sql_databases",
    "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, NEO4J, Hbase)": "nosql_databases",
    "Массово параллельная обработка и анализ данных": "parallel_data_processing",
    "Hadoop, SPARK, Hive": "hadoop_spark_hive",
    "Шины данных (kafka)": "data_buses_kafka",
    "Качество и предобработка данных, подходы и инструменты": "data_quality_preprocessing",
    "Графы знаний и онтологии": "knowledge_graphs_ontologies"
}

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="parser",
                user="postgres",
                password="TemaiSofaBF1!",
                host="localhost",
                port="5433"
            )
            print("✅ Успешное подключение к PostgreSQL!")
            self._create_tables_if_not_exists()
        except Exception as e:
            print(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise

    def _create_tables_if_not_exists(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(100),
                    hard_skills JSONB,
                    soft_skills TEXT[],
                    profession VARCHAR(100),
                    percent DECIMAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS skills_matrix (
                    id SERIAL PRIMARY KEY,
                    profession VARCHAR(100) UNIQUE NOT NULL,
                    ai_definitions_history_trends INT NOT NULL,
                    ai_development_process INT NOT NULL,
                    statistical_methods INT NOT NULL,
                    prompt_engineering INT NOT NULL,
                    citizen_ds_tools INT NOT NULL,
                    ai_methods_quality_assessment INT NOT NULL,
                    programming_languages INT NOT NULL,
                    ai_ethics INT NOT NULL,
                    ai_security INT NOT NULL,
                    digital_twins INT NOT NULL,
                    machine_learning_methods INT NOT NULL,
                    optimization_methods INT NOT NULL,
                    information_retrieval INT NOT NULL,
                    recommendation_systems INT NOT NULL,
                    image_video_analysis INT NOT NULL,
                    natural_language_analysis INT NOT NULL,
                    deep_learning_basics INT NOT NULL,
                    deep_learning_image_video INT NOT NULL,
                    deep_learning_nlp INT NOT NULL,
                    reinforcement_learning INT NOT NULL,
                    hybrid_models_piml INT NOT NULL,
                    geodata_analysis INT NOT NULL,
                    gpu_computing INT NOT NULL,
                    distributed_cluster_systems INT NOT NULL,
                    big_data_ml INT NOT NULL,
                    data_streaming INT NOT NULL,
                    graph_neural_networks INT NOT NULL,
                    sql_databases INT NOT NULL,
                    nosql_databases INT NOT NULL,
                    parallel_data_processing INT NOT NULL,
                    hadoop_spark_hive INT NOT NULL,
                    data_buses_kafka INT NOT NULL,
                    data_quality_preprocessing INT NOT NULL,
                    knowledge_graphs_ontologies INT NOT NULL
                );
            """)
            self.conn.commit()

        self._insert_initial_data()

    def _insert_initial_data(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM skills_matrix")
            if cur.fetchone()[0] > 0:
                print("⏩ Таблица skills_matrix уже заполнена, пропускаем вставку")
                return

        columns = [
            'profession', 'ai_definitions_history_trends', 'ai_development_process',
            'statistical_methods', 'prompt_engineering', 'citizen_ds_tools',
            'ai_methods_quality_assessment', 'programming_languages', 'ai_ethics',
            'ai_security', 'digital_twins', 'machine_learning_methods',
            'optimization_methods', 'information_retrieval', 'recommendation_systems',
            'image_video_analysis', 'natural_language_analysis', 'deep_learning_basics',
            'deep_learning_image_video', 'deep_learning_nlp', 'reinforcement_learning',
            'hybrid_models_piml', 'geodata_analysis', 'gpu_computing',
            'distributed_cluster_systems', 'big_data_ml', 'data_streaming',
            'graph_neural_networks', 'sql_databases', 'nosql_databases',
            'parallel_data_processing', 'hadoop_spark_hive', 'data_buses_kafka',
            'data_quality_preprocessing', 'knowledge_graphs_ontologies'
        ]

        data = [
            ('Аналитик данных', 1, 2, 2, 0, 0, 2, 2, 0, 0, 0, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 2, 0),
            ('Инженер данных', 1, 2, 1, 0, 0, 1, 2, 0, 0, 0, 2, 1, 1, 0, 1, 1, 2, 2, 2, 0, 0, 0, 1, 2, 2, 2, 0, 3, 3, 2, 2, 0, 3, 0),
            ('Технический аналитик в ИИ', 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0),
            ('Менеджер в ИИ', 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0)
        ]

        insert_query = sql.SQL("""
            INSERT INTO skills_matrix ({})
            VALUES %s
            ON CONFLICT (profession) DO NOTHING
        """).format(sql.SQL(', ').join(map(sql.Identifier, columns)))

        with self.conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                insert_query.as_string(cur.connection),
                data
            )
            self.conn.commit()
        print("✅ Начальные данные skills_matrix успешно добавлены")

    def insert_candidate(self, data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO candidates
                (full_name, hard_skills, soft_skills)
                VALUES (%s, %s::jsonb, %s::text[])
                RETURNING id
            """, (
                data["full_name"],
                json.dumps(data["hard_skills"]),
                data["soft_skills"]
            ))
            candidate_id = cur.fetchone()[0]
            self.conn.commit()
            return candidate_id

    def get_skills_matrix(self, role):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM skills_matrix WHERE profession = %s", (role,))
            columns = [desc[0] for desc in cur.description]
            result = cur.fetchone()
            if not result:
                return {}
            row_dict = dict(zip(columns, result))
            required_skills = {}
            for skill_name, db_column in SKILLS_MAPPING.items():
                if db_column in row_dict:
                    required_skills[skill_name] = row_dict[db_column]
            return required_skills

    def get_all_roles(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT profession FROM skills_matrix")
            return [row[0] for row in cur.fetchall()]

    def load_skills_matrix_from_excel(self, file_path='skills_matrix.xlsx'):
        try:
            df = pd.read_excel(file_path, index_col=0)
            with self.conn.cursor() as cur:
                for role in df.columns:
                    for skill, level in df[role].dropna().items():
                        cur.execute("""
                            INSERT INTO skills_matrix (profession, {}) 
                            VALUES (%s, %s)
                            ON CONFLICT (profession) DO NOTHING
                        """.format(sql.Identifier(skill).string),
                        (role, int(level)))
                self.conn.commit()
            print("✅ Матрица компетенций загружена в базу данных!")
        except Exception as e:
            print(f"❌ Ошибка загрузки матрицы компетенций: {e}")

    def get_last_candidate(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, hard_skills, soft_skills, created_at
                FROM candidates
                ORDER BY created_at DESC
                LIMIT 1
            """)
            result = cur.fetchone()
            if result:
                candidate = {
                    "id": result[0],
                    "full_name": result[1],
                    "hard_skills": result[2],
                    "soft_skills": result[3],
                    "created_at": result[4],
                }
                return candidate
            return None

    def get_user_skills(self, candidate_id: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT hard_skills, soft_skills
                FROM candidates
                WHERE id = %s
            """, (candidate_id,))
            result = cur.fetchone()
            return {
                "hard_skills": result[0] if result else {},
                "soft_skills": result[1] if result else []
            } if result else {"hard_skills": {}, "soft_skills": []}
    
    def update_candidate_profession(self, candidate_id: int, profession: str, percent: float):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE candidates
                SET profession = %s, percent = %s
                WHERE id = %s
            """, (profession, percent, candidate_id))
            self.conn.commit()


if __name__ == "__main__":
    db = Database()
    db.load_skills_matrix_from_excel()
