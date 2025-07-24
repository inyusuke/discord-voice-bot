# Discord Voice Bot - Phase 2 設計書

## 概要
ai-keisukeの優れた設計パターンを参考に、discord-voice-botを高機能な音声処理Botへと進化させる。

## Phase 2の主要機能

### 1. リアクションベースの拡張機能
音声メッセージに対してリアクションを追加することで、追加の処理を実行する。

#### 実装するリアクション機能
- 📝 **文字起こし＋要約**: 長い音声の要点をまとめる
- 🌐 **多言語翻訳**: 文字起こし結果を指定言語に翻訳
- 📋 **議事録作成**: 会議音声から構造化された議事録を生成
- 🔍 **アクションアイテム抽出**: TODOやタスクを自動抽出
- 💬 **スレッド作成**: 文字起こし結果を新規スレッドで共有
- 📊 **感情分析**: 話者の感情や雰囲気を分析

### 2. モジュール化されたアーキテクチャ

```
discord-voice-bot/
├── bot.py                 # メインエントリーポイント
├── cogs/                  # Discord.py Cogs
│   ├── voice_handler.py   # 音声処理
│   ├── reaction_handler.py # リアクション処理
│   └── slash_commands.py  # スラッシュコマンド
├── services/              # ビジネスロジック
│   ├── dify_service.py    # Dify API連携
│   ├── transcription.py   # 文字起こし処理
│   └── analytics.py       # 分析機能
├── utils/                 # ユーティリティ
│   ├── logger.py          # ロギング設定
│   ├── permissions.py     # 権限管理
│   └── rate_limiter.py    # レート制限
├── prompts/               # AIプロンプト
│   ├── summary.txt        # 要約用
│   ├── meeting_notes.txt  # 議事録用
│   └── translation.txt    # 翻訳用
├── config/                # 設定ファイル
│   ├── settings.json      # アプリ設定
│   └── reactions.json     # リアクション設定
└── data/                  # データ保存
    ├── transcripts/       # 文字起こし履歴
    └── analytics/         # 統計データ
```

### 3. スラッシュコマンド

#### 基本コマンド
- `/voice help` - ヘルプとガイド表示
- `/voice stats` - 利用統計表示
- `/voice history` - 文字起こし履歴

#### 設定コマンド
- `/voice config language [言語]` - デフォルト言語設定
- `/voice config auto_transcribe [on/off]` - 自動文字起こし
- `/voice config reactions [on/off]` - リアクション機能

#### 管理コマンド（管理者のみ）
- `/voice admin limits` - 利用制限設定
- `/voice admin premium @user` - プレミアムユーザー設定
- `/voice admin stats` - サーバー全体の統計

### 4. データベース設計

#### SQLiteを使用したローカルDB
```sql
-- ユーザー情報
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    premium_status BOOLEAN DEFAULT 0,
    daily_usage INTEGER DEFAULT 0,
    total_usage INTEGER DEFAULT 0,
    last_reset DATE
);

-- 文字起こし履歴
CREATE TABLE transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE,
    user_id TEXT,
    guild_id TEXT,
    channel_id TEXT,
    file_name TEXT,
    transcription TEXT,
    summary TEXT,
    language TEXT,
    duration REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- リアクション履歴
CREATE TABLE reaction_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcription_id INTEGER,
    reaction TEXT,
    action_type TEXT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id)
);
```

### 5. 高度な機能

#### A. インテリジェントな要約
- 音声の長さに応じて要約レベルを自動調整
- キーポイントの箇条書き
- 重要な数値や日付の強調表示

#### B. コンテキスト認識
- チャンネル名から会議タイプを推測
- 過去の文字起こしを参照して文脈を理解
- 専門用語の学習と適用

#### C. 通知システム
- 特定キーワードが含まれる場合に通知
- メンション（@ユーザー名）の検出と通知
- 緊急度の自動判定

### 6. パフォーマンスとスケーラビリティ

#### 非同期処理の最適化
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncVoiceProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_voice_batch(self, voice_messages):
        """複数の音声を並列処理"""
        tasks = []
        for msg in voice_messages:
            task = asyncio.create_task(self.process_single_voice(msg))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

#### キャッシング戦略
- 頻繁に使用されるプロンプトのキャッシュ
- 文字起こし結果の一時キャッシュ
- ユーザー設定のメモリキャッシュ

### 7. セキュリティとプライバシー

#### データ保護
- 文字起こしデータの暗号化保存
- 一定期間後の自動削除オプション
- GDPR準拠のデータエクスポート機能

#### アクセス制御
- サーバーごとの機能有効/無効設定
- チャンネル別のBot権限設定
- ユーザーブロックリスト

### 8. 実装ロードマップ

#### Phase 2.1（2週間）
- [ ] プロジェクト構造のリファクタリング
- [ ] 基本的なリアクション機能（📝要約）
- [ ] ロギングとエラーハンドリングの強化

#### Phase 2.2（2週間）
- [ ] データベース実装
- [ ] スラッシュコマンドの追加
- [ ] 利用統計機能

#### Phase 2.3（3週間）
- [ ] 全リアクション機能の実装
- [ ] 多言語対応
- [ ] パフォーマンス最適化

#### Phase 2.4（1週間）
- [ ] テストとバグ修正
- [ ] ドキュメント整備
- [ ] デプロイとモニタリング

## 技術スタック

### 必須
- Python 3.11+
- discord.py 2.x
- aiohttp（非同期HTTP）
- aiosqlite（非同期SQLite）
- python-dotenv

### オプション
- Redis（キャッシング用）
- Prometheus（メトリクス）
- Sentry（エラートラッキング）

## 移行計画

1. 現在のbot.pyをバックアップ
2. 新構造でプロジェクトを再構築
3. 既存機能を新構造に移植
4. 段階的に新機能を追加
5. 本番環境でのA/Bテスト

## 成功指標

- 平均処理時間: 5秒以内
- エラー率: 1%未満
- ユーザー満足度: 90%以上
- 日次アクティブユーザー: 100+