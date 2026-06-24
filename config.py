import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'chat_memory.db')
    
    # LLM Configuration
    LLM_MODEL = 'gpt-4o-mini'
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 1500
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'pt': 'Portuguese',
    }
    
    # Flask Configuration
    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
    TESTING = False
    
    # Ensure API key is configured
    @staticmethod
    def validate_config():
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
