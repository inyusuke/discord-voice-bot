import aiosqlite
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from utils.logger import setup_logger

class Database:
    """SQLiteデータベース管理クラス"""
    
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path
        self.logger = setup_logger('Database')
        
    async def initialize(self):
        """データベースの初期化とテーブル作成"""
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # ユーザー情報テーブル
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    premium_status INTEGER DEFAULT 0,
                    daily_usage INTEGER DEFAULT 0,
                    total_usage INTEGER DEFAULT 0,
                    last_reset TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 文字起こし履歴テーブル
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    user_id TEXT,
                    guild_id TEXT,
                    channel_id TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    duration REAL,
                    transcription TEXT,
                    summary TEXT,
                    language TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # リアクション履歴テーブル
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reaction_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription_id INTEGER,
                    user_id TEXT,
                    reaction TEXT,
                    action_type TEXT,
                    result TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # 統計情報テーブル
            await db.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT,
                    guild_id TEXT,
                    total_transcriptions INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    PRIMARY KEY (date, guild_id)
                )
            """)
            
            await db.commit()
            self.logger.info("Database initialized successfully")
    
    # ユーザー管理
    async def get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        """ユーザーを取得または作成"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 既存ユーザーを確認
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()
            
            if user:
                return dict(user)
            
            # 新規ユーザーを作成
            await db.execute(
                "INSERT INTO users (user_id, last_reset) VALUES (?, ?)",
                (user_id, datetime.now().date().isoformat())
            )
            await db.commit()
            
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()
            return dict(user)
    
    async def check_and_reset_daily_usage(self, user_id: str) -> None:
        """日次使用量をリセット（必要な場合）"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT last_reset FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            
            if result:
                last_reset = datetime.fromisoformat(result[0]).date()
                today = datetime.now().date()
                
                if last_reset < today:
                    await db.execute(
                        "UPDATE users SET daily_usage = 0, last_reset = ? WHERE user_id = ?",
                        (today.isoformat(), user_id)
                    )
                    await db.commit()
    
    async def increment_usage(self, user_id: str) -> int:
        """使用回数を増やして現在の日次使用量を返す"""
        await self.check_and_reset_daily_usage(user_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE users 
                   SET daily_usage = daily_usage + 1, 
                       total_usage = total_usage + 1 
                   WHERE user_id = ?""",
                (user_id,)
            )
            await db.commit()
            
            cursor = await db.execute(
                "SELECT daily_usage FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    # 文字起こし履歴
    async def save_transcription(self, message_id: str, user_id: str, 
                               guild_id: Optional[str], channel_id: str,
                               file_name: str, file_size: int,
                               transcription: str, language: str = "ja") -> int:
        """文字起こし結果を保存"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO transcriptions 
                   (message_id, user_id, guild_id, channel_id, file_name, 
                    file_size, transcription, language)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (message_id, user_id, guild_id, channel_id, file_name, 
                 file_size, transcription, language)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_transcription_by_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """メッセージIDから文字起こしを取得"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transcriptions WHERE message_id = ?",
                (message_id,)
            )
            result = await cursor.fetchone()
            return dict(result) if result else None
    
    async def update_transcription_summary(self, transcription_id: int, summary: str):
        """文字起こしに要約を追加"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE transcriptions SET summary = ? WHERE id = ?",
                (summary, transcription_id)
            )
            await db.commit()
    
    # リアクション履歴
    async def save_reaction_action(self, transcription_id: int, user_id: str,
                                 reaction: str, action_type: str, result: str):
        """リアクションアクションを保存"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO reaction_actions 
                   (transcription_id, user_id, reaction, action_type, result)
                   VALUES (?, ?, ?, ?, ?)""",
                (transcription_id, user_id, reaction, action_type, result)
            )
            await db.commit()
    
    # 統計情報
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """ユーザーの統計情報を取得"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # ユーザー情報
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()
            
            if not user:
                return {}
            
            # 今月の統計
            first_day = datetime.now().replace(day=1).date().isoformat()
            cursor = await db.execute(
                """SELECT COUNT(*) as monthly_count, 
                          SUM(file_size) as total_size
                   FROM transcriptions 
                   WHERE user_id = ? AND date(created_at) >= ?""",
                (user_id, first_day)
            )
            monthly_stats = await cursor.fetchone()
            
            # よく使うチャンネル
            cursor = await db.execute(
                """SELECT channel_id, COUNT(*) as count 
                   FROM transcriptions 
                   WHERE user_id = ? 
                   GROUP BY channel_id 
                   ORDER BY count DESC 
                   LIMIT 3""",
                (user_id,)
            )
            top_channels = await cursor.fetchall()
            
            return {
                'user': dict(user),
                'monthly_count': monthly_stats['monthly_count'] or 0,
                'total_size_mb': (monthly_stats['total_size'] or 0) / 1024 / 1024,
                'top_channels': [dict(ch) for ch in top_channels]
            }
    
    async def get_guild_stats(self, guild_id: str, days: int = 30) -> Dict[str, Any]:
        """ギルドの統計情報を取得"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # 全体統計
            cursor = await db.execute(
                """SELECT COUNT(*) as total_count,
                          COUNT(DISTINCT user_id) as unique_users,
                          SUM(file_size) as total_size,
                          AVG(LENGTH(transcription)) as avg_length
                   FROM transcriptions 
                   WHERE guild_id = ? AND date(created_at) >= ?""",
                (guild_id, since_date)
            )
            overall = await cursor.fetchone()
            
            # 日別統計
            cursor = await db.execute(
                """SELECT date(created_at) as date, 
                          COUNT(*) as count
                   FROM transcriptions 
                   WHERE guild_id = ? AND date(created_at) >= ?
                   GROUP BY date(created_at)
                   ORDER BY date DESC""",
                (guild_id, since_date)
            )
            daily_stats = await cursor.fetchall()
            
            # アクティブユーザー
            cursor = await db.execute(
                """SELECT user_id, COUNT(*) as count 
                   FROM transcriptions 
                   WHERE guild_id = ? AND date(created_at) >= ?
                   GROUP BY user_id 
                   ORDER BY count DESC 
                   LIMIT 10""",
                (guild_id, since_date)
            )
            top_users = await cursor.fetchall()
            
            return {
                'total_transcriptions': overall['total_count'] or 0,
                'unique_users': overall['unique_users'] or 0,
                'total_size_mb': (overall['total_size'] or 0) / 1024 / 1024,
                'avg_transcription_length': int(overall['avg_length'] or 0),
                'daily_stats': [dict(d) for d in daily_stats],
                'top_users': [dict(u) for u in top_users]
            }