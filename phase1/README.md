# Discord Voice Transcription Bot - Phase 1

## 概要
Discord音声メッセージを自動的に文字起こしするシンプルなBot。OpenAI Whisper APIを使用（Dify経由）。

## 機能
- 🎙️ Discord音声メッセージの自動検出
- 📝 リアルタイム文字起こし（OpenAI Whisper使用）
- 📊 メタデータ表示（送信者、チャンネル情報）
- ⚡ 高速レスポンス（Difyワークフロー経由）

## 対応フォーマット
- .ogg, .mp3, .wav, .m4a, .webm

## セットアップ

### 1. 環境変数の設定（.env）
```env
DISCORD_TOKEN=your_discord_bot_token
DIFY_API_URL=https://api.dify.ai/v1/workflows/run
DIFY_API_KEY=your_dify_api_key
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. Botの起動
```bash
python bot.py
```

## コマンド
- `!test` - Bot動作確認とAPI設定状況の表示
- `!help_voice` - ヘルプ表示

## ファイル構成
- `bot.py` - メインのBotファイル
- `requirements.txt` - Python依存関係
- `runtime.txt` - Python バージョン指定（3.11.9）
- `Procfile` - Render用設定
- `render.yaml` - Renderデプロイ設定

## 技術スタック
- Python 3.11.9
- discord.py 2.x
- requests
- Dify API

## 備考
- Phase 1は基本的な音声文字起こし機能のみ
- より高度な機能はPhase 2で実装