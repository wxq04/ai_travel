from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import redis

# 初始化数据库
db = SQLAlchemy()

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'

# CSRF 保护
csrf = CSRFProtect()

# 数据库迁移
migrate = Migrate()

# Redis 客户端（延迟初始化）
redis_client = None


def init_redis(app):
    """初始化 Redis 连接"""
    global redis_client
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        app.logger.info('Redis 连接成功')
    except Exception as e:
        app.logger.warning(f'Redis 连接失败: {e}')
        redis_client = None