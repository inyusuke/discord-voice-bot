import os
import openai
from typing import Optional
import tempfile
from utils.logger import setup_logger

class OpenAIService:
    """OpenAI APIとの連携を管理"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.logger = setup_logger('OpenAIService')
        
        if self.api_key:
            # 環境変数を設定（古い方式）
            openai.api_key = self.api_key
        else:
            self.logger.error("OpenAI API key not found in environment variables")
    
    async def transcribe_audio(self, file_data: bytes, filename: str) -> Optional[str]:
        """音声ファイルを文字起こし"""
        if not self.api_key:
            self.logger.error("OpenAI API key not configured")
            return None
        
        try:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(file_data)
                tmp_file_path = tmp_file.name
            
            # Whisper APIで文字起こし
            with open(tmp_file_path, 'rb') as audio_file:
                response = await openai.Audio.atranscribe(
                    model="whisper-1",
                    file=audio_file,
                    language="ja"  # 日本語指定
                )
            
            # 一時ファイルを削除
            os.unlink(tmp_file_path)
            
            transcription = response.get('text', '')
            self.logger.info(f"Transcription completed: {len(transcription)} characters")
            return transcription
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            return None
    
    async def summarize_text(self, text: str, max_length: int = 100) -> Optional[str]:
        """テキストを要約"""
        if not self.api_key:
            self.logger.error("OpenAI API key not configured")
            return None
        
        if len(text) < 50:
            return "短いテキストのため要約は不要です。"
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは要約の専門家です。日本語のテキストを簡潔に要約してください。"},
                    {"role": "user", "content": f"以下のテキストを{max_length}文字以内で要約してください：\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content.strip()
            self.logger.info(f"Summary generated: {len(summary)} characters")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing text: {str(e)}")
            return None
    
    async def translate_text(self, text: str, target_language: str = "English") -> Optional[str]:
        """テキストを翻訳"""
        if not self.api_key:
            self.logger.error("OpenAI API key not configured")
            return None
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"あなたは翻訳の専門家です。日本語のテキストを{target_language}に翻訳してください。"},
                    {"role": "user", "content": f"以下のテキストを{target_language}に翻訳してください：\n\n{text}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            self.logger.info(f"Translation completed to {target_language}")
            return translation
            
        except Exception as e:
            self.logger.error(f"Error translating text: {str(e)}")
            return None