from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    weather_api_key: str 
    llm_api_key: str
    llm_base_url: str
    llm_model_name: str
    sqlite_url: str
    postgres_url: str
settings = Settings()

