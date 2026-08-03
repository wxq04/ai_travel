import requests
import re

session = requests.Session()

# 获取登录页
response = session.get('http://127.0.0.1:5000/auth/login')
print('登录页状态:', response.status_code)

# 提取CSRF令牌
csrf_match = re.search(r"var csrfToken\s*=\s*['\"]([^'\"]+)['\"]", response.text)
csrf_token = csrf_match.group(1) if csrf_match else None
print('CSRF Token:', csrf_token)

# 测试分享功能（未登录状态）
headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrf_token
}
data = {
    'id': 1
}
response = session.post('http://127.0.0.1:5000/itineraries/share', json=data, headers=headers)
print('分享状态:', response.status_code)
print('分享响应:', response.text)