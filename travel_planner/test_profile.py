# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

from app import create_app
from flask_testing import TestCase

class TestAuth(TestCase):
    def create_app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF便于测试
        return app
    
    def test_login_and_profile(self):
        """测试登录和访问个人资料"""
        # 测试登录
        response = self.client.post('/auth/login', data={
            'username_or_email': 'testuser5',
            'password': '123456'
        })
        print(f"登录状态: {response.status_code}")
        
        # 测试访问个人资料
        response = self.client.get('/auth/profile')
        print(f"个人资料状态: {response.status_code}")
        
        # 测试公开用户主页
        response = self.client.get('/auth/user/testuser5')
        print(f"公开主页状态: {response.status_code}")
        
        return response.status_code == 200

if __name__ == '__main__':
    test = TestAuth()
    app = test.create_app()
    with app.app_context():
        result = test.test_login_and_profile()
        print(f"\n测试结果: {'通过' if result else '失败'}")