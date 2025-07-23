import discord
from discord.ext import commands
import os
import asyncio
import io
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

# .envファイルを読み込む
load_dotenv()

# OpenAIクライアントの初期化
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Botの初期設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 録音の設定
RECORDING_DURATION = 10  # 秒単位
SAMPLE_RATE = 48000
CHANNELS = 2

class VoiceRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        
    def receive_audio(self, data):
        if self.recording:
            self.audio_data.append(data)

@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました！')

@bot.command(name='join')
async def join(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f'✅ {channel.name} に参加しました。')
    else:
        await ctx.send('❌ 先にボイスチャンネルに参加してください。')

@bot.command(name='leave')
async def leave(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('👋 ボイスチャンネルから退出しました。')
    else:
        await ctx.send('❌ ボイスチャンネルに参加していません。')

@bot.command(name='record')
async def record(ctx, duration: int = 10):
    """音声を録音して文字起こし"""
    if not ctx.voice_client:
        await ctx.send('❌ 先に !join コマンドでボイスチャンネルに参加させてください。')
        return
    
    if not os.getenv('OPENAI_API_KEY'):
        await ctx.send('❌ OpenAI APIキーが設定されていません。')
        return
    
    # 録音時間の制限
    duration = min(max(duration, 1), 60)  # 1-60秒の範囲
    
    await ctx.send(f'🎙️ {duration}秒間録音を開始します...')
    
    # 録音用のソースを作成
    recorder = VoiceRecorder()
    recorder.recording = True
    
    # 音声データを受信
    voice_client = ctx.voice_client
    voice_client.start_recording(
        discord.sinks.WaveSink(),
        finished_callback,
        ctx.channel
    )
    
    # 指定時間待機
    await asyncio.sleep(duration)
    
    # 録音停止
    voice_client.stop_recording()
    recorder.recording = False
    
    await ctx.send('⏹️ 録音を停止しました。文字起こしを処理中...')

async def finished_callback(sink, channel):
    """録音完了時のコールバック"""
    try:
        # 各ユーザーの音声を処理
        for user_id, audio in sink.audio_data.items():
            # 音声データを一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                audio.file.seek(0)
                tmp_file.write(audio.file.read())
                tmp_file_path = tmp_file.name
            
            # OpenAI Whisper APIで文字起こし
            try:
                with open(tmp_file_path, 'rb') as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ja"  # 日本語を指定
                    )
                
                # 結果を送信
                user = await bot.fetch_user(user_id)
                if transcript.text.strip():
                    await channel.send(f"**{user.name}**: {transcript.text}")
                else:
                    await channel.send(f"**{user.name}**: (音声が検出されませんでした)")
                    
            except Exception as e:
                await channel.send(f"❌ 文字起こしエラー: {str(e)}")
            finally:
                # 一時ファイルを削除
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                    
    except Exception as e:
        await channel.send(f"❌ エラーが発生しました: {str(e)}")

@bot.command(name='test')
async def test(ctx):
    """Botの動作テスト"""
    await ctx.send('✅ Botは正常に動作しています！')

@bot.command(name='help_voice')
async def help_voice(ctx):
    """ヘルプを表示"""
    embed = discord.Embed(
        title="🎙️ Voice Transcription Bot",
        description="音声を録音して文字起こしするBotです",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="コマンド一覧",
        value="""
        `!join` - ボイスチャンネルに参加
        `!leave` - ボイスチャンネルから退出
        `!record [秒数]` - 音声を録音して文字起こし（1-60秒）
        `!test` - Botの動作確認
        `!help_voice` - このヘルプを表示
        """,
        inline=False
    )
    embed.add_field(
        name="使い方",
        value="1. ボイスチャンネルに参加\n2. `!join`でBotを招待\n3. `!record 10`で10秒間録音",
        inline=False
    )
    await ctx.send(embed=embed)

# Botを起動
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))