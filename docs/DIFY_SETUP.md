# Dify Setup Guide

Discord Voice Message Transfer Botと連携するDifyワークフローの設定ガイドです。

## 概要

Difyでは以下の処理を実装します：
1. Discord Botから音声ファイルを受信
2. OpenAI Whisper APIで文字起こし
3. 文字起こし結果を処理（必要に応じてAI応答生成）
4. 結果をDiscord Botに返却

## 前提条件

- Difyアカウント
- OpenAI APIキー（Whisper用）
- Discord Bot（設定済み）

## Step 1: Difyワークフローの作成

### 1.1 新規ワークフローを作成

1. Difyダッシュボードにログイン
2. 「ワークフロー」→「新規作成」
3. ワークフロー名: `Discord Voice Transcription`

### 1.2 ワークフローの構成

```
[開始] → [HTTPリクエスト受信] → [音声ファイル処理] → [Whisper API] → [応答生成] → [HTTPレスポンス]
```

## Step 2: HTTPエンドポイントの設定

### 2.1 HTTPリクエストノードの追加

- ノードタイプ: `HTTP Request`
- メソッド: `POST`
- パス: `/voice-transcription`

### 2.2 受信パラメータの定義

```json
{
  "file": "音声ファイル（バイナリ）",
  "inputs": {
    "username": "送信者名",
    "channel": "チャンネル名",
    "server": "サーバー名"
  },
  "user": "ユーザーID"
}
```

## Step 3: Whisper API統合

### 3.1 OpenAI Whisperノードの追加

1. ノードを追加: `ツール` → `OpenAI` → `音声書き起こし（Whisper）`
2. APIキーを設定
3. 入力設定:
   - ファイル: HTTPリクエストから受信した音声ファイル
   - 言語: `ja`（日本語）
   - モデル: `whisper-1`

### 3.2 文字起こし結果の処理

- 出力変数名: `transcription_text`
- エラーハンドリング: 文字起こし失敗時のメッセージ

## Step 4: 応答生成（オプション）

文字起こし結果に基づいてAI応答を生成する場合：

### 4.1 LLMノードの追加

1. ノードを追加: `LLM`
2. プロンプト設定:
```
ユーザー「{{username}}」からの音声メッセージ:
{{transcription_text}}

このメッセージに対して適切な応答を生成してください。
```

### 4.2 応答のカスタマイズ

- チャンネルやサーバー情報を使って文脈を考慮
- 音声メッセージの内容に応じた処理分岐

## Step 5: HTTPレスポンスの設定

### 5.1 レスポンスノードの設定

```json
{
  "status": 200,
  "message": "{{transcription_text}}",
  "metadata": {
    "username": "{{inputs.username}}",
    "processed_at": "{{timestamp}}",
    "ai_response": "{{llm_response}}"  // オプション
  }
}
```

## Step 6: APIエンドポイントの確認

### 6.1 APIキーの生成

1. ワークフロー設定 → API設定
2. 「APIキーを生成」
3. キーを安全に保存

### 6.2 エンドポイントURL

```
https://api.dify.ai/v1/workflows/{workflow_id}/run
```

または

```
https://your-dify-instance.com/api/workflows/{workflow_id}/run
```

## Step 7: Discord Botの環境変数設定

`.env`ファイルを更新:

```bash
DIFY_API_URL=https://api.dify.ai/v1/workflows/{your_workflow_id}/run
DIFY_API_KEY=your_dify_api_key_here
```

## テスト手順

1. Discord Botを起動
2. テストチャンネルで音声メッセージを送信
3. Difyワークフローのログで処理を確認
4. Discordに返信が来ることを確認

## トラブルシューティング

### 音声ファイルが受信できない場合
- ファイルサイズ制限を確認
- Content-Typeが正しいか確認

### Whisper APIエラー
- OpenAI APIキーの有効性を確認
- 音声ファイル形式が対応しているか確認

### レスポンスが返らない場合
- Difyワークフローのログを確認
- HTTPタイムアウト設定を調整

## 高度な設定

### 音声ファイルの前処理
- ノイズ除去
- 音声フォーマット変換

### 文字起こし結果の後処理
- 句読点の追加
- 話者の識別
- 要約生成

### 条件分岐
- 特定のキーワードで処理を分岐
- チャンネルごとに異なる応答

## 参考リンク

- [Dify公式ドキュメント](https://docs.dify.ai)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Discord Bot設定ガイド](./SETUP_GUIDE.md)