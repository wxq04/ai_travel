# -*- coding: utf-8 -*-
"""
用户认证功能测试
测试注册、登录、登出、个人资料修改等功能
"""

import pytest
from flask import url_for
from app.models.user import User
from app.extensions import db


class TestRegister:
    """注册功能测试"""

    def test_register_success(self, client):
        """测试正常注册"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'password_confirm': 'NewPassword123'
        }, follow_redirects=True)

        # 检查注册成功后跳转到首页
        assert response.status_code == 200
        assert '注册成功' in response.data.decode('utf-8')

        # 检查用户已创建
        with client.application.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('NewPassword123')

    def test_register_duplicate_username(self, client):
        """测试用户名重复注册"""
        # 先注册一个用户
        client.post('/auth/register', data={
            'username': 'duplicateuser',
            'email': 'duplicate1@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123'
        })

        # 尝试使用相同用户名注册
        response = client.post('/auth/register', data={
            'username': 'duplicateuser',
            'email': 'duplicate2@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123'
        })

        # 检查注册失败
        assert response.status_code == 200
        assert '用户名已被使用' in response.data.decode('utf-8') or '已存在' in response.data.decode('utf-8')

    def test_register_duplicate_email(self, client):
        """测试邮箱重复注册"""
        # 先注册一个用户
        client.post('/auth/register', data={
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123'
        })

        # 尝试使用相同邮箱注册
        response = client.post('/auth/register', data={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'Password123',
            'password_confirm': 'Password123'
        })

        # 检查注册失败
        assert response.status_code == 200
        assert '邮箱已被使用' in response.data.decode('utf-8') or '已存在' in response.data.decode('utf-8')

    def test_register_password_too_short(self, client):
        """测试密码过短注册"""
        response = client.post('/auth/register', data={
            'username': 'shortpassuser',
            'email': 'shortpass@example.com',
            'password': 'short',  # 密码过短
            'password_confirm': 'short'
        })

        # 检查注册失败
        assert response.status_code == 200
        # 应显示密码长度错误提示
        assert '密码' in response.data.decode('utf-8')

    def test_register_password_mismatch(self, client):
        """测试密码不匹配注册"""
        response = client.post('/auth/register', data={
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123',
            'password_confirm': 'DifferentPassword'  # 确认密码不匹配
        })

        # 检查注册失败
        assert response.status_code == 200
        assert '密码' in response.data.decode('utf-8')

    def test_register_already_logged_in(self, logged_in_user):
        """测试已登录用户访问注册页面"""
        response = logged_in_user.get('/auth/register', follow_redirects=True)

        # 已登录用户应被重定向到首页
        assert response.status_code == 200


class TestLogin:
    """登录功能测试"""

    def test_login_success_with_username(self, client):
        """测试使用用户名正确登录"""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPassword123',
            'remember_me': False
        }, follow_redirects=True)

        # 检查登录成功
        assert response.status_code == 200
        assert '登录成功' in response.data.decode('utf-8')

    def test_login_success_with_email(self, client):
        """测试使用邮箱正确登录"""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser@example.com',
            'password': 'TestPassword123',
            'remember_me': False
        }, follow_redirects=True)

        # 检查登录成功
        assert response.status_code == 200
        assert '登录成功' in response.data.decode('utf-8')

    def test_login_wrong_password(self, client):
        """测试错误密码登录"""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'WrongPassword',
            'remember_me': False
        }, follow_redirects=True)

        # 检查登录失败
        assert response.status_code == 200
        assert '错误' in response.data.decode('utf-8')

    def test_login_nonexistent_user(self, client):
        """测试不存在用户登录"""
        response = client.post('/auth/login', data={
            'username_or_email': 'nonexistent',
            'password': 'SomePassword',
            'remember_me': False
        }, follow_redirects=True)

        # 检查登录失败
        assert response.status_code == 200
        assert '错误' in response.data.decode('utf-8')

    def test_login_remember_me(self, client):
        """测试记住我功能"""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPassword123',
            'remember_me': True
        }, follow_redirects=True)

        # 检查登录成功
        assert response.status_code == 200
        # 检查是否有记住我的 cookie
        assert 'remember_token' in [cookie.name for cookie in client.cookie_jar] or 'session' in [cookie.name for cookie in client.cookie_jar]

    def test_login_already_logged_in(self, logged_in_user):
        """测试已登录用户访问登录页面"""
        response = logged_in_user.get('/auth/login', follow_redirects=True)

        # 已登录用户应被重定向到首页
        assert response.status_code == 200


class TestLogout:
    """登出功能测试"""

    def test_logout_success(self, logged_in_user):
        """测试登出成功"""
        response = logged_in_user.get('/auth/logout', follow_redirects=True)

        # 检查登出成功
        assert response.status_code == 200
        assert '登出' in response.data.decode('utf-8')

    def test_logout_not_logged_in(self, client):
        """测试未登录用户登出"""
        response = client.get('/auth/logout', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200


class TestProfile:
    """个人资料测试"""

    def test_profile_view(self, logged_in_user):
        """测试查看个人资料页面"""
        response = logged_in_user.get('/auth/profile')

        # 检查页面正常显示
        assert response.status_code == 200
        assert 'testuser' in response.data.decode('utf-8')

    def test_profile_update_username(self, logged_in_user, app):
        """测试更新用户名"""
        response = logged_in_user.post('/auth/profile', data={
            'username': 'newtestuser',
            'email': 'testuser@example.com',
            'bio': '更新后的简介'
        }, follow_redirects=True)

        # 检查更新成功
        assert response.status_code == 200

        # 验证数据库中的用户名已更新
        with app.app_context():
            user = User.query.filter_by(email='testuser@example.com').first()
            assert user.username == 'newtestuser'

    def test_profile_update_email(self, logged_in_user, app):
        """测试更新邮箱"""
        response = logged_in_user.post('/auth/profile', data={
            'username': 'testuser',
            'email': 'newemail@example.com',
            'bio': '测试用户'
        }, follow_redirects=True)

        # 检查更新成功
        assert response.status_code == 200

        # 验证数据库中的邮箱已更新
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.email == 'newemail@example.com'

    def test_profile_update_bio(self, logged_in_user, app):
        """测试更新简介"""
        response = logged_in_user.post('/auth/profile', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'bio': '这是我的新简介'
        }, follow_redirects=True)

        # 检查更新成功
        assert response.status_code == 200

        # 验证数据库中的简介已更新
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.bio == '这是我的新简介'

    def test_profile_not_logged_in(self, client):
        """测试未登录用户访问个人资料页面"""
        response = client.get('/auth/profile', follow_redirects=True)

        # 未登录用户应被重定向到登录页面
        assert response.status_code == 200
        assert '登录' in response.data.decode('utf-8')

    def test_change_password_success(self, logged_in_user, app):
        """测试修改密码成功"""
        response = logged_in_user.post('/auth/profile', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'bio': '测试用户',
            'current_password': 'TestPassword123',
            'new_password': 'NewTestPassword456',
            'new_password_confirm': 'NewTestPassword456'
        }, follow_redirects=True)

        # 检查修改成功
        assert response.status_code == 200

        # 验证密码已更新
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.check_password('NewTestPassword456')
            assert not user.check_password('TestPassword123')

    def test_change_password_wrong_current(self, logged_in_user):
        """测试修改密码时当前密码错误"""
        response = logged_in_user.post('/auth/profile', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'bio': '测试用户',
            'current_password': 'WrongPassword',
            'new_password': 'NewPassword123',
            'new_password_confirm': 'NewPassword123'
        }, follow_redirects=True)

        # 检查修改失败
        assert response.status_code == 200
        assert '密码' in response.data.decode('utf-8')