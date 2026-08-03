import requests
import json
from typing import Dict, List, Optional
from flask import current_app
from app.extensions import redis_client
from datetime import datetime, timedelta


class WeatherService:
    """
    天气服务类
    调用和风天气 API（或 OpenWeatherMap）获取目的地未来7天天气
    根据天气数据给行程活动打标签：☀️适合户外 / 🌧建议室内
    结果缓存到 Redis（TTL 3小时）
    """

    def __init__(self, app=None):
        # 和风天气 API 配置
        if app:
            self.api_key = app.config.get('WEATHER_API_KEY', '')
        else:
            self.api_key = current_app.config.get('WEATHER_API_KEY', '')
        self.base_url = 'https://devapi.qweather.com/v7'  # 和风天气开发版 API
        self.timeout = 10

    def _get_cache_key(self, location: str) -> str:
        """生成缓存键"""
        return f"weather:{location}"

    def get_location_id(self, city: str) -> Optional[str]:
        """获取城市 Location ID（和风天气需要）"""
        try:
            # 先查缓存
            cache_key = f"location_id:{city}"
            if redis_client:
                cached_id = redis_client.get(cache_key)
                if cached_id:
                    return cached_id

            # 调用 GeoAPI 查询城市 ID
            url = f"https://geoapi.qweather.com/v2/cities/lookup"
            params = {
                'location': city,
                'key': self.api_key
            }

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data['code'] == '200' and 'location' in data and len(data['location']) > 0:
                    location_id = data['location'][0]['id']

                    # 缓存结果（TTL 24小时）
                    if redis_client:
                        redis_client.setex(cache_key, 86400, location_id)

                    return location_id

            current_app.logger.error(f'获取城市 ID 失败: {city}')
            return None

        except Exception as e:
            current_app.logger.error(f'查询城市 ID 异常: {str(e)}')
            return None

    def get_7day_weather(self, city: str) -> Optional[List[Dict]]:
        """获取未来7天天气预报"""
        try:
            # 获取城市 Location ID
            location_id = self.get_location_id(city)
            if not location_id:
                # 如果无法获取 ID，尝试使用城市名直接查询（OpenWeatherMap 方式）
                return self._get_weather_openweathermap(city)

            # 查缓存
            cache_key = self._get_cache_key(location_id)
            if redis_client:
                cached_weather = redis_client.get(cache_key)
                if cached_weather:
                    try:
                        return json.loads(cached_weather)
                    except json.JSONDecodeError:
                        pass

            # 调用和风天气 API
            url = f"{self.base_url}/weather/7d"
            params = {
                'location': location_id,
                'key': self.api_key
            }

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data['code'] == '200':
                    weather_list = []

                    for day_data in data['daily']:
                        weather_info = {
                            'date': day_data['fxDate'],
                            'temp_max': int(day_data['tempMax']),
                            'temp_min': int(day_data['tempMin']),
                            'weather_day': day_data['textDay'],
                            'weather_night': day_data['textNight'],
                            'wind_dir': day_data['windDirDay'],
                            'wind_scale': day_data['windScaleDay'],
                            'humidity': int(day_data['humidity']),
                            'precipitation': float(day_data['precip']),
                            'uv_index': int(day_data.get('uvIndex', 0)),
                            'suitability': self._analyze_weather_suitability(day_data)
                        }
                        weather_list.append(weather_info)

                    # 缓存结果（TTL 3小时）
                    if redis_client:
                        redis_client.setex(cache_key, 10800, json.dumps(weather_list))

                    return weather_list

            current_app.logger.error(f'获取天气数据失败: {response.status_code}')
            return None

        except Exception as e:
            current_app.logger.error(f'获取天气数据异常: {str(e)}')
            return None

    def _get_weather_openweathermap(self, city: str) -> Optional[List[Dict]]:
        """使用 OpenWeatherMap API 获取天气（备用方案）"""
        try:
            # OpenWeatherMap API 配置（需要在 .env 中配置）
            owm_api_key = current_app.config.get('OPENWEATHERMAP_API_KEY', '')
            if not owm_api_key:
                return None

            # 查缓存
            cache_key = self._get_cache_key(city)
            if redis_client:
                cached_weather = redis_client.get(cache_key)
                if cached_weather:
                    try:
                        return json.loads(cached_weather)
                    except json.JSONDecodeError:
                        pass

            # 调用 OpenWeatherMap API
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': city,
                'appid': owm_api_key,
                'units': 'metric',
                'cnt': 7  # 7天数据
            }

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                weather_list = []

                for item in data['list']:
                    weather_info = {
                        'date': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d'),
                        'temp_max': int(item['main']['temp_max']),
                        'temp_min': int(item['main']['temp_min']),
                        'weather_day': item['weather'][0]['main'],
                        'weather_night': item['weather'][0]['main'],
                        'humidity': item['main']['humidity'],
                        'suitability': self._analyze_owm_weather_suitability(item)
                    }
                    weather_list.append(weather_info)

                # 缓存结果（TTL 3小时）
                if redis_client:
                    redis_client.setex(cache_key, 10800, json.dumps(weather_list))

                return weather_list

            return None

        except Exception as e:
            current_app.logger.error(f'OpenWeatherMap API 调用异常: {str(e)}')
            return None

    def _analyze_weather_suitability(self, weather_data: Dict) -> Dict:
        """分析天气适宜性，返回活动建议标签"""
        weather_text = weather_data['textDay']
        precip = float(weather_data['precip'])
        wind_scale = int(weather_data['windScaleDay'])
        temp_max = int(weather_data['tempMax'])
        uv_index = int(weather_data.get('uvIndex', 0))

        # 判断是否适合户外活动
        outdoor_suitable = True
        indoor_recommended = False
        tags = []

        # 雨雪天气
        if '雨' in weather_text or '雪' in weather_text or precip > 10:
            outdoor_suitable = False
            indoor_recommended = True
            tags.append('🌧建议室内')

        # 大风天气
        if wind_scale >= 6:
            outdoor_suitable = False
            tags.append('💨风力较大')

        # 高温天气
        if temp_max >= 35:
            tags.append('🔥高温预警')
            tags.append('建议避开中午时段')

        # 低温天气
        if temp_max <= 5:
            tags.append('❄️低温天气')
            tags.append('注意保暖')

        # 强紫外线
        if uv_index >= 8:
            tags.append('☀️紫外线强')
            tags.append('建议防晒')

        # 晴好天气
        if weather_text in ['晴', '多云', '少云'] and precip == 0:
            tags.append('☀️适合户外')
            tags.append('天气宜人')

        return {
            'outdoor_suitable': outdoor_suitable,
            'indoor_recommended': indoor_recommended,
            'tags': tags,
            'overall': '适合户外活动' if outdoor_suitable else '建议室内活动'
        }

    def _analyze_owm_weather_suitability(self, weather_data: Dict) -> Dict:
        """分析 OpenWeatherMap 天气适宜性"""
        weather_main = weather_data['weather'][0]['main']
        temp_max = weather_data['main']['temp_max']

        outdoor_suitable = True
        indoor_recommended = False
        tags = []

        # 雨雪天气
        if weather_main in ['Rain', 'Snow', 'Thunderstorm']:
            outdoor_suitable = False
            indoor_recommended = True
            tags.append('🌧建议室内')

        # 高温天气
        if temp_max >= 35:
            tags.append('🔥高温预警')

        # 晴好天气
        if weather_main in ['Clear', 'Clouds']:
            tags.append('☀️适合户外')

        return {
            'outdoor_suitable': outdoor_suitable,
            'indoor_recommended': indoor_recommended,
            'tags': tags,
            'overall': '适合户外活动' if outdoor_suitable else '建议室内活动'
        }

    def get_weather_for_activities(self, city: str, activities: List[Dict]) -> List[Dict]:
        """为行程活动添加天气标签"""
        weather_data = self.get_7day_weather(city)

        if not weather_data:
            # 无法获取天气数据，返回原活动列表
            return activities

        # 为每个活动添加天气建议
        for i, activity in enumerate(activities):
            if i < len(weather_data):
                weather_info = weather_data[i]
                activity['weather'] = {
                    'date': weather_info['date'],
                    'temp': f"{weather_info['temp_min']}°C - {weather_info['temp_max']}°C",
                    'weather': weather_info['weather_day'],
                    'suitability': weather_info['suitability']
                }

        return activities

    def get_weather_summary(self, city: str) -> Optional[str]:
        """获取天气摘要文字"""
        weather_data = self.get_7day_weather(city)

        if not weather_data:
            return None

        # 分析7天天气趋势
        avg_temp = sum([w['temp_max'] for w in weather_data]) / len(weather_data)
        rainy_days = sum([1 for w in weather_data if '雨' in w['weather_day'] or w['precipitation'] > 0])

        summary = f"未来7天平均气温 {avg_temp:.1f}°C"

        if rainy_days > 3:
            summary += f"，有{rainy_days}天可能降雨，建议准备雨具"
        elif rainy_days > 0:
            summary += f"，有{rainy_days}天可能降雨"
        else:
            summary += "，天气晴好，适合出行"

        return summary


# 全局天气服务实例
weather_service = None


def init_weather_service(app=None):
    """初始化天气服务"""
    global weather_service
    weather_service = WeatherService(app)
    return weather_service