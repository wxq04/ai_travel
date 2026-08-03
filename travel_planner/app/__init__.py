from flask import Flask
from config import config
from app.extensions import db, login_manager, csrf, migrate, init_redis


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    init_redis(app)

    # 注册蓝图
    from app.blueprints.auth import auth_bp
    from app.blueprints.destinations import destinations_bp
    from app.blueprints.itineraries import itineraries_bp
    from app.blueprints.community import community_bp
    from app.blueprints.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(destinations_bp, url_prefix='/destinations')
    app.register_blueprint(itineraries_bp, url_prefix='/itineraries')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(ai_bp, url_prefix='/ai')

    # 注册首页路由
    @app.route('/')
    def index():
        from flask import render_template
        from app.models.destination import Destination
        from app.models.itinerary import Itinerary

        # 热门目的地（按浏览量排序）
        hot_destinations = Destination.query.order_by(Destination.view_count.desc()).limit(6).all()

        # 精选行程（公开行程，按点赞数排序）
        featured_itineraries = Itinerary.query.filter_by(is_public=True).order_by(
            Itinerary.like_count.desc()
        ).limit(6).all()

        return render_template('index.html',
                               hot_destinations=hot_destinations,
                               featured_itineraries=featured_itineraries)

    # 用户加载回调
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # 创建上传目录
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 初始化服务层
    from app.services.ai_service import init_ai_service
    from app.services.weather_service import init_weather_service
    from app.services.pdf_service import init_pdf_service

    init_ai_service(app)
    init_weather_service(app)
    init_pdf_service(app)

    return app