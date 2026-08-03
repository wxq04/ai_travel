# 数据库列迁移脚本
# 运行: python -c "from migrations.add_columns import add_columns; add_columns()"

from app import create_app
from app.extensions import db


def add_columns():
    """添加新的列到现有表"""
    app = create_app()

    with app.app_context():
        connection = db.engine.connect()

        # 检查 destinations 表是否需要添加 latitude 和 longitude
        try:
            connection.execute(db.text("SELECT latitude FROM destinations LIMIT 1"))
            print("destinations.latitude 列已存在")
        except Exception:
            print("添加 destinations.latitude 列...")
            connection.execute(db.text("ALTER TABLE destinations ADD COLUMN latitude FLOAT"))
            print("已添加 destinations.latitude")

        try:
            connection.execute(db.text("SELECT longitude FROM destinations LIMIT 1"))
            print("destinations.longitude 列已存在")
        except Exception:
            print("添加 destinations.longitude 列...")
            connection.execute(db.text("ALTER TABLE destinations ADD COLUMN longitude FLOAT"))
            print("已添加 destinations.longitude")

        # 检查 day_activities 表是否需要添加 latitude 和 longitude
        try:
            connection.execute(db.text("SELECT latitude FROM day_activities LIMIT 1"))
            print("day_activities.latitude 列已存在")
        except Exception:
            print("添加 day_activities.latitude 列...")
            connection.execute(db.text("ALTER TABLE day_activities ADD COLUMN latitude FLOAT"))
            print("已添加 day_activities.latitude")

        try:
            connection.execute(db.text("SELECT longitude FROM day_activities LIMIT 1"))
            print("day_activities.longitude 列已存在")
        except Exception:
            print("添加 day_activities.longitude 列...")
            connection.execute(db.text("ALTER TABLE day_activities ADD COLUMN longitude FLOAT"))
            print("已添加 day_activities.longitude")

        connection.commit()
        connection.close()

        print("\n列迁移完成！现在可以运行 seed_destinations 了。")


if __name__ == '__main__':
    add_columns()
