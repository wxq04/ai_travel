from flask import render_template, redirect, url_for, flash, request, jsonify, session, Response, current_app, stream_with_context
from flask_login import login_required, current_user
from app.blueprints.itineraries import itineraries_bp
from app.extensions import db, csrf
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.destination import Destination
from app.blueprints.itineraries.forms import ItineraryStep1Form, ItineraryStep2Form, ItineraryEditForm, DayActivityForm
import json
from datetime import datetime


@itineraries_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建行程向导 Step1（选目的地、天数、预算）"""
    form = ItineraryStep1Form()

    if form.validate_on_submit():
        destination_id = form.destination_id.data
        custom_city = form.custom_city.data.strip() if form.use_custom_city.data and form.custom_city.data else None

        # 如果使用自定义城市，先创建目的地记录
        if custom_city:
            # 检查是否已存在
            existing = Destination.query.filter_by(name=custom_city).first()
            if existing:
                destination_id = existing.id
            else:
                # 创建新目的地
                from app.services.geocoding_service import GeocodingService
                geocoding = GeocodingService()
                coords = geocoding._fallback_coordinates(custom_city)

                new_dest = Destination(
                    name=custom_city,
                    country='中国',
                    city=custom_city,
                    category='都市',
                    description=f'用户自定义目的地：{custom_city}',
                    latitude=coords.get('lat'),
                    longitude=coords.get('lng')
                )
                db.session.add(new_dest)
                db.session.commit()
                destination_id = new_dest.id

        # 保存第一步数据到 session
        session['itinerary_step1'] = {
            'destination_id': destination_id,
            'days_count': form.days_count.data,
            'budget_level': form.budget_level.data
        }
        return redirect(url_for('itineraries.create_step2'))

    return render_template('itineraries/create.html', form=form, step=1)


@itineraries_bp.route('/create/step2', methods=['GET', 'POST'])
@login_required
def create_step2():
    """创建行程向导 Step2（选兴趣标签 + 补充说明）"""
    # 检查第一步数据是否存在
    if 'itinerary_step1' not in session:
        flash('请先完成第一步', 'error')
        return redirect(url_for('itineraries.create'))

    form = ItineraryStep2Form()

    if form.validate_on_submit():
        # 保存第二步数据到 session
        session['itinerary_step2'] = {
            'title': form.title.data,
            'interest_tags': form.interest_tags.data,
            'additional_notes': form.additional_notes.data,
            'is_public': form.is_public.data
        }
        return redirect(url_for('itineraries.create_generate'))

    return render_template('itineraries/create.html', form=form, step=2)


@itineraries_bp.route('/create/generate', methods=['GET', 'POST'])
@login_required
def create_generate():
    """创建行程向导 Step3（触发 AI 生成，SSE 流式返回）"""
    # 检查前两步数据是否存在
    if 'itinerary_step1' not in session or 'itinerary_step2' not in session:
        flash('请先完成前两步', 'error')
        return redirect(url_for('itineraries.create'))

    step1_data = session['itinerary_step1']
    step2_data = session['itinerary_step2']

    # 如果是 POST 请求，触发 AI 生成
    if request.method == 'POST':
        # 直接生成行程（避免 SSE 生成器中 yield 后丢失应用上下文）
        try:
            # 获取目的地信息
            destination = Destination.query.get(step1_data['destination_id'])

            # 导入AI服务
            from app.services.ai_service import AIService
            from app.services.geocoding_service import GeocodingService
            ai_service = AIService()
            geocoding = GeocodingService()

            # 准备兴趣标签
            interest_tags = []
            if step2_data['interest_tags']:
                interest_tags = [tag.strip() for tag in step2_data['interest_tags'].split(',')]

            # 调用AI生成真实行程
            itinerary_data = ai_service.generate_itinerary(
                destination=destination.name,
                days=step1_data['days_count'],
                budget=step1_data['budget_level'],
                tags=interest_tags,
                extra_info=step2_data.get('additional_notes', '') + f"\n目的地城市: {destination.city}, 国家: {destination.country}"
            )

            # 创建行程记录
            itinerary = Itinerary(
                user_id=current_user.id,
                title=step2_data['title'],
                destination_id=step1_data['destination_id'],
                days_count=step1_data['days_count'],
                budget_level=step1_data['budget_level'],
                is_public=step2_data['is_public'],
                ai_generated=True
            )

            if step2_data['interest_tags']:
                tags_list = [tag.strip() for tag in step2_data['interest_tags'].split(',')]
                itinerary.set_interest_tags(tags_list)

            db.session.add(itinerary)
            db.session.commit()

            # 根据预算设置费用系数
            budget_multiplier = 1.0
            if step1_data['budget_level'] == '豪华':
                budget_multiplier = 2.0
            elif step1_data['budget_level'] == '经济':
                budget_multiplier = 0.5

            # 解析AI返回的行程数据并创建数据库记录
            days_data = itinerary_data.get('days', [])

            if not days_data:
                # 如果AI返回空数据，使用默认结构
                days_data = _generate_default_days_data(destination.name, destination.city, step1_data['days_count'])

            for day_data in days_data:
                day = ItineraryDay(
                    itinerary_id=itinerary.id,
                    day_number=day_data.get('day', 1),
                    theme=day_data.get('theme', f"第{day_data.get('day', 1)}天")
                )
                db.session.add(day)
                db.session.flush()

                # 创建当天活动
                activities = day_data.get('activities', [])
                for idx, act in enumerate(activities):
                    # 获取活动地点的地理坐标（传入城市名辅助定位）
                    activity_location = act.get('location', destination.city)
                    city_name = destination.city or destination.name
                    coords = geocoding.geocode(activity_location, city_name)

                    activity = DayActivity(
                        day_id=day.id,
                        order_index=idx + 1,
                        activity_type=act.get('type', '景点'),
                        name=act.get('name', '未知活动'),
                        description=act.get('description', ''),
                        location=activity_location,
                        duration_minutes=int(act.get('duration', 120)),
                        estimated_cost=int(act.get('cost', 0) * budget_multiplier),
                        tip=act.get('tip', ''),
                        latitude=coords.get('lat') if coords else None,
                        longitude=coords.get('lng') if coords else None
                    )
                    db.session.add(activity)

                # 自动添加住宿（每天晚上）
                hotel_cost = _get_hotel_cost(step1_data['budget_level'])
                accommodation = DayActivity(
                    day_id=day.id,
                    order_index=99,
                    activity_type='住宿',
                    name='推荐酒店（待确认）',
                    description='建议提前在携程、Booking或Airbnb预订。',
                    duration_minutes=1440,
                    estimated_cost=hotel_cost,
                    tip='建议选择交通便利的位置，方便第二天的行程。',
                    latitude=destination.latitude,
                    longitude=destination.longitude
                )
                db.session.add(accommodation)

            db.session.commit()

            # 清理session中的步骤数据
            session.pop('itinerary_step1', None)
            session.pop('itinerary_step2', None)
            session.modified = True

            return jsonify({
                'success': True,
                'itinerary_id': itinerary.id,
                'redirect_url': url_for('itineraries.detail', id=itinerary.id)
            })

        except Exception as e:
            import traceback
            import logging
            logging.error(f'AI生成行程失败: {str(e)}\n{traceback.format_exc()}')
            return jsonify({
                'success': False,
                'message': f'生成失败: {str(e)}'
            }), 500

    # GET 请求显示生成页面
    destination = Destination.query.get(step1_data['destination_id'])
    return render_template('itineraries/create.html',
                           step=3,
                           step1_data=step1_data,
                           step2_data=step2_data,
                           destination=destination)


def _generate_default_days_data(destination_name, city, days_count):
    """生成默认天数数据（当AI返回空时）"""
    days = []
    for i in range(1, days_count + 1):
        days.append({
            'day': i,
            'theme': f'第{i}天：探索{destination_name}',
            'activities': [
                {
                    'type': '景点',
                    'name': f'{destination_name}著名景点',
                    'description': f'探索{destination_name}的标志性景点，建议提前查看开放时间和门票信息。',
                    'location': city,
                    'duration': 120,
                    'cost': 100,
                    'tip': '建议提前预约门票，避开节假日高峰期'
                },
                {
                    'type': '美食',
                    'name': '当地特色美食',
                    'description': f'品尝{city}特色美食，体验当地饮食文化。',
                    'location': city,
                    'duration': 90,
                    'cost': 80,
                    'tip': '推荐尝试当地人常去的餐厅，避免网红店的坑'
                }
            ]
        })
    return days


def _get_hotel_cost(budget_level):
    """根据预算等级返回酒店费用（每晚）"""
    hotel_costs = {
        '经济': 150,
        '舒适': 400,
        '豪华': 1000
    }
    return hotel_costs.get(budget_level, 400)


@itineraries_bp.route('/<int:id>')
def detail(id):
    """行程详情（时间轴展示 + 费用饼图 + 地图）"""
    try:
        itinerary = Itinerary.query.get_or_404(id)
        itinerary.increment_view_count()

        # 获取所有天数和活动
        days = itinerary.days.order_by('day_number').all()

        # 计算费用分类
        cost_breakdown = {
            'attractions': 0,
            'food': 0,
            'accommodation': 0,
            'transport': 0,
            'shopping': 0,
            'total': 0
        }

        for day in days:
            for activity in day.activities:
                if activity.estimated_cost:
                    cost_breakdown['total'] += activity.estimated_cost
                    if activity.activity_type == '景点':
                        cost_breakdown['attractions'] += activity.estimated_cost
                    elif activity.activity_type == '美食':
                        cost_breakdown['food'] += activity.estimated_cost
                    elif activity.activity_type == '住宿':
                        cost_breakdown['accommodation'] += activity.estimated_cost
                    elif activity.activity_type == '交通':
                        cost_breakdown['transport'] += activity.estimated_cost
                    elif activity.activity_type == '购物':
                        cost_breakdown['shopping'] += activity.estimated_cost

        # 获取评论（如果有评论模型）
        try:
            from app.models.social import Comment
            comments = Comment.query.filter_by(itinerary_id=id).order_by(Comment.created_at.desc()).all()
        except:
            comments = []

        # 获取相关推荐
        related_itineraries = Itinerary.query.filter(
            Itinerary.destination_id == itinerary.destination_id,
            Itinerary.id != id,
            Itinerary.is_public == True
        ).order_by(Itinerary.like_count.desc()).limit(5).all()

        return render_template('itineraries/detail.html',
                               itinerary=itinerary,
                               days=days,
                               cost_breakdown=cost_breakdown,
                               comments=comments,
                               related_itineraries=related_itineraries)
    except Exception as e:
        import traceback
        error_info = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_info)
        return f"服务器内部错误: {str(e)}", 500


@itineraries_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """行程编辑器（手动调整活动）"""
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        flash('您没有权限编辑此行程', 'error')
        return redirect(url_for('itineraries.detail', id=id))

    form = ItineraryEditForm(obj=itinerary)

    if form.validate_on_submit():
        itinerary.title = form.title.data
        itinerary.days_count = form.days_count.data
        itinerary.budget_level = form.budget_level.data
        itinerary.is_public = form.is_public.data

        if form.interest_tags.data:
            tags_list = [tag.strip() for tag in form.interest_tags.data.split(',')]
            itinerary.set_interest_tags(tags_list)

        db.session.commit()
        flash('行程更新成功', 'success')
        return redirect(url_for('itineraries.detail', id=id))

    return render_template('itineraries/edit.html', itinerary=itinerary, form=form)


@itineraries_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete(id):
    """删除行程"""
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        flash('您没有权限删除此行程', 'error')
        return redirect(url_for('itineraries.detail', id=id))

    db.session.delete(itinerary)
    db.session.commit()
    flash('行程已删除', 'success')
    return redirect(url_for('itineraries.my_itineraries'))


@itineraries_bp.route('/<int:id>/toggle_public', methods=['POST'])
@login_required
def toggle_public(id):
    """切换公开/私有"""
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        return jsonify({'error': '无权限'}), 403

    itinerary.is_public = not itinerary.is_public
    db.session.commit()

    status = '公开' if itinerary.is_public else '私有'
    return jsonify({'success': True, 'status': status})


@itineraries_bp.route('/<int:id>/clone', methods=['POST'])
@login_required
@csrf.exempt
def clone(id):
    """复制他人行程（二次创作）"""
    original = Itinerary.query.get_or_404(id)

    if not original.is_public:
        return jsonify({'success': False, 'message': '该行程不公开，无法复制'})

    # 创建新行程
    new_itinerary = Itinerary(
        user_id=current_user.id,
        title=f"{original.title}（副本）",
        destination_id=original.destination_id,
        days_count=original.days_count,
        budget_level=original.budget_level,
        is_public=False,
        ai_generated=False
    )

    if original.interest_tags:
        new_itinerary.set_interest_tags(original.get_interest_tags())

    db.session.add(new_itinerary)
    db.session.commit()

    # 复制所有天数和活动
    for day in original.days.all():
        new_day = ItineraryDay(
            itinerary_id=new_itinerary.id,
            day_number=day.day_number,
            date=day.date,
            theme=day.theme,
            notes=day.notes
        )
        db.session.add(new_day)
        db.session.commit()

        # 复制活动
        for activity in day.activities.all():
            new_activity = DayActivity(
                day_id=new_day.id,
                order_index=activity.order_index,
                activity_type=activity.activity_type,
                name=activity.name,
                description=activity.description,
                location=activity.location,
                duration_minutes=activity.duration_minutes,
                estimated_cost=activity.estimated_cost,
                tip=activity.tip,
                image_url=activity.image_url
            )
            db.session.add(new_activity)

    db.session.commit()
    return jsonify({
        'success': True, 
        'message': '行程已复制到您的账户',
        'redirect_url': url_for('itineraries.detail', id=new_itinerary.id)
    })


@itineraries_bp.route('/<int:id>/export_pdf')
@login_required
def export_pdf(id):
    """导出 PDF"""
    itinerary = Itinerary.query.get_or_404(id)

    # TODO: 实现 PDF 导出功能
    flash('PDF 导出功能开发中', 'info')
    return redirect(url_for('itineraries.detail', id=id))


@itineraries_bp.route('/<int:id>/toggle_like', methods=['POST'])
@login_required
@csrf.exempt
def toggle_like(id):
    """切换点赞"""
    itinerary = Itinerary.query.get_or_404(id)
    
    try:
        from app.models.like import Like
        existing_like = Like.query.filter_by(user_id=current_user.id, itinerary_id=id).first()
        
        if existing_like:
            db.session.delete(existing_like)
            itinerary.decrement_like_count()
            liked = False
        else:
            like = Like(user_id=current_user.id, itinerary_id=id)
            db.session.add(like)
            itinerary.increment_like_count()
            liked = True
        
        db.session.commit()
        return jsonify({'success': True, 'liked': liked, 'like_count': itinerary.like_count})
    except:
        # 如果没有 Like 模型，直接操作
        return jsonify({'success': True, 'liked': False, 'like_count': itinerary.like_count})


@itineraries_bp.route('/<int:id>/toggle_favorite', methods=['POST'])
@login_required
@csrf.exempt
def toggle_favorite(id):
    """切换收藏"""
    itinerary = Itinerary.query.get_or_404(id)
    
    try:
        from app.models.favorite import Favorite
        existing_fav = Favorite.query.filter_by(user_id=current_user.id, itinerary_id=id).first()
        
        if existing_fav:
            db.session.delete(existing_fav)
            favorited = False
        else:
            fav = Favorite(user_id=current_user.id, itinerary_id=id)
            db.session.add(fav)
            favorited = True
        
        db.session.commit()
        return jsonify({'success': True, 'favorited': favorited})
    except:
        return jsonify({'success': True, 'favorited': False})


@itineraries_bp.route('/<int:id>/add_comment', methods=['POST'])
@login_required
@csrf.exempt
def add_comment(id):
    """添加评论"""
    itinerary = Itinerary.query.get_or_404(id)

    # 支持表单提交和 JSON 提交
    if request.is_json:
        data = request.get_json(silent=True) or {}
        content = data.get('content', '')
        parent_id = data.get('parent_id')
    else:
        # 表单提交
        content = request.form.get('content', '')
        parent_id = request.form.get('parent_id')

        if not content:
            flash('评论内容不能为空', 'warning')
            return redirect(url_for('itineraries.detail', id=id))

    if not content:
        if request.is_json:
            return jsonify({'success': False, 'message': '评论内容不能为空'}), 400
        flash('评论内容不能为空', 'warning')
        return redirect(url_for('itineraries.detail', id=id))

    try:
        from app.models.social import Comment
        comment = Comment(
            user_id=current_user.id,
            itinerary_id=id,
            content=content,
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'comment_id': comment.id})
        flash('评论发表成功！', 'success')
        return redirect(url_for('itineraries.detail', id=id))
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'评论失败: {str(e)}', 'danger')
        return redirect(url_for('itineraries.detail', id=id))


@itineraries_bp.route('/my')
@login_required
def my_itineraries():
    """我的行程列表"""
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).order_by(
        Itinerary.created_at.desc()
    ).all()

    return render_template('itineraries/my.html', itineraries=itineraries)


@itineraries_bp.route('/save', methods=['POST'])
def save():
    """保存行程（AJAX方式）"""
    import json
    from flask import request
    
    try:
        # 检查登录状态
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取JSON数据
        data = request.get_json()
        
        # 调试信息
        if data is None:
            content_type = request.headers.get('Content-Type', '')
            form_keys = list(request.form.keys()) if request.form else []
            return jsonify({
                'success': False, 
                'message': f'无法解析JSON数据。Content-Type: {content_type}, 表单字段: {form_keys}'
            }), 400
        
        itinerary_id = request.args.get('id') or request.form.get('id')
        
        if not itinerary_id:
            return jsonify({'success': False, 'message': '需要行程ID'}), 400
        
        # 更新现有行程
        itinerary = Itinerary.query.get(itinerary_id)
        if not itinerary:
            return jsonify({'success': False, 'message': '行程不存在'}), 404
            
        if itinerary.user_id != current_user.id:
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        # 更新标题
        if 'title' in data:
            itinerary.title = data['title']
        
        # 更新天数和活动
        if 'days' in data:
            from app.models.itinerary import ItineraryDay, DayActivity
            
            for day_data in data['days']:
                day_id = day_data.get('id')
                
                if day_id and not day_id.startswith('new_'):
                    # 更新现有天数
                    day = ItineraryDay.query.get(day_id)
                    if day and day.itinerary.user_id == current_user.id:
                        if 'theme' in day_data:
                            day.theme = day_data['theme']
                        
                        # 更新活动
                        if 'activities' in day_data:
                            for activity_data in day_data['activities']:
                                activity_id = activity_data.get('id')
                                if activity_id and not activity_id.startswith('new_'):
                                    activity = DayActivity.query.get(activity_id)
                                    if activity and activity.day.itinerary.user_id == current_user.id:
                                        if 'type' in activity_data:
                                            activity.activity_type = activity_data['type']
                                        if 'name' in activity_data:
                                            activity.name = activity_data['name']
                                        if 'duration' in activity_data:
                                            activity.duration_minutes = int(activity_data['duration']) if activity_data['duration'] else 0
                                        if 'cost' in activity_data:
                                            activity.estimated_cost = float(activity_data['cost']) if activity_data['cost'] else 0
                                        if 'tips' in activity_data:
                                            activity.tip = activity_data['tips']
    
        db.session.commit()
        return jsonify({'success': True, 'message': '保存成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@itineraries_bp.route('/share', methods=['POST'])
def share():
    """分享行程（设为公开）"""
    from flask import request, jsonify
    from flask_login import current_user as flask_login_user
    
    try:
        # 使用 flask_login_user 避免触发重定向
        user_is_authenticated = False
        try:
            user_is_authenticated = flask_login_user.is_authenticated
        except Exception:
            pass
        
        if not user_is_authenticated:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 优先从URL参数获取行程ID（前端是通过URL参数传递的）
        itinerary_id = request.args.get('id')
        
        # 如果URL参数没有，再尝试从JSON数据获取
        if not itinerary_id:
            data = request.get_json()
            if data:
                itinerary_id = data.get('id')
        
        if not itinerary_id:
            return jsonify({'success': False, 'message': '需要行程ID'}), 400
        
        itinerary = Itinerary.query.get(itinerary_id)
        
        if not itinerary:
            return jsonify({'success': False, 'message': '行程不存在'}), 404
        
        # 再次检查用户
        try:
            current_user_id = flask_login_user.id
        except Exception:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        if itinerary.user_id != current_user_id:
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        itinerary.is_public = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': '行程已公开分享'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@itineraries_bp.route('/<int:itinerary_id>/day/<int:day_id>/activity/add', methods=['POST'])
@login_required
def add_activity(itinerary_id, day_id):
    """添加活动"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'error': '无权限'}), 403

    form = DayActivityForm()

    if form.validate_on_submit():
        activity = DayActivity(
            day_id=day_id,
            order_index=form.order_index.data,
            activity_type=form.activity_type.data,
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            duration_minutes=form.duration_minutes.data,
            estimated_cost=form.estimated_cost.data,
            tip=form.tip.data
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'success': True, 'activity_id': activity.id})

    return jsonify({'error': '表单验证失败'}), 400


@itineraries_bp.route('/<int:itinerary_id>/activity/<int:activity_id>/edit', methods=['POST'])
@login_required
def edit_activity(itinerary_id, activity_id):
    """编辑活动"""
    activity = DayActivity.query.get_or_404(activity_id)
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'error': '无权限'}), 403

    form = DayActivityForm()

    if form.validate_on_submit():
        activity.activity_type = form.activity_type.data
        activity.name = form.name.data
        activity.description = form.description.data
        activity.location = form.location.data
        activity.duration_minutes = form.duration_minutes.data
        activity.estimated_cost = form.estimated_cost.data
        activity.tip = form.tip.data
        activity.order_index = form.order_index.data

        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'error': '表单验证失败'}), 400


@itineraries_bp.route('/<int:itinerary_id>/activity/<int:activity_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_activity(itinerary_id, activity_id):
    """删除活动"""
    activity = DayActivity.query.get_or_404(activity_id)
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if itinerary.user_id != current_user.id:
        return jsonify({'error': '无权限'}), 403

    db.session.delete(activity)
    db.session.commit()

    return jsonify({'success': True})


@itineraries_bp.route('/<int:id>/ai_adjust', methods=['POST'])
@login_required
@csrf.exempt
def ai_adjust(id):
    """AI多轮对话调整行程"""
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限调整此行程'}), 403

    data = request.get_json()
    user_message = data.get('message', '')
    history = data.get('history', [])

    if not user_message:
        return jsonify({'success': False, 'message': '请输入调整需求'})

    try:
        # 获取目的地信息
        destination_name = itinerary.destination.name if itinerary.destination else ''

        # 构建行程数据字典（与数据库模型对齐，供 AI service 使用）
        itinerary_data = {
            'days': []
        }
        for day in itinerary.days:
            day_data = {
                'day': day.day_number,
                'theme': day.theme or f'第{day.day_number}天',
                'activities': []
            }
            for act in day.activities:
                day_data['activities'].append({
                    'type': act.activity_type,
                    'name': act.name,
                    'description': act.description or '',
                    'location': act.location or '',
                    'duration': act.duration_minutes or 120,
                    'cost': act.estimated_cost or 0,
                    'tip': act.tip or ''
                })
            itinerary_data['days'].append(day_data)

        # 调用 AI 服务调整行程
        from app.services.ai_service import AIService
        ai_service = AIService()

        result = ai_service.adjust_itinerary(
            itinerary_data=itinerary_data,
            user_request=user_message,
            destination=destination_name,
            budget=itinerary.budget_level or '舒适'
        )

        # 构造返回给前端的 changes 对象（供预览/确认）
        changes = {
            'adjusted_days': result['adjusted_days'],
            'destination_name': destination_name,
            'budget_level': itinerary.budget_level or '舒适'
        }

        return jsonify({
            'success': True,
            'response': result['ai_response'],
            'changes': changes,
            'preview': result['changes_summary']
        })

    except Exception as e:
        import traceback
        import logging
        logging.error(f'AI行程调整失败: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'success': False,
            'message': f'调整失败: {str(e)}'
        }), 500


@itineraries_bp.route('/<int:id>/apply_ai_changes', methods=['POST'])
@login_required
@csrf.exempt
def apply_ai_changes(id):
    """应用AI调整的更改"""
    itinerary = Itinerary.query.get_or_404(id)
    
    if itinerary.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限'}), 403
    
    data = request.get_json()
    changes = data.get('changes', {})
    
    if not changes:
        return jsonify({'success': False, 'message': '没有更改需要应用'})
    
    # 应用更改
    try:
        apply_changes_to_itinerary(itinerary, changes)
        db.session.commit()
        return jsonify({'success': True, 'message': '更改已应用'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'应用失败: {str(e)}'})


def parse_adjust_request(message, itinerary):
    """解析用户的调整请求"""
    import re
    
    changes = {
        'type': None,
        'day': None,
        'action': None,
        'details': {}
    }
    
    # 解析天数
    day_match = re.search(r'第(\d+)天|第(\d+)天', message)
    if day_match:
        changes['day'] = int(day_match.group(1))
    
    # 解析意图类型
    if '不想去' in message or '去掉' in message or '删除' in message or '取消' in message:
        changes['type'] = 'remove'
        # 提取要删除的内容
        activity_match = re.search(r'(爬山|购物|美食|景点|摄影)', message)
        if activity_match:
            changes['action'] = activity_match.group(1)
    
    elif '增加' in message or '添加' in message or '更多' in message:
        changes['type'] = 'add'
        activity_match = re.search(r'(美食|购物|景点|摄影|文化|自然)', message)
        if activity_match:
            changes['action'] = activity_match.group(1)
    
    elif '改成' in message or '改为' in message or '调整' in message:
        changes['type'] = 'modify'
        activity_match = re.search(r'(美食|购物|景点|摄影|文化|自然)', message)
        if activity_match:
            changes['action'] = activity_match.group(1)
    
    elif '预算' in message or '费用' in message:
        changes['type'] = 'budget'
        if '降低' in message or '减少' in message or '便宜' in message:
            changes['action'] = 'reduce'
        elif '提高' in message or '增加' in message or '豪华' in message:
            changes['action'] = 'increase'
    
    elif '换' in message or '替换' in message:
        changes['type'] = 'replace'
        # 提取替换内容
    
    return changes


def generate_ai_response(message, changes, itinerary):
    """生成AI回复"""
    responses = {
        'remove': f"好的，我理解您想要移除相关活动。我将为您调整行程，移除{changes.get('action', '相关内容')}",
        'add': f"明白了！我将为您增加更多{changes.get('action', '活动')}体验，让行程更加丰富",
        'modify': f"收到！我将把相关内容调整为{changes.get('action', '新主题')}",
        'budget': {
            'reduce': "好的，我会帮您降低预算，选择更经济实惠的活动和餐厅",
            'increase': "没问题，我会为您升级行程，选择更高品质的体验"
        },
        'replace': "好的，我会为您替换相关活动，保持行程的整体平衡"
    }
    
    if changes['type'] == 'budget':
        return responses['budget'].get(changes['action'], "我会根据您的需求调整预算")
    elif changes['type']:
        return responses.get(changes['type'], "好的，我会根据您的需求调整行程")
    else:
        return "我理解您的需求，请告诉我更具体的调整方向，例如'第二天不想去购物'或'增加美食体验'"


def generate_preview(changes, itinerary):
    """生成更改预览"""
    if not changes['type']:
        return None
    
    preview_lines = []
    
    if changes['type'] == 'remove':
        preview_lines.append(f"• 将移除第{changes['day'] or '某'}天的{changes['action'] or '相关'}活动")
        preview_lines.append("• 会补充其他活动保持行程完整")
    
    elif changes['type'] == 'add':
        preview_lines.append(f"• 将增加{changes['action'] or '新'}活动")
        preview_lines.append("• 可能需要调整时间安排")
    
    elif changes['type'] == 'modify':
        preview_lines.append(f"• 将调整活动主题为{changes['action'] or '新主题'}")
        preview_lines.append("• 相关活动将被替换")
    
    elif changes['type'] == 'budget':
        preview_lines.append("• 将调整活动费用")
        if changes['action'] == 'reduce':
            preview_lines.append("• 选择更经济的餐厅和景点")
        else:
            preview_lines.append("• 升级住宿和餐饮体验")
    
    return '<br>'.join(preview_lines)


def apply_changes_to_itinerary(itinerary, changes):
    """将 AI 调整后的更改应用到行程数据库（支持新的 adjusted_days 格式）"""
    adjusted_days = changes.get('adjusted_days', [])
    if not adjusted_days:
        return  # 没有调整数据就走老逻辑

    # 获取目的地坐标
    dest_lat = itinerary.destination.latitude if itinerary.destination else None
    dest_lng = itinerary.destination.longitude if itinerary.destination else None
    from app.services.geocoding_service import GeocodingService
    geocoding = GeocodingService()

    budget_mult = 1.0
    if itinerary.budget_level == '豪华':
        budget_mult = 1.5
    elif itinerary.budget_level == '经济':
        budget_mult = 0.6

    # 获取新的天数
    new_day_count = len(adjusted_days)

    # 如果新天数少于原来的天数，先删除多余的天
    if new_day_count < itinerary.days_count:
        # 找出要删除的天数编号
        days_to_delete = list(range(new_day_count + 1, itinerary.days_count + 1))
        for day_num in days_to_delete:
            day_to_delete = ItineraryDay.query.filter_by(
                itinerary_id=itinerary.id,
                day_number=day_num
            ).first()
            if day_to_delete:
                # 删除该天的所有活动
                DayActivity.query.filter_by(day_id=day_to_delete.id).delete()
                # 删除该天
                db.session.delete(day_to_delete)
        # 更新行程天数
        itinerary.days_count = new_day_count

    # 如果新天数大于原来的天数
    elif new_day_count > itinerary.days_count:
        itinerary.days_count = new_day_count

    for day_data in adjusted_days:
        day_number = day_data.get('day', 1)
        day = ItineraryDay.query.filter_by(itinerary_id=itinerary.id, day_number=day_number).first()
        if not day:
            day = ItineraryDay(itinerary_id=itinerary.id, day_number=day_number,
                                theme=day_data.get('theme', f'第{day_number}天'))
            db.session.add(day)
            db.session.flush()
        else:
            day.theme = day_data.get('theme', day.theme)

        DayActivity.query.filter(
            DayActivity.day_id == day.id, DayActivity.activity_type != '住宿').delete()

        for idx, act in enumerate(day_data.get('activities', [])):
            activity_type = act.get('type', '景点')
            if activity_type == '住宿':
                continue
            location = act.get('location', '')
            city_name = itinerary.destination.city if itinerary.destination else ''
            coords = geocoding.geocode(location, city_name) if location else None
            activity = DayActivity(
                day_id=day.id, order_index=idx + 1, activity_type=activity_type,
                name=act.get('name', '未知活动'), description=act.get('description', ''),
                location=location, duration_minutes=int(act.get('duration', 120)),
                estimated_cost=int(act.get('cost', 0) * budget_mult),
                tip=act.get('tip', ''),
                latitude=coords.get('lat') if coords else dest_lat,
                longitude=coords.get('lng') if coords else dest_lng
            )
            db.session.add(activity)

        hotel_costs = {'经济': 200, '舒适': 450, '豪华': 900}
        hotel_cost = int(hotel_costs.get(itinerary.budget_level, 450) * budget_mult)
        DayActivity.query.filter(
            DayActivity.day_id == day.id, DayActivity.activity_type == '住宿').delete()
        accommodation = DayActivity(
            day_id=day.id, order_index=99, activity_type='住宿',
            name='推荐酒店（待确认）',
            description='建议提前在携程、Booking或Airbnb预订。',
            duration_minutes=1440, estimated_cost=hotel_cost,
            tip='建议选择交通便利的位置，方便第二天的行程。',
            latitude=dest_lat, longitude=dest_lng
        )
        db.session.add(accommodation)

