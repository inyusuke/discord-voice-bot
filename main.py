import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.logger import setup_logger
import json

# 環境変数の読み込み
load_dotenv()

# ロガーのセットアップ
logger = setup_logger('VoiceBot')

class VoiceBot(commands.Bot):
    """シンプル版Bot（データベースなし）"""
    
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
    
    async def setup_hook(self):
        """Bot起動時のセットアップ"""
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
                logger.error(f"Failed to load cog {cog}: {e}")
        
        # スラッシュコマンドの同期
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
    
    async def on_ready(self):
        """Bot準備完了時のイベント"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot version: {self.settings["bot"]["version"]}')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # ステータスの設定
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="音声メッセージ"
            )
        )

async def main():
    """メイン関数"""
    # Discord Tokenの確認
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return
    
    # Botインスタンスの作成
    bot = VoiceBot()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())