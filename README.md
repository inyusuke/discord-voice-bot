# Discord Voice Message Transfer Bot

Discordのボイスメモ（音声メッセージ）を自動でDifyに転送するBotです。

## 機能
- 音声メッセージの自動検出
- Dify APIへの音声ファイル転送
- メタデータ（送信者、チャンネル、サーバー情報）の付与
- 対応形式: .ogg, .mp3, .wav, .m4a, .webm

## 使い方
1. BotをDiscordサーバーに招待
2. チャンネルに音声メッセージを送信
3. Botが自動的にDifyに転送
4. 処理結果が返信として表示

## コマンド一覧
- `!test` - Bot動作確認とAPI設定状況の表示
- `!help_voice` - ヘルプ表示

## セットアップ
詳細は以下のドキュメントを参照：
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 基本的なセットアップ
- [DIFY_SETUP.md](DIFY_SETUP.md) - Difyワークフローの設定
- [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) - Google Drive経由での複数PC開発

## 必要な環境変数
`.env.example`をコピーして`.env`を作成し、以下を設定：
- `DISCORD_TOKEN` - Discord Botトークン
- `DIFY_API_URL` - Dify APIエンドポイント
- `DIFY_API_KEY` - Dify APIキー

## 備考
- 音声の文字起こし処理はDify側で実装されます
- BotはDiscordとDifyの橋渡し役として機能します

## デプロイ
Renderでホスティング中（Starter $7/月）

## 開発状況
[PROJECT_STATUS.md](PROJECT_STATUS.md)を参照