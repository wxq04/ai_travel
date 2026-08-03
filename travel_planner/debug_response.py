import requests

# 直接测试分享API
response = requests.post(
    'http://127.0.0.1:5000/itineraries/share',
    json={'id': 1},
    headers={'Content-Type': 'application/json'}
)

print('Status Code:', response.status_code)
print('Content-Type:', response.headers.get('Content-Type', 'N/A'))
print('Content Length:', len(response.text))
print('First 500 chars:', response.text[:500])