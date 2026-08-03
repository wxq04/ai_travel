from flask import render_template, request, jsonify, flash
from flask_login import login_required, current_user
from app.blueprints.community import community_bp
from app.extensions import db, csrf
from app.models.itinerary import Itinerary
from app.models.social import Like, Favorite, Comment


@community_bp.route('/')
def index():
    """社区广场（公开行程瀑布流，支持按热度/最新排序、标签筛选）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    sort_by = request.args.get('sort', 'latest')  # latest 或 hot
    tag = request.args.get('tag', '')

    # 构建查询
    query = Itinerary.query.filter_by(is_public=True)

    # 标签筛选
    if tag:
        query = query.filter(Itinerary.interest_tags.contains(tag))

    # 排序
    if sort_by == 'hot':
        query = query.order_by(Itinerary.like_count.desc(), Itinerary.view_count.desc())
    else:  # latest
        query = query.order_by(Itinerary.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    itineraries = pagination.items

    return render_template('community/index.html',
                           itineraries=itineraries,
                           pagination=pagination,
                           sort_by=sort_by,
                           current_tag=tag)


@community_bp.route('/like/<int:itinerary_id>', methods=['POST'])
@login_required
@csrf.exempt
def like(itinerary_id):
    """点赞（AJAX，无刷新）"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    # 检查是否已经点赞
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        itinerary_id=itinerary_id
    ).first()

    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        itinerary.decrement_like_count()
        db.session.commit()
        return jsonify({
            'success': True,
            'liked': False,
            'like_count': itinerary.like_count
        })
    else:
        # 添加点赞
        new_like = Like(user_id=current_user.id, itinerary_id=itinerary_id)
        db.session.add(new_like)
        itinerary.increment_like_count()
        db.session.commit()
        return jsonify({
            'success': True,
            'liked': True,
            'like_count': itinerary.like_count
        })


@community_bp.route('/favorite/<int:itinerary_id>', methods=['POST'])
@login_required
@csrf.exempt
def favorite(itinerary_id):
    """收藏（AJAX）"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    # 检查是否已经收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        itinerary_id=itinerary_id
    ).first()

    if existing_favorite:
        # 取消收藏
        db.session.delete(existing_favorite)
        db.session.commit()
        return jsonify({
            'success': True,
            'favorited': False,
            'message': '已取消收藏'
        })
    else:
        # 添加收藏
        new_favorite = Favorite(user_id=current_user.id, itinerary_id=itinerary_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
            'success': True,
            'favorited': True,
            'message': '已添加收藏'
        })


@community_bp.route('/comment/<int:itinerary_id>', methods=['POST'])
@login_required
@csrf.exempt
def add_comment(itinerary_id):
    """发表评论（支持回复）"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    content = request.form.get('content')
    parent_id = request.form.get('parent_id', type=int)
    rating = request.form.get('rating', type=int)

    if not content:
        return jsonify({'error': '评论内容不能为空'}), 400

    # 创建评论
    comment = Comment(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        content=content,
        parent_id=parent_id if parent_id else None,
        rating=rating if rating and 1 <= rating <= 5 else None
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'user': current_user.username,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'rating': comment.rating
        }
    })


@community_bp.route('/comment/<int:id>', methods=['DELETE'])
@login_required
def delete_comment(id):
    """删除评论"""
    comment = Comment.query.get_or_404(id)

    # 只有评论作者可以删除
    if comment.user_id != current_user.id:
        return jsonify({'error': '无权限删除此评论'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'success': True, 'message': '评论已删除'})


@community_bp.route('/comments/<int:itinerary_id>')
def get_comments(itinerary_id):
    """获取行程的所有评论"""
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    # 获取所有评论（包括回复）
    comments = Comment.query.filter_by(itinerary_id=itinerary_id).order_by(
        Comment.created_at.desc()
    ).all()

    # 组织评论数据
    comments_data = []
    for comment in comments:
        comment_dict = {
            'id': comment.id,
            'user': comment.author.username,
            'user_avatar': comment.author.avatar,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'rating': comment.rating,
            'parent_id': comment.parent_id,
            'replies': []
        }

        # 如果是顶级评论，添加回复
        if not comment.parent_id:
            replies = Comment.query.filter_by(parent_id=comment.id).order_by(
                Comment.created_at.asc()
            ).all()
            for reply in replies:
                comment_dict['replies'].append({
                    'id': reply.id,
                    'user': reply.author.username,
                    'user_avatar': reply.author.avatar,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M')
                })

            comments_data.append(comment_dict)

    return jsonify({'success': True, 'comments': comments_data})