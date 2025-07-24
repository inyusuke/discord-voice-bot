import discord
from discord.ext import commands
import json
import os
from utils.logger import setup_logger

class ReactionHandler(commands.Cog):
    """リアクションベースの機能を処理"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = setup_logger('ReactionHandler')
        self.reaction_config = self._load_reaction_config()
    
    def _load_reaction_config(self) -> dict:
        """リアクション設定を読み込み"""
        config_path = 'config/reactions.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # デフォルト設定
            default = {
                "📝": {
                    "name": "summarize",
                    "description": "文字起こし結果を要約",
                    "enabled": True
                },
                "🌐": {
                    "name": "translate",
                    "description": "英語に翻訳",
                    "enabled": True
                }
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default, f, indent=2)
            return default
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """リアクション追加イベント"""
        # Bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            return
        
        # 設定されたリアクションかチェック
        emoji = str(payload.emoji)
        if emoji not in self.reaction_config:
            return
        
        # リアクション設定が有効かチェック
        reaction_info = self.reaction_config[emoji]
        if not reaction_info.get('enabled', False):
            return
        
        # メッセージを取得
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
            
            # Botのメッセージかチェック
            if message.author != self.bot.user:
                return
            
            # 文字起こし結果のEmbedかチェック
            if not message.embeds or not message.embeds[0].title == "📝 文字起こし結果":
                return
            
            # リアクションを処理
            await self.process_reaction(
                message=message,
                emoji=emoji,
                user_id=payload.user_id,
                reaction_info=reaction_info
            )
            
        except Exception as e:
            self.logger.error(f"Error processing reaction: {str(e)}")
    
    async def process_reaction(self, message: discord.Message, emoji: str, 
                             user_id: int, reaction_info: dict):
        """リアクションに基づいて処理を実行"""
        action = reaction_info['name']
        self.logger.info(f"Processing reaction {emoji} ({action}) from user {user_id}")
        
        # 元の文字起こしテキストを取得
        original_embed = message.embeds[0]
        transcription = original_embed.description
        
        # アクションに応じて処理
        if action == "summarize":
            await self.summarize_transcription(message, transcription, user_id)
        elif action == "translate":
            await self.translate_transcription(message, transcription, user_id)
    
    async def summarize_transcription(self, message: discord.Message, transcription: str, user_id: int):
        """文字起こし結果を要約"""
        user = self.bot.get_user(user_id)
        if not user:
            return
        
        # DifyServiceで要約を生成
        voice_handler = self.bot.get_cog('VoiceHandler')
        if voice_handler and voice_handler.dify_service:
            summary = voice_handler.dify_service._generate_simple_summary(transcription)
        else:
            summary = "要約サービスが利用できません。"
        
        # 要約をDMで送信
        embed = discord.Embed(
            title="📝 要約結果",
            description=summary,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="元のメッセージ", value=f"[こちら]({message.jump_url})", inline=False)
        embed.set_footer(text=f"文字数: {len(transcription)} → {len(summary)}")
        
        try:
            await user.send(embed=embed)
            await message.add_reaction('✅')
        except discord.Forbidden:
            await message.reply(f"{user.mention} 要約結果をDMで送信しようとしましたが、DMを受け取る設定になっていません。", delete_after=10)
    
    async def translate_transcription(self, message: discord.Message, transcription: str, user_id: int):
        """文字起こし結果を翻訳"""
        user = self.bot.get_user(user_id)
        if not user:
            return
        
        # DifyServiceで翻訳
        voice_handler = self.bot.get_cog('VoiceHandler')
        if voice_handler and voice_handler.dify_service:
            translation = await voice_handler.dify_service.translate_text(transcription, "English")
        else:
            translation = "翻訳サービスが利用できません。"
        
        # 翻訳結果をDMで送信
        embed = discord.Embed(
            title="🌐 翻訳結果（English）",
            description=translation,
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="元のメッセージ", value=f"[こちら]({message.jump_url})", inline=False)
        embed.set_footer(text="※ 高度な翻訳機能は開発中です")
        
        try:
            await user.send(embed=embed)
            await message.add_reaction('✅')
        except discord.Forbidden:
            await message.reply(f"{user.mention} 翻訳結果をDMで送信しようとしましたが、DMを受け取る設定になっていません。", delete_after=10)

async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    await bot.add_cog(ReactionHandler(bot))