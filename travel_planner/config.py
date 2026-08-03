import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # MySQL 数据库配置
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+pymysql://1:root1234@localhost:3306/travel'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # CSRF配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_SSL_STRICT = False

    # AI 接口配置（支持替换为讯飞星火、百度文心等兼容 OpenAI 格式的接口）
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_API_SECRET = os.getenv('AI_API_SECRET', '')
    AI_API_FID = os.getenv('AI_API_FID', '')
    AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://api.openai.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')

    # 天气 API（和风天气）
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

    # 高德地图 API
    AMAP_KEY = os.getenv('AMAP_KEY', '')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}