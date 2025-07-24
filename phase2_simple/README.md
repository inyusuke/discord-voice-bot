# Discord Voice Bot - Phase 2 Simple

SQLiteなし・統計なし・会員管理なしのシンプル版です。

## ✨ 機能

### 基本機能
- 🎙️ 音声メッセージの自動文字起こし
- 📝 リアクションで要約
- 🌐 リアクションで翻訳
- 🔧 スラッシュコマンド

### 削除した機能
- ❌ SQLiteデータベース
- ❌ 利用統計（/voice_stats）
- ❌ 会員管理・利用制限
- ❌ 履歴保存

## 📁 シンプルな構造

```
phase2_simple/
├── main.py              # メインファイル
├── cogs/                # Discord機能
│   ├── voice_handler.py # 音声処理
│   ├── reaction_handler.py # リアクション
│   └── slash_commands.py # コマンド
├── services/            # サービス
│   └── dify_service.py  # Dify API
├── utils/               # ユーティリティ
│   └── logger.py        # ロギング
├── config/              # 設定
│   └── settings.json    # アプリ設定
└── requirements.txt     # 依存関係
```

## 🚀 セットアップ

### 1. 環境準備
```bash
cd phase2_simple
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数（.env）
```env
DISCORD_TOKEN=your_discord_bot_token
DIFY_API_URL=https://api.dify.ai/v1/workflows/run
DIFY_API_KEY=your_dify_api_key
```

### 3. 起動
```bash
python main.py
```

## 📝 使い方

1. **音声を送信** → 自動で文字起こし
2. **📝をリアクション** → 要約をDMで受信
3. **🌐をリアクション** → 翻訳をDMで受信

### スラッシュコマンド
- `/voice_help` - ヘルプ表示
- `/voice_test` - 動作確認

## 🔧 Renderデプロイ

### Procfile
```
worker: python main.py
```

### render.yaml
```yaml
services:
  - type: worker
    name: discord-voice-bot-simple
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
```

## 📌 特徴

- **軽量**: SQLiteなしで軽快動作
- **シンプル**: 必要最小限の機能のみ
- **管理不要**: 会員管理や統計機能なし
- **即使える**: 複雑な設定不要

## ⚡ パフォーマンス

- メモリ使用量: 最小
- 起動時間: 高速
- レスポンス: 即座

これでストレージ不要のシンプルなBotの完成です！