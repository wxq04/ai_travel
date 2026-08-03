from flask import render_template, abort, jsonify, request, session, url_for
from flask_login import login_required, current_user
from . import attractions_bp
from app.models.attraction import Attraction
from app.extensions import db, csrf


@attractions_bp.route('/<int:id>')
def detail(id):
    """景点详情页"""
    attraction = Attraction.query.get_or_404(id)
    attraction.increment_view_count()
    return render_template('attractions/detail.html', attraction=attraction)


@attractions_bp.route('/<int:id>/add_to_itinerary', methods=['POST'])
@login_required
@csrf.exempt
def add_to_itinerary(id):
    """将景点添加到行程"""
    try:
        attraction = Attraction.query.get_or_404(id)
        data = request.get_json() or {}

        # 获取用户选择的行程ID（如果有的话）
        itinerary_id = data.get('itinerary_id')
        day_number = data.get('day_number', 1)

        # 如果没有指定行程ID，保存到session供后续使用
        if not itinerary_id:
            # 保存到session
            cart_items = session.get('attraction_cart', [])
            cart_items.append({
                'attraction_id': attraction.id,
                'attraction_name': attraction.name,
                'destination_id': attraction.destination_id,
                'destination_name': attraction.destination.name if attraction.destination else '',
                'day_number': day_number
            })
            session['attraction_cart'] = cart_items

            return jsonify({
                'success': True,
                'message': f'已将"{attraction.name}"添加到行程清单',
                'redirect_url': url_for('itineraries.my_itineraries')
            })

        # 如果指定了行程ID，直接添加到行程
        from app.models.itinerary import Itinerary, ItineraryDay, DayActivity

        itinerary = Itinerary.query.get(itinerary_id)
        if not itinerary:
            return jsonify({'success': False, 'message': '行程不存在'}), 404

        if itinerary.user_id != current_user.id:
            return jsonify({'success': False, 'message': '无权限'}), 403

        # 查找或创建对应的天数
        day = ItineraryDay.query.filter_by(
            itinerary_id=itinerary_id,
            day_number=day_number
        ).first()

        if not day:
            day = ItineraryDay(
                itinerary_id=itinerary_id,
                day_number=day_number,
                theme=f"第{day_number}天"
            )
            db.session.add(day)
            db.session.commit()

        # 创建活动
        activity = DayActivity(
            day_id=day.id,
            order_index=1,
            activity_type='景点',
            name=attraction.name,
            description=attraction.description or '',
            location=attraction.address or '',
            duration_minutes=attraction.suggested_duration or 120,
            estimated_cost=0,
            tip='从景点库添加',
            latitude=attraction.latitude,
            longitude=attraction.longitude
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'已将"{attraction.name}"添加到行程'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@attractions_bp.route('/<int:id>/generate_details', methods=['POST'])
@csrf.exempt
def generate_details(id):
    """AI生成景点详细信息"""
    attraction = Attraction.query.get_or_404(id)

    try:
        from app.services.ai_service import AIService
        from app.services.geocoding_service import GeocodingService

        ai_service = AIService()
        geocoding = GeocodingService()

        # 获取目的地信息
        destination_name = ''
        destination_city = ''
        if attraction.destination:
            destination_name = attraction.destination.name
            destination_city = attraction.destination.city

        # 调用AI生成详情
        system_prompt = """你是一位专业的旅行攻略作家，精通中国各地景点的历史文化、特色玩法、美食推荐等。

请根据提供的信息，生成景点的详细攻略内容。

【输出格式】
返回JSON格式：
{
  "description": "景点详细介绍，100字以上，包含历史背景、建筑特色、文化内涵等",
  "play_tips": "游玩攻略建议，100字以上，包含最佳游览路线、拍摄点、注意事项等",
  "recommended_dishes": ["推荐美食1", "推荐美食2", "推荐美食3"],
  "nearby_attractions": ["附近景点1", "附近景点2", "附近景点3"],
  "practical_info": {
    "best_visit_time": "最佳游览时间建议",
    "ticket_info": "门票信息",
    "transportation": "交通指南",
    "accommodation": "住宿推荐"
  }
}"""

        user_prompt = f"""请为以下景点生成详细攻略：

景点名称：{attraction.name}
景点类别：{attraction.category or '景点'}
所在城市：{destination_city}
所在目的地：{destination_name}
已有描述：{attraction.description or '暂无'}

请生成详细的景点攻略内容。"""

        result = ai_service._call_ai_api([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ])

        if result:
            import json
            # 清理响应
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

            # 更新景点信息
            if data.get('description'):
                attraction.description = data['description']
            if data.get('play_tips'):
                attraction.play_tips = data['play_tips']
            if data.get('recommended_dishes'):
                attraction.recommended_dishes = json.dumps(data['recommended_dishes'], ensure_ascii=False)
            if data.get('nearby_attractions'):
                attraction.nearby_attractions = json.dumps(data['nearby_attractions'], ensure_ascii=False)

            # 获取地理坐标
            if attraction.latitude is None or attraction.longitude is None:
                coords = geocoding.geocode(attraction.name, destination_city)
                if coords:
                    attraction.latitude = coords.get('lat')
                    attraction.longitude = coords.get('lng')

            from app.extensions import db
            db.session.commit()

            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': False, 'message': 'AI服务暂时不可用'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@attractions_bp.route('/search')
def search():
    """搜索景点（本地数据库 + AI补充）"""
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    use_ai = request.args.get('ai', 'false').lower() == 'true'  # 是否强制使用AI搜索
    use_ai_for_empty = request.args.get('ai_fallback', 'true').lower() == 'true'  # 本地无结果时使用AI

    local_attractions = []
    ai_attractions = []
    is_ai_generated = False

    # 获取当前用户已保存的景点ID
    saved_attraction_ids = []
    if current_user.is_authenticated:
        from app.models.social import SavedAttraction
        saved = SavedAttraction.query.filter_by(user_id=current_user.id).all()
        saved_attraction_ids = [s.attraction_id for s in saved]

    # 1. 搜索本地数据库
    query = Attraction.query
    if keyword:
        query = query.filter(
            Attraction.name.contains(keyword) |
            Attraction.description.contains(keyword)
        )
    if category:
        query = query.filter_by(category=category)

    local_attractions = query.order_by(Attraction.view_count.desc()).all()

    # 2. 判断是否需要AI搜索
    need_ai_search = use_ai  # 用户主动要求AI
    need_ai_search = need_ai_search or (use_ai_for_empty and len(local_attractions) == 0 and keyword)  # 本地无结果

    if need_ai_search and keyword:
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()

            # 获取目的地信息（从URL参数或session中）
            destination_name = request.args.get('destination', '')
            if not destination_name:
                # 尝试从session获取当前目的地
                destination_name = session.get('current_destination', '')

            # 调用AI搜索景点
            ai_results = ai_service.search_attractions(
                keyword=keyword,
                destination=destination_name,
                category=category if category else ''
            )

            if ai_results:
                is_ai_generated = True
                # 将AI结果转换为Attraction对象格式（用于模板显示）
                ai_attractions = []
                for attr_data in ai_results:
                    # 创建临时对象用于模板显示（不存入数据库）
                    class AIGeneratedAttraction:
                        def __init__(self, data):
                            self.id = 0  # 特殊ID表示AI生成
                            self.name = data.get('name', '')
                            self.category = data.get('category', '景点')
                            self.description = data.get('description', '')
                            self.address = data.get('address', '')
                            self.ticket_price = data.get('ticket_price', '')
                            self.opening_hours = data.get('opening_hours', '')
                            self.best_season = data.get('best_season', '')
                            self.suggested_duration = data.get('suggested_duration', 120)
                            self.play_tips = data.get('play_tips', '')
                            self.recommended_dishes = data.get('recommended_dishes', [])
                            self.is_ai_generated = True
                            self._ai_data = data

                    ai_attractions.append(AIGeneratedAttraction(attr_data))

        except Exception as e:
            import logging
            logging.error(f'AI景点搜索失败: {str(e)}')

    return render_template(
        'attractions/search.html',
        attractions=local_attractions,
        ai_attractions=ai_attractions,
        keyword=keyword,
        category=category,
        is_ai_generated=is_ai_generated,
        saved_attraction_ids=saved_attraction_ids
    )


@attractions_bp.route('/search/api')
def search_api():
    """景点搜索API（返回JSON，支持AI补充）"""
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    destination_id = request.args.get('destination_id', '')
    use_ai_fallback = request.args.get('ai_fallback', 'true').lower() == 'true'

    results = []

    # 1. 搜索本地数据库
    query = Attraction.query
    if keyword:
        query = query.filter(
            Attraction.name.contains(keyword) |
            Attraction.description.contains(keyword)
        )
    if category:
        query = query.filter_by(category=category)
    if destination_id:
        query = query.filter_by(destination_id=int(destination_id))

    local_attractions = query.order_by(Attraction.view_count.desc()).limit(20).all()

    for attr in local_attractions:
        results.append({
            'id': attr.id,
            'name': attr.name,
            'category': attr.category,
            'description': attr.description[:100] if attr.description else '',
            'address': attr.address or '',
            'ticket_price': attr.ticket_price or '',
            'is_local': True,
            'is_ai_generated': False
        })

    # 2. 如果本地结果少，使用AI补充
    need_ai = use_ai_fallback and len(results) < 5 and keyword

    if need_ai:
        try:
            from app.services.ai_service import AIService
            from app.models.destination import Destination

            ai_service = AIService()

            # 获取目的地名称
            destination_name = ''
            if destination_id:
                dest = Destination.query.get(int(destination_id))
                if dest:
                    destination_name = dest.name

            # 调用AI搜索
            ai_results = ai_service.search_attractions(
                keyword=keyword,
                destination=destination_name,
                category=category
            )

            if ai_results:
                for attr_data in ai_results:
                    # 检查是否已在本地结果中
                    if not any(r['name'] == attr_data['name'] for r in results):
                        results.append({
                            'name': attr_data.get('name', ''),
                            'category': attr_data.get('category', '景点'),
                            'description': attr_data.get('description', '')[:100],
                            'address': attr_data.get('address', ''),
                            'ticket_price': attr_data.get('ticket_price', ''),
                            'is_local': False,
                            'is_ai_generated': True,
                            '_ai_data': attr_data
                        })

        except Exception as e:
            import logging
            logging.error(f'AI景点搜索失败: {str(e)}')

    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })


@attractions_bp.route('/ai/add', methods=['POST'])
@login_required
@csrf.exempt
def add_ai_attraction():
    """将AI搜索到的景点添加到本地数据库"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        data = request.get_json()
        logger.info(f"添加AI景点请求: {data}")
        if not data:
            return jsonify({'success': False, 'message': '无效的数据'}), 400

        # 检查是否已存在
        existing = Attraction.query.filter(
            Attraction.name == data.get('name')
        ).first()

        if existing:
            logger.info(f"景点已存在: ID={existing.id}")
            return jsonify({
                'success': True,
                'message': '景点已存在',
                'attraction_id': existing.id
            })

        # 获取目的地ID
        destination_id = data.get('destination_id')
        if not destination_id:
            # 尝试根据目的地名称查找
            dest_name = data.get('destination_name', '')
            if dest_name:
                from app.models.destination import Destination
                dest = Destination.query.filter(
                    Destination.name.contains(dest_name) |
                    Destination.city.contains(dest_name)
                ).first()
                if dest:
                    destination_id = dest.id

        # 创建景点记录
        attraction = Attraction(
            name=data.get('name', ''),
            destination_id=destination_id,
            category=data.get('category', '景点'),
            description=data.get('description', ''),
            address=data.get('address', ''),
            ticket_price=data.get('ticket_price', ''),
            opening_hours=data.get('opening_hours', ''),
            best_season=data.get('best_season', ''),
            suggested_duration=data.get('suggested_duration', 120),
            play_tips=data.get('play_tips', '')
        )

        if data.get('recommended_dishes'):
            import json
            attraction.recommended_dishes = json.dumps(data['recommended_dishes'], ensure_ascii=False)

        db.session.add(attraction)
        db.session.commit()

        # 获取地理坐标
        if not attraction.latitude or not attraction.longitude:
            try:
                from app.services.geocoding_service import GeocodingService
                geocoding = GeocodingService()
                coords = geocoding.geocode(attraction.name, data.get('destination_name', ''))
                if coords:
                    attraction.latitude = coords.get('lat')
                    attraction.longitude = coords.get('lng')
                    db.session.commit()
            except:
                pass

        return jsonify({
            'success': True,
            'message': '景点已添加到数据库',
            'attraction_id': attraction.id
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@attractions_bp.route('/by-destination/<int:destination_id>')
def by_destination(destination_id):
    """按目的地获取景点"""
    from app.models.destination import Destination

    destination = Destination.query.get_or_404(destination_id)
    attractions = Attraction.query.filter_by(destination_id=destination_id).order_by(Attraction.rating.desc()).all()

    return render_template('attractions/by_destination.html', attractions=attractions, destination=destination)


@attractions_bp.route('/<int:id>/save', methods=['POST'])
@login_required
@csrf.exempt
def save_attraction(id):
    """保存景点到我的收藏"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"收藏景点请求: attraction_id={id}, user_id={current_user.id}")
        attraction = Attraction.query.get_or_404(id)
        logger.info(f"找到景点: {attraction.name}")

        # 检查是否已保存
        from app.models.social import SavedAttraction
        existing = SavedAttraction.query.filter_by(
            user_id=current_user.id,
            attraction_id=id
        ).first()

        if existing:
            # 取消保存
            db.session.delete(existing)
            db.session.commit()
            logger.info(f"已取消收藏")
            return jsonify({
                'success': True,
                'saved': False,
                'message': '已取消收藏'
            })

        # 添加收藏
        saved = SavedAttraction(
            user_id=current_user.id,
            attraction_id=id
        )
        db.session.add(saved)
        db.session.commit()
        logger.info(f"收藏成功")

        return jsonify({
            'success': True,
            'saved': True,
            'message': '景点已收藏'
        })

    except Exception as e:
        logger.error(f"收藏失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@attractions_bp.route('/my-saved')
@login_required
def my_saved_attractions():
    """我的收藏景点列表"""
    from app.models.social import SavedAttraction

    saved = SavedAttraction.query.filter_by(
        user_id=current_user.id
    ).order_by(SavedAttraction.created_at.desc()).all()

    return render_template('attractions/my_saved.html', saved_attractions=saved)


@attractions_bp.route('/<int:id>/unsave', methods=['POST'])
@login_required
@csrf.exempt
def unsave_attraction(id):
    """取消收藏景点"""
    try:
        from app.models.social import SavedAttraction

        saved = SavedAttraction.query.filter_by(
            user_id=current_user.id,
            attraction_id=id
        ).first()

        if saved:
            db.session.delete(saved)
            db.session.commit()
            return jsonify({'success': True, 'message': '已取消收藏'})
        else:
            return jsonify({'success': False, 'message': '未找到收藏记录'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
