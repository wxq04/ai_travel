import requests
import re

session = requests.Session()

# 获取登录页获取CSRF令牌
response = session.get('http://127.0.0.1:5000/auth/login')
csrf_match = re.search(r"var csrfToken\s*=\s*['\"]([^'\"]+)['\"]", response.text)
csrf_token = csrf_match.group(1) if csrf_match else None
print('CSRF Token:', csrf_token)

# 测试分享API（带CSRF令牌）
response = session.post(
    'http://127.0.0.1:5000/itineraries/share',
    json={'id': 1},
    headers={
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
)

print('Status Code:', response.status_code)
print('Content-Type:', response.headers.get('Content-Type', 'N/A'))
print('Response:', response.text)