# 目的地数据初始化脚本
# 运行: python -c "from migrations.seed_destinations import seed_destinations; seed_destinations()"

from app import create_app
from app.extensions import db
from app.models.destination import Destination


def seed_destinations():
    """初始化目的地数据"""
    app = create_app()

    destinations_data = [
        # 一线城市
        {'name': '上海', 'country': '中国', 'province': '上海', 'city': '上海', 'category': '都市', 'description': '中国最大的城市之一，国际金融中心，拥有丰富的历史文化遗产和现代都市风光。', 'latitude': 31.2304, 'longitude': 121.4737},
        {'name': '北京', 'country': '中国', 'province': '北京', 'city': '北京', 'category': '都市', 'description': '中国的首都，拥有三千多年的历史，是中国的政治、文化和国际交流中心。', 'latitude': 39.9042, 'longitude': 116.4074},
        {'name': '广州', 'country': '中国', 'province': '广东', 'city': '广州', 'category': '都市', 'description': '中国南方重要的中心城市，国际商贸枢纽，岭南文化的重要代表。', 'latitude': 23.1291, 'longitude': 113.2644},
        {'name': '深圳', 'country': '中国', 'province': '广东', 'city': '深圳', 'category': '都市', 'description': '中国第一个经济特区，年轻而充满活力的现代化都市。', 'latitude': 22.5431, 'longitude': 114.0579},

        # 新一线城市
        {'name': '成都', 'country': '中国', 'province': '四川', 'city': '成都', 'category': '都市', 'description': '天府之国四川省会，以大熊猫、美食和悠闲生活著称。', 'latitude': 30.6598, 'longitude': 104.0657},
        {'name': '杭州', 'country': '中国', 'province': '浙江', 'city': '杭州', 'category': '都市', 'description': '人间天堂，西湖是世界文化遗产，电子商务之都。', 'latitude': 30.2741, 'longitude': 120.1551},
        {'name': '重庆', 'country': '中国', 'province': '重庆', 'city': '重庆', 'category': '都市', 'description': '山城雾都，长江和嘉陵江交汇处，以火锅和立体城市著称。', 'latitude': 29.5632, 'longitude': 106.5516},
        {'name': '西安', 'country': '中国', 'province': '陕西', 'city': '西安', 'category': '历史', 'description': '十三朝古都，兵马俑所在地，中华文明的重要发祥地。', 'latitude': 34.3416, 'longitude': 108.9402},
        {'name': '苏州', 'country': '中国', 'province': '江苏', 'city': '苏州', 'category': '历史', 'description': '园林之城，江南水乡代表，中国园林艺术的巅峰。', 'latitude': 31.2990, 'longitude': 120.6196},
        {'name': '南京', 'country': '中国', 'province': '江苏', 'city': '南京', 'category': '历史', 'description': '六朝古都，明孝陵、中山陵所在地，历史底蕴深厚。', 'latitude': 32.0603, 'longitude': 118.7969},

        # 二线城市
        {'name': '武汉', 'country': '中国', 'province': '湖北', 'city': '武汉', 'category': '都市', 'description': '江城，九省通衢，长江和汉江交汇处。', 'latitude': 30.5928, 'longitude': 114.3055},
        {'name': '长沙', 'country': '中国', 'province': '湖南', 'city': '长沙', 'category': '都市', 'description': '星城，湘江之畔，娱乐之都，臭豆腐发源地。', 'latitude': 28.2282, 'longitude': 112.9388},
        {'name': '厦门', 'country': '中国', 'province': '福建', 'city': '厦门', 'category': '海滨', 'description': '海上花园，鼓浪屿世界遗产，闽南文化代表。', 'latitude': 24.4798, 'longitude': 118.0894},
        {'name': '青岛', 'country': '中国', 'province': '山东', 'city': '青岛', 'category': '海滨', 'description': '帆船之都，啤酒之城，美丽的海滨城市。', 'latitude': 36.0671, 'longitude': 120.3826},
        {'name': '大连', 'country': '中国', 'province': '辽宁', 'city': '大连', 'category': '海滨', 'description': '浪漫之都，北方明珠，美丽的港口城市。', 'latitude': 38.9140, 'longitude': 121.6147},
        {'name': '天津', 'country': '中国', 'province': '天津', 'city': '天津', 'category': '都市', 'description': '津门故里，北方第二大城市，中西合璧的城市风貌。', 'latitude': 39.3434, 'longitude': 117.3616},
        {'name': '哈尔滨', 'country': '中国', 'province': '黑龙江', 'city': '哈尔滨', 'category': '都市', 'description': '冰城夏都，东方莫斯科，冰雪旅游胜地。', 'latitude': 45.8038, 'longitude': 126.5340},
        {'name': '沈阳', 'country': '中国', 'province': '辽宁', 'city': '沈阳', 'category': '都市', 'description': '工业重镇，清朝发祥地，历史文化名城。', 'latitude': 41.8057, 'longitude': 123.4315},
        {'name': '郑州', 'country': '中国', 'province': '河南', 'city': '郑州', 'category': '都市', 'description': '中原之城，铁路枢纽，中华文明发源地之一。', 'latitude': 34.7466, 'longitude': 113.6254},
        {'name': '济南', 'country': '中国', 'province': '山东', 'city': '济南', 'category': '都市', 'description': '泉城，七十二名泉所在地，趵突泉闻名天下。', 'latitude': 36.6562, 'longitude': 116.9940},
        {'name': '昆明', 'country': '中国', 'province': '云南', 'city': '昆明', 'category': '自然', 'description': '春城，四季如春，云南旅游的枢纽城市。', 'latitude': 25.0406, 'longitude': 102.7129},
        {'name': '贵阳', 'country': '中国', 'province': '贵州', 'city': '贵阳', 'category': '自然', 'description': '林城，山中有城，城中有山，夏季避暑胜地。', 'latitude': 26.5983, 'longitude': 106.7135},
        {'name': '南宁', 'country': '中国', 'province': '广西', 'city': '南宁', 'category': '都市', 'description': '绿城，中国面向东盟的桥头堡。', 'latitude': 22.8170, 'longitude': 108.3661},
        {'name': '南昌', 'country': '中国', 'province': '江西', 'city': '南昌', 'category': '都市', 'description': '英雄城，八一起义所在地，赣江之滨。', 'latitude': 28.6829, 'longitude': 115.8581},
        {'name': '合肥', 'country': '中国', 'province': '安徽', 'city': '合肥', 'category': '都市', 'description': '科技之城，中国科学技术大学所在地。', 'latitude': 31.8612, 'longitude': 117.2830},
        {'name': '太原', 'country': '中国', 'province': '山西', 'city': '太原', 'category': '都市', 'description': '龙城，山西省会，煤炭之都。', 'latitude': 37.8706, 'longitude': 112.5489},
        {'name': '长春', 'country': '中国', 'province': '吉林', 'city': '长春', 'category': '都市', 'description': '汽车城，电影城，中国汽车工业的摇篮。', 'latitude': 43.8171, 'longitude': 125.3245},

        # 旅游热门城市
        {'name': '三亚', 'country': '中国', 'province': '海南', 'city': '三亚', 'category': '海滨', 'description': '天涯海角，热带海滨度假胜地，阳光沙滩的代名词。', 'latitude': 18.2528, 'longitude': 109.5119},
        {'name': '海口', 'country': '中国', 'province': '海南', 'city': '海口', 'category': '海滨', 'description': '椰城，海南省会，热带海岛风情。', 'latitude': 20.0444, 'longitude': 110.1999},
        {'name': '丽江', 'country': '中国', 'province': '云南', 'city': '丽江', 'category': '自然', 'description': '艳遇之城，世界文化遗产，纳西族古都。', 'latitude': 26.8721, 'longitude': 100.2296},
        {'name': '大理', 'country': '中国', 'province': '云南', 'city': '大理', 'category': '自然', 'description': '风花雪月，下关风、上关花、苍山雪、洱海月。', 'latitude': 25.6065, 'longitude': 100.2679},
        {'name': '桂林', 'country': '中国', 'province': '广西', 'city': '桂林', 'category': '自然', 'description': '山水甲天下，喀斯特地貌的典型代表。', 'latitude': 25.2742, 'longitude': 110.2901},
        {'name': '阳朔', 'country': '中国', 'province': '广西', 'city': '桂林', 'category': '自然', 'description': '桂林山水甲天下，阳朔山水甲桂林。', 'latitude': 24.7796, 'longitude': 110.4855},
        {'name': '敦煌', 'country': '中国', 'province': '甘肃', 'city': '酒泉', 'category': '历史', 'description': '丝路明珠，莫高窟所在地，沙漠中的艺术宝库。', 'latitude': 40.1421, 'longitude': 94.6620},
        {'name': '拉萨', 'country': '中国', 'province': '西藏', 'city': '拉萨', 'category': '文化', 'description': '日光城，布达拉宫所在地，世界屋脊的圣城。', 'latitude': 29.6500, 'longitude': 91.1322},
        {'name': '张家界', 'country': '中国', 'province': '湖南', 'city': '张家界', 'category': '自然', 'description': '国家森林公园所在地，阿凡达取景地。', 'latitude': 29.1175, 'longitude': 110.4794},
        {'name': '九寨沟', 'country': '中国', 'province': '四川', 'city': '阿坝', 'category': '自然', 'description': '人间仙境，彩色水池和原始森林的完美结合。', 'latitude': 33.2537, 'longitude': 103.9129},
        {'name': '黄山', 'country': '中国', 'province': '安徽', 'city': '黄山', 'category': '自然', 'description': '五岳归来不看山，黄山归来不看岳。', 'latitude': 29.7148, 'longitude': 118.3376},
        {'name': '峨眉山', 'country': '中国', 'province': '四川', 'city': '乐山', 'category': '自然', 'description': '佛教名山，普贤菩萨道场，金顶日出壮观。', 'latitude': 29.5247, 'longitude': 103.3364},
        {'name': '泰山', 'country': '中国', 'province': '山东', 'city': '泰安', 'category': '自然', 'description': '五岳之首，中华民族的精神象征。', 'latitude': 36.2075, 'longitude': 117.1056},
        {'name': '乌镇', 'country': '中国', 'province': '浙江', 'city': '嘉兴', 'category': '自然', 'description': '中国最后的枕水人家，江南水乡的典型代表。', 'latitude': 30.7443, 'longitude': 120.4875},
        {'name': '西塘', 'country': '中国', 'province': '浙江', 'city': '嘉兴', 'category': '自然', 'description': '活着的千年古镇，生活着的古镇博物馆。', 'latitude': 30.9275, 'longitude': 120.8418},
        {'name': '凤凰古城', 'country': '中国', 'province': '湖南', 'city': '湘西', 'category': '历史', 'description': '中国最美小城，吊脚楼群和沱江风光。', 'latitude': 27.9476, 'longitude': 109.5998},
        {'name': '平遥古城', 'country': '中国', 'province': '山西', 'city': '晋中', 'category': '历史', 'description': '保存最完整的明清古城，世界文化遗产。', 'latitude': 37.2011, 'longitude': 112.1535},
        {'name': '婺源', 'country': '中国', 'province': '江西', 'city': '上饶', 'category': '自然', 'description': '中国最美乡村，油菜花海的代表。', 'latitude': 29.3624, 'longitude': 117.8617},
        {'name': '北海', 'country': '中国', 'province': '广西', 'city': '北海', 'category': '海滨', 'description': '北部湾畔的海滨城市，银滩闻名遐迩。', 'latitude': 21.4735, 'longitude': 109.1193},
        {'name': '珠海', 'country': '中国', 'province': '广东', 'city': '珠海', 'category': '海滨', 'description': '百岛之市，环境优美的海滨城市。', 'latitude': 22.2243, 'longitude': 113.5537},
        {'name': '江门', 'country': '中国', 'province': '广东', 'city': '江门', 'category': '文化', 'description': '中国侨都，五邑文化发祥地，开平碉楼与村落世界文化遗产所在地。', 'latitude': 22.5789, 'longitude': 113.0815},

        # 江浙沪周边
        {'name': '宁波', 'country': '中国', 'province': '浙江', 'city': '宁波', 'category': '都市', 'description': '港口城市，浙商的发源地，天一阁所在地。', 'latitude': 29.8683, 'longitude': 121.5440},
        {'name': '温州', 'country': '中国', 'province': '浙江', 'city': '温州', 'category': '都市', 'description': '瓯江之畔，民营经济的发源地。', 'latitude': 28.0006, 'longitude': 120.6994},
        {'name': '无锡', 'country': '中国', 'province': '江苏', 'city': '无锡', 'category': '都市', 'description': '太湖之滨，灵山大佛所在地。', 'latitude': 31.5747, 'longitude': 120.2994},
        {'name': '常州', 'country': '中国', 'province': '江苏', 'city': '常州', 'category': '都市', 'description': '乐园之都，中华恐龙园所在地。', 'latitude': 31.8113, 'longitude': 119.9740},
        {'name': '南通', 'country': '中国', 'province': '江苏', 'city': '南通', 'category': '都市', 'description': '江海之城，中国近代第一城。', 'latitude': 32.0150, 'longitude': 120.8646},
        {'name': '绍兴', 'country': '中国', 'province': '浙江', 'city': '绍兴', 'category': '历史', 'description': '水乡名城，鲁迅故里，黄酒之乡。', 'latitude': 30.0304, 'longitude': 120.5802},
        {'name': '嘉兴', 'country': '中国', 'province': '浙江', 'city': '嘉兴', 'category': '自然', 'description': '红船精神发源地，江南水乡代表。', 'latitude': 30.7480, 'longitude': 120.7550},
        {'name': '扬州', 'country': '中国', 'province': '江苏', 'city': '扬州', 'category': '历史', 'description': '淮左名都，烟花三月下扬州。', 'latitude': 32.3932, 'longitude': 119.4126},
        {'name': '镇江', 'country': '中国', 'province': '江苏', 'city': '镇江', 'category': '历史', 'description': '金山寺所在地，千年古城镇江。', 'latitude': 32.2044, 'longitude': 119.4564},

        # 北方城市
        {'name': '秦皇岛', 'country': '中国', 'province': '河北', 'city': '秦皇岛', 'category': '海滨', 'description': '夏都，避暑胜地，万里长城入海处。', 'latitude': 39.9354, 'longitude': 119.5885},
        {'name': '承德', 'country': '中国', 'province': '河北', 'city': '承德', 'category': '历史', 'description': '皇家猎苑，避暑山庄所在地。', 'latitude': 40.9514, 'longitude': 117.9633},
        {'name': '保定', 'country': '中国', 'province': '河北', 'city': '保定', 'category': '历史', 'description': '京畿重地，直隶总督府所在地。', 'latitude': 38.8738, 'longitude': 115.4647},
        {'name': '洛阳', 'country': '中国', 'province': '河南', 'city': '洛阳', 'category': '历史', 'description': '千年帝都，牡丹花城，龙门石窟所在地。', 'latitude': 34.6197, 'longitude': 112.4540},
        {'name': '开封', 'country': '中国', 'province': '河南', 'city': '开封', 'category': '历史', 'description': '八朝古都，包拯故里，清明上河图的原型地。', 'latitude': 34.7971, 'longitude': 114.3074},
        {'name': '西安', 'country': '中国', 'province': '陕西', 'city': '西安', 'category': '历史', 'description': '十三朝古都，兵马俑所在地。', 'latitude': 34.3416, 'longitude': 108.9402},
        {'name': '兰州', 'country': '中国', 'province': '甘肃', 'city': '兰州', 'category': '都市', 'description': '黄河之都，丝绸之路的重要节点。', 'latitude': 36.0611, 'longitude': 103.8343},
        {'name': '乌鲁木齐', 'country': '中国', 'province': '新疆', 'city': '乌鲁木齐', 'category': '都市', 'description': '亚心之都，新疆旅游的起点。', 'latitude': 43.7928, 'longitude': 87.6177},
        {'name': '呼伦贝尔', 'country': '中国', 'province': '内蒙古', 'city': '呼伦贝尔', 'category': '自然', 'description': '草原之都，世界四大草原之一。', 'latitude': 49.2122, 'longitude': 119.7654},
        {'name': '阿尔山', 'country': '中国', 'province': '内蒙古', 'city': '兴安盟', 'category': '自然', 'description': '火山地质公园，温泉与森林的完美结合。', 'latitude': 47.1833, 'longitude': 119.9439},
    ]

    with app.app_context():
        for data in destinations_data:
            existing = Destination.query.filter_by(name=data['name']).first()
            if not existing:
                dest = Destination(**data)
                db.session.add(dest)

        db.session.commit()
        print(f'已添加 {len(destinations_data)} 个目的地')


if __name__ == '__main__':
    seed_destinations()
