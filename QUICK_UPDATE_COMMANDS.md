# Phase 1 → Phase 2 Simple 更新コマンド集

## 🚀 クイック更新手順

以下のコマンドをコピー＆ペーストして実行してください。

### 1. 既存のリポジトリをクローン（まだの場合）
```bash
git clone https://github.com/yuin15/discord-voice-bot.git
cd discord-voice-bot
```

### 2. 更新ファイルをコピー
```bash
# 現在のディレクトリを確認
pwd

# Phase 2 Simpleのファイルをコピー（パスは環境に合わせて調整）
cp -r /Users/in9/Library/CloudStorage/GoogleDrive-yuhsuke.in@newstory-inc.com/マイドライブ/claude_code/discord-voice-bot/phase1_to_phase2_update/* .

# 古いbot.pyを削除
rm -f bot.py

# ファイル構造を確認
ls -la
```

### 3. Gitにコミット＆プッシュ
```bash
# 変更を確認
git status

# すべての変更を追加
git add .

# コミット
git commit -m "Upgrade to Phase 2 Simple - Add reaction features without database"

# プッシュ
git push origin main
```

### 4. Renderでの確認
```
1. https://dashboard.render.com にアクセス
2. あなたのサービスを選択
3. "Logs"タブで以下を確認：
   - "Bot version: 2.0-simple"
   - "Loaded cog: cogs.voice_handler"
   - "Loaded cog: cogs.reaction_handler"
```

## 📝 もし手動でコピーする場合

1. **削除するファイル:**
   - bot.py

2. **追加するファイル:**
   - main.py
   - cogs/フォルダ全体
   - services/フォルダ全体
   - utils/フォルダ全体
   - config/フォルダ全体

3. **更新するファイル:**
   - requirements.txt（aiosqliteを削除）

## ⚠️ 注意事項

- 環境変数（.env）は変更不要
- Procfileは自動的に`python main.py`を使用
- スラッシュコマンドの同期に数分かかる場合があります