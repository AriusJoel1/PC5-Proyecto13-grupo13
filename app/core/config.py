import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env de la raíz del proyecto si existe
env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data.db")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")


settings = Settings()
