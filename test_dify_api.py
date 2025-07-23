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

# テストリクエスト
headers = {
    'Authorization': f'Bearer {DIFY_API_KEY}',
    'Content-Type': 'application/json'
}

# シンプルなテストデータ
data = {
    'inputs': {
        'username': 'test_user',
        'channel': 'test_channel',
        'server': 'test_server'
    },
    'response_mode': 'blocking',
    'user': 'test_user_123'
}

print("\nSending test request...")
response = requests.post(DIFY_API_URL, headers=headers, json=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")