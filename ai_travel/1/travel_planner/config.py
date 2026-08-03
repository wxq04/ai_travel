import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'travel_planner.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # CSRF配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_SSL_STRICT = False

    # AI 接口配置（支持 Deepseek/讯飞星火/百度文心等兼容 OpenAI 格式的接口）
    # 推荐使用 Deepseek API（免费额度大，价格低）
    # Deepseek官网: https://platform.deepseek.com/
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_API_SECRET = os.getenv('AI_API_SECRET', '')
    AI_API_FID = os.getenv('AI_API_FID', '')
    AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://api.deepseek.com/v1')  # 默认使用Deepseek
    AI_MODEL = os.getenv('AI_MODEL', 'deepseek-chat')  # 默认模型

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