import discord
from discord.ext import commands
from services.openai_service import OpenAIService
from utils.logger import setup_logger, log_voice_processing, log_error

class VoiceHandler(commands.Cog):
    """音声メッセージの処理を担当"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.openai_service = OpenAIService()
        self.logger = setup_logger('VoiceHandler')
        
        # サポートする音声フォーマット
        self.supported_formats = ('.ogg', '.mp3', '.wav', '.m4a', '.webm')
        
        # 処理中のメッセージIDを追跡
        self.processing_messages = set()
    
    async def cog_load(self):
        """Cogのロード時に実行"""
        self.logger.info("VoiceHandler cog loaded")
    
    async def cog_unload(self):
        """Cogのアンロード時に実行"""
        self.logger.info("VoiceHandler cog unloaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """メッセージイベントのリスナー"""
        # Bot自身のメッセージは無視
        if message.author == self.bot.user:
            return
        
        # 音声ファイルの処理
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(self.supported_formats):
                await self.process_voice_message(message, attachment)
    
    async def process_voice_message(self, message: discord.Message, attachment: discord.Attachment):
        """音声メッセージを処理"""
        # 重複処理を防ぐ
        if message.id in self.processing_messages:
            self.logger.warning(f"Message {message.id} is already being processed, skipping...")
            return
        
        self.processing_messages.add(message.id)
        
        try:
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
                
                # 文字起こし
                transcription = await self.openai_service.transcribe_audio(
                    file_data=file_data,
                    filename=attachment.filename
                )
                
                # 処理中メッセージを削除
                await processing_msg.delete()
                
                if transcription:
                    # 結果を表示
                    embed = self.create_transcription_embed(
                        transcription=transcription,
                        author=message.author,
                        channel=message.channel
                    )
                    
                    # メッセージを送信し、リアクションを追加
                    result_msg = await message.reply(embed=embed)
                    
                    # リアクションを追加
                    await result_msg.add_reaction('📝')  # 要約
                    await result_msg.add_reaction('🌐')  # 翻訳
                    
                    self.logger.info(f"Transcription completed for {attachment.filename}")
                else:
                    await message.reply('❌ 文字起こしに失敗しました。')
                    self.logger.error(f"Transcription failed for {attachment.filename}")
                    
            except Exception as e:
                log_error(self.logger, e, f"during voice processing of {attachment.filename}")
                await processing_msg.edit(content=f'❌ エラーが発生しました: {str(e)}')
        finally:
            # 処理完了後、メッセージIDを削除
            self.processing_messages.discard(message.id)
    
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