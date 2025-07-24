import discord
from discord.ext import commands
import os
import tempfile
import requests
import json
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# Dify API設定
DIFY_API_URL = os.getenv('DIFY_API_URL')
DIFY_API_KEY = os.getenv('DIFY_API_KEY')

# Botの初期設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました！')
    print('ボイスメモ転送Bot準備完了')


@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    
    # 音声ファイルが添付されているかチェック
    for attachment in message.attachments:
        # 音声ファイルの拡張子をチェック（Discord音声メッセージは通常.oggまたは.mp3）
        if attachment.filename.lower().endswith(('.ogg', '.mp3', '.wav', '.m4a', '.webm')):
            await process_voice_message(message, attachment)
    
    # コマンド処理も継続
    await bot.process_commands(message)


async def process_voice_message(message, attachment):
    """音声メッセージをDifyに送信する"""
    if not DIFY_API_URL or not DIFY_API_KEY:
        await message.reply('❌ Dify APIが設定されていません。')
        return
    
    try:
        # 処理中のメッセージを送信
        processing_msg = await message.reply('🎙️ 音声を処理中...')
        
        # 音声ファイルをダウンロード
        with tempfile.NamedTemporaryFile(suffix=f'_{attachment.filename}', delete=False) as tmp_file:
            await attachment.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Dify APIに音声ファイルを送信
        try:
            with open(tmp_file_path, 'rb') as audio_file:
                headers = {
                    'Authorization': f'Bearer {DIFY_API_KEY}'
                }
                
                files = {
                    'file': (attachment.filename, audio_file, attachment.content_type or 'audio/ogg')
                }
                
                data = {
                    'user': str(message.author.id),
                    'inputs': {
                        'username': message.author.name,
                        'channel': message.channel.name,
                        'server': message.guild.name if message.guild else 'DM'
                    }
                }
                
                # まずファイルをアップロード
                upload_response = requests.post(
                    'https://api.dify.ai/v1/files/upload',
                    headers={
                        'Authorization': f'Bearer {DIFY_API_KEY}'
                    },
                    files={'file': (attachment.filename, audio_file, attachment.content_type or 'audio/ogg')},
                    data={'user': str(message.author.id)}
                )
                
                if upload_response.status_code == 201:
                    file_id = upload_response.json().get('id')
                    
                    # ワークフロー実行
                    workflow_data = {
                        'inputs': {
                            'username': message.author.name,
                            'channel': message.channel.name,
                            'server': message.guild.name if message.guild else 'DM'
                        },
                        'files': [{
                            'transfer_method': 'local_file',
                            'upload_file_id': file_id,
                            'type': 'audio'
                        }],
                        'response_mode': 'blocking',
                        'user': str(message.author.id)
                    }
                    
                    response = requests.post(
                        DIFY_API_URL,
                        headers={
                            'Authorization': f'Bearer {DIFY_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json=workflow_data
                    )
                else:
                    response = upload_response
                
                if response.status_code == 200:
                    result = response.json()
                    # 処理中メッセージを削除
                    await processing_msg.delete()
                    
                    # ワークフローの実行結果から文字起こしテキストを取得
                    outputs = result.get('data', {}).get('outputs', {})
                    transcription = outputs.get('transcription', '') or outputs.get('text', '')
                    
                    if not transcription:
                        # デバッグ用 - 全体の構造を確認
                        transcription = f"文字起こし結果が見つかりません。outputs: {json.dumps(outputs, ensure_ascii=False)[:300]}"
                    
                    # Difyからの応答を表示
                    embed = discord.Embed(
                        title="📝 文字起こし結果",
                        description=transcription,
                        color=discord.Color.green()
                    )
                    embed.add_field(name="送信者", value=message.author.name, inline=True)
                    embed.add_field(name="チャンネル", value=message.channel.name, inline=True)
                    await message.reply(embed=embed)
                else:
                    error_msg = f'❌ API エラー: {response.status_code}'
                    if response.text:
                        error_details = response.text[:500]
                        error_msg += f'\n詳細: {error_details}'
                    # デバッグ用: リクエストURLも表示
                    error_msg += f'\nURL: {DIFY_API_URL}'
                    await processing_msg.edit(content=error_msg)
                    
        except Exception as e:
            await processing_msg.edit(content=f'❌ エラー: {str(e)}')
        finally:
            # 一時ファイルを削除
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                
    except Exception as e:
        await message.reply(f'❌ エラーが発生しました: {str(e)}')


@bot.command(name='test')
async def test(ctx):
    """Botの動作テスト"""
    status_msg = f'✅ Botは正常に動作しています！\n'
    status_msg += f'Dify API: {"設定済み" if DIFY_API_URL and DIFY_API_KEY else "未設定"}'
    await ctx.send(status_msg)


@bot.command(name='help_voice')
async def help_voice(ctx):
    """ヘルプを表示"""
    embed = discord.Embed(
        title="🎙️ Voice Message Transfer Bot",
        description="Discordのボイスメモを自動でDifyに転送するBotです",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="使い方",
        value="""
        1. チャンネルに音声メッセージを送信
        2. Botが自動的にDifyに転送
        3. 処理結果が返信されます
        
        対応形式: .ogg, .mp3, .wav, .m4a, .webm
        """,
        inline=False
    )
    embed.add_field(
        name="コマンド",
        value="""
        `!test` - Botの動作確認
        `!help_voice` - このヘルプを表示
        """,
        inline=False
    )
    embed.add_field(
        name="備考",
        value="音声の文字起こしはDify側で処理されます",
        inline=False
    )
    await ctx.send(embed=embed)


# Botを起動
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))