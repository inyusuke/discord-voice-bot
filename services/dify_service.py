import aiohttp
import os
from typing import Dict, Any, Optional
import tempfile
from utils.logger import setup_logger

class DifyService:
    """Dify APIとの連携を管理"""
    
    def __init__(self):
        self.api_url = os.getenv('DIFY_API_URL')
        self.api_key = os.getenv('DIFY_API_KEY')
        self.logger = setup_logger('DifyService')
        self.session = None
    
    async def initialize(self):
        """非同期セッションの初期化"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """セッションのクローズ"""
        if self.session:
            await self.session.close()
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str, user_id: str) -> Optional[str]:
        """ファイルをDifyにアップロード"""
        if not self.api_url or not self.api_key:
            self.logger.error("Dify API credentials not configured")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = aiohttp.FormData()
        data.add_field('file', file_data, filename=filename, content_type=content_type)
        data.add_field('user', user_id)
        
        try:
            async with self.session.post(
                'https://api.dify.ai/v1/files/upload',
                headers=headers,
                data=data
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    file_id = result.get('id')
                    self.logger.info(f"File uploaded successfully: {file_id}")
                    return file_id
                else:
                    error_text = await response.text()
                    self.logger.error(f"File upload failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            return None
    
    async def run_workflow(self, file_id: str, inputs: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Difyワークフローを実行"""
        if not self.api_url or not self.api_key:
            self.logger.error("Dify API credentials not configured")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        workflow_data = {
            'inputs': inputs,
            'files': [{
                'transfer_method': 'local_file',
                'upload_file_id': file_id,
                'type': 'audio'
            }],
            'response_mode': 'blocking',
            'user': user_id
        }
        
        try:
            async with self.session.post(
                self.api_url,
                headers=headers,
                json=workflow_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info("Workflow executed successfully")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"Workflow execution failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            self.logger.error(f"Error executing workflow: {str(e)}")
            return None
    
    async def transcribe_audio(self, file_data: bytes, filename: str, content_type: str, 
                             user_info: Dict[str, str]) -> Optional[str]:
        """音声ファイルを文字起こし"""
        await self.initialize()
        
        # ファイルアップロード
        file_id = await self.upload_file(
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            user_id=user_info.get('user_id', 'unknown')
        )
        
        if not file_id:
            return None
        
        # ワークフロー実行
        result = await self.run_workflow(
            file_id=file_id,
            inputs={
                'username': user_info.get('username', 'Unknown'),
                'channel': user_info.get('channel', 'Unknown'),
                'server': user_info.get('server', 'DM')
            },
            user_id=user_info.get('user_id', 'unknown')
        )
        
        if result:
            outputs = result.get('data', {}).get('outputs', {})
            transcription = outputs.get('transcription', '') or outputs.get('text', '')
            return transcription
        
        return None
    
    async def transcribe_and_summarize(self, file_data: bytes, filename: str, content_type: str,
                                     user_info: Dict[str, str]) -> Dict[str, Optional[str]]:
        """音声ファイルを文字起こしして要約"""
        # 現在は通常の文字起こしを使用
        # TODO: Difyで要約機能付きワークフローを作成後、切り替え
        transcription = await self.transcribe_audio(file_data, filename, content_type, user_info)
        
        if transcription:
            # 簡易的な要約生成（仮実装）
            summary = self._generate_simple_summary(transcription)
            return {
                'transcription': transcription,
                'summary': summary
            }
        
        return {
            'transcription': None,
            'summary': None
        }
    
    def _generate_simple_summary(self, text: str) -> str:
        """簡易的な要約を生成（仮実装）"""
        if len(text) < 100:
            return "短いテキストのため要約は不要です。"
        
        # 文を分割
        sentences = text.split('。')
        if len(sentences) < 3:
            return text
        
        # 最初の3文を要約として返す（仮実装）
        summary_sentences = sentences[:3]
        summary = '。'.join(summary_sentences) + '。'
        
        return f"【要約】\n{summary}\n\n※ 高度な要約機能は開発中です。"
    
    async def translate_text(self, text: str, target_language: str = "English") -> Optional[str]:
        """テキストを翻訳（将来実装）"""
        # TODO: Dify翻訳ワークフローを実装
        self.logger.info(f"Translation requested to {target_language}")
        
        # 仮実装
        if target_language.lower() == "english":
            return f"[Translation to {target_language}]\nThis is a placeholder translation.\nOriginal text length: {len(text)} characters."
        else:
            return f"[{target_language}への翻訳]\n翻訳機能は開発中です。"