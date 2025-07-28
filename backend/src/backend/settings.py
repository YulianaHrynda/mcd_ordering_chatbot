from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Base paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = ROOT_DIR / "data"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Debug
    DEBUG: bool = False

settings = Settings()
