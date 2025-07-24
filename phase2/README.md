# Discord Voice Bot - Phase 2

## 🎉 Phase 2.2 実装完了（2025年1月）

### Phase 2.1の機能
1. **プロジェクト構造のリファクタリング**
   - モジュール化されたアーキテクチャ
   - Cogs、Services、Utils層の分離

2. **基本的なリアクション機能**
   - 📝 要約機能
   - 🌐 翻訳機能

3. **ロギングとエラーハンドリング**
   - ローテーション付きログ
   - 詳細なエラー追跡

### Phase 2.2の新機能
1. **SQLiteデータベース実装** ✅
   - ユーザー管理と利用制限
   - 文字起こし履歴の保存
   - リアクション履歴の記録
   - 統計情報の集計

2. **拡張スラッシュコマンド** ✅
   - `/voice_help` - ヘルプ表示
   - `/voice_test` - 動作確認
   - `/voice_stats` - 個人統計表示
   - `/voice_server_stats` - サーバー統計（管理者用）

3. **利用統計機能** ✅
   - 日次/月次の利用状況
   - チャンネル別統計
   - アクティブユーザーランキング

4. **Difyワークフロー対応** ✅
   - 要約機能（簡易版実装済み）
   - 翻訳機能（簡易版実装済み）
   - ワークフロー設計ドキュメント作成

## 📁 プロジェクト構造

```
phase2/
├── main.py                 # エントリーポイント
├── cogs/                   # Discord.py Cogs
│   ├── voice_handler.py    # 音声処理（DB連携追加）
│   ├── reaction_handler.py # リアクション処理（DB連携追加）
│   └── slash_commands.py   # スラッシュコマンド（統計追加）
├── services/               # ビジネスロジック
│   └── dify_service.py     # Dify API連携（要約・翻訳追加）
├── utils/                  # ユーティリティ
│   ├── logger.py           # ロギング
│   ├── permissions.py      # 権限管理
│   └── database.py         # データベース管理（新規）
├── config/                 # 設定ファイル
├── data/                   # データ保存
│   ├── bot.db             # SQLiteデータベース（自動生成）
│   └── transcripts/        # 文字起こし保存用
├── prompts/                # AIプロンプト
├── DIFY_WORKFLOWS.md       # Difyワークフロー設定ガイド
└── requirements.txt        # 依存関係
```

## 🚀 セットアップ

### 1. 環境準備
```bash
cd phase2
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
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

初回起動時に以下が自動生成されます：
- SQLiteデータベース（data/bot.db）
- 権限設定（config/permissions.json）
- リアクション設定（config/reactions.json）

## 📝 使い方

### 基本機能
1. **音声文字起こし**
   - 音声メッセージを送信すると自動で文字起こし
   - 対応形式: .ogg, .mp3, .wav, .m4a, .webm
   - 利用制限: 無料ユーザー10回/日、プレミアム無制限

2. **リアクション機能**
   - 📝 → 文字起こし結果を要約してDMで送信
   - 🌐 → 英語に翻訳してDMで送信

### スラッシュコマンド
- `/voice_help` - 使い方を表示
- `/voice_test` - Bot状態確認
- `/voice_stats` - あなたの利用統計
- `/voice_server_stats` - サーバー全体の統計（管理者のみ）

## 🔧 設定

### プレミアムユーザー設定
`config/permissions.json`を編集：
```json
{
  "premium_roles": ["Premium", "VIP", "Supporter"],
  "daily_limits": {
    "free": 10,
    "premium": -1
  }
}
```

### リアクション機能の有効/無効
`config/reactions.json`を編集：
```json
{
  "📝": {
    "enabled": true
  },
  "🌐": {
    "enabled": true
  }
}
```

## 📊 データベース情報

### テーブル構造
- **users**: ユーザー情報と利用制限
- **transcriptions**: 文字起こし履歴
- **reaction_actions**: リアクション使用履歴
- **daily_stats**: 日別統計

### データ保存期間
- 文字起こし履歴: 無期限
- 統計情報: 最新30日分を表示

## 🚧 今後の開発予定（Phase 2.3）

1. **Difyワークフロー統合**
   - 高度な要約機能
   - 多言語翻訳
   - 議事録生成

2. **追加機能**
   - 音声ファイルの自動削除オプション
   - エクスポート機能
   - Webhookサポート

## 🐛 トラブルシューティング

### よくある問題
1. **「利用制限に達しました」エラー**
   - 無料ユーザーは1日10回まで
   - 日本時間0時にリセット

2. **データベースエラー**
   - `data/`フォルダの書き込み権限を確認
   - `bot.db`を削除して再起動

3. **DM送信エラー**
   - ユーザーのDM設定を確認
   - サーバーメンバーからのDMを許可

## 📄 ライセンス

MIT License