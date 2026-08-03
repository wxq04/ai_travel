from flask import render_template, request, jsonify, session, current_app
from flask_login import login_required, current_user
from . import ai_assistant_bp
from app.services.ai_service import AIService
from app.extensions import csrf
import json


@ai_assistant_bp.route('/')
@login_required
def index():
    """AI助手页面"""
    # 获取对话历史
    chat_history = session.get('ai_chat_history', [])
    return render_template('ai_assistant/index.html', chat_history=chat_history)


@ai_assistant_bp.route('/chat', methods=['POST'])
@login_required
@csrf.exempt
def chat():
    """AI对话接口"""
    try:
        # 尝试多种方式获取JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # 尝试从表单数据中解析JSON
            if 'data' in data:
                try:
                    data = json.loads(data['data'])
                except:
                    data = {}
        
        user_message = ''
        if data:
            user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'success': False, 'message': '请输入消息'}), 400

        # 获取对话历史
        history = session.get('ai_chat_history', [])

        # 构建消息列表
        system_prompt = """你是一位专业、友好的AI旅行规划助手。你可以：

1. 回答用户关于旅游规划的问题
2. 推荐旅游景点、美食、住宿
3. 提供行程建议和优化方案
4. 解答旅行中的各类问题
5. 分享实用的旅行技巧

请用亲切、专业的语气回答。如果不确定某事，请诚实告知用户。
"""

        messages = [{'role': 'system', 'content': system_prompt}]

        # 添加历史对话（保留最近10条）
        for msg in history[-10:]:
            messages.append({'role': msg['role'], 'content': msg['content']})

        # 添加当前用户消息
        messages.append({'role': 'user', 'content': user_message})

        # 调用AI服务
        ai_service = AIService()
        response = ai_service._call_ai_api(messages)

        if response:
            # 清理AI返回的内容，移除markdown格式符号
            import re
            # 移除代码块标记
            response = re.sub(r'```[\w]*', '', response)
            response = re.sub(r'```', '', response)
            # 移除行首的特殊符号（如#、*、-等用于列表的）
            response = re.sub(r'^[\s]*[-*+]\s+', '', response, flags=re.MULTILINE)
            response = re.sub(r'^[\s]*\d+\.\s+', '', response, flags=re.MULTILINE)
            response = re.sub(r'^[\s]*[#*]+', '', response, flags=re.MULTILINE)
            # 清理多余的空行
            response = re.sub(r'\n{3,}', '\n\n', response)
            response = response.strip()

            # 更新对话历史
            history.append({'role': 'user', 'content': user_message})
            history.append({'role': 'assistant', 'content': response})
            session['ai_chat_history'] = history[-20:]  # 保留最近20条

            return jsonify({
                'success': True,
                'response': response
            })
        else:
            return jsonify({
                'success': False,
                'message': '抱歉，AI服务暂时不可用。请检查API配置或稍后再试。'
            }), 503

    except Exception as e:
        current_app.logger.error(f'AI助手错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'服务错误: {str(e)}'
        }), 500


@ai_assistant_bp.route('/clear', methods=['POST'])
@login_required
@csrf.exempt
def clear_history():
    """清除对话历史"""
    session.pop('ai_chat_history', None)
    return jsonify({'success': True})


@ai_assistant_bp.route('/quick-ask', methods=['POST'])
@login_required
@csrf.exempt
def quick_ask():
    """快捷问题"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            if 'data' in data:
                try:
                    data = json.loads(data['data'])
                except:
                    data = {}
        
        question_type = ''
        if data:
            question_type = data.get('type', '')

        quick_questions = {
            'attractions': '请推荐一些适合亲子游的国内景点，要求风景好、有教育意义。',
            'food': '请推荐一些必吃的中国特色美食，以及它们的最佳品尝地点。',
            'budget': '请给我推荐一个3天2晚的经济型旅行预算方案，目的地不限。',
            'season': '7月份去哪里旅游比较好？请推荐避暑胜地。',
            'transport': '国内旅游选择什么交通方式最划算？高铁和飞机各有什么优劣？',
            'tips': '旅行前有哪些必备物品？请列一个清单。'
        }

        user_message = quick_questions.get(question_type, '请介绍一下旅行的基本知识。')

        # 获取对话历史
        history = session.get('ai_chat_history', [])

        # 构建消息
        system_prompt = """你是一位专业、友好的AI旅行规划助手。请用亲切、专业的语气回答。"""

        messages = [{'role': 'system', 'content': system_prompt}]

        for msg in history[-10:]:
            messages.append({'role': msg['role'], 'content': msg['content']})

        messages.append({'role': 'user', 'content': user_message})

        # 调用AI服务
        ai_service = AIService()
        response = ai_service._call_ai_api(messages)

        if response:
            # 清理AI返回的内容，移除markdown格式符号
            import re
            # 移除代码块标记
            response = re.sub(r'```[\w]*', '', response)
            response = re.sub(r'```', '', response)
            # 移除行首的特殊符号
            response = re.sub(r'^[\s]*[-*+]\s+', '', response, flags=re.MULTILINE)
            response = re.sub(r'^[\s]*\d+\.\s+', '', response, flags=re.MULTILINE)
            response = re.sub(r'^[\s]*[#*]+', '', response, flags=re.MULTILINE)
            # 清理多余的空行
            response = re.sub(r'\n{3,}', '\n\n', response)
            response = response.strip()

            history.append({'role': 'user', 'content': user_message})
            history.append({'role': 'assistant', 'content': response})
            session['ai_chat_history'] = history[-20:]

            return jsonify({
                'success': True,
                'response': response,
                'user_message': user_message
            })
        else:
            return jsonify({
                'success': False,
                'message': 'AI服务暂时不可用'
            }), 503

    except Exception as e:
        current_app.logger.error(f'AI快捷问题错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'服务错误: {str(e)}'
        }), 500
