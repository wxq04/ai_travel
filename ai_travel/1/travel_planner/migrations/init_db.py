# 数据库迁移脚本
# 运行: python -c "from migrations.init_db import init_db; init_db()"

from app import create_app
from app.extensions import db
from app.models.attraction import seed_attractions


def init_db():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")

        # 添加景点数据
        try:
            seed_attractions()
            print("景点数据添加完成")
        except Exception as e:
            print(f"景点数据添加失败: {e}")


if __name__ == '__main__':
    init_db()
