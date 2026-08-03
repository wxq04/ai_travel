import json
import requests
import time
import hashlib
import base64
import hmac
import logging
from typing import List, Dict, Optional
from app.extensions import redis_client
from flask import current_app

# 使用Python标准logger以避免应用上下文问题
logger = logging.getLogger(__name__)


def try_parse_json(text: str) -> Optional[Dict]:
    """
    尝试从任意文本中提取并解析 JSON。
    支持：纯 JSON、```json ``` 包裹、``` ``` 包裹、混在文本中。
    """
    if not text:
        return None

    text = text.strip()

    # 方法1：直接解析（如果是纯JSON）
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 方法2：提取 ```json ``` 块
    if '```json' in text:
        start = text.find('```json') + 7
        end = text.find('```', start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # 方法3：提取 ``` ``` 块
    if '```' in text:
        start = text.find('```') + 3
        end = text.find('```', start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # 方法4：尝试用正则提取第一个 { ... } 对象
    import re
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


class AIService:
    """
    AI 服务封装类，支持多种免费AI API（Deepseek/讯飞星火/OpenAI等）
    所有调用统一 timeout=60s，异常时返回友好错误信息
    """

    def __init__(self, app=None):
        # 如果传入 app，使用 app.config
        if app:
            self.api_key = app.config.get('AI_API_KEY', '')
            self.api_secret = app.config.get('AI_API_SECRET', '')
            self.api_fid = app.config.get('AI_API_FID', '')
            self.base_url = app.config.get('AI_BASE_URL', 'https://api.deepseek.com/v1')
            self.model = app.config.get('AI_MODEL', 'deepseek-chat')
        else:
            # 否则使用 current_app
            self.api_key = current_app.config.get('AI_API_KEY', '')
            self.api_secret = current_app.config.get('AI_API_SECRET', '')
            self.api_fid = current_app.config.get('AI_API_FID', '')
            self.base_url = current_app.config.get('AI_BASE_URL', 'https://api.deepseek.com/v1')
            self.model = current_app.config.get('AI_MODEL', 'deepseek-chat')
        
        self.timeout = 60
        # 判断是否使用讯飞星火 API
        self.is_xunfei = 'xf-yun' in self.base_url.lower()
        
        # 如果没有配置API密钥，使用内置的免费API密钥（Deepseek）
        if not self.api_key:
            # Deepseek免费API（示例密钥，实际使用时请替换）
            self.api_key = 'sk-demo-key-replace-with-your-own'
            self.base_url = 'https://api.deepseek.com/v1'
            self.model = 'deepseek-chat'

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
            logger.error('AI API 调用超时')
            return None
        except Exception as e:
            logger.error(f'AI API 调用异常: {str(e)}')
            return None

    def _call_openai_api(self, messages: List[Dict], stream: bool = False):
        """调用 OpenAI/Deeksseek 兼容 API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 4000,
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
            logger.error(f'AI API 调用失败: {response.status_code} - {response.text}')
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
            logger.error(f'讯飞星火 API 调用失败: {response.status_code} - {response.text}')
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
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    try:
                        return json.loads(cached_result)
                    except json.JSONDecodeError:
                        pass
            except:
                pass  # Redis不可用时继续

        # 构造 system prompt - 更详细的指令
        system_prompt = """你是一位专业的旅行规划师，精通中国各大城市的旅游景点、美食、住宿和交通。

请根据用户的需求生成详细的旅行行程规划。

【重要要求】
1. 你必须返回严格的JSON格式数据，不要包含任何其他文字说明
2. JSON结构必须符合以下格式，每个字段都要填写：
{
  "days": [
    {
      "day": 1,
      "theme": "当天主题（如：历史文化之旅、美食探索等）",
      "activities": [
        {
          "type": "景点" 或 "美食" 或 "交通" 或 "住宿" 或 "购物",
          "name": "具体名称（如：洪崖洞、磁器口古镇）",
          "description": "详细介绍，50字以上，包含历史背景、特色、推荐理由等",
          "location": "详细地址或位置描述",
          "duration": 游览时长（分钟）,
          "cost": 预估费用（人民币元）,
          "tip": "实用小贴士，如预约方式、最佳游览时间、注意事项等"
        }
      ]
    }
  ]
}

【行程规划原则】
1. 每天安排3-5个活动，包含景点、美食
2. 景点要有真实性和代表性，选择当地最值得去的
3. 美食推荐要具体到餐厅名称或菜品
4. 费用要合理，符合预算等级（经济/舒适/豪华）
5. 每项活动都要有详细的小贴士
6. 行程要有逻辑性，考虑交通时间和顺序"""

        # 构造 user prompt - 根据预算调整费用
        budget_desc = {
            '经济': '节省预算，选择性价比高的选项',
            '舒适': '中等消费，注重体验和舒适度',
            '豪华': '高品质体验，可以选择高端选项'
        }
        budget_info = budget_desc.get(budget, '舒适型')

        user_prompt = f"""请为以下旅行需求生成行程规划：

目的地城市：{destination}
旅行天数：{days} 天
预算等级：{budget} - {budget_info}
兴趣偏好：{', '.join(tags) if tags else '无特定偏好'}
补充信息：{extra_info if extra_info else '无'}

请生成JSON格式的行程安排，确保每个景点都是{destination}真实存在的著名景点。

【关键要求】
1. location 字段必须填写完整地址，格式为："城市名+景点名/详细地址"，例如："苏州市姑苏区东北街178号拙政园" 或 "苏州市吴中区留园路拙政园"
2. 每个 location 都要以城市名开头，方便地理编码"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # 调用 AI API
        result = self._call_ai_api(messages)

        if not result:
            logger.warning('AI API 调用失败，使用默认行程')
            return self._generate_default_itinerary(destination, days, budget)

        try:
            # 使用健壮的 JSON 解析
            itinerary_data = try_parse_json(result)

            if itinerary_data is None:
                raise ValueError('无法解析 AI 返回的 JSON')

            # 验证数据结构
            if 'days' not in itinerary_data:
                raise ValueError('Invalid response format')

            # 确保 days 是列表
            if not isinstance(itinerary_data.get('days'), list):
                raise ValueError('days 必须是列表')

            # 缓存结果（TTL 1小时）
            if redis_client:
                try:
                    redis_client.setex(cache_key, 3600, json.dumps(itinerary_data))
                except:
                    pass

            return itinerary_data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f'AI 返回的不是有效 JSON: {e}\n原始响应前500字: {result[:500]}')
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

    def search_attractions(self, keyword: str, destination: str = '', category: str = '') -> List[Dict]:
        """使用 AI 搜索景点信息（当本地数据库不足时补充）"""
        try:
            system_prompt = """你是一位专业的中国旅行攻略专家，精通全国各地的景点、美食、购物、文化体验等信息。

请根据用户输入的关键词，搜索并推荐相关景点。

【输出要求】
返回JSON格式的景点列表（最多10个）：
{
  "attractions": [
    {
      "name": "景点名称",
      "category": "景点/餐厅/购物/文化/自然",
      "description": "景点简介，50字以上",
      "address": "建议地址（可填"待确认"）",
      "ticket_price": "门票信息（如：免费、50元、80元等）",
      "opening_hours": "开放时间（如：全天开放、09:00-18:00等）",
      "best_season": "最佳游览季节",
      "suggested_duration": "建议游玩时长（分钟数字）",
      "play_tips": "游玩建议，30字以上",
      "recommended_dishes": ["推荐美食1", "推荐美食2"]（可为空数组）
    }
  ]
}

请确保返回的景点真实存在且有实际价值，不要编造虚假信息。"""

            user_content = f"""请搜索以下关键词相关的景点：

关键词：{keyword}"""

            if destination:
                user_content += f"\n所在目的地/城市：{destination}"
            if category:
                user_content += f"\n景点类别：{category}"

            user_content += "\n\n请返回JSON格式的景点列表。"

            result = self._call_ai_api([
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ])

            if not result:
                return []

            # 解析 JSON
            result_clean = result.strip()
            if '```json' in result_clean:
                start = result_clean.find('```json') + 7
                end = result_clean.find('```', start)
                result_clean = result_clean[start:end].strip()
            elif '```' in result_clean:
                start = result_clean.find('```') + 3
                end = result_clean.find('```', start)
                result_clean = result_clean[start:end].strip()

            data = json.loads(result_clean)
            attractions = data.get('attractions', [])

            # 清理并格式化数据
            cleaned_attractions = []
            for attr in attractions:
                cleaned = {
                    'name': attr.get('name', '').strip(),
                    'category': attr.get('category', '景点'),
                    'description': attr.get('description', ''),
                    'address': attr.get('address', ''),
                    'ticket_price': attr.get('ticket_price', ''),
                    'opening_hours': attr.get('opening_hours', ''),
                    'best_season': attr.get('best_season', ''),
                    'suggested_duration': int(attr.get('suggested_duration', 120)),
                    'play_tips': attr.get('play_tips', ''),
                    'recommended_dishes': attr.get('recommended_dishes', []),
                    'is_ai_generated': True
                }
                cleaned_attractions.append(cleaned)

            return cleaned_attractions

        except json.JSONDecodeError:
            logger.error(f'AI 景点搜索返回的不是有效 JSON')
            return []
        except Exception as e:
            logger.error(f'AI 景点搜索失败: {str(e)}')
            return []

    def adjust_itinerary(self, itinerary_data: Dict, user_request: str, destination: str = '',
                         budget: str = '舒适') -> Dict:
        """
        使用 AI 智能调整行程。

        Args:
            itinerary_data: 原始行程数据
            user_request: 用户调整需求（如"第二天不想去爬山，增加更多美食"）
            destination: 目的地名称
            budget: 预算等级

        Returns:
            包含以下键的字典:
                - adjusted_days: 调整后的 days 列表（可直接用于数据库）
                - ai_response: AI 对用户需求的理解和建议的文本回复
                - changes_summary: 更改摘要（用于预览）
        """
        # 构建行程摘要供 AI 参考
        days_summary = []
        for day in itinerary_data.get('days', []):
            activities_str = []
            for act in day.get('activities', []):
                activities_str.append(
                    f"- {act.get('name', '')} ({act.get('type', '')}, "
                    f"约{act.get('duration', 0)}分钟, 费用约{act.get('cost', 0)}元)"
                )
            days_summary.append(
                f"第{day.get('day', 0)}天【{day.get('theme', '自由活动')}】：\n" +
                "\n".join(activities_str)
            )

        system_prompt = """你是一位专业的旅行规划师。你需要理解用户的行程调整需求，并给出具体的、可执行的调整方案。

【重要】
1. 用户会提出各种调整需求（如不想去某类活动、增加美食、调整预算、减少天数等）
2. 你必须根据用户需求，直接修改行程 JSON 数据
3. 你必须返回严格的 JSON 格式，包含两个字段：
{
  "ai_response": "你对用户的回复，说明你理解了需求以及你做了什么调整（用中文，50字以上）",
  "adjusted_days": [修改后的 days 列表，每个 day 包含 day, theme, activities 字段]
}

【行程修改原则】
- 增加活动：选择该城市真实存在的景点/餐厅，给出具体名称和地址
- 删除活动：直接移除对应的 activities 项
- 替换活动：保持 activities 总数不变，替换为用户期望的类型
- 调整顺序：调换 activities 的顺序
- 预算调整：调整 cost 字段数值（经济×0.6，豪华×1.8）
- 不要创建不存在的景点，确保所有地点真实可信

【天数调整原则】（非常重要！）
- 如果用户要求减少天数（如4天变3天），必须将 adjusted_days 缩减到指定天数
- 做法：将后面几天的内容合并到前面，或者直接删除后面的天数
- 如果合并，要合并 activities（注意去重，不要重复相同活动）
- 最终 adjusted_days 数组长度必须等于用户要求的天数
- day 字段要重新编号（1, 2, 3...），不能有缺失或重复

【天数调整示例】
- 原始4天，用户要求减少到3天：
  adjusted_days 应该只包含3个元素（第1、2、3天）
  第4天的活动可以合并到第3天，或者直接删除

- 原始3天，用户要求增加1天：
  adjusted_days 应该包含4个元素
  新增的第4天需要规划合理的活动"""

        user_prompt = f"""请帮我调整以下行程：

【目的地】：{destination}
【预算】：{budget}
【用户需求】：{user_request}

【当前行程】：
{chr(10).join(days_summary)}

请根据用户需求修改行程，返回 JSON 格式结果。"""

        result = self._call_ai_api([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ])

        if not result:
            return {
                'adjusted_days': itinerary_data.get('days', []),
                'ai_response': '抱歉，AI 服务暂时不可用，无法处理您的请求。',
                'changes_summary': '未做任何更改'
            }

        parsed = try_parse_json(result)

        if parsed is None:
            logger.warning(f'AI 行程调整返回无效 JSON: {result[:300]}')
            return {
                'adjusted_days': itinerary_data.get('days', []),
                'ai_response': f'我已经收到您的需求"{user_request}"，但当前无法处理。请稍后重试或尝试更简洁的描述。',
                'changes_summary': '未做任何更改'
            }

        # 验证 adjusted_days
        adjusted_days = parsed.get('adjusted_days', itinerary_data.get('days', []))
        if not isinstance(adjusted_days, list):
            adjusted_days = itinerary_data.get('days', [])

        ai_response = parsed.get('ai_response',
            f'好的，我已根据"{user_request}"调整了行程。')

        # 生成更改摘要
        changes_summary = self._generate_changes_summary(itinerary_data.get('days', []), adjusted_days)

        return {
            'adjusted_days': adjusted_days,
            'ai_response': ai_response,
            'changes_summary': changes_summary
        }

    def _generate_changes_summary(self, old_days: List, new_days: List) -> str:
        """生成更改摘要"""
        lines = []

        old_flat = []
        for day in old_days:
            for act in day.get('activities', []):
                old_flat.append(f"{day.get('day', 0)}:{act.get('name', '')}")

        new_flat = []
        for day in new_days:
            for act in day.get('activities', []):
                new_flat.append(f"{day.get('day', 0)}:{act.get('name', '')}")

        removed = set(old_flat) - set(new_flat)
        added = set(new_flat) - set(old_flat)

        if removed:
            lines.append(f'• 移除：{"、".join(removed)}')
        if added:
            lines.append(f'• 新增：{"、".join(added)}')
        if not lines:
            lines.append('• 已调整活动顺序或内容')

        return '\n'.join(lines)

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