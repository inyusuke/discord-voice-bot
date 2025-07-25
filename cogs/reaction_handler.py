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
        self.logger.info(f"Extracted transcription text: {transcription[:100] if transcription else 'None'}")
        
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
        
        # OpenAIServiceで要約を生成
        voice_handler = self.bot.get_cog('VoiceHandler')
        self.logger.info(f"VoiceHandler found: {voice_handler is not None}")
        
        if voice_handler and voice_handler.openai_service:
            self.logger.info(f"OpenAI service found, API key exists: {voice_handler.openai_service.api_key is not None}")
            self.logger.info(f"Generating summary for text: {transcription[:50]}...")
            
            try:
                summary = voice_handler.openai_service.summarize_text(transcription)
                if not summary:
                    summary = "要約の生成に失敗しました。"
                    self.logger.error("Summary generation returned None")
                else:
                    self.logger.info(f"Summary generated successfully: {summary[:50]}...")
            except Exception as e:
                summary = f"要約生成中にエラーが発生しました: {str(e)}"
                self.logger.error(f"Error in summarize_text: {str(e)}")
        else:
            summary = "要約サービスが利用できません。"
            self.logger.error(f"OpenAI service not available - VoiceHandler: {voice_handler}, OpenAI service: {voice_handler.openai_service if voice_handler else 'N/A'}")
        
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
            self.logger.info(f"Summary sent to user {user_id}")
        except discord.Forbidden:
            self.logger.warning(f"Failed to send DM to user {user_id} - DMs disabled")
            await message.reply(f"{user.mention} 要約結果をDMで送信しようとしましたが、DMを受け取る設定になっていません。", delete_after=10)
        except Exception as e:
            self.logger.error(f"Error sending summary: {str(e)}")
            await message.reply(f"エラーが発生しました: {str(e)}", delete_after=10)
    
    async def translate_transcription(self, message: discord.Message, transcription: str, user_id: int):
        """文字起こし結果を翻訳"""
        user = self.bot.get_user(user_id)
        if not user:
            return
        
        # OpenAIServiceで翻訳
        voice_handler = self.bot.get_cog('VoiceHandler')
        self.logger.info(f"VoiceHandler found: {voice_handler is not None}")
        
        if voice_handler and voice_handler.openai_service:
            self.logger.info(f"OpenAI service found, API key exists: {voice_handler.openai_service.api_key is not None}")
            self.logger.info(f"Generating translation for text: {transcription[:50]}...")
            
            try:
                translation = voice_handler.openai_service.translate_text(transcription, "English")
                if not translation:
                    translation = "翻訳の生成に失敗しました。"
                    self.logger.error("Translation generation returned None")
                else:
                    self.logger.info(f"Translation generated successfully: {translation[:50]}...")
            except Exception as e:
                translation = f"翻訳生成中にエラーが発生しました: {str(e)}"
                self.logger.error(f"Error in translate_text: {str(e)}")
        else:
            translation = "翻訳サービスが利用できません。"
            self.logger.error(f"OpenAI service not available - VoiceHandler: {voice_handler}, OpenAI service: {voice_handler.openai_service if voice_handler else 'N/A'}")
        
        # 翻訳結果をDMで送信
        embed = discord.Embed(
            title="🌐 翻訳結果（English）",
            description=translation,
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="元のメッセージ", value=f"[こちら]({message.jump_url})", inline=False)
        embed.set_footer(text="Powered by OpenAI")
        
        try:
            await user.send(embed=embed)
            await message.add_reaction('✅')
            self.logger.info(f"Translation sent to user {user_id}")
        except discord.Forbidden:
            self.logger.warning(f"Failed to send DM to user {user_id} - DMs disabled")
            await message.reply(f"{user.mention} 翻訳結果をDMで送信しようとしましたが、DMを受け取る設定になっていません。", delete_after=10)
        except Exception as e:
            self.logger.error(f"Error sending translation: {str(e)}")
            await message.reply(f"エラーが発生しました: {str(e)}", delete_after=10)

async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    await bot.add_cog(ReactionHandler(bot))