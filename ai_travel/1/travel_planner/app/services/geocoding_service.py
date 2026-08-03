import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class GeocodingService:
    """地理编码服务 - 将地址转换为坐标"""

    def __init__(self, app=None):
        if app:
            self.amap_key = app.config.get('AMAP_KEY', '')
        else:
            self.amap_key = current_app.config.get('AMAP_KEY', '')

    def geocode(self, address, city=''):
        """调用高德地图地理编码API"""
        if not self.amap_key:
            return self._fallback_coordinates(city)

        # 如果地址不包含城市名，自动添加
        search_address = address
        if city and city not in address:
            search_address = f'{city}{address}'

        try:
            url = 'https://restapi.amap.com/v3/geocode/geo'
            params = {
                'key': self.amap_key,
                'address': search_address,
                'city': city
            }

            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            if data.get('geocodes'):
                location = data['geocodes'][0]['location'].split(',')
                return {
                    'lng': float(location[0]),
                    'lat': float(location[1])
                }
        except Exception as e:
            logger.error(f'地理编码失败: {e}')

        return self._fallback_coordinates(city)

    def geocode_batch(self, addresses, city=''):
        """批量地理编码"""
        results = []
        for address in addresses:
            coords = self.geocode(address, city)
            results.append({
                'address': address,
                'lng': coords.get('lng', 121.4737),
                'lat': coords.get('lat', 31.2304)
            })
        return results

    def _fallback_coordinates(self, city):
        """城市默认坐标"""
        city_coords = {
            '上海': {'lng': 121.4737, 'lat': 31.2304},
            '北京': {'lng': 116.4074, 'lat': 39.9042},
            '杭州': {'lng': 120.1551, 'lat': 30.2741},
            '成都': {'lng': 104.0657, 'lat': 30.6598},
            '重庆': {'lng': 106.5516, 'lat': 29.5632},
            '西安': {'lng': 108.9402, 'lat': 34.3416},
            '苏州': {'lng': 120.6196, 'lat': 31.2990},
            '南京': {'lng': 118.7969, 'lat': 32.0603},
            '广州': {'lng': 113.2644, 'lat': 23.1291},
            '深圳': {'lng': 114.0579, 'lat': 22.5431},
            '武汉': {'lng': 114.3055, 'lat': 30.5928},
            '长沙': {'lng': 112.9388, 'lat': 28.2282},
            '厦门': {'lng': 118.0894, 'lat': 24.4798},
            '青岛': {'lng': 120.3826, 'lat': 36.0671},
            '大连': {'lng': 121.6147, 'lat': 38.9140},
            '天津': {'lng': 117.3616, 'lat': 39.3434},
            '哈尔滨': {'lng': 126.5340, 'lat': 45.8038},
            '长春': {'lng': 125.3245, 'lat': 43.8171},
            '沈阳': {'lng': 123.4315, 'lat': 41.8057},
            '郑州': {'lng': 113.6254, 'lat': 34.7466},
            '济南': {'lng': 116.9940, 'lat': 36.6562},
            '太原': {'lng': 112.5489, 'lat': 37.8706},
            '合肥': {'lng': 117.2830, 'lat': 31.8612},
            '南昌': {'lng': 115.8581, 'lat': 28.6829},
            '昆明': {'lng': 102.7129, 'lat': 25.0406},
            '贵阳': {'lng': 106.7135, 'lat': 26.5983},
            '南宁': {'lng': 108.3661, 'lat': 22.8170},
            '海口': {'lng': 110.1999, 'lat': 20.0444},
            '三亚': {'lng': 109.5119, 'lat': 18.2528},
            '珠海': {'lng': 113.5537, 'lat': 22.2243},
            '东莞': {'lng': 113.7518, 'lat': 23.0489},
            '佛山': {'lng': 113.1227, 'lat': 23.0288},
            '无锡': {'lng': 120.2994, 'lat': 31.5747},
            '常州': {'lng': 119.9740, 'lat': 31.8113},
            '南通': {'lng': 120.8646, 'lat': 32.0150},
            '温州': {'lng': 120.6994, 'lat': 28.0006},
            '宁波': {'lng': 121.5440, 'lat': 29.8683},
            '义乌': {'lng': 120.0819, 'lat': 29.3062},
            '绍兴': {'lng': 120.5802, 'lat': 30.0304},
            '嘉兴': {'lng': 120.7550, 'lat': 30.7480},
            '洛阳': {'lng': 112.4540, 'lat': 34.6197},
            '开封': {'lng': 114.3074, 'lat': 34.7971},
            '敦煌': {'lng': 94.6620, 'lat': 40.1421},
            '拉萨': {'lng': 91.1322, 'lat': 29.6500},
            '丽江': {'lng': 100.2296, 'lat': 26.8721},
            '大理': {'lng': 100.2679, 'lat': 25.6065},
            '桂林': {'lng': 110.2901, 'lat': 25.2742},
            '阳朔': {'lng': 110.4855, 'lat': 24.7796},
            '乌鲁木齐': {'lng': 87.6177, 'lat': 43.7928},
            '兰州': {'lng': 103.8343, 'lat': 36.0611},
            '呼和浩特': {'lng': 111.7656, 'lat': 40.8429},
        }
        return city_coords.get(city, {'lng': 121.4737, 'lat': 31.2304})


# 全局实例
geocoding_service = None


def init_geocoding_service(app=None):
    """初始化地理编码服务"""
    global geocoding_service
    geocoding_service = GeocodingService(app)
    return geocoding_service
