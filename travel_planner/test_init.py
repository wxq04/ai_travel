# -*- coding: utf-8 -*-
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Step 1: Loading dotenv...")
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))
print("Step 1: OK")

print("Step 2: Importing create_app...")
from app import create_app
print("Step 2: OK")

print("Step 3: Creating app...")
app = create_app('development')
print("Step 3: OK")

print("Step 4: Creating app context...")
with app.app_context():
    print("Step 4: OK")
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

    print("Step 5: Dropping all tables...")
    from app.extensions import db
    db.drop_all()
    print("Step 5: OK")

    print("Step 6: Creating all tables...")
    db.create_all()
    print("Step 6: OK")

    print("Step 7: Importing models...")
    from app.models.destination import Destination
    from app.models.user import User
    from app.models.social import Tag
    print("Step 7: OK")

    print("Step 8: Inserting destinations...")
    destinations_data = [
        {
            "name": "北京",
            "country": "中国",
            "province": "北京市",
            "city": "北京市",
            "description": "北京是中华人民共和国的首都",
            "cover_image": "https://picsum.photos/seed/beijing/800/600",
            "images": '[]',
            "best_season": "春秋两季",
            "category": "历史",
            "avg_rating": 4.8,
            "view_count": 100
        },
        {
            "name": "上海",
            "country": "中国",
            "province": "上海市",
            "city": "上海市",
            "description": "上海是中国最大的城市和经济中心",
            "cover_image": "https://picsum.photos/seed/shanghai/800/600",
            "images": '[]',
            "best_season": "春秋两季",
            "category": "都市",
            "avg_rating": 4.7,
            "view_count": 100
        }
    ]

    for data in destinations_data:
        destination = Destination(**data)
        db.session.add(destination)

    db.session.commit()
    print(f"Step 8: Inserted {len(destinations_data)} destinations")

    count = Destination.query.count()
    print(f"Total destinations in DB: {count}")

print("Done!")