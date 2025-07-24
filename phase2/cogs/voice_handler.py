import discord
from discord.ext import commands
import tempfile
import os
from typing import Optional
import aiosqlite
from services.dify_service import DifyService
from utils.logger import setup_logger, log_voice_processing, log_error
from utils.permissions import PermissionManager

class VoiceHandler(commands.Cog):
    """音声メッセージの処理を担当"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dify_service = DifyService()
        self.logger = setup_logger('VoiceHandler')
        self.permission_manager = PermissionManager()
        
        # サポートする音声フォーマット
        self.supported_formats = ('.ogg', '.mp3', '.wav', '.m4a', '.webm')
    
    async def cog_load(self):
        """Cogのロード時に実行"""
        await self.dify_service.initialize()
        self.logger.info("VoiceHandler cog loaded")
    
    async def cog_unload(self):
        """Cogのアンロード時に実行"""
        await self.dify_service.close()
        self.logger.info("VoiceHandler cog unloaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """メッセージイベントのリスナー"""
        # Bot自身のメッセージは無視
        if message.author == self.bot.user:
            return
        
        # ブロックされたユーザーは無視
        if self.permission_manager.is_blocked(message.author.id):
            return
        
        # 音声ファイルの処理
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(self.supported_formats):
                await self.process_voice_message(message, attachment)
    
    async def process_voice_message(self, message: discord.Message, attachment: discord.Attachment):
        """音声メッセージを処理"""
        log_voice_processing(self.logger, message, attachment)
        
        # 処理中メッセージ
        processing_msg = await message.reply('🎙️ 音声を処理中...')
        
        try:
            # 音声ファイルをダウンロード
            file_data = await attachment.read()
            
            # ユーザー情報
            user_info = {
                'user_id': str(message.author.id),
                'username': message.author.name,
                'channel': message.channel.name if hasattr(message.channel, 'name') else 'DM',
                'server': message.guild.name if message.guild else 'DM'
            }
            
            # データベースからユーザー情報を取得/作成
            db = self.bot.database
            user_db = await db.get_or_create_user(str(message.author.id))
            
            # 利用制限チェック
            member = message.guild.get_member(message.author.id) if message.guild else None
            daily_limit = self.permission_manager.get_daily_limit(member)
            
            if daily_limit > 0 and user_db['daily_usage'] >= daily_limit:
                await processing_msg.edit(content='❌ 本日の利用制限に達しました。')
                return
            
            # 文字起こし
            transcription = await self.dify_service.transcribe_audio(
                file_data=file_data,
                filename=attachment.filename,
                content_type=attachment.content_type or 'audio/ogg',
                user_info=user_info
            )
            
            # 処理中メッセージを削除
            await processing_msg.delete()
            
            if transcription:
                # 使用回数を増やす
                await db.increment_usage(str(message.author.id))
                
                # データベースに保存
                transcription_id = await db.save_transcription(
                    message_id=str(message.id),
                    user_id=str(message.author.id),
                    guild_id=str(message.guild.id) if message.guild else None,
                    channel_id=str(message.channel.id),
                    file_name=attachment.filename,
                    file_size=attachment.size,
                    transcription=transcription,
                    language="ja"
                )
                # 結果を表示
                embed = self.create_transcription_embed(
                    transcription=transcription,
                    author=message.author,
                    channel=message.channel
                )
                
                # メッセージを送信し、リアクションを追加
                result_msg = await message.reply(embed=embed)
                
                # データベースに結果メッセージIDを更新
                async with aiosqlite.connect(self.bot.database.db_path) as update_db:
                    await update_db.execute(
                        "UPDATE transcriptions SET message_id = ? WHERE id = ?",
                        (str(result_msg.id), transcription_id)
                    )
                    await update_db.commit()
                
                # リアクションを追加（将来の機能拡張用）
                await result_msg.add_reaction('📝')  # 要約
                await result_msg.add_reaction('🌐')  # 翻訳
                
                self.logger.info(f"Transcription completed for {attachment.filename}")
            else:
                await message.reply('❌ 文字起こしに失敗しました。')
                self.logger.error(f"Transcription failed for {attachment.filename}")
                
        except Exception as e:
            log_error(self.logger, e, f"during voice processing of {attachment.filename}")
            await processing_msg.edit(content=f'❌ エラーが発生しました: {str(e)}')
    
    def create_transcription_embed(self, transcription: str, author: discord.User, 
                                 channel: discord.abc.Messageable) -> discord.Embed:
        """文字起こし結果のEmbedを作成"""
        embed = discord.Embed(
            title="📝 文字起こし結果",
            description=transcription[:4000],  # Discord埋め込みの制限
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="送信者", value=author.mention, inline=True)
        embed.add_field(name="チャンネル", value=channel.mention if hasattr(channel, 'mention') else 'DM', inline=True)
        embed.set_footer(text="リアクションを追加して追加の処理を実行できます")
        
        return embed

async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    await bot.add_cog(VoiceHandler(bot))