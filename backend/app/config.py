"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application
    app_name: str = "医药市场画像与策略生成系统"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./pharma.db"
    
    # Dify API (for future AI integration)
    dify_api_key: str = ""
    dify_api_url: str = ""
    
    # Data paths
    raw_data_path: str = r"E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cache and return application settings.
    """
    return Settings()
