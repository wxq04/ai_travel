# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

from app import create_app

app = create_app('development')

# 使用测试客户端
with app.test_client() as client:
    # 登录
    response = client.post('/auth/login', data={
        'username_or_email': 'testuser5',
        'password': '123456'
    }, follow_redirects=True)
    
    # 获取个人资料页面
    response = client.get('/auth/profile')
    
    print("状态码:", response.status_code)
    print("\n响应内容:")
    print(response.data.decode('utf-8'))