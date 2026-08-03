from flask import request, jsonify, Response, session, current_app
from flask_login import login_required, current_user
from app.blueprints.ai import ai_bp
from app.extensions import db, redis_client
from app.models.destination import Destination
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.social import Tag
import json
from datetime import datetime


@ai_bp.route('/generate_itinerary', methods=['POST'])
@login_required
def generate_itinerary():
    """行程生成（SSE 流式输出，Redis 缓存 TTL 1小时）"""
    data = request.get_json()

    destination_id = data.get('destination_id')
    days_count = data.get('days_count', 3)
    budget_level = data.get('budget_level', '舒适')
    interest_tags = data.get('interest_tags', [])
    additional_notes = data.get('additional_notes', '')

    # 验证数据
    if not destination_id:
        return jsonify({'error': '请选择目的地'}), 400

    destination = Destination.query.get_or_404(destination_id)

    # 使用 SSE 流式返回
    def generate():
        try:
            yield f"data: {json.dumps({'status': 'starting', 'message': '正在分析您的需求...'})}\n\n"

            # 检查 Redis 缓存
            cache_key = f"itinerary:{destination_id}:{days_count}:{budget_level}:{','.join(interest_tags)}"
            if redis_client:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    yield f"data: {json.dumps({'status': 'cached', 'message': '从缓存加载行程...'})}\n\n"
                    cached_data = json.loads(cached_result)
                    yield f"data: {json.dumps({'status': 'completed', 'data': cached_data})}\n\n"
                    return

            yield f"data: {json.dumps({'status': 'progress', 'message': '正在生成行程框架...'})}\n\n"

            # 模拟 AI 生成（实际应调用 AI 服务）
            # 创建行程
            itinerary = Itinerary(
                user_id=current_user.id,
                title=f"{destination.name} {days_count}日游",
                destination_id=destination_id,
                days_count=days_count,
                budget_level=budget_level,
                is_public=False,
                ai_generated=True
            )

            if interest_tags:
                itinerary.set_interest_tags(interest_tags)

            db.session.add(itinerary)
            db.session.commit()

            yield f"data: {json.dumps({'status': 'progress', 'message': '行程框架创建完成，正在生成详细活动...'})}\n\n"

            # 生成行程天数和活动
            itinerary_data = {
                'id': itinerary.id,
                'title': itinerary.title,
                'days': []
            }

            for day_num in range(1, days_count + 1):
                day = ItineraryDay(
                    itinerary_id=itinerary.id,
                    day_number=day_num,
                    theme=f"第{day_num}天：探索{destination.name}"
                )
                db.session.add(day)
                db.session.commit()

                day_data = {
                    'day_number': day_num,
                    'theme': day.theme,
                    'activities': []
                }

                # 添加示例活动（实际应由 AI 生成）
                activities = [
                    {
                        'order_index': 1,
                        'activity_type': '景点',
                        'name': f"{destination.name}著名景点",
                        'description': f"探索{destination.name}的标志性景点",
                        'location': destination.city,
                        'duration_minutes': 120,
                        'estimated_cost': 100 if budget_level == '经济' else 200 if budget_level == '舒适' else 500
                    },
                    {
                        'order_index': 2,
                        'activity_type': '餐厅',
                        'name': '当地特色餐厅',
                        'description': '品尝当地美食',
                        'location': destination.city,
                        'duration_minutes': 60,
                        'estimated_cost': 50 if budget_level == '经济' else 100 if budget_level == '舒适' else 300
                    }
                ]

                for act_data in activities:
                    activity = DayActivity(
                        day_id=day.id,
                        **act_data
                    )
                    db.session.add(activity)
                    db.session.commit()

                    day_data['activities'].append({
                        'id': activity.id,
                        'name': activity.name,
                        'type': activity.activity_type,
                        'description': activity.description,
                        'duration': activity.duration_minutes,
                        'cost': activity.estimated_cost
                    })

                itinerary_data['days'].append(day_data)

            # 缓存结果到 Redis（TTL 1小时）
            if redis_client:
                redis_client.setex(cache_key, 3600, json.dumps(itinerary_data))

            yield f"data: {json.dumps({'status': 'completed', 'message': '行程生成完成', 'itinerary_id': itinerary.id, 'data': itinerary_data})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@ai_bp.route('/chat_adjust', methods=['POST'])
@login_required
def chat_adjust():
    """多轮对话调整行程（维护 session 中的对话历史）"""
    data = request.get_json()

    itinerary_id = data.get('itinerary_id')
    message = data.get('message')

    if not itinerary_id or not message:
        return jsonify({'error': '缺少必要参数'}), 400

    itinerary = Itinerary.query.get_or_404(itinerary_id)

    # 维护对话历史
    chat_history_key = f"chat_history:{current_user.id}:{itinerary_id}"
    if 'chat_history' not in session:
        session['chat_history'] = {}

    if chat_history_key not in session['chat_history']:
        session['chat_history'][chat_history_key] = []

    # 添加用户消息到历史
    session['chat_history'][chat_history_key].append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.utcnow().isoformat()
    })

    # 模拟 AI 响应（实际应调用 AI 服务）
    ai_response = f"收到您的请求：'{message}'。正在调整行程..."

    # 添加 AI 响应到历史
    session['chat_history'][chat_history_key].append({
        'role': 'assistant',
        'content': ai_response,
        'timestamp': datetime.utcnow().isoformat()
    })

    # 标记 session 已修改
    session.modified = True

    return jsonify({
        'success': True,
        'response': ai_response,
        'history_length': len(session['chat_history'][chat_history_key])
    })


@ai_bp.route('/recommend', methods=['GET'])
@login_required
def recommend():
    """景点猜你喜欢（基于用户标签和历史行为）"""
    # 获取用户偏好标签
    user_tags = current_user.get_preference_tags()

    # 获取用户历史浏览的目的地
    from app.models.itinerary import Itinerary
    user_itineraries = Itinerary.query.filter_by(user_id=current_user.id).limit(10).all()
    visited_destination_ids = [i.destination_id for i in user_itineraries]

    # 推荐逻辑
    recommendations = []

    # 基于用户标签推荐
    if user_tags:
        for tag in user_tags:
            # 查找匹配标签的目的地
            matching_destinations = Destination.query.filter(
                Destination.category.contains(tag),
                Destination.id.notin_(visited_destination_ids)
            ).limit(3).all()

            for dest in matching_destinations:
                recommendations.append({
                    'id': dest.id,
                    'name': dest.name,
                    'city': dest.city,
                    'category': dest.category,
                    'match_reason': f'匹配您的"{tag}"兴趣',
                    'avg_rating': dest.avg_rating
                })

    # 如果没有足够推荐，补充热门目的地
    if len(recommendations) < 5:
        hot_destinations = Destination.query.filter(
            Destination.id.notin_(visited_destination_ids)
        ).order_by(Destination.view_count.desc()).limit(5 - len(recommendations)).all()

        for dest in hot_destinations:
            recommendations.append({
                'id': dest.id,
                'name': dest.name,
                'city': dest.city,
                'category': dest.category,
                'match_reason': '热门目的地',
                'avg_rating': dest.avg_rating
            })

    return jsonify({
        'success': True,
        'recommendations': recommendations[:10],
        'user_tags': user_tags
    })


@ai_bp.route('/clear_chat_history', methods=['POST'])
@login_required
def clear_chat_history():
    """清除对话历史"""
    itinerary_id = request.form.get('itinerary_id', type=int)

    if itinerary_id:
        chat_history_key = f"chat_history:{current_user.id}:{itinerary_id}"
        if 'chat_history' in session and chat_history_key in session['chat_history']:
            del session['chat_history'][chat_history_key]
            session.modified = True
    else:
        # 清除所有对话历史
        session['chat_history'] = {}
        session.modified = True

    return jsonify({'success': True, 'message': '对话历史已清除'})