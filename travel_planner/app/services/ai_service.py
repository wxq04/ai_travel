import json
import requests
import time
import hashlib
import base64
import hmac
from typing import List, Dict, Optional
from app.extensions import redis_client
from flask import current_app


class AIService:
    """
    AI 服务封装类，支持替换不同 AI 接口（OpenAI/讯飞星火/百度文心等）
    所有调用统一 timeout=30s，异常时返回友好错误信息
    """

    def __init__(self, app=None):
        # 如果传入 app，使用 app.config
        if app:
            self.api_key = app.config.get('AI_API_KEY', '')
            self.api_secret = app.config.get('AI_API_SECRET', '')
            self.api_fid = app.config.get('AI_API_FID', '')
            self.base_url = app.config.get('AI_BASE_URL', 'https://api.openai.com/v1')
            self.model = app.config.get('AI_MODEL', 'gpt-3.5-turbo')
        else:
            # 否则使用 current_app
            self.api_key = current_app.config.get('AI_API_KEY', '')
            self.api_secret = current_app.config.get('AI_API_SECRET', '')
            self.api_fid = current_app.config.get('AI_API_FID', '')
            self.base_url = current_app.config.get('AI_BASE_URL', 'https://api.openai.com/v1')
            self.model = current_app.config.get('AI_MODEL', 'gpt-3.5-turbo')
        
        self.timeout = 30
        # 判断是否使用讯飞星火 API
        self.is_xunfei = 'xf-yun' in self.base_url.lower()

    def _get_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def _generate_xunfei_signature(self, date: str) -> str:
        """生成讯飞星火 API 签名"""
        if not self.api_key or not self.api_secret:
            return ""
        
        # 构造签名串
        signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /chat/completions HTTP/1.1"
        
        # 使用 HMAC-SHA256 签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64 编码
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构造 Authorization
        authorization = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        
        return authorization

    def _call_ai_api(self, messages: List[Dict], stream: bool = False) -> Optional[str]:
        """调用 AI API"""
        try:
            if self.is_xunfei:
                return self._call_xunfei_api(messages, stream)
            else:
                return self._call_openai_api(messages, stream)

        except requests.Timeout:
            current_app.logger.error('AI API 调用超时')
            return None
        except Exception as e:
            current_app.logger.error(f'AI API 调用异常: {str(e)}')
            return None

    def _call_openai_api(self, messages: List[Dict], stream: bool = False):
        """调用 OpenAI 兼容 API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream': stream
        }

        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=self.timeout,
            stream=stream
        )

        if response.status_code != 200:
            current_app.logger.error(f'AI API 调用失败: {response.status_code} - {response.text}')
            return None

        if stream:
            return response
        else:
            result = response.json()
            return result['choices'][0]['message']['content']

    def _call_xunfei_api(self, messages: List[Dict], stream: bool = False):
        """调用讯飞星火 API"""
        # 获取当前时间（UTC）
        now = time.time()
        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(now))
        
        # 生成签名
        authorization = self._generate_xunfei_signature(date)
        
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json',
            'Host': 'spark-api.xf-yun.com',
            'Date': date
        }

        # 构造讯飞星火格式的请求体
        # 提取用户消息
        user_content = ""
        system_content = ""
        for msg in messages:
            if msg['role'] == 'system':
                system_content = msg['content']
            elif msg['role'] == 'user':
                user_content = msg['content']

        payload = {
            'header': {
                'app_id': self.api_key,
                'uid': 'travel_planner_user'
            },
            'parameter': {
                'chat': {
                    'domain': 'general',
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'top_k': 4,
                    'stream': stream,
                    'system_prompt': system_content
                }
            },
            'payload': {
                'message': {
                    'text': [
                        {
                            'role': 'user',
                            'content': user_content
                        }
                    ]
                }
            }
        }

        # 根据模型版本选择正确的端点
        url = f'{self.base_url}/chat/completions'
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
            stream=stream
        )

        if response.status_code != 200:
            current_app.logger.error(f'讯飞星火 API 调用失败: {response.status_code} - {response.text}')
            return None

        if stream:
            return response
        else:
            result = response.json()
            # 解析讯飞星火格式的响应
            if result.get('code') == 0 and result.get('payload'):
                choices = result['payload'].get('choices', {}).get('text', [])
                if choices:
                    return choices[0].get('content', '')
            return None

    def generate_itinerary(self, destination: str, days: int, budget: str,
                          tags: List[str], extra_info: str = "") -> Optional[Dict]:
        """
        生成行程，返回 JSON 格式数据结构
        """
        # 构造缓存键
        cache_key = self._get_cache_key('itinerary', destination, days, budget, tags, extra_info)

        # 先查 Redis 缓存
        if redis_client:
            cached_result = redis_client.get(cache_key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass

        # 构造 system prompt
        system_prompt = """你是一位专业的旅行规划师。请根据用户提供的信息生成详细的旅行行程。

要求：
1. 必须返回严格的 JSON 格式，不要包含任何其他文字说明
2. JSON 结构必须符合以下格式：
{
  "days": [
    {
      "day": 1,
      "theme": "当天主题",
      "activities": [
        {
          "type": "景点/餐厅/交通/住宿",
          "name": "活动名称",
          "description": "活动描述",
          "location": "地点",
          "duration": 120,
          "cost": 50,
          "tip": "小贴士"
        }
      ]
    }
  ]
}

3. 每天的活动数量建议 3-5 个
4. 活动类型包括：景点、餐厅、交通、住宿
5. duration 单位为分钟，cost 单位为人民币
6. tip 提供实用建议"""

        # 构造 user prompt
        user_prompt = f"""请为以下旅行需求生成行程：

目的地：{destination}
天数：{days} 天
预算等级：{budget}
兴趣标签：{', '.join(tags) if tags else '无特定偏好'}
补充信息：{extra_info if extra_info else '无'}

请生成 JSON 格式的行程安排。"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # 调用 AI API
        result = self._call_ai_api(messages)

        if not result:
            # 返回默认行程结构
            return self._generate_default_itinerary(destination, days, budget)

        try:
            # 解析 JSON
            itinerary_data = json.loads(result)

            # 缓存结果（TTL 1小时）
            if redis_client:
                redis_client.setex(cache_key, 3600, json.dumps(itinerary_data))

            return itinerary_data
        except json.JSONDecodeError:
            current_app.logger.error('AI 返回的不是有效 JSON')
            return self._generate_default_itinerary(destination, days, budget)

    def generate_itinerary_stream(self, destination: str, days: int, budget: str,
                                   tags: List[str], extra_info: str = ""):
        """流式生成，yield SSE 格式数据"""
        # 构造 system prompt
        system_prompt = """你是一位专业的旅行规划师。请根据用户提供的信息生成详细的旅行行程。

要求：
1. 必须返回严格的 JSON 格式
2. JSON 结构必须符合以下格式：
{
  "days": [
    {
      "day": 1,
      "theme": "当天主题",
      "activities": [
        {
          "type": "景点/餐厅/交通/住宿",
          "name": "活动名称",
          "description": "活动描述",
          "location": "地点",
          "duration": 120,
          "cost": 50,
          "tip": "小贴士"
        }
      ]
    }
  ]
}"""

        user_prompt = f"""请为以下旅行需求生成行程：

目的地：{destination}
天数：{days} 天
预算等级：{budget}
兴趣标签：{', '.join(tags) if tags else '无特定偏好'}
补充信息：{extra_info if extra_info else '无'}

请生成 JSON 格式的行程安排。"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # 调用 AI API（流式）
        response = self._call_ai_api(messages, stream=True)

        if not response:
            yield f"data: {json.dumps({'error': 'AI 服务暂时不可用'})}\n\n"
            return

        try:
            full_content = ""
            if self.is_xunfei:
                # 讯飞星火流式响应解析
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get('code') == 0 and data.get('payload'):
                                    choices = data['payload'].get('choices', {}).get('text', [])
                                    if choices:
                                        content = choices[0].get('content', '')
                                        if content:
                                            full_content += content
                                            yield f"data: {json.dumps({'content': content})}\n\n"
                                    # 检查是否结束
                                    status = data['payload'].get('choices', {}).get('status', 0)
                                    if status == 2:
                                        break
                            except json.JSONDecodeError:
                                continue
            else:
                # OpenAI 格式流式响应解析
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0]['delta']
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_content += content
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue

            # 发送完成信号
            yield f"data: {json.dumps({'status': 'completed', 'full_content': full_content})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    def chat_adjust(self, itinerary_data: Dict, conversation_history: List[Dict],
                   user_message: str) -> Optional[str]:
        """多轮对话调整行程，维护对话上下文"""
        # 构造 system prompt
        system_prompt = """你是一位专业的旅行规划师助手。用户会根据已生成的行程提出调整建议。

要求：
1. 理解用户的调整需求
2. 返回调整后的完整行程 JSON 或说明无法调整的原因
3. 保持友好和专业的语气"""

        # 构造消息历史
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]

        # 添加对话历史（只保留最近几条）
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        for msg in recent_history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # 添加当前行程数据
        messages.append({
            'role': 'assistant',
            'content': f'当前行程数据：\n{json.dumps(itinerary_data, ensure_ascii=False)}'
        })

        # 添加用户消息
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # 调用 AI API
        result = self._call_ai_api(messages)

        if not result:
            return "抱歉，我暂时无法处理您的请求。请稍后再试。"

        return result

    def generate_summary(self, itinerary_data: Dict) -> str:
        """生成行程摘要（200字以内，突出亮点），用于 PDF 导出"""
        system_prompt = """你是一位专业的旅行文案撰写师。请根据行程数据生成简洁的摘要。

要求：
1. 字数控制在200字以内
2. 突出行程亮点和特色
3. 语言简洁优美，吸引人
4. 不要包含具体的时间和费用信息"""

        user_prompt = f"""请为以下行程生成摘要：

行程数据：
{json.dumps(itinerary_data, ensure_ascii=False)}

请生成简洁的摘要文字。"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self._call_ai_api(messages)

        if not result:
            # 生成默认摘要
            days_count = len(itinerary_data.get('days', []))
            return f"这是一次精彩的{days_count}日旅行，涵盖多个特色景点和美食体验，让您充分感受旅途的魅力。"

        return result

    def recommend_destinations(self, user_tags: List[str],
                               visited_destinations: List[str]) -> List[Dict]:
        """个性化推荐，从数据库已有目的地中挑选最匹配的3-5个"""
        from app.models.destination import Destination
        from app.extensions import db

        # 构造缓存键
        cache_key = self._get_cache_key('recommend', user_tags, visited_destinations)

        # 查缓存
        if redis_client:
            cached_result = redis_client.get(cache_key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass

        # 从数据库查询目的地
        query = Destination.query

        # 排除已访问的目的地
        if visited_destinations:
            query = query.filter(Destination.name.notin_(visited_destinations))

        # 基于标签匹配
        recommendations = []
        if user_tags:
            for tag in user_tags:
                matching = query.filter(
                    Destination.category.contains(tag) |
                    Destination.description.contains(tag)
                ).limit(2).all()

                for dest in matching:
                    if dest.id not in [r['id'] for r in recommendations]:
                        recommendations.append({
                            'id': dest.id,
                            'name': dest.name,
                            'city': dest.city,
                            'category': dest.category,
                            'match_reason': f'匹配您的"{tag}"兴趣',
                            'avg_rating': dest.avg_rating,
                            'description': dest.description[:100] if dest.description else ''
                        })

        # 补充热门目的地
        if len(recommendations) < 5:
            hot_dests = query.order_by(Destination.view_count.desc()).limit(5 - len(recommendations)).all()
            for dest in hot_dests:
                if dest.id not in [r['id'] for r in recommendations]:
                    recommendations.append({
                        'id': dest.id,
                        'name': dest.name,
                        'city': dest.city,
                        'category': dest.category,
                        'match_reason': '热门目的地',
                        'avg_rating': dest.avg_rating,
                        'description': dest.description[:100] if dest.description else ''
                    })

        # 缓存结果（TTL 1小时）
        if redis_client:
            redis_client.setex(cache_key, 3600, json.dumps(recommendations))

        return recommendations[:5]

    def _generate_default_itinerary(self, destination: str, days: int, budget: str) -> Dict:
        """生成默认行程结构（当 AI 调用失败时）"""
        budget_multiplier = 1 if budget == '经济' else 2 if budget == '舒适' else 5

        itinerary = {
            'days': []
        }

        for day_num in range(1, days + 1):
            day_data = {
                'day': day_num,
                'theme': f'第{day_num}天：探索{destination}',
                'activities': [
                    {
                        'type': '景点',
                        'name': f'{destination}著名景点',
                        'description': f'探索{destination}的标志性景点',
                        'location': destination,
                        'duration': 120,
                        'cost': 100 * budget_multiplier,
                        'tip': '建议提前预约门票'
                    },
                    {
                        'type': '餐厅',
                        'name': '当地特色餐厅',
                        'description': '品尝当地美食',
                        'location': destination,
                        'duration': 60,
                        'cost': 50 * budget_multiplier,
                        'tip': '推荐尝试当地特色菜'
                    }
                ]
            }
            itinerary['days'].append(day_data)

        return itinerary


# 全局 AI 服务实例
ai_service = None


def init_ai_service(app=None):
    """初始化 AI 服务"""
    global ai_service
    ai_service = AIService(app)
    return ai_service