# -*- coding: utf-8 -*-
"""
社区功能测试
测试点赞、收藏、发表评论、删除评论等功能
"""

import pytest
import json
from app.models.user import User
from app.models.itinerary import Itinerary
from app.models.social import Like, Favorite, Comment
from app.models.destination import Destination
from app.extensions import db


class TestLike:
    """点赞功能测试"""

    def test_like_itinerary(self, logged_in_user, app):
        """测试点赞行程"""
        with app.app_context():
            # 获取一个公开行程（非当前用户的）
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter(
                Itinerary.is_public == True,
                Itinerary.user_id != user.id
            ).first()

            if not itinerary:
                # 创建一个其他用户的公开行程
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=admin.id,
                    title='可点赞的行程',
                    destination_id=destination.id,
                    days_count=2,
                    is_public=True,
                    like_count=0
                )
                db.session.add(itinerary)
                db.session.commit()

            itinerary_id = itinerary.id
            initial_like_count = itinerary.like_count

        # 发送点赞请求
        response = logged_in_user.post(f'/community/like/{itinerary_id}')

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['liked'] == True

        # 验证数据库中的点赞记录
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            like = Like.query.filter_by(user_id=user.id, itinerary_id=itinerary_id).first()
            assert like is not None

            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary.like_count == initial_like_count + 1

    def test_unlike_itinerary(self, logged_in_user, app):
        """测试取消点赞"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()

            # 获取一个已点赞的行程
            existing_like = Like.query.filter_by(user_id=user.id).first()

            if existing_like:
                itinerary_id = existing_like.itinerary_id
                itinerary = Itinerary.query.get(itinerary_id)
                initial_like_count = itinerary.like_count
            else:
                # 先点赞一个行程
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=admin.id,
                    title='取消点赞测试行程',
                    destination_id=destination.id,
                    days_count=1,
                    is_public=True,
                    like_count=1
                )
                db.session.add(itinerary)
                db.session.commit()

                new_like = Like(user_id=user.id, itinerary_id=itinerary.id)
                db.session.add(new_like)
                db.session.commit()

                itinerary_id = itinerary.id
                initial_like_count = 1

        # 发送取消点赞请求
        response = logged_in_user.post(f'/community/like/{itinerary_id}')

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['liked'] == False

        # 验证数据库中的点赞记录已删除
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            like = Like.query.filter_by(user_id=user.id, itinerary_id=itinerary_id).first()
            assert like is None

            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary.like_count == initial_like_count - 1

    def test_like_not_logged_in(self, client, app):
        """测试未登录用户点赞"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            itinerary_id = itinerary.id

        response = client.post(f'/community/like/{itinerary_id}')

        # 未登录用户应被拒绝
        assert response.status_code in [401, 403, 302]

    def test_like_nonexistent_itinerary(self, logged_in_user):
        """测试点赞不存在的行程"""
        response = logged_in_user.post('/community/like/99999')

        # 应返回 404
        assert response.status_code == 404

    def test_like_twice_same_itinerary(self, logged_in_user, app):
        """测试重复点赞同一行程"""
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            destination = Destination.query.first()
            itinerary = Itinerary(
                user_id=admin.id,
                title='重复点赞测试',
                destination_id=destination.id,
                days_count=1,
                is_public=True,
                like_count=0
            )
            db.session.add(itinerary)
            db.session.commit()
            itinerary_id = itinerary.id

        # 第一次点赞
        response1 = logged_in_user.post(f'/community/like/{itinerary_id}')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['liked'] == True

        # 第二次点赞（应取消点赞）
        response2 = logged_in_user.post(f'/community/like/{itinerary_id}')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['liked'] == False


class TestFavorite:
    """收藏功能测试"""

    def test_favorite_itinerary(self, logged_in_user, app):
        """测试收藏行程"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter(
                Itinerary.is_public == True,
                Itinerary.user_id != user.id
            ).first()

            if not itinerary:
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=admin.id,
                    title='可收藏的行程',
                    destination_id=destination.id,
                    days_count=2,
                    is_public=True
                )
                db.session.add(itinerary)
                db.session.commit()

            itinerary_id = itinerary.id

        # 发送收藏请求
        response = logged_in_user.post(f'/community/favorite/{itinerary_id}')

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['favorited'] == True

        # 验证数据库中的收藏记录
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            favorite = Favorite.query.filter_by(user_id=user.id, itinerary_id=itinerary_id).first()
            assert favorite is not None

    def test_unfavorite_itinerary(self, logged_in_user, app):
        """测试取消收藏"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()

            # 获取一个已收藏的行程
            existing_favorite = Favorite.query.filter_by(user_id=user.id).first()

            if existing_favorite:
                itinerary_id = existing_favorite.itinerary_id
            else:
                # 先收藏一个行程
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=admin.id,
                    title='取消收藏测试行程',
                    destination_id=destination.id,
                    days_count=1,
                    is_public=True
                )
                db.session.add(itinerary)
                db.session.commit()

                new_favorite = Favorite(user_id=user.id, itinerary_id=itinerary.id)
                db.session.add(new_favorite)
                db.session.commit()

                itinerary_id = itinerary.id

        # 发送取消收藏请求
        response = logged_in_user.post(f'/community/favorite/{itinerary_id}')

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['favorited'] == False

        # 验证数据库中的收藏记录已删除
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            favorite = Favorite.query.filter_by(user_id=user.id, itinerary_id=itinerary_id).first()
            assert favorite is None

    def test_favorite_not_logged_in(self, client, app):
        """测试未登录用户收藏"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            itinerary_id = itinerary.id

        response = client.post(f'/community/favorite/{itinerary_id}')

        # 未登录用户应被拒绝
        assert response.status_code in [401, 403, 302]

    def test_favorite_nonexistent_itinerary(self, logged_in_user):
        """测试收藏不存在的行程"""
        response = logged_in_user.post('/community/favorite/99999')

        # 应返回 404
        assert response.status_code == 404


class TestComment:
    """评论功能测试"""

    def test_add_comment(self, logged_in_user, app):
        """测试发表评论"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter(
                Itinerary.is_public == True,
                Itinerary.user_id != user.id
            ).first()

            if not itinerary:
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=admin.id,
                    title='可评论的行程',
                    destination_id=destination.id,
                    days_count=2,
                    is_public=True
                )
                db.session.add(itinerary)
                db.session.commit()

            itinerary_id = itinerary.id

        # 发送评论请求
        response = logged_in_user.post(f'/community/comment/{itinerary_id}', data={
            'content': '这是一条测试评论',
            'rating': 5
        })

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['comment']['content'] == '这是一条测试评论'
        assert data['comment']['rating'] == 5

        # 验证数据库中的评论记录
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            comment = Comment.query.filter_by(
                user_id=user.id,
                itinerary_id=itinerary_id,
                content='这是一条测试评论'
            ).first()
            assert comment is not None
            assert comment.rating == 5

    def test_add_reply_comment(self, logged_in_user, app):
        """测试回复评论"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            admin = User.query.filter_by(username='admin').first()
            destination = Destination.query.first()

            # 创建行程
            itinerary = Itinerary(
                user_id=admin.id,
                title='回复评论测试行程',
                destination_id=destination.id,
                days_count=1,
                is_public=True
            )
            db.session.add(itinerary)
            db.session.commit()

            # 创建父评论
            parent_comment = Comment(
                user_id=admin.id,
                itinerary_id=itinerary.id,
                content='这是一条父评论'
            )
            db.session.add(parent_comment)
            db.session.commit()

            itinerary_id = itinerary.id
            parent_id = parent_comment.id

        # 发送回复请求
        response = logged_in_user.post(f'/community/comment/{itinerary_id}', data={
            'content': '这是一条回复',
            'parent_id': parent_id
        })

        # 检查响应
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True

        # 验证数据库中的回复记录
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            reply = Comment.query.filter_by(
                user_id=user.id,
                itinerary_id=itinerary_id,
                parent_id=parent_id
            ).first()
            assert reply is not None

    def test_add_comment_empty_content(self, logged_in_user, app):
        """测试发表空评论"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            itinerary_id = itinerary.id

        # 发送空评论请求
        response = logged_in_user.post(f'/community/comment/{itinerary_id}', data={
            'content': ''
        })

        # 检查响应（应返回错误）
        assert response.status_code == 400

    def test_add_comment_not_logged_in(self, client, app):
        """测试未登录用户发表评论"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            itinerary_id = itinerary.id

        response = client.post(f'/community/comment/{itinerary_id}', data={
            'content': '未登录用户评论'
        })

        # 未登录用户应被拒绝
        assert response.status_code in [401, 403, 302]

    def test_delete_comment_owner(self, logged_in_user, app):
        """测试作者删除评论"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            admin = User.query.filter_by(username='admin').first()
            destination = Destination.query.first()

            # 创建行程和评论
            itinerary = Itinerary(
                user_id=admin.id,
                title='删除评论测试行程',
                destination_id=destination.id,
                days_count=1,
                is_public=True
            )
            db.session.add(itinerary)
            db.session.commit()

            comment = Comment(
                user_id=user.id,
                itinerary_id=itinerary.id,
                content='待删除的评论'
            )
            db.session.add(comment)
            db.session.commit()

            comment_id = comment.id

        # 发送删除请求
        response = logged_in_user.delete(f'/community/comment/{comment_id}')

        # 检查响应
        assert response.status_code == 200

        # 验证数据库中的评论已删除
        with app.app_context():
            comment = Comment.query.get(comment_id)
            assert comment is None

    def test_delete_comment_non_owner(self, logged_in_admin, app):
        """测试非作者删除评论"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            admin = User.query.filter_by(username='admin').first()
            destination = Destination.query.first()

            # 创建行程和评论（testuser 的评论）
            itinerary = Itinerary(
                user_id=admin.id,
                title='非作者删除测试行程',
                destination_id=destination.id,
                days_count=1,
                is_public=True
            )
            db.session.add(itinerary)
            db.session.commit()

            comment = Comment(
                user_id=user.id,
                itinerary_id=itinerary.id,
                content='testuser 的评论'
            )
            db.session.add(comment)
            db.session.commit()

            comment_id = comment.id

        # admin 尝试删除 testuser 的评论
        response = logged_in_admin.delete(f'/community/comment/{comment_id}')

        # 非作者不能删除评论
        assert response.status_code in [403, 404]

        # 验证评论未被删除
        with app.app_context():
            comment = Comment.query.get(comment_id)
            assert comment is not None

    def test_delete_comment_not_logged_in(self, client, app):
        """测试未登录用户删除评论"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(is_public=True).first()

            comment = Comment(
                user_id=user.id,
                itinerary_id=itinerary.id,
                content='测试评论'
            )
            db.session.add(comment)
            db.session.commit()

            comment_id = comment.id

        response = client.delete(f'/community/comment/{comment_id}')

        # 未登录用户应被拒绝
        assert response.status_code in [401, 403, 302]


class TestCommunityIndex:
    """社区广场测试"""

    def test_community_index(self, client):
        """测试访问社区广场"""
        response = client.get('/community/')

        # 检查页面正常显示
        assert response.status_code == 200

    def test_community_index_sort_latest(self, client):
        """测试按最新排序"""
        response = client.get('/community/?sort=latest')

        assert response.status_code == 200

    def test_community_index_sort_hot(self, client):
        """测试按热度排序"""
        response = client.get('/community/?sort=hot')

        assert response.status_code == 200

    def test_community_index_tag_filter(self, client):
        """测试标签筛选"""
        response = client.get('/community/?tag=美食')

        assert response.status_code == 200

    def test_community_index_pagination(self, client):
        """测试分页"""
        response = client.get('/community/?page=1&per_page=12')

        assert response.status_code == 200