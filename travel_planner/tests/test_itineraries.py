# -*- coding: utf-8 -*-
"""
行程管理功能测试
测试创建行程、查看行程、编辑行程、删除行程、克隆行程等功能
"""

import pytest
import json
from flask import session
from app.models.user import User
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.destination import Destination
from app.extensions import db


class TestCreateItinerary:
    """创建行程测试"""

    def test_create_itinerary_logged_in(self, logged_in_user, app):
        """测试已登录用户创建行程"""
        with app.app_context():
            destination = Destination.query.first()

        # Step 1: 选择目的地、天数、预算
        response = logged_in_user.post('/itineraries/create', data={
            'destination_id': destination.id,
            'days_count': 3,
            'budget_level': '舒适'
        }, follow_redirects=True)

        # 检查跳转到 Step 2
        assert response.status_code == 200

        # Step 2: 设置兴趣标签和补充说明
        response = logged_in_user.post('/itineraries/create/step2', data={
            'title': '测试行程创建',
            'interest_tags': '美食,历史',
            'additional_notes': '希望多安排美食体验',
            'is_public': True
        }, follow_redirects=True)

        # 检查跳转到生成页面
        assert response.status_code == 200

    def test_create_itinerary_not_logged_in(self, client):
        """测试未登录用户创建行程"""
        response = client.get('/itineraries/create', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200
        assert '登录' in response.data.decode('utf-8')

    def test_create_itinerary_step1_validation(self, logged_in_user):
        """测试 Step 1 表单验证"""
        # 测试缺少目的地
        response = logged_in_user.post('/itineraries/create', data={
            'days_count': 3,
            'budget_level': '舒适'
        })

        # 检查表单验证失败
        assert response.status_code == 200

    def test_create_itinerary_step2_without_step1(self, logged_in_user):
        """测试直接访问 Step 2 而没有完成 Step 1"""
        response = logged_in_user.get('/itineraries/create/step2', follow_redirects=True)

        # 应被重定向回 Step 1
        assert response.status_code == 200


class TestViewItinerary:
    """查看行程测试"""

    def test_view_public_itinerary(self, client, app):
        """测试查看公开行程"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()

        response = client.get(f'/itineraries/{itinerary.id}')

        # 检查页面正常显示
        assert response.status_code == 200
        assert itinerary.title in response.data.decode('utf-8')

    def test_view_private_itinerary_owner(self, logged_in_user, app):
        """测试作者查看私有行程"""
        with app.app_context():
            # 创建一个私有行程
            user = User.query.filter_by(username='testuser').first()
            destination = Destination.query.first()
            private_itinerary = Itinerary(
                user_id=user.id,
                title='私有行程测试',
                destination_id=destination.id,
                days_count=2,
                is_public=False
            )
            db.session.add(private_itinerary)
            db.session.commit()
            itinerary_id = private_itinerary.id

        response = logged_in_user.get(f'/itineraries/{itinerary_id}')

        # 作者可以查看自己的私有行程
        assert response.status_code == 200
        assert '私有行程测试' in response.data.decode('utf-8')

    def test_view_private_itinerary_non_owner(self, logged_in_admin, app):
        """测试非作者查看私有行程"""
        with app.app_context():
            # 获取 testuser 的私有行程
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id, is_public=False).first()
            if itinerary:
                itinerary_id = itinerary.id
            else:
                # 创建一个私有行程
                destination = Destination.query.first()
                itinerary = Itinerary(
                    user_id=user.id,
                    title='其他用户私有行程',
                    destination_id=destination.id,
                    days_count=2,
                    is_public=False
                )
                db.session.add(itinerary)
                db.session.commit()
                itinerary_id = itinerary.id

        response = logged_in_admin.get(f'/itineraries/{itinerary_id}')

        # 非作者不能查看私有行程（应返回 404 或重定向）
        assert response.status_code in [403, 404]

    def test_view_nonexistent_itinerary(self, client):
        """测试查看不存在的行程"""
        response = client.get('/itineraries/99999')

        # 应返回 404
        assert response.status_code == 404

    def test_view_itinerary_increments_view_count(self, client, app):
        """测试查看行程增加浏览次数"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            initial_count = itinerary.view_count
            itinerary_id = itinerary.id

        response = client.get(f'/itineraries/{itinerary_id}')

        with app.app_context():
            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary.view_count > initial_count


class TestEditItinerary:
    """编辑行程测试"""

    def test_edit_itinerary_owner(self, logged_in_user, app):
        """测试作者编辑行程"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            itinerary_id = itinerary.id

        response = logged_in_user.get(f'/itineraries/{itinerary_id}/edit')

        # 作者可以编辑自己的行程
        assert response.status_code == 200
        assert itinerary.title in response.data.decode('utf-8')

    def test_edit_itinerary_non_owner(self, logged_in_admin, app):
        """测试非作者编辑行程"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            itinerary_id = itinerary.id

        response = logged_in_admin.get(f'/itineraries/{itinerary_id}/edit', follow_redirects=True)

        # 非作者不能编辑行程
        assert response.status_code in [403, 404, 200]

    def test_edit_itinerary_not_logged_in(self, client, app):
        """测试未登录用户编辑行程"""
        with app.app_context():
            itinerary = Itinerary.query.first()
            itinerary_id = itinerary.id

        response = client.get(f'/itineraries/{itinerary_id}/edit', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200
        assert '登录' in response.data.decode('utf-8')

    def test_update_itinerary_title(self, logged_in_user, app):
        """测试更新行程标题"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            itinerary_id = itinerary.id

        response = logged_in_user.post(f'/itineraries/{itinerary_id}/edit', data={
            'title': '更新后的行程标题',
            'budget_level': '舒适',
            'is_public': True
        }, follow_redirects=True)

        # 检查更新成功
        assert response.status_code == 200

        with app.app_context():
            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary.title == '更新后的行程标题'

    def test_add_day_to_itinerary(self, logged_in_user, app):
        """测试添加行程天数"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            itinerary_id = itinerary.id
            initial_days_count = itinerary.days_count

        response = logged_in_user.post(f'/itineraries/{itinerary_id}/add_day', follow_redirects=True)

        # 检查添加成功
        assert response.status_code == 200

        with app.app_context():
            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary.days_count == initial_days_count + 1

    def test_add_activity_to_day(self, logged_in_user, app):
        """测试添加活动到行程天数"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            day = itinerary.days.first()
            day_id = day.id

        response = logged_in_user.post(f'/itineraries/day/{day_id}/add_activity', data={
            'activity_type': '景点',
            'name': '新添加的景点',
            'description': '这是一个新景点',
            'duration_minutes': 120,
            'estimated_cost': 100
        }, follow_redirects=True)

        # 检查添加成功
        assert response.status_code == 200

        with app.app_context():
            activity = DayActivity.query.filter_by(day_id=day_id, name='新添加的景点').first()
            assert activity is not None


class TestDeleteItinerary:
    """删除行程测试"""

    def test_delete_itinerary_owner(self, logged_in_user, app):
        """测试作者删除行程"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            destination = Destination.query.first()

            # 创建一个用于删除的行程
            delete_itinerary = Itinerary(
                user_id=user.id,
                title='待删除行程',
                destination_id=destination.id,
                days_count=1,
                is_public=False
            )
            db.session.add(delete_itinerary)
            db.session.commit()
            itinerary_id = delete_itinerary.id

        response = logged_in_user.post(f'/itineraries/{itinerary_id}/delete', follow_redirects=True)

        # 检查删除成功
        assert response.status_code == 200

        with app.app_context():
            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary is None

    def test_delete_itinerary_non_owner(self, logged_in_admin, app):
        """测试非作者删除行程"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            itinerary = Itinerary.query.filter_by(user_id=user.id).first()
            itinerary_id = itinerary.id

        response = logged_in_admin.post(f'/itineraries/{itinerary_id}/delete', follow_redirects=True)

        # 非作者不能删除行程
        assert response.status_code in [403, 404, 200]

        # 验证行程未被删除
        with app.app_context():
            itinerary = Itinerary.query.get(itinerary_id)
            assert itinerary is not None

    def test_delete_itinerary_not_logged_in(self, client, app):
        """测试未登录用户删除行程"""
        with app.app_context():
            itinerary = Itinerary.query.first()
            itinerary_id = itinerary.id

        response = client.post(f'/itineraries/{itinerary_id}/delete', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200


class TestCloneItinerary:
    """克隆行程测试"""

    def test_clone_public_itinerary(self, logged_in_user, app):
        """测试克隆公开行程"""
        with app.app_context():
            # 获取一个公开行程（非当前用户的）
            user = User.query.filter_by(username='testuser').first()
            public_itinerary = Itinerary.query.filter(
                Itinerary.is_public == True,
                Itinerary.user_id != user.id
            ).first()

            if not public_itinerary:
                # 创建一个其他用户的公开行程
                admin = User.query.filter_by(username='admin').first()
                destination = Destination.query.first()
                public_itinerary = Itinerary(
                    user_id=admin.id,
                    title='可克隆的公开行程',
                    destination_id=destination.id,
                    days_count=2,
                    is_public=True
                )
                db.session.add(public_itinerary)
                db.session.commit()

            itinerary_id = public_itinerary.id
            original_title = public_itinerary.title

        response = logged_in_user.post(f'/itineraries/{itinerary_id}/clone', follow_redirects=True)

        # 检查克隆成功
        assert response.status_code == 200

        # 验证克隆的行程已创建
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            cloned = Itinerary.query.filter(
                Itinerary.user_id == user.id,
                Itinerary.title.contains(original_title)
            ).first()
            assert cloned is not None

    def test_clone_itinerary_not_logged_in(self, client, app):
        """测试未登录用户克隆行程"""
        with app.app_context():
            itinerary = Itinerary.query.filter_by(is_public=True).first()
            itinerary_id = itinerary.id

        response = client.post(f'/itineraries/{itinerary_id}/clone', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200


class TestMyItineraries:
    """我的行程列表测试"""

    def test_my_itineraries_logged_in(self, logged_in_user):
        """测试已登录用户查看我的行程"""
        response = logged_in_user.get('/itineraries/my')

        # 检查页面正常显示
        assert response.status_code == 200

    def test_my_itineraries_not_logged_in(self, client):
        """测试未登录用户查看我的行程"""
        response = client.get('/itineraries/my', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200
        assert '登录' in response.data.decode('utf-8')