import requests
import json
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

DIFY_API_KEY = os.getenv('DIFY_API_KEY')

print(f"API Key: {DIFY_API_KEY[:15]}...")

# 最もシンプルなテスト（ファイルなし）
url = "https://api.dify.ai/v1/workflows/run"
headers = {
    'Authorization': f'Bearer {DIFY_API_KEY}',
    'Content-Type': 'application/json'
}

data = {
    'inputs': {
        'username': 'test_user',
        'channel': 'test_channel',
        'server': 'test_server'
    },
    'response_mode': 'blocking',
    'user': 'test_123'
}

print(f"\nURL: {url}")
print(f"Headers: {headers}")
print(f"Data: {json.dumps(data, indent=2)}")

print("\nSending request...")
response = requests.post(url, headers=headers, json=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Text: {response.text}")

# もし401エラーの場合、別の認証方法を試す
if response.status_code == 401:
    print("\n\n=== Trying with different auth header ===")
    headers2 = {
        'Authorization': f'{DIFY_API_KEY}',  # Bearerなし
        'Content-Type': 'application/json'
    }
    response2 = requests.post(url, headers=headers2, json=data)
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.text[:500]}")