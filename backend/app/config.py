import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TYPESAFE_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    JEV_MODEL: str = "jev-1.13.0"
    MAX_RAG_RETRIES: int = 2

    CHROMA_DB_DIR: str = "./data/chroma"
    DOCUMENTS_DIR: str = "./data/documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
