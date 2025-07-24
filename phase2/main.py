import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.logger import setup_logger
from utils.database import Database
import json

# 環境変数の読み込み
load_dotenv()

# ロガーのセットアップ
logger = setup_logger('VoiceBot')

class VoiceBot(commands.Bot):
    """カスタムBotクラス"""
    
    def __init__(self):
        # 設定の読み込み
        with open('config/settings.json', 'r') as f:
            self.settings = json.load(f)
        
        # Intentsの設定
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description=self.settings['bot']['name']
        )
        
        # 従来のヘルプコマンドを削除
        self.remove_command('help')
        
        # データベースの初期化
        self.database = Database()
    
    async def setup_hook(self):
        """Bot起動時のセットアップ"""
        # データベースの初期化
        await self.database.initialize()
        
        # Cogsの読み込み
        cogs = [
            'cogs.voice_handler',
            'cogs.reaction_handler',
            'cogs.slash_commands'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {str(e)}")
        
        # スラッシュコマンドの同期
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {str(e)}")
    
    async def on_ready(self):
        """Bot準備完了時"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot version: {self.settings["bot"]["version"]}')
        logger.info(f'Phase: {self.settings["bot"]["phase"]}')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # ステータスの設定
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="音声メッセージ | /voice_help"
            )
        )

async def main():
    """メイン関数"""
    # Botトークンの確認
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    # Botの作成と起動
    bot = VoiceBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
    finally:
        await bot.close()
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    # Windows環境でのイベントループポリシー設定
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Botの実行
    asyncio.run(main())