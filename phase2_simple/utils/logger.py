import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = 'bot.log', level: int = logging.INFO) -> logging.Logger:
    """
    カスタムロガーのセットアップ
    
    Args:
        name: ロガー名
        log_file: ログファイル名
        level: ログレベル
    
    Returns:
        設定済みのロガー
    """
    # ログディレクトリの作成
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # ロガーの作成
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラーをクリア
    logger.handlers = []
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ファイルハンドラー（ローテーション付き）
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_command_usage(logger: logging.Logger, ctx, command_name: str):
    """コマンド使用のログ"""
    logger.info(
        f"Command used: {command_name} | "
        f"User: {ctx.author.name}#{ctx.author.discriminator} | "
        f"Guild: {ctx.guild.name if ctx.guild else 'DM'} | "
        f"Channel: {ctx.channel.name if hasattr(ctx.channel, 'name') else 'DM'}"
    )

def log_voice_processing(logger: logging.Logger, message, attachment):
    """音声処理のログ"""
    logger.info(
        f"Voice processing started | "
        f"File: {attachment.filename} | "
        f"Size: {attachment.size / 1024:.2f}KB | "
        f"User: {message.author.name} | "
        f"Guild: {message.guild.name if message.guild else 'DM'}"
    )

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """エラーのログ"""
    logger.error(
        f"Error occurred {context} | "
        f"Type: {type(error).__name__} | "
        f"Message: {str(error)}",
        exc_info=True
    )