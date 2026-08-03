from app import create_app
from app.models.attraction import Attraction
import os

app = create_app()

# 图片映射表 - 根据命名规则匹配
photo_mapping = {
    'badalingchangcheng.jpg': '八达岭长城',
    'dongfangmingzhuta.jpg': '东方明珠塔',
    'gugong.jpg': '故宫',
    'kuanzhaixiangzi.jpg': '宽窄巷子',
    'lingyinsi.jpg': '灵隐寺',
    'tianzifang.jpg': '田子坊',
    'waitan.jpg': '外滩',
    'xihu.jpg': '西湖',
    'yuyuan.jpg': '豫园',
}

with app.app_context():
    photo_dir = r'D:\GCC\System\final\1\travel_planner\photo'
    
    for photo_file, keyword in photo_mapping.items():
        photo_path = os.path.join(photo_dir, photo_file)
        if not os.path.exists(photo_path):
            print(f'文件不存在: {photo_file}')
            continue
        
        # 查找匹配的景点
        attraction = Attraction.query.filter(Attraction.name.contains(keyword)).first()
        if attraction:
            attraction.image_url = f'/photo/{photo_file}'
            print(f'已更新: {attraction.name} -> {photo_file}')
        else:
            print(f'未找到匹配景点: {keyword}')

    from app.extensions import db
    db.session.commit()
    print('\n所有图片更新完成！')
