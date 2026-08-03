from flask import render_template, request
from app.blueprints.destinations import destinations_bp
from app.models.destination import Destination
from app.models.itinerary import Itinerary
from app.extensions import db


@destinations_bp.route('/')
def list():
    """目的地列表（支持分类筛选 + 关键词搜索 + 分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')

    # 构建查询
    query = Destination.query

    # 分类筛选
    if category:
        query = query.filter_by(category=category)

    # 关键词搜索
    if search:
        query = query.filter(
            db.or_(
                Destination.name.contains(search),
                Destination.city.contains(search),
                Destination.country.contains(search),
                Destination.description.contains(search)
            )
        )

    # 分页
    pagination = query.order_by(Destination.view_count.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    destinations = pagination.items

    # 获取所有分类
    categories = ['自然', '历史', '美食', '都市', '海滨']

    return render_template('destinations/list.html',
                           destinations=destinations,
                           pagination=pagination,
                           categories=categories,
                           current_category=category,
                           search=search)


@destinations_bp.route('/<int:id>')
def detail(id):
    """目的地详情（图片画廊、介绍、热门行程推荐）"""
    try:
        destination = Destination.query.get_or_404(id)
        destination.increment_view_count()

        # 获取该目的地的热门行程
        hot_itineraries = Itinerary.query.filter_by(
            destination_id=id,
            is_public=True
        ).order_by(Itinerary.view_count.desc()).limit(6).all()

        # 获取图片列表
        images = destination.get_images()

        return render_template('destinations/detail.html',
                               destination=destination,
                               hot_itineraries=hot_itineraries,
                               images=images)
    except Exception as e:
        import traceback
        error_info = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_info)
        return f"服务器内部错误: {str(e)}", 500