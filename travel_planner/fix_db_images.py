import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models.destination import Destination
from app.extensions import db

app = create_app('development')
with app.app_context():
    # 检查所有目的地的图片 URL
    destinations = Destination.query.all()
    print("检查数据库中的图片 URL：")
    for d in destinations:
        print(f"{d.name}: {d.cover_image[:60]}...")
    
    # 修复所有带有错误前缀的 URL
    print("\n修复错误的图片 URL...")
    fixed_count = 0
    for d in destinations:
        if d.cover_image and ('/static/uploads/' in d.cover_image or 'source.unsplash.com' not in d.cover_image):
            # 设置正确的图片 URL
            urls = {
                '北京': 'https://source.unsplash.com/800x600/?beijing,forbidden-city',
                '上海': 'https://source.unsplash.com/800x600/?shanghai,cityscape',
                '成都': 'https://source.unsplash.com/800x600/?chengdu,panda',
                '拉萨': 'https://source.unsplash.com/800x600/?tibet,monastery',
                '大理': 'https://source.unsplash.com/800x600/?dali,ancient-town',
                '三亚': 'https://source.unsplash.com/800x600/?sanya,beach',
                '桂林': 'https://source.unsplash.com/800x600/?guilin,mountains',
                '杭州': 'https://source.unsplash.com/800x600/?hangzhou,west-lake',
                '厦门': 'https://source.unsplash.com/800x600/?xiamen,island',
                '张家界': 'https://source.unsplash.com/800x600/?zhangjiajie,forest'
            }
            if d.name in urls:
                d.cover_image = urls[d.name]
                print(f"修复: {d.name} -> {d.cover_image}")
                fixed_count += 1
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n已修复 {fixed_count} 个目的地的图片 URL")
    else:
        print("\n没有需要修复的图片 URL")