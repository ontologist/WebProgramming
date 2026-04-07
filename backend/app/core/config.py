from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Course
    COURSE_ID: str = "wp200"
    COURSE_NAME: str = "WP-200 Web Programming"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Database
    DATABASE_URL: str = "postgresql://wp200bot:wp200bot_password@localhost:5432/wp200bot"
    REDIS_URL: str = "redis://localhost:6379"

    # RAG
    CHROMA_DB_PATH: str = "./chroma_db"
    KNOWLEDGE_BASE_PATH: str = "./knowledge_base"

    # Server
    BACKEND_PORT: int = 8001

    # Instructor auth
    INSTRUCTOR_PASSWORD: str = "CHANGE_THIS_TO_A_SECURE_PASSWORD"
    JWT_SECRET: str = "CHANGE_THIS_TO_A_RANDOM_SECRET"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
