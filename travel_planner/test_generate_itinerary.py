# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, 'c:\\Users\\Administrator\\Downloads\\智能系统作业\\期末作业\\travel_planner')

os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app
from app.extensions import db
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.destination import Destination
from app.models.user import User

app = create_app('development')

with app.app_context():
    # 创建测试行程
    user = User.query.first()
    destination = Destination.query.filter_by(name='上海').first()
    
    if not user:
        print("No user found")
        sys.exit(1)
    
    if not destination:
        print("No destination found")
        sys.exit(1)
    
    print(f"User: {user.username}")
    print(f"Destination: {destination.name}")
    print()
    
    # 根据用户描述创建行程：4天上海都市摄影
    itinerary = Itinerary(
        user_id=user.id,
        title='上海都市摄影4日游',
        destination_id=destination.id,
        days_count=4,
        budget_level='舒适',
        is_public=True,
        ai_generated=True
    )
    db.session.add(itinerary)
    db.session.commit()
    
    # 创建活动模板
    activity_templates = {
        '景点': [
            {'name': '东方明珠塔', 'cost': 220, 'duration': 120, 'desc': '上海标志性建筑，俯瞰全城美景'},
            {'name': '外滩', 'cost': 0, 'duration': 90, 'desc': '上海著名的观光带，万国建筑博览'},
            {'name': '豫园', 'cost': 40, 'duration': 90, 'desc': '江南古典园林，体验传统韵味'},
            {'name': '上海博物馆', 'cost': 0, 'duration': 180, 'desc': '国家级博物馆，文物珍品众多'},
            {'name': '田子坊', 'cost': 0, 'duration': 120, 'desc': '文艺小资聚集地，充满艺术气息'},
            {'name': '上海迪士尼', 'cost': 599, 'duration': 480, 'desc': '童话乐园，亲子游玩胜地'},
            {'name': '陆家嘴', 'cost': 0, 'duration': 120, 'desc': '金融中心，现代都市风光'},
            {'name': '思南公馆', 'cost': 0, 'duration': 60, 'desc': '历史风貌区，名人故居云集'}
        ],
        '美食': [
            {'name': '上海菜体验', 'cost': 150, 'duration': 120, 'desc': '品尝地道上海本帮菜'},
            {'name': '小笼包早餐', 'cost': 60, 'duration': 60, 'desc': '特色早餐，蟹黄小笼包'},
            {'name': '外滩下午茶', 'cost': 200, 'duration': 90, 'desc': '优雅环境，精致点心'}
        ],
        '摄影': [
            {'name': '日出摄影', 'cost': 0, 'duration': 120, 'desc': '外滩日出美景拍摄'},
            {'name': '夜景摄影', 'cost': 0, 'duration': 150, 'desc': '上海璀璨夜景'},
            {'name': '建筑摄影', 'cost': 0, 'duration': 180, 'desc': '城市建筑风貌'}
        ]
    }
    
    # 为4天摄影行程创建活动
    days_activities = [
        # 第1天：外滩+摄影
        [('摄影', '日出摄影'), ('景点', '外滩'), ('摄影', '夜景摄影')],
        # 第2天：陆家嘴+东方明珠
        [('景点', '陆家嘴'), ('景点', '东方明珠塔'), ('摄影', '建筑摄影')],
        # 第3天：豫园+田子坊
        [('景点', '豫园'), ('景点', '田子坊'), ('美食', '小笼包早餐')],
        # 第4天：博物馆+思南公馆
        [('景点', '上海博物馆'), ('景点', '思南公馆'), ('美食', '上海菜体验')]
    ]
    
    total_cost = 0
    for day_num, activities in enumerate(days_activities, 1):
        day = ItineraryDay(
            itinerary_id=itinerary.id,
            day_number=day_num,
            theme=f"第{day_num}天：上海都市摄影之旅"
        )
        db.session.add(day)
        db.session.flush()
        
        for idx, (act_type, act_name) in enumerate(activities, 1):
            template = next((t for t in activity_templates[act_type] if t['name'] == act_name), None)
            if template:
                activity = DayActivity(
                    day_id=day.id,
                    order_index=idx,
                    activity_type=act_type,
                    name=template['name'],
                    description=template['desc'],
                    duration_minutes=template['duration'],
                    estimated_cost=template['cost']
                )
                db.session.add(activity)
                total_cost += template['cost']
    
    db.session.commit()
    
    print(f"行程创建成功！ID: {itinerary.id}")
    print(f"行程标题: {itinerary.title}")
    print(f"目的地: {destination.name}")
    print(f"天数: {itinerary.days_count}天")
    print(f"总费用: ¥{total_cost}")
    print()
    print("详细活动:")
    
    for day in itinerary.days:
        print(f"\n 第{day.day_number}天: {day.theme}")
        for activity in day.activities:
            print(f"    - {activity.activity_type}: {activity.name} (¥{activity.estimated_cost}, {activity.duration_minutes}分钟)")
    
    print(f"\n访问地址: http://127.0.0.1:5000/itineraries/{itinerary.id}")