import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models.destination import Destination

app = create_app('development')
with app.app_context():
    print("=" * 60)
    print("目的地图片 URL 检查")
    print("=" * 60)
    destinations = Destination.query.all()
    for d in destinations:
        print(f"\n{d.name} ({d.category}):")
        print(f"  Cover: {d.cover_image}")
    print("=" * 60)