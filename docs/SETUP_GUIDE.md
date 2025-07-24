# Discord Voice Bot - 別PC開発環境セットアップガイド

## 必要なもの
- Python 3.11.x
- Git
- テキストエディタ（VS Code推奨）

## セットアップ手順

### 1. コードの取得

#### 方法A: GitHub経由（推奨）
```bash
git clone https://github.com/inyusuke/discord-voice-bot.git
cd discord-voice-bot
```

#### 方法B: 直接コピー
現在のPCから`Discor_bot`フォルダ全体をUSBやクラウドストレージ経由でコピー

### 2. Python環境のセットアップ

```bash
# Python 3.11がインストールされているか確認
python --version

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env`ファイルを作成し、以下を設定：

```env
DISCORD_TOKEN=あなたのDiscordボットトークン
OPENAI_API_KEY=あなたのOpenAI APIキー（音声文字起こし用）
```

**重要**: `.env`ファイルは絶対にGitにコミットしないでください！

### 4. 開発の開始

```bash
# ローカルでBotを起動
python bot.py

# コードを編集したら、変更をコミット
git add .
git commit -m "変更内容の説明"
git push
```

### 5. 別PCでの更新取得

```bash
# 最新のコードを取得
git pull

# 依存関係が更新された場合
pip install -r requirements.txt
```

## トラブルシューティング

### Pythonバージョンエラー
- Python 3.11.xを使用してください
- pyenvやpyenv-winでバージョン管理推奨

### モジュールが見つからない
```bash
pip install -r requirements.txt
```

### Gitの設定
```bash
git config --global user.name "あなたの名前"
git config --global user.email "your.email@example.com"
```

## VS Code推奨拡張機能
- Python
- Pylance
- GitLens
- Discord Presence

## 同期開発のベストプラクティス

1. **ブランチを使う**
   ```bash
   git checkout -b feature/新機能名
   ```

2. **定期的にプル**
   ```bash
   git pull origin main
   ```

3. **コミットメッセージを明確に**
   - 良い例: "Add user statistics command"
   - 悪い例: "update"

4. **.envファイルの管理**
   - 各PCで個別に作成
   - 絶対にコミットしない
   - .env.exampleを参考に

5. **コンフリクトの解決**
   - 両方のPCで同じファイルを編集した場合
   - VS Codeのマージエディタを使用

## 便利なコマンド

```bash
# 現在の状態確認
git status

# 変更履歴確認
git log --oneline

# 作業を一時保存
git stash

# 一時保存を復元
git stash pop

# リモートの最新状態を確認
git fetch
```