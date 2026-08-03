from datetime import datetime
from app.extensions import db
import json


class Attraction(db.Model):
    """景点详情表 - 存储景点的详细信息"""
    __tablename__ = 'attractions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), index=True)
    category = db.Column(db.String(50))  # 景点/餐厅/购物/文化/自然
    description = db.Column(db.Text)  # 详细介绍
    address = db.Column(db.String(255))  # 详细地址
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度

    # 票务信息
    ticket_price = db.Column(db.String(100))  # 门票信息
    opening_hours = db.Column(db.String(100))  # 开放时间
    best_season = db.Column(db.String(50))  # 最佳季节
    suggested_duration = db.Column(db.Integer)  # 建议游玩时长（分钟）

    # 推荐内容
    recommended_dishes = db.Column(db.Text)  # 推荐美食（JSON数组）
    play_tips = db.Column(db.Text)  # 玩法推荐
    nearby_attractions = db.Column(db.Text)  # 附近景点（JSON数组）
    nearby_distance = db.Column(db.Text)  # 附近距离（JSON）

    # 评分和统计
    image_url = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0.0)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    destination = db.relationship('Destination', backref=db.backref('attractions', lazy='dynamic'))

    def get_recommended_dishes(self):
        """获取推荐美食列表"""
        if self.recommended_dishes:
            try:
                return json.loads(self.recommended_dishes)
            except json.JSONDecodeError:
                return []
        return []

    def set_recommended_dishes(self, dishes_list):
        """设置推荐美食"""
        if isinstance(dishes_list, list):
            self.recommended_dishes = json.dumps(dishes_list, ensure_ascii=False)
        else:
            self.recommended_dishes = json.dumps([], ensure_ascii=False)

    def get_nearby_attractions(self):
        """获取附近景点列表"""
        if self.nearby_attractions:
            try:
                return json.loads(self.nearby_attractions)
            except json.JSONDecodeError:
                return []
        return []

    def set_nearby_attractions(self, attractions_list, distance_list=None):
        """设置附近景点"""
        if isinstance(attractions_list, list):
            self.nearby_attractions = json.dumps(attractions_list, ensure_ascii=False)
            if distance_list:
                self.nearby_distance = json.dumps(distance_list, ensure_ascii=False)

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()

    def __repr__(self):
        return f'<Attraction {self.name}>'


def seed_attractions():
    """初始化景点数据"""
    from app.models.destination import Destination

    # 获取目的地
    shanghai = Destination.query.filter_by(name='上海').first()
    beijing = Destination.query.filter_by(name='北京').first()
    hangzhou = Destination.query.filter_by(name='杭州').first()
    chengdu = Destination.query.filter_by(name='成都').first()
    chongqing = Destination.query.filter_by(name='重庆').first()

    attractions_data = []

    if chongqing:
        attractions_data.extend([
            {
                'name': '洪崖洞',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '洪崖洞是重庆最具代表性的旅游景点之一，是一座依山就势、临崖而建的仿古建筑群。共有11层，1楼和11楼都是马路，形成独特的立体城市景观。夜晚灯火璀璨，被誉为"现实版千与千寻"。',
                'address': '重庆市渝中区嘉陵江滨江路88号',
                'latitude': 29.5628,
                'longitude': 106.5828,
                'ticket_price': '免费',
                'opening_hours': '全天开放（店铺10:00-22:00）',
                'best_season': '四季皆宜（夜晚最佳）',
                'suggested_duration': 120,
                'play_tips': '建议晚上去，灯光亮起后非常震撼。从11楼的解放碑商圈可以直接走楼梯到1楼的江边。节假日人很多，建议错峰前往。',
                'recommended_dishes': json.dumps(['重庆火锅', '酸辣粉', '串串香', '糍粑'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['解放碑', '长江索道', '朝天门'], ensure_ascii=False),
                'nearby_distance': json.dumps(['0.5km', '1km', '1.5km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1534251365389-980f6f0b169c?w=800'
            },
            {
                'name': '磁器口古镇',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '磁器口古镇是重庆主城区内保存最完好的古镇，始建于宋代，有"小重庆"之称。古镇内青石板路蜿蜒，两旁是明清风格的建筑，充满浓郁的巴渝风情。',
                'address': '重庆市沙坪坝区磁南街1号',
                'latitude': 29.5794,
                'longitude': 106.4488,
                'ticket_price': '免费',
                'opening_hours': '全天开放（店铺9:00-20:00）',
                'best_season': '四季皆宜',
                'suggested_duration': 180,
                'play_tips': '建议下午去，可以逛3-4小时。可以品尝各种重庆小吃，如陈麻花、毛血旺等。避开节假日，人会非常多。',
                'recommended_dishes': json.dumps(['陈麻花', '毛血旺', '鸡杂', '酸辣粉'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['渣滓洞', '白公馆', '歌乐山'], ensure_ascii=False),
                'nearby_distance': json.dumps(['2km', '2.5km', '3km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1548930289-86478f6f7e28.jpg?w=800'
            },
            {
                'name': '长江索道',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '长江索道是重庆独特的交通工具，被誉为"山城空中巴士"。乘坐索道横跨长江，可以俯瞰两江四岸的城市风光，是重庆必体验的项目之一。',
                'address': '重庆市渝中区新华路151号（新华路站）',
                'latitude': 29.5535,
                'longitude': 106.5797,
                'ticket_price': '单程20元，往返30元',
                'opening_hours': '07:30-22:00',
                'best_season': '四季皆宜',
                'suggested_duration': 60,
                'play_tips': '建议从上新街站乘坐到新华路站，可以避开解放碑的人流。傍晚时分乘坐可以看到美丽的日落和夜景。单程约5分钟。',
                'recommended_dishes': json.dumps(['火锅', '小面', '江湖菜'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['洪崖洞', '解放碑', '南山一棵树'], ensure_ascii=False),
                'nearby_distance': json.dumps(['1km', '1.5km', '3km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800'
            },
            {
                'name': '武隆天生三桥',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '武隆天生三桥是世界规模最大、最高的串珠式天生桥群，由天龙桥、青龙桥和黑龙桥组成，是《变形金刚4》和《满城尽带黄金甲》的取景地。',
                'address': '重庆市武隆区仙女山镇',
                'latitude': 29.4108,
                'longitude': 107.9017,
                'ticket_price': '125元（含观光车）',
                'opening_hours': '08:30-17:00',
                'best_season': '春季秋季',
                'suggested_duration': 240,
                'play_tips': '建议早上去，人少景美。从景区入口到景点需要乘坐观光车，然后步行游览约2小时。穿舒适的鞋子，带上雨具。',
                'recommended_dishes': json.dumps(['农家菜', '腊肉', '竹笋'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['芙蓉洞', '仙女山', '龙水峡地缝'], ensure_ascii=False),
                'nearby_distance': json.dumps(['5km', '10km', '8km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=800'
            },
            {
                'name': '解放碑',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '解放碑是重庆的地标性建筑，全名"人民解放纪念碑"，是中国唯一一座纪念抗日战争胜利的纪念碑。周边是重庆最繁华的商业中心，集购物、美食、娱乐于一体。',
                'address': '重庆市渝中区解放碑商圈',
                'latitude': 29.5589,
                'longitude': 106.5783,
                'ticket_price': '免费',
                'opening_hours': '全天开放',
                'best_season': '四季皆宜',
                'suggested_duration': 120,
                'play_tips': '建议晚上去，可以看到璀璨的霓虹灯。可以逛八一好吃街，品尝各种重庆美食。周边商场众多，是购物的好去处。',
                'recommended_dishes': json.dumps(['重庆小面', '酸辣粉', '串串', '抄手'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['洪崖洞', '长江索道', '较场口夜市'], ensure_ascii=False),
                'nearby_distance': json.dumps(['0.8km', '1km', '0.5km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800'
            },
            {
                'name': '大足石刻',
                'destination_id': chongqing.id,
                'category': '景点',
                'description': '大足石刻是世界八大石窟之一，始建于唐代，历经250多年完成。石刻群以宝顶山和北山两处最为集中，展现了中国石窟艺术晚期的最高成就。',
                'address': '重庆市大足区宝顶镇',
                'latitude': 29.7578,
                'longitude': 105.8628,
                'ticket_price': '135元（含观光车）',
                'opening_hours': '08:30-18:00（17:00停止入场）',
                'best_season': '春季秋季',
                'suggested_duration': 300,
                'play_tips': '建议早上8点半开门就去，避开人流。宝顶山石刻最为壮观，建议请导游讲解才能更好地理解石刻背后的故事。',
                'recommended_dishes': json.dumps(['邮亭鲫鱼', '丁家坡洋芋', '大足冬菜'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['北山石刻', '龙水湖', '昌州古镇'], ensure_ascii=False),
                'nearby_distance': json.dumps(['2km', '15km', '5km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1569388037493-6f8de6e6a4c1?w=800'
            }
        ])

    if shanghai:
        attractions_data.extend([
            {
                'name': '外滩',
                'destination_id': shanghai.id,
                'category': '景点',
                'description': '外滩是上海最著名的观光区，全长约1.5公里，位于黄浦江畔。这里汇集了52幢不同风格的古典复兴大楼，被誉为"万国建筑博览群"。夜晚的外滩灯火辉煌，对岸陆家嘴的现代建筑与外滩的古典建筑形成鲜明对比，是拍摄上海夜景的绝佳位置。',
                'address': '上海市黄浦区外滩',
                'latitude': 31.2400,
                'longitude': 121.4903,
                'ticket_price': '免费',
                'opening_hours': '全天开放',
                'best_season': '四季皆宜',
                'suggested_duration': 120,
                'play_tips': '建议傍晚时分前往，可以同时欣赏日景和夜景。可以从外滩出发，沿着黄浦江散步，感受上海的历史与现代交融。拍照建议选择外滩观景台或者外白渡桥。',
                'recommended_dishes': json.dumps(['上海老饭店本帮菜', '南翔小笼包', '沈大成糕团'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['东方明珠塔', '豫园', '南京路步行街'], ensure_ascii=False),
                'nearby_distance': json.dumps(['1.5km', '2km', '1km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1548473872-d5d7b19c8d04?w=800'
            },
            {
                'name': '东方明珠塔',
                'destination_id': shanghai.id,
                'category': '景点',
                'description': '东方明珠广播电视塔是上海的标志性建筑之一，塔高468米，是亚洲第一高塔。塔内设有多个观光层、旋转餐厅和太空舱，登上塔顶可以俯瞰整个上海的城市风光，尤其夜景最为震撼。',
                'address': '上海市浦东新区陆家嘴世纪大道1号',
                'latitude': 31.2397,
                'longitude': 121.4995,
                'ticket_price': '观光票180元起，旋转餐厅自助餐328元起',
                'opening_hours': '08:00-21:00（视季节调整）',
                'best_season': '四季皆宜',
                'suggested_duration': 180,
                'play_tips': '建议提前网上购票避免排队。最上层观光厅（351米）需要额外购票，但视野更好。晚上登塔可以欣赏上海璀璨夜景。',
                'recommended_dishes': json.dumps(['旋转餐厅自助餐', '上海菜'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['外滩', '陆家嘴金融中心', '上海中心大厦'], ensure_ascii=False),
                'nearby_distance': json.dumps(['1.5km', '0.5km', '0.8km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1508503699445-9cf1e7a4f0d9?w=800'
            },
            {
                'name': '豫园',
                'destination_id': shanghai.id,
                'category': '景点',
                'description': '豫园是江南古典园林的代表作，始建于明代嘉靖年间，距今已有400多年历史。园内假山、流水、亭台楼阁错落有致，展现了中国传统园林艺术的精华。豫园商城环绕其周，是购买上海特产和品尝小吃的好去处。',
                'address': '上海市黄浦区豫园老街279号',
                'latitude': 31.2270,
                'longitude': 121.4925,
                'ticket_price': '旺季40元，淡季30元',
                'opening_hours': '09:00-17:00',
                'best_season': '春季秋季',
                'suggested_duration': 120,
                'play_tips': '建议清晨或傍晚前往，避开人流高峰。豫园商城的小吃值得一试，尤其是南翔馒头店的蟹黄小笼包。不要错过九曲桥和湖心亭。',
                'recommended_dishes': json.dumps(['南翔小笼包', '绿波廊点心', '五香豆'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['城隍庙', '外滩', '新天地'], ensure_ascii=False),
                'nearby_distance': json.dumps(['0.3km', '2km', '3km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1537531383496-f4749b8032cf?w=800'
            },
            {
                'name': '田子坊',
                'destination_id': shanghai.id,
                'category': '景点',
                'description': '田子坊是上海最具文艺气息的弄堂之一，由原来的石库门里弄改造而成。这里汇集了众多艺术家工作室、创意店铺、咖啡馆和酒吧，是体验老上海弄堂文化与现代创意产业融合的理想之地。',
                'address': '上海市黄浦区泰康路210弄',
                'latitude': 31.2117,
                'longitude': 121.4687,
                'ticket_price': '免费',
                'opening_hours': '全天（店铺一般10:00-22:00）',
                'best_season': '四季皆宜',
                'suggested_duration': 120,
                'play_tips': '建议下午或傍晚前往，可以逛店铺、喝咖啡、拍照。弄堂里有很多隐藏的小店需要细心发现。夜晚的田子坊灯光氛围更好。',
                'recommended_dishes': json.dumps(['老上海雪菜面', '生煎包', '本帮红烧肉'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['新天地', '淮海路', '思南路'], ensure_ascii=False),
                'nearby_distance': json.dumps(['0.5km', '1km', '0.8km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1511735643442-503bb3bd348a?w=800'
            }
        ])

    if beijing:
        attractions_data.extend([
            {
                'name': '故宫',
                'destination_id': beijing.id,
                'category': '景点',
                'description': '故宫又名紫禁城，是明清两代的皇家宫殿，是世界现存规模最大、保存最完整的木质结构古建筑群。占地72万平方米，建筑面积约15万平方米，有大小宫殿70多座，房屋9000余间。',
                'address': '北京市东城区景山前街4号',
                'latitude': 39.9163,
                'longitude': 116.3972,
                'ticket_price': '旺季60元，淡季40元（需预约）',
                'opening_hours': '08:30-17:00（周一闭馆）',
                'best_season': '春季秋季',
                'suggested_duration': 300,
                'play_tips': '建议提前在故宫博物院官网预约。参观顺序：中轴线（午门-太和殿-中和殿-保和殿-乾清宫-坤宁宫-御花园）→东六宫→西六宫。建议请导游或租借讲解器。',
                'nearby_attractions': json.dumps(['天安门广场', '景山公园', '北海公园'], ensure_ascii=False),
                'nearby_distance': json.dumps(['0.5km', '0.3km', '1.5km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800'
            },
            {
                'name': '八达岭长城',
                'destination_id': beijing.id,
                'category': '景点',
                'description': '八达岭长城是明长城最具代表性的段落之一，是居庸关的重要前哨，海拔1015米，地势险要。长城气势磅礴，是来北京必游的世界文化遗产。',
                'address': '北京市延庆区八达岭镇',
                'latitude': 40.3654,
                'longitude': 116.6042,
                'ticket_price': '旺季45元，淡季40元，缆车120元',
                'opening_hours': '07:00-18:00（夏季至19:00）',
                'best_season': '春季秋季',
                'suggested_duration': 360,
                'play_tips': '建议早上去，避开人流。登城方式有步行、缆车、滑车。建议乘坐缆车上山，步行下山。春秋季节天气最为舒适。',
                'nearby_attractions': json.dumps(['居庸关长城', '十三陵', '八达岭野生动物园'], ensure_ascii=False),
                'nearby_distance': json.dumps(['15km', '20km', '5km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1508807526345-15e9b5f4eaff?w=800'
            }
        ])

    if hangzhou:
        attractions_data.extend([
            {
                'name': '西湖',
                'destination_id': hangzhou.id,
                'category': '景点',
                'description': '西湖是中国最著名的湖泊之一，被列入世界文化遗产名录，以"西湖十景"闻名于世。湖面面积约6.38平方公里，三面环山，自然风光与人文景观完美融合。',
                'address': '杭州市西湖区西湖风景名胜区',
                'latitude': 30.2465,
                'longitude': 120.1486,
                'ticket_price': '免费（部分景点需单独购票）',
                'opening_hours': '全天开放',
                'best_season': '春季秋季',
                'suggested_duration': 240,
                'play_tips': '建议骑行环湖，或者乘船游湖。经典路线：断桥残雪→白堤→苏堤→花港观鱼→雷峰塔→柳浪闻莺。建议清晨或傍晚前往，避开人流。',
                'recommended_dishes': json.dumps(['东坡肉', '龙井虾仁', '西湖醋鱼', '叫化鸡'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['雷峰塔', '灵隐寺', '宋城'], ensure_ascii=False),
                'nearby_distance': json.dumps(['2km', '5km', '8km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1598887142487-3c854d51eabb?w=800'
            },
            {
                'name': '灵隐寺',
                'destination_id': hangzhou.id,
                'category': '景点',
                'description': '灵隐寺是杭州最著名的佛教寺院，始建于东晋咸和元年，距今已有1700多年历史。寺内有飞来峰、永福寺、韬光寺等众多景点，香火旺盛。',
                'address': '杭州市西湖区灵隐路法云弄1号',
                'latitude': 30.2347,
                'longitude': 120.1024,
                'ticket_price': '飞来峰45元，灵隐寺30元（香花券）',
                'opening_hours': '06:30-18:00',
                'best_season': '四季皆宜',
                'suggested_duration': 180,
                'play_tips': '建议早上去，可以避开人流。请香需要在门口购买，寺内有免费三炷香。素斋是灵隐寺的特色，可以尝试。',
                'nearby_attractions': json.dumps(['西湖', '龙井村', '梅家坞'], ensure_ascii=False),
                'nearby_distance': json.dumps(['5km', '3km', '4km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1545893835-abaa50cbe628?w=800'
            }
        ])

    if chengdu:
        attractions_data.extend([
            {
                'name': '大熊猫繁育研究基地',
                'destination_id': chengdu.id,
                'category': '景点',
                'description': '成都大熊猫繁育研究基地是世界著名的大熊猫迁地保护基地，拥有世界上最大的大熊猫人工圈养种群。可以近距离观赏大熊猫的日常生活，是来成都必去的景点。',
                'address': '成都市成华区外北熊猫大道1375号',
                'latitude': 30.7375,
                'longitude': 104.1452,
                'ticket_price': '全价票55元，半价票27元',
                'opening_hours': '07:30-18:00（17:00停止入园）',
                'best_season': '四季皆宜（夏季熊猫在空调房）',
                'suggested_duration': 180,
                'play_tips': '建议早上去（9点前），此时熊猫最活跃。基地很大，建议乘坐观光车。月亮产房在特定季节开放，值得一看。',
                'nearby_attractions': json.dumps(['宽窄巷子', '锦里', '武侯祠'], ensure_ascii=False),
                'nearby_distance': json.dumps(['10km', '12km', '11km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800'
            },
            {
                'name': '宽窄巷子',
                'destination_id': chengdu.id,
                'category': '景点',
                'description': '宽窄巷子是成都现存规模最大的清古街道，由宽巷子、窄巷子和井巷子三条平行排列的老街组成。这里是成都最具老成都风情的商业街区，汇集了众多茶馆、餐厅和特色小店。',
                'address': '成都市青羊区长顺街附近',
                'latitude': 30.6598,
                'longitude': 104.0535,
                'ticket_price': '免费',
                'opening_hours': '全天（店铺一般10:00-22:00）',
                'best_season': '四季皆宜',
                'suggested_duration': 120,
                'play_tips': '建议下午或傍晚前往，可以喝茶、看川剧、吃小吃。掏耳朵是成都特色体验，可以尝试。宽巷子比较热闹，窄巷子更有格调。',
                'recommended_dishes': json.dumps(['担担面', '龙抄手', '三大炮', '串串香'], ensure_ascii=False),
                'nearby_attractions': json.dumps(['锦里', '武侯祠', '春熙路'], ensure_ascii=False),
                'nearby_distance': json.dumps(['2km', '2.5km', '3km'], ensure_ascii=False),
                'image_url': 'https://images.unsplash.com/photo-1590053886622-3f0a87eb5c6b?w=800'
            }
        ])

    # 添加到数据库
    for data in attractions_data:
        existing = Attraction.query.filter_by(name=data['name']).first()
        if not existing:
            attraction = Attraction(**data)
            db.session.add(attraction)

    db.session.commit()
    print(f'已添加 {len(attractions_data)} 个景点数据')
