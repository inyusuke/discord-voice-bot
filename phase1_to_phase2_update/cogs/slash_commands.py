import discord
from discord import app_commands
from discord.ext import commands
from utils.logger import setup_logger, log_command_usage

class SlashCommands(commands.Cog):
    """スラッシュコマンドの実装"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = setup_logger('SlashCommands')
    
    @app_commands.command(name="voice_help", description="Voice Botのヘルプを表示")
    async def voice_help(self, interaction: discord.Interaction):
        """ヘルプコマンド"""
        log_command_usage(self.logger, interaction, "voice_help")
        
        embed = discord.Embed(
            title="🎙️ Voice Transcription Bot - ヘルプ",
            description="Discord音声メッセージを自動で文字起こしするBotです",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📌 基本的な使い方",
            value=(
                "1. 音声メッセージを録音・送信\n"
                "2. Botが自動的に文字起こし\n"
                "3. 結果が返信として表示\n"
                "4. リアクションで追加機能を利用"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 リアクション機能",
            value=(
                "📝 - 文字起こし結果を要約\n"
                "🌐 - 英語に翻訳"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 対応フォーマット",
            value=".ogg, .mp3, .wav, .m4a, .webm",
            inline=True
        )
        
        embed.add_field(
            name="🔧 スラッシュコマンド",
            value=(
                "`/voice_help` - このヘルプを表示\n"
                "`/voice_test` - Bot動作確認"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="voice_test", description="Botの動作確認")
    async def voice_test(self, interaction: discord.Interaction):
        """動作確認コマンド"""
        log_command_usage(self.logger, interaction, "voice_test")
        
        # API設定確認
        voice_handler = self.bot.get_cog('VoiceHandler')
        dify_configured = False
        if voice_handler and voice_handler.dify_service:
            dify_configured = bool(voice_handler.dify_service.api_url and 
                                 voice_handler.dify_service.api_key)
        
        embed = discord.Embed(
            title="✅ Bot動作確認",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Bot状態",
            value="✅ オンライン",
            inline=True
        )
        
        embed.add_field(
            name="Dify API",
            value="✅ 設定済み" if dify_configured else "❌ 未設定",
            inline=True
        )
        
        embed.add_field(
            name="レイテンシ",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="バージョン",
            value="Phase 2 Simple (データベースなし版)",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    await bot.add_cog(SlashCommands(bot))