import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models.destination import Destination

app = create_app('development')
with app.app_context():
    destinations = Destination.query.all()
    print("检查图片 URL...")
    has_fix = False
    for d in destinations:
        if d.cover_image and d.cover_image.startswith('/static/uploads/'):
            print(f"修复 {d.name}: {d.cover_image}")
            d.cover_image = d.cover_image.replace('/static/uploads/', '')
            has_fix = True
    
    if has_fix:
        from app.extensions import db
        db.session.commit()
        print("修复完成！")
    else:
        print("没有需要修复的图片 URL")