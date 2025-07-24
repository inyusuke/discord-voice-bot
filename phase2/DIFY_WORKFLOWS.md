# Dify ワークフロー設定ガイド - Phase 2

Phase 2で必要なDifyワークフローの設定方法を説明します。

## 必要なワークフロー

### 1. 音声文字起こし + 要約ワークフロー

**ワークフロー名**: `voice-transcribe-summarize`

**構成**:
1. **File Upload** (Input)
   - Type: Audio
   - Variable name: `audio_file`

2. **Speech to Text** (OpenAI Whisper)
   - Model: `whisper-1`
   - Input: `audio_file`
   - Output variable: `transcription`

3. **Text Summary** (GPT-4)
   - Prompt:
   ```
   以下の文字起こしテキストを簡潔に要約してください。
   重要なポイントを3-5個の箇条書きで示してください。
   
   文字起こしテキスト:
   {{transcription}}
   ```
   - Output variable: `summary`

4. **Output**
   - `transcription`: 文字起こしテキスト
   - `summary`: 要約結果

### 2. テキスト翻訳ワークフロー

**ワークフロー名**: `text-translation`

**構成**:
1. **Text Input**
   - Variable name: `source_text`
   - Variable name: `target_language` (デフォルト: "English")

2. **Translation** (GPT-4)
   - Prompt:
   ```
   以下のテキストを{{target_language}}に翻訳してください。
   自然で読みやすい翻訳を心がけてください。
   
   原文:
   {{source_text}}
   ```
   - Output variable: `translation`

3. **Output**
   - `translation`: 翻訳結果

### 3. 議事録生成ワークフロー（将来実装用）

**ワークフロー名**: `meeting-notes-generator`

**構成**:
1. **Text Input**
   - Variable name: `transcription`

2. **Meeting Notes Generation** (GPT-4)
   - Prompt:
   ```
   以下の文字起こしテキストから議事録を作成してください。
   
   含めるべき項目:
   - 日時・参加者（もしあれば）
   - 議題
   - 主な議論内容
   - 決定事項
   - アクションアイテム
   - 次回の予定
   
   文字起こしテキスト:
   {{transcription}}
   ```
   - Output variable: `meeting_notes`

3. **Output**
   - `meeting_notes`: 議事録

## API設定

### ワークフローAPI設定

各ワークフローで以下の設定を行ってください：

1. **APIアクセスを有効化**
   - ワークフロー設定 → API Access → Enable

2. **APIキーの生成**
   - 各ワークフロー用に個別のAPIキーを生成
   - 環境変数に追加:
   ```
   DIFY_TRANSCRIBE_API_KEY=xxx
   DIFY_TRANSLATE_API_KEY=xxx
   DIFY_MEETING_API_KEY=xxx
   ```

3. **エンドポイント**
   - 基本URL: `https://api.dify.ai/v1/workflows/run`
   - 各ワークフローIDを環境変数に追加

## コード実装例

```python
# services/dify_service.py への追加

async def transcribe_and_summarize(self, file_data: bytes, filename: str, 
                                  content_type: str, user_info: Dict[str, str]) -> Dict[str, str]:
    """音声ファイルを文字起こしして要約"""
    # 新しいワークフローエンドポイントを使用
    workflow_url = os.getenv('DIFY_TRANSCRIBE_SUMMARIZE_URL')
    api_key = os.getenv('DIFY_TRANSCRIBE_API_KEY')
    
    # ファイルアップロードと実行
    # ... 実装
    
    return {
        'transcription': result['outputs']['transcription'],
        'summary': result['outputs']['summary']
    }

async def translate_text(self, text: str, target_language: str = "English") -> str:
    """テキストを翻訳"""
    workflow_url = os.getenv('DIFY_TRANSLATE_URL')
    api_key = os.getenv('DIFY_TRANSLATE_API_KEY')
    
    # ワークフロー実行
    # ... 実装
    
    return result['outputs']['translation']
```

## テスト方法

1. **Difyプレイグラウンドでテスト**
   - 各ワークフローをプレイグラウンドで実行
   - 期待する出力が得られることを確認

2. **API経由でテスト**
   ```bash
   curl -X POST https://api.dify.ai/v1/workflows/run \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "inputs": {
         "source_text": "こんにちは",
         "target_language": "English"
       },
       "user": "test"
     }'
   ```

## 注意事項

- 各ワークフローで使用するモデルの料金を確認
- レート制限に注意（必要に応じてアップグレード）
- エラーハンドリングを適切に実装
- ワークフローの実行時間を監視