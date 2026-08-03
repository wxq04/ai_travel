# -*- coding: utf-8 -*-
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

print("更新目的地图片...")

from app import create_app
from app.extensions import db
from app.models.destination import Destination
import json

app = create_app('development')

with app.app_context():
    # Unsplash Source API - 根据关键词自动匹配相关图片
    destinations_data = [
        {
            "name": "北京",
            "country": "中国",
            "province": "北京市",
            "city": "北京市",
            "description": "北京是中华人民共和国的首都，中国政治、文化、交通、科研、教育以及国际交往中心。拥有故宫、天安门、长城、颐和园等众多世界文化遗产，是世界著名的历史文化名城。",
            "cover_image": "https://source.unsplash.com/800x600/?beijing,forbidden-city",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?beijing,great-wall",
                "https://source.unsplash.com/800x600/?beijing,temple",
                "https://source.unsplash.com/800x600/?china,architecture"
            ]),
            "best_season": "春秋两季",
            "category": "历史",
            "avg_rating": 4.8,
            "view_count": 12580
        },
        {
            "name": "上海",
            "country": "中国",
            "province": "上海市",
            "city": "上海市",
            "description": "上海是中国最大的城市和经济中心，中国金融、科技、创新中心。既有外滩万国建筑群、豫园等历史文化景点，也有陆家嘴摩天大楼等现代都市景观。",
            "cover_image": "https://source.unsplash.com/800x600/?shanghai,cityscape",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?shanghai,bund",
                "https://source.unsplash.com/800x600/?shanghai,night"
            ]),
            "best_season": "春秋两季",
            "category": "都市",
            "avg_rating": 4.7,
            "view_count": 15890
        },
        {
            "name": "成都",
            "country": "中国",
            "province": "四川省",
            "city": "成都市",
            "description": "成都被誉为天府之国，是美食之都、熊猫之乡。拥有武侯祠、杜甫草堂、都江堰等历史文化景点，也是品尝川菜、感受慢生活的绝佳目的地。",
            "cover_image": "https://source.unsplash.com/800x600/?chengdu,panda",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?panda",
                "https://source.unsplash.com/800x600/?chinese-food"
            ]),
            "best_season": "春秋两季",
            "category": "美食",
            "avg_rating": 4.6,
            "view_count": 8920
        },
        {
            "name": "拉萨",
            "country": "中国",
            "province": "西藏自治区",
            "city": "拉萨市",
            "description": "拉萨是中国西藏自治区首府，海拔3650米，有日光城美誉。布达拉宫、大昭寺是藏传佛教圣地，是体验藏族文化、感受信仰力量的圣地。",
            "cover_image": "https://source.unsplash.com/800x600/?tibet,monastery",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?tibet,mountain",
                "https://source.unsplash.com/800x600/?buddhism,temple"
            ]),
            "best_season": "5-10月",
            "category": "自然",
            "avg_rating": 4.9,
            "view_count": 6540
        },
        {
            "name": "大理",
            "country": "中国",
            "province": "云南省",
            "city": "大理市",
            "description": "大理白族自治州位于云南省西部，风花雪月（下关风、上关花、苍山雪、洱海月）闻名全国。古城、洱海、苍山构成独特的自然人文景观。",
            "cover_image": "https://source.unsplash.com/800x600/?dali,ancient-town",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?yunnan,lake",
                "https://source.unsplash.com/800x600/?china,nature"
            ]),
            "best_season": "3-5月",
            "category": "自然",
            "avg_rating": 4.7,
            "view_count": 7890
        },
        {
            "name": "三亚",
            "country": "中国",
            "province": "海南省",
            "city": "三亚市",
            "description": "三亚位于海南岛最南端，是中国最著名的热带海滨旅游城市。天涯海角、亚龙湾、蜈支洲岛等景点，使其成为冬季避寒、度假休闲的首选。",
            "cover_image": "https://source.unsplash.com/800x600/?sanya,beach",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?tropical,beach",
                "https://source.unsplash.com/800x600/?ocean,sunset"
            ]),
            "best_season": "11月-次年3月",
            "category": "海滨",
            "avg_rating": 4.5,
            "view_count": 11230
        },
        {
            "name": "桂林",
            "country": "中国",
            "province": "广西壮族自治区",
            "city": "桂林市",
            "description": "桂林山水甲天下，以喀斯特地貌闻名于世。象鼻山、漓江、阳朔西街等景点构成一幅幅诗意的山水画卷，是典型的山水观光旅游目的地。",
            "cover_image": "https://source.unsplash.com/800x600/?guilin,mountains",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?karst,landscape",
                "https://source.unsplash.com/800x600/?river,mountains"
            ]),
            "best_season": "4-10月",
            "category": "自然",
            "avg_rating": 4.8,
            "view_count": 9230
        },
        {
            "name": "杭州",
            "country": "中国",
            "province": "浙江省",
            "city": "杭州市",
            "description": "杭州是浙江省省会，有上有天堂、下有苏杭的美誉。西湖、京杭大运河、灵隐寺等景点将自然风光与历史文化完美融合，是著名的休闲度假城市。",
            "cover_image": "https://source.unsplash.com/800x600/?hangzhou,west-lake",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?lake,temple",
                "https://source.unsplash.com/800x600/?china,garden"
            ]),
            "best_season": "3-5月、9-11月",
            "category": "自然",
            "avg_rating": 4.8,
            "view_count": 13450
        },
        {
            "name": "厦门",
            "country": "中国",
            "province": "福建省",
            "city": "厦门市",
            "description": "厦门是中国最早的经济特区之一，环境优美、气候宜人。鼓浪屿、南普陀寺、环岛路等景点兼具海滨风光与历史文化底蕴，是热门海滨旅游城市。",
            "cover_image": "https://source.unsplash.com/800x600/?xiamen,island",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?island,beach",
                "https://source.unsplash.com/800x600/?coast,city"
            ]),
            "best_season": "3-5月、9-11月",
            "category": "海滨",
            "avg_rating": 4.6,
            "view_count": 9870
        },
        {
            "name": "张家界",
            "country": "中国",
            "province": "湖南省",
            "city": "张家界市",
            "description": "张家界是中国第一个国家森林公园，以独特的石英砂岩峰林地貌著称。天门山玻璃栈道、黄石寨、金鞭溪等景点让您体验大自然的鬼斧神工。",
            "cover_image": "https://source.unsplash.com/800x600/?zhangjiajie,forest",
            "images": json.dumps([
                "https://source.unsplash.com/800x600/?mountain,forest",
                "https://source.unsplash.com/800x600/?cliff,nature"
            ]),
            "best_season": "4-6月、9-11月",
            "category": "自然",
            "avg_rating": 4.7,
            "view_count": 7650
        }
    ]

    # 清空并重新插入
    db.session.query(Destination).delete()

    for data in destinations_data:
        dest = Destination(**data)
        db.session.add(dest)

    db.session.commit()

    print(f"已更新 {len(destinations_data)} 个目的地的图片")
    print("完成！")