# -*- coding: utf-8 -*-
from app import create_app
from app.extensions import db
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.destination import Destination
from app.models.user import User

app = create_app()
with app.app_context():
    # 检查行程
    itineraries = Itinerary.query.all()
    print(f'现有行程数量: {len(itineraries)}')
    for i in itineraries:
        print(f'{i.id}: {i.title} - {i.destination.name}')
    
    # 如果没有行程，创建测试数据
    if not itineraries:
        print('\n创建测试行程...')
        
        # 获取第一个用户和第一个目的地
        user = User.query.first()
        destination = Destination.query.first()
        
        if user and destination:
            # 创建测试行程
            itinerary = Itinerary(
                user_id=user.id,
                title=f'{destination.name}三日游',
                destination_id=destination.id,
                days_count=3,
                budget_level='舒适',
                is_public=True,
                ai_generated=True
            )
            db.session.add(itinerary)
            db.session.commit()
            
            # 添加天数和活动
            for day_num in range(1, 4):
                day = ItineraryDay(
                    itinerary_id=itinerary.id,
                    day_number=day_num,
                    theme=f'第{day_num}天 - {destination.name}经典游'
                )
                db.session.add(day)
                
                # 添加活动
                activity = DayActivity(
                    day_id=day.id,
                    order_index=1,
                    activity_type='景点',
                    name=f'{destination.name}热门景点',
                    description=f'{destination.name}著名旅游景点',
                    duration_minutes=120,
                    estimated_cost=100
                )
                db.session.add(activity)
            
            db.session.commit()
            print(f'创建成功！行程ID: {itinerary.id}')
        else:
            print('用户或目的地不存在')
