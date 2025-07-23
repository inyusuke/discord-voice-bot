import requests
import json
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

DIFY_API_URL = os.getenv('DIFY_API_URL')
DIFY_API_KEY = os.getenv('DIFY_API_KEY')

print(f"API URL: {DIFY_API_URL}")
print(f"API Key: {DIFY_API_KEY[:10]}...")

# シンプルなテストデータ（ファイルなし）
data = {
    'inputs': json.dumps({
        'username': 'test_user',
        'channel': 'test_channel', 
        'server': 'test_server'
    }),
    'response_mode': 'blocking',
    'user': 'test_user_123'
}

headers = {
    'Authorization': f'Bearer {DIFY_API_KEY}'
}

print("\nSending test request without file...")
response = requests.post(DIFY_API_URL, headers=headers, data=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response: {response.text}")

# 別のエンドポイント形式を試す
alt_url = DIFY_API_URL.replace('/run', '')
print(f"\n\nTrying alternative URL: {alt_url}")
response2 = requests.post(alt_url, headers=headers, data=data)
print(f"Status Code: {response2.status_code}")
print(f"Response: {response2.text[:500] if response2.text else 'No content'}")