import discord
from discord import app_commands
from discord.ext import commands
from utils.logger import setup_logger, log_command_usage
from utils.permissions import PermissionManager

class SlashCommands(commands.Cog):
    """スラッシュコマンドの実装"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = setup_logger('SlashCommands')
        self.permission_manager = PermissionManager()
    
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
                "🌐 - 英語に翻訳\n"
                "📋 - 議事録形式に整形（開発中）\n"
                "🔍 - アクションアイテム抽出（開発中）"
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
                "`/voice_stats` - 利用統計を表示\n"
                "`/voice_test` - Bot動作確認\n"
                "`/voice_history` - 文字起こし履歴（開発中）\n"
                "`/voice_server_stats` - サーバー統計（管理者用）"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="voice_test", description="Botの動作確認")
    async def voice_test(self, interaction: discord.Interaction):
        """動作確認コマンド"""
        log_command_usage(self.logger, interaction, "voice_test")
        
        # API設定確認
        dify_configured = bool(self.bot.get_cog('VoiceHandler').dify_service.api_url and 
                             self.bot.get_cog('VoiceHandler').dify_service.api_key)
        
        # ユーザー権限確認
        is_premium = False
        is_admin = False
        if interaction.guild and isinstance(interaction.user, discord.Member):
            is_premium = self.permission_manager.is_premium(interaction.user)
            is_admin = self.permission_manager.is_admin(interaction.user)
        
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
        
        if interaction.guild:
            embed.add_field(
                name="あなたの権限",
                value=(
                    f"プレミアム: {'✅' if is_premium else '❌'}\n"
                    f"管理者: {'✅' if is_admin else '❌'}"
                ),
                inline=False
            )
        
        embed.add_field(
            name="バージョン",
            value="Phase 2.1 (開発中)",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="voice_stats", description="利用統計を表示")
    async def voice_stats(self, interaction: discord.Interaction):
        """統計表示コマンド"""
        log_command_usage(self.logger, interaction, "voice_stats")
        
        # データベースから統計を取得
        db = self.bot.database
        user_stats = await db.get_user_stats(str(interaction.user.id))
        
        if not user_stats or not user_stats.get('user'):
            embed = discord.Embed(
                title="📊 利用統計",
                description="まだ音声文字起こしを利用していません。",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_data = user_stats['user']
        
        embed = discord.Embed(
            title="📊 あなたの利用統計",
            color=discord.Color.blue()
        )
        
        # 基本統計
        embed.add_field(
            name="利用状況",
            value=(
                f"本日の利用: {user_data['daily_usage']}回\n"
                f"累計利用: {user_data['total_usage']}回\n"
                f"プレミアム: {'✅' if user_data['premium_status'] else '❌'}"
            ),
            inline=True
        )
        
        # 今月の統計
        embed.add_field(
            name="今月の統計",
            value=(
                f"文字起こし数: {user_stats['monthly_count']}回\n"
                f"処理データ量: {user_stats['total_size_mb']:.1f} MB"
            ),
            inline=True
        )
        
        # よく使うチャンネル
        if user_stats['top_channels']:
            channel_list = []
            for ch in user_stats['top_channels'][:3]:
                channel = self.bot.get_channel(int(ch['channel_id']))
                channel_name = channel.mention if channel else f"<#{ch['channel_id']}>"
                channel_list.append(f"{channel_name}: {ch['count']}回")
            
            embed.add_field(
                name="よく使うチャンネル",
                value="\n".join(channel_list),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="voice_server_stats", description="サーバーの利用統計を表示（管理者用）")
    @app_commands.guild_only()
    async def voice_server_stats(self, interaction: discord.Interaction):
        """サーバー統計表示コマンド（管理者のみ）"""
        log_command_usage(self.logger, interaction, "voice_server_stats")
        
        # 管理者権限チェック
        if not self.permission_manager.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ このコマンドは管理者のみ使用できます。",
                ephemeral=True
            )
            return
        
        # サーバー統計を取得
        db = self.bot.database
        guild_stats = await db.get_guild_stats(str(interaction.guild_id))
        
        embed = discord.Embed(
            title=f"📊 {interaction.guild.name} の統計",
            description="過去30日間の利用統計",
            color=discord.Color.gold()
        )
        
        # 全体統計
        embed.add_field(
            name="全体統計",
            value=(
                f"総文字起こし数: {guild_stats['total_transcriptions']}回\n"
                f"ユニークユーザー: {guild_stats['unique_users']}人\n"
                f"処理データ量: {guild_stats['total_size_mb']:.1f} MB\n"
                f"平均文字数: {guild_stats['avg_transcription_length']}文字"
            ),
            inline=False
        )
        
        # 日別統計（最近7日）
        if guild_stats['daily_stats']:
            daily_text = []
            for day_stat in guild_stats['daily_stats'][:7]:
                daily_text.append(f"{day_stat['date']}: {day_stat['count']}回")
            
            embed.add_field(
                name="最近7日間",
                value="\n".join(daily_text) or "データなし",
                inline=True
            )
        
        # アクティブユーザー
        if guild_stats['top_users']:
            user_text = []
            for i, user_stat in enumerate(guild_stats['top_users'][:5], 1):
                user = self.bot.get_user(int(user_stat['user_id']))
                user_name = user.mention if user else f"User {user_stat['user_id']}"
                user_text.append(f"{i}. {user_name}: {user_stat['count']}回")
            
            embed.add_field(
                name="アクティブユーザー TOP5",
                value="\n".join(user_text),
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    await bot.add_cog(SlashCommands(bot))