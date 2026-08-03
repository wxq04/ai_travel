# -*- coding: utf-8 -*-
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.destination import Destination
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.social import Comment, Like, Favorite, Tag
import json

app = create_app('development')
with app.app_context():
    print('开始初始化数据库...')

    # 清空现有数据
    db.session.query(DayActivity).delete()
    db.session.query(ItineraryDay).delete()
    db.session.query(Comment).delete()
    db.session.query(Like).delete()
    db.session.query(Favorite).delete()
    db.session.query(Itinerary).delete()
    db.session.query(Destination).delete()
    db.session.query(User).delete()
    db.session.query(Tag).delete()
    db.session.commit()
    print('已清空旧数据')

    # 创建测试用户
    users = [
        User(username='admin', email='admin@example.com'),
        User(username='test', email='test@example.com'),
    ]
    users[0].set_password('Admin123456')
    users[1].set_password('Test123456')

    for user in users:
        db.session.add(user)
    db.session.commit()
    print(f'创建用户: {len(users)}个')

    # 创建目的地
    destinations_data = [
        {
            'name': '北京',
            'country': '中国',
            'province': '北京市',
            'city': '北京',
            'description': '中国的首都，拥有故宫、长城等世界文化遗产，是一座充满历史底蕴的现代化大都市。',
            'cover_image': '/static/images/beijing.jpg',
            'images': json.dumps([
                '/static/images/beijing1.jpg',
                '/static/images/beijing2.jpg',
                '/static/images/beijing3.jpg'
            ], ensure_ascii=False),
            'best_season': '春秋两季',
            'category': '历史',
            'view_count': 1000
        },
        {
            'name': '上海',
            'country': '中国',
            'province': '上海市',
            'city': '上海',
            'description': '中国最大的城市之一，东方明珠、外滩等标志性建筑展现了这座国际化大都市的魅力。',
            'cover_image': '/static/images/shanghai.jpg',
            'images': json.dumps([
                '/static/images/shanghai1.jpg',
                '/static/images/shanghai2.jpg',
                '/static/images/shanghai3.jpg'
            ], ensure_ascii=False),
            'best_season': '春秋两季',
            'category': '都市',
            'view_count': 950
        },
        {
            'name': '杭州',
            'country': '中国',
            'province': '浙江省',
            'city': '杭州',
            'description': '西湖美景闻名天下，素有"人间天堂"之称，是中国最著名的旅游城市之一。',
            'cover_image': '/static/images/hangzhou.jpg',
            'images': json.dumps([
                '/static/images/hangzhou1.jpg',
                '/static/images/hangzhou2.jpg',
                '/static/images/hangzhou3.jpg'
            ], ensure_ascii=False),
            'best_season': '春季',
            'category': '自然',
            'view_count': 800
        },
        {
            'name': '成都',
            'country': '中国',
            'province': '四川省',
            'city': '成都',
            'description': '天府之国，大熊猫的故乡，以悠闲的生活方式和美味的川菜闻名。',
            'cover_image': '/static/images/chengdu.jpg',
            'images': json.dumps([
                '/static/images/chengdu1.jpg',
                '/static/images/chengdu2.jpg',
                '/static/images/chengdu3.jpg'
            ], ensure_ascii=False),
            'best_season': '春秋两季',
            'category': '美食',
            'view_count': 750
        },
        {
            'name': '三亚',
            'country': '中国',
            'province': '海南省',
            'city': '三亚',
            'description': '中国最南端的热带滨海旅游城市，拥有亚龙湾、天涯海角等著名景点。',
            'cover_image': '/static/images/sanya.jpg',
            'images': json.dumps([
                '/static/images/sanya1.jpg',
                '/static/images/sanya2.jpg',
                '/static/images/sanya3.jpg'
            ], ensure_ascii=False),
            'best_season': '冬季',
            'category': '海滨',
            'view_count': 700
        },
        {
            'name': '西安',
            'country': '中国',
            'province': '陕西省',
            'city': '西安',
            'description': '十三朝古都，兵马俑、大雁塔等历史遗迹见证了中华文明的辉煌。',
            'cover_image': '/static/images/xian.jpg',
            'images': json.dumps([
                '/static/images/xian1.jpg',
                '/static/images/xian2.jpg',
                '/static/images/xian3.jpg'
            ], ensure_ascii=False),
            'best_season': '春秋两季',
            'category': '历史',
            'view_count': 650
        },
    ]

    destinations = []
    for data in destinations_data:
        dest = Destination(**data)
        destinations.append(dest)
        db.session.add(dest)
    db.session.commit()
    print(f'创建目的地: {len(destinations)}个')

    # 创建标签
    tags_data = [
        {'name': '美食', 'category': '兴趣', 'icon': 'fa-utensils'},
        {'name': '历史', 'category': '兴趣', 'icon': 'fa-landmark'},
        {'name': '自然', 'category': '兴趣', 'icon': 'fa-tree'},
        {'name': '购物', 'category': '兴趣', 'icon': 'fa-shopping-bag'},
        {'name': '摄影', 'category': '兴趣', 'icon': 'fa-camera'},
        {'name': '休闲', 'category': '兴趣', 'icon': 'fa-coffee'},
    ]

    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.session.add(tag)
    db.session.commit()
    print(f'创建标签: {len(tags_data)}个')

    # 创建示例行程
    user = users[0]  # admin用户
    dest = destinations[0]  # 北京

    itinerary = Itinerary(
        user_id=user.id,
        title='北京三日精华游',
        destination_id=dest.id,
        days_count=3,
        budget_level='舒适',
        interest_tags=json.dumps(['历史', '美食'], ensure_ascii=False),
        is_public=True,
        ai_generated=True,
        like_count=42,
        view_count=156
    )
    db.session.add(itinerary)
    db.session.commit()

    # 创建行程天数和活动
    days_data = [
        {
            'day_number': 1,
            'theme': '第一天 - 皇城根下的历史',
            'activities': [
                {
                    'activity_type': '景点',
                    'name': '故宫博物院',
                    'description': '中国最大的古代文化艺术博物馆，明清两代的皇宫',
                    'location': '北京市东城区景山前街4号',
                    'duration_minutes': 180,
                    'estimated_cost': 60,
                    'tip': '建议提前网上预约门票，避开节假日高峰'
                },
                {
                    'activity_type': '餐厅',
                    'name': '全聚德烤鸭店',
                    'description': '中华老字号，北京烤鸭的代表',
                    'location': '前门大街30号',
                    'duration_minutes': 90,
                    'estimated_cost': 200,
                    'tip': '建议提前预订座位'
                },
                {
                    'activity_type': '景点',
                    'name': '景山公园',
                    'description': '可以俯瞰故宫全景的最佳位置',
                    'location': '景山西街44号',
                    'duration_minutes': 60,
                    'estimated_cost': 2,
                    'tip': '日落时分景色最美'
                }
            ]
        },
        {
            'day_number': 2,
            'theme': '第二天 - 长城雄风',
            'activities': [
                {
                    'activity_type': '景点',
                    'name': '八达岭长城',
                    'description': '万里长城的重要组成部分，景色壮观',
                    'location': '延庆区军都山关沟古道北口',
                    'duration_minutes': 240,
                    'estimated_cost': 40,
                    'tip': '建议早起出发，避开人流高峰'
                },
                {
                    'activity_type': '餐厅',
                    'name': '长城脚下的农家菜',
                    'description': '品尝地道的延庆农家美食',
                    'location': '八达岭镇',
                    'duration_minutes': 60,
                    'estimated_cost': 80,
                    'tip': '推荐柴鸡炖蘑菇和农家豆腐'
                }
            ]
        },
        {
            'day_number': 3,
            'theme': '第三天 - 胡同文化',
            'activities': [
                {
                    'activity_type': '景点',
                    'name': '南锣鼓巷',
                    'description': '北京最古老的街区之一，充满老北京风情',
                    'location': '东城区南锣鼓巷',
                    'duration_minutes': 120,
                    'estimated_cost': 0,
                    'tip': '可以购买一些特色手工艺品'
                },
                {
                    'activity_type': '餐厅',
                    'name': '护国寺小吃',
                    'description': '品尝正宗北京传统小吃',
                    'location': '护国寺大街',
                    'duration_minutes': 60,
                    'estimated_cost': 50,
                    'tip': '推荐豆汁、焦圈、驴打滚'
                },
                {
                    'activity_type': '景点',
                    'name': '什刹海',
                    'description': '老北京风貌保存最完好的地区',
                    'location': '西城区什刹海',
                    'duration_minutes': 90,
                    'estimated_cost': 0,
                    'tip': '可以体验人力三轮车游胡同'
                }
            ]
        }
    ]

    for day_data in days_data:
        activities_data = day_data.pop('activities')
        day = ItineraryDay(itinerary_id=itinerary.id, **day_data)
        db.session.add(day)
        db.session.commit()

        for idx, activity_data in enumerate(activities_data):
            activity = DayActivity(
                day_id=day.id,
                order_index=idx + 1,
                **activity_data
            )
            db.session.add(activity)
        db.session.commit()

    print(f'创建行程: {itinerary.title}')
    print(f'  - 天数: {len(days_data)}天')
    # 计算总活动数（days_data中的activities已在循环中被pop）
    total_activities = sum(len(d.get('activities', [])) for d in days_data)
    print(f'  - 活动: {total_activities}个')

    # 创建评论
    comment = Comment(
        user_id=users[1].id,  # test用户
        itinerary_id=itinerary.id,
        content='这个行程安排得很棒！故宫和长城都是必去的景点。',
        rating=5
    )
    db.session.add(comment)
    db.session.commit()
    print('创建评论: 1条')

    # 创建点赞
    like = Like(user_id=users[1].id, itinerary_id=itinerary.id)
    db.session.add(like)
    db.session.commit()
    print('创建点赞: 1个')

    # 创建收藏
    favorite = Favorite(user_id=users[1].id, itinerary_id=itinerary.id)
    db.session.add(favorite)
    db.session.commit()
    print('创建收藏: 1个')

    print('\n数据库初始化完成！')
    print(f'\n测试账号:')
    print(f'  - 管理员: admin / Admin123456')
    print(f'  - 测试用户: test / Test123456')
