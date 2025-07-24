import requests
import json
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

DIFY_API_KEY = os.getenv('DIFY_API_KEY')

print(f"API Key: {DIFY_API_KEY[:15]}...")

# テスト用の音声ファイルパス（存在する音声ファイルに変更してください）
audio_file_path = "test_audio.wav"  # WAVファイルを使用

# 1. ファイルアップロード
print("\n=== Step 1: Upload audio file ===")
upload_url = "https://api.dify.ai/v1/files/upload"
headers = {
    'Authorization': f'Bearer {DIFY_API_KEY}'
}

# WAVファイルが存在しない場合は作成
if not os.path.exists(audio_file_path):
    print("Creating test WAV file...")
    from create_test_audio import create_test_wav
    create_test_wav(audio_file_path)

with open(audio_file_path, 'rb') as audio_file:
    mime_type = 'audio/wav' if audio_file_path.endswith('.wav') else 'audio/mpeg'
    files = {'file': (audio_file_path, audio_file, mime_type)}
    data = {'user': 'test_123'}
    
    print(f"Uploading file: {audio_file_path}")
    upload_response = requests.post(upload_url, headers=headers, files=files, data=data)
    
    print(f"Upload Status Code: {upload_response.status_code}")
    print(f"Upload Response: {upload_response.text}")
    
    if upload_response.status_code == 201:
        file_id = upload_response.json().get('id')
        print(f"File ID: {file_id}")
        
        # 2. ワークフロー実行（単一ファイルとして）
        print("\n=== Step 2: Execute workflow with single file ===")
        workflow_url = "https://api.dify.ai/v1/workflows/run"
        
        # パターン1: filesをinputsの外に配置（配列として）
        workflow_data = {
            'inputs': {
                'username': 'test_user',
                'channel': 'test_channel',
                'server': 'test_server'
            },
            'files': [{  # 配列として
                'transfer_method': 'local_file',
                'upload_file_id': file_id,
                'type': 'audio'
            }],
            'response_mode': 'blocking',
            'user': 'test_123'
        }
        
        workflow_headers = {
            'Authorization': f'Bearer {DIFY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        print(f"Workflow Data: {json.dumps(workflow_data, indent=2)}")
        
        response = requests.post(workflow_url, headers=workflow_headers, json=workflow_data)
        
        print(f"\nWorkflow Status Code: {response.status_code}")
        print(f"Workflow Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and 'outputs' in result['data']:
                outputs = result['data']['outputs']
                print(f"\nOutputs: {json.dumps(outputs, indent=2, ensure_ascii=False)}")

# クリーンアップ（テストファイルは残す）
print(f"\nTest file '{audio_file_path}' size: {os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0} bytes")