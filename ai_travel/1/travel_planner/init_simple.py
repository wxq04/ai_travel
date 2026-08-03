# -*- coding: utf-8 -*-
import sys
import os
import traceback

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

print("=" * 50)
print("数据库初始化开始...")
print("=" * 50)

try:
    print("1. Importing create_app...")
    from app import create_app
    print("   OK")

    print("2. Creating app...")
    app = create_app('development')
    print(f"   OK - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    print("3. Creating app context...")
    with app.app_context():
        print("   OK")

        print("4. Dropping all tables...")
        from app.extensions import db
        db.drop_all()
        print("   OK")

        print("5. Creating all tables...")
        db.create_all()
        print("   OK")

        print("6. Inserting destinations...")
        from app.models.destination import Destination
        import json

        destinations_data = [
            {"name": "北京", "country": "中国", "province": "北京市", "city": "北京市",
             "description": "北京是中华人民共和国的首都", "cover_image": "https://picsum.photos/seed/beijing/800/600",
             "images": json.dumps(["https://picsum.photos/seed/beijing1/800/600"]),
             "best_season": "春秋两季", "category": "历史", "avg_rating": 4.8, "view_count": 100},
            {"name": "上海", "country": "中国", "province": "上海市", "city": "上海市",
             "description": "上海是中国最大的城市", "cover_image": "https://picsum.photos/seed/shanghai/800/600",
             "images": json.dumps(["https://picsum.photos/seed/shanghai1/800/600"]),
             "best_season": "春秋两季", "category": "都市", "avg_rating": 4.7, "view_count": 100},
            {"name": "成都", "country": "中国", "province": "四川省", "city": "成都市",
             "description": "成都被誉为天府之国", "cover_image": "https://picsum.photos/seed/chengdu/800/600",
             "images": json.dumps(["https://picsum.photos/seed/chengdu1/800/600"]),
             "best_season": "春秋两季", "category": "美食", "avg_rating": 4.6, "view_count": 100},
            {"name": "大理", "country": "中国", "province": "云南省", "city": "大理市",
             "description": "大理风花雪月", "cover_image": "https://picsum.photos/seed/dali/800/600",
             "images": json.dumps(["https://picsum.photos/seed/dali1/800/600"]),
             "best_season": "3-5月", "category": "自然", "avg_rating": 4.7, "view_count": 100},
            {"name": "三亚", "country": "中国", "province": "海南省", "city": "三亚市",
             "description": "三亚是中国最著名的热带海滨旅游城市",
             "cover_image": "https://picsum.photos/seed/sanya/800/600",
             "images": json.dumps(["https://picsum.photos/seed/sanya1/800/600"]),
             "best_season": "11月-次年3月", "category": "海滨", "avg_rating": 4.5, "view_count": 100},
        ]

        for data in destinations_data:
            dest = Destination(**data)
            db.session.add(dest)

        db.session.commit()
        print(f"   OK - Inserted {len(destinations_data)} destinations")

        print("7. Verifying data...")
        count = Destination.query.count()
        print(f"   Destinations in DB: {count}")

    print("=" * 50)
    print("数据库初始化完成!")
    print("=" * 50)

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()