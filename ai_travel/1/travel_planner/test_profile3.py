# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'c:\Users\Administrator\Downloads\智能系统作业\期末作业\travel_planner')

from app import create_app

app = create_app('development')

# 使用测试客户端
with app.test_client() as client:
    # 测试登录
    print("测试登录...")
    response = client.post('/auth/login', data={
        'username_or_email': 'testuser5',
        'password': '123456'
    }, follow_redirects=True)
    print(f"登录状态: {response.status_code}")
    
    # 测试访问个人资料
    print("\n测试个人资料页面...")
    response = client.get('/auth/profile')
    print(f"个人资料状态: {response.status_code}")
    print(f"内容长度: {len(response.data)}")
    print(f"部分内容: {response.data[:500].decode('utf-8', errors='ignore')}")