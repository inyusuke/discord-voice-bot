# Discord Voice Transcription Bot - プロジェクトステータス

## 概要
Discord音声メッセージ転送Botの開発プロジェクト。Discordのボイスメモを自動でDifyに転送し、Dify側で文字起こし処理を行う。

## Phase 1 完了（2025年1月24日）

### 完了済み
- ✅ Discord Bot基本機能の実装
- ✅ GitHubリポジトリへのアップロード（https://github.com/yuin15/discord-voice-bot）※リポジトリ移動
- ✅ Renderでのデプロイ（Starter $7/月プラン）
- ✅ Bot動作確認（!testコマンド）
- ✅ 音声メッセージ自動検出機能の実装
- ✅ 音声ファイルのダウンロード処理
- ✅ Difyワークフロー作成（Speech to Text）
- ✅ ワークフローAPI統合実装

### 実装済み機能
1. 音声メッセージの自動検出
2. 音声ファイルのダウンロード
3. Dify APIへの音声ファイル転送
4. メタデータ（送信者、チャンネル、サーバー情報）の付与
5. `!test` - Bot動作確認とAPI設定状況表示
6. `!help_voice` - ヘルプ表示

### 必要な環境変数
- `DISCORD_TOKEN` - Discord Botトークン（設定済み）
- `DIFY_API_URL` - Dify APIエンドポイント（未設定）
- `DIFY_API_KEY` - Dify APIキー（未設定）

### 技術スタック
- Python 3.11.9
- discord.py 2.x
- requests
- Dify API
- Render（ホスティング）

### Phase 1 成果物
- 音声メッセージの自動文字起こし機能
- Difyワークフローとの完全な統合
- Renderでの安定稼働
- エラーハンドリングの実装

### Phase 2 候補（将来の拡張）
1. 長い音声の要約機能
2. 多言語対応（自動言語検出）
3. 文字起こし結果のデータベース保存
4. 特定キーワードへの自動反応
5. ユーザーごとの利用統計

### トラブルシューティング
- Python 3.13での`audioop`モジュールエラー → Python 3.11で解決
- Privileged Intents エラー → Developer PortalでMESSAGE CONTENT INTENT有効化で解決
- 401エラー: APIキーの不一致 → Render環境変数の更新で解決
- 404エラー: APIエンドポイントの形式 → `/workflows/run`を使用
- ファイルパラメータエラー → `files`を配列として`inputs`の外に配置

### 重要なファイル
- `bot.py` - メインのBotファイル（Discord→Dify転送専用）
- `requirements.txt` - 依存関係
- `runtime.txt` - Python バージョン指定
- `.env` - 環境変数（Gitignore対象）
- `render.yaml` - Render設定
- `DIFY_SETUP.md` - Difyワークフロー設定ガイド

### 備考
- 音声文字起こしの実際の処理はDify側のワークフローで実装
- Botはシンプルなブリッジとして機能