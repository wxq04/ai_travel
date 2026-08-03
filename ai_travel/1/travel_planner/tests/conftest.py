# -*- coding: utf-8 -*-
"""
测试配置文件
提供测试所需的 Flask 应用实例和数据库配置
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.destination import Destination
from app.models.itinerary import Itinerary, ItineraryDay, DayActivity
from app.models.social import Tag, Comment, Like, Favorite
import json


@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    # 使用测试配置
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # 使用内存数据库
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # 测试时禁用 CSRF
        'SECRET_KEY': 'test-secret-key',
        'REDIS_URL': None,  # 测试时禁用 Redis
        'AI_API_KEY': 'test-api-key',
        'AI_API_BASE': 'https://test-api.example.com',
        'AI_MODEL': 'test-model'
    }

    app = create_app(test_config)

    # 创建应用上下文
    with app.app_context():
        # 创建所有表
        db.create_all()

        # 插入测试数据
        insert_test_data()

        yield app

        # 清理
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """创建测试 CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """数据库会话"""
    with app.app_context():
        yield db.session
        db.session.rollback()


def insert_test_data():
    """插入测试数据"""
    # 创建测试用户
    test_user = User(
        username='testuser',
        email='testuser@example.com',
        bio='测试用户'
    )
    test_user.set_password('TestPassword123')

    admin_user = User(
        username='admin',
        email='admin@example.com',
        bio='管理员用户'
    )
    admin_user.set_password('AdminPassword123')

    db.session.add(test_user)
    db.session.add(admin_user)
    db.session.commit()

    # 创建测试目的地
    destination = Destination(
        name='测试目的地',
        country='中国',
        province='测试省',
        city='测试市',
        description='这是一个测试目的地',
        cover_image='https://picsum.photos/seed/test/800/600',
        category='自然',
        avg_rating=4.5,
        view_count=100
    )
    db.session.add(destination)
    db.session.commit()

    # 创建测试标签
    tags = [
        Tag(name='美食', category='兴趣', icon='utensils'),
        Tag(name='历史', category='兴趣', icon='landmark'),
        Tag(name='自然', category='兴趣', icon='tree')
    ]
    for tag in tags:
        db.session.add(tag)
    db.session.commit()

    # 创建测试行程（公开）
    public_itinerary = Itinerary(
        user_id=test_user.id,
        title='公开测试行程',
        destination_id=destination.id,
        days_count=3,
        budget_level='舒适',
        interest_tags=json.dumps(['美食', '自然']),
        is_public=True,
        ai_generated=True,
        like_count=10,
        view_count=50
    )
    db.session.add(public_itinerary)
    db.session.commit()

    # 创建行程天数
    day1 = ItineraryDay(
        itinerary_id=public_itinerary.id,
        day_number=1,
        theme='第一天测试'
    )
    db.session.add(day1)
    db.session.commit()

    # 创建活动
    activity1 = DayActivity(
        day_id=day1.id,
        order_index=1,
        activity_type='景点',
        name='测试景点',
        description='这是一个测试景点',
        location='测试市',
        duration_minutes=120,
        estimated_cost=100,
        tip='测试小贴士'
    )
    db.session.add(activity1)
    db.session.commit()

    # 创建私有行程
    private_itinerary = Itinerary(
        user_id=test_user.id,
        title='私有测试行程',
        destination_id=destination.id,
        days_count=2,
        budget_level='经济',
        is_public=False,
        ai_generated=False
    )
    db.session.add(private_itinerary)
    db.session.commit()


@pytest.fixture
def logged_in_user(client):
    """已登录的测试用户"""
    client.post('/auth/login', data={
        'username_or_email': 'testuser',
        'password': 'TestPassword123'
    })
    return client


@pytest.fixture
def logged_in_admin(client):
    """已登录的管理员"""
    client.post('/auth/login', data={
        'username_or_email': 'admin',
        'password': 'AdminPassword123'
    })
    return client