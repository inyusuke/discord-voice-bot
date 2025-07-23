# Google Drive デスクトップを使った複数PC開発環境

## セットアップ手順

### 1. Google Drive デスクトップのインストール

#### 両方のPCで実行：
1. [Google Drive デスクトップ](https://www.google.com/drive/download/)をダウンロード
2. インストールして、Googleアカウントでログイン
3. 「マイドライブ」を同期する設定を選択

### 2. 開発フォルダの作成

#### 最初のPC（現在のPC）で：
```bash
# Google Driveにプロジェクトフォルダを作成
mkdir "G:\マイドライブ\claude_code"
mkdir "G:\マイドライブ\claude_code\discord-voice-bot"

# 現在のプロジェクトをコピー
xcopy /E /I "C:\Users\yuhsu\Cloude_Code_Prj\Discor_bot" "G:\マイドライブ\claude_code\discord-voice-bot"
```

### 3. Git設定の調整

`G:\マイドライブ\claude_code\discord-voice-bot\.gitignore`に追加：
```
# Google Drive同期ファイル
.tmp.drivedownload
.tmp.driveupload
desktop.ini
Icon?

# 環境依存ファイル
.env
.env.local
venv/
__pycache__/
*.pyc
```

### 4. 別PCでの設定

#### 2台目のPCで：
1. Google Drive デスクトップがインストール済みか確認
2. 同期が完了するまで待つ（初回は時間がかかる場合あり）
3. フォルダを確認：
   ```
   G:\マイドライブ\claude_code\discord-voice-bot
   ```

### 5. 各PCで個別に設定が必要なもの

#### 両方のPCで実行：
```bash
# プロジェクトフォルダに移動
cd "G:\マイドライブ\claude_code\discord-voice-bot"

# Python仮想環境を作成（各PCで個別に必要）
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# .envファイルを作成（.env.exampleを参考に）
copy .env.example .env
# メモ帳などで.envを編集してトークンを設定
```

## 同期の注意点

### ✅ 同期されるもの
- Pythonソースコード（.py）
- 設定ファイル（.yaml, .txt, .md）
- Gitリポジトリ情報

### ❌ 同期されないもの（.gitignoreで除外）
- .envファイル（セキュリティのため）
- venv/フォルダ（各PCで作成）
- __pycache__/（Pythonキャッシュ）

## 開発フロー

### 1. 作業開始前
```bash
# 最新の変更を確認
git status
git pull
```

### 2. コード編集
- VS CodeなどでG:\マイドライブ\claude_code\discord-voice-bot を開く
- 通常通り開発

### 3. 作業終了時
```bash
# 変更をコミット
git add .
git commit -m "変更内容"
git push
```

### 4. 別PCで作業再開時
```bash
# Google Drive同期を待つ（通常は自動）
# Gitで最新を取得
git pull
```

## トラブルシューティング

### 同期の競合が発生した場合
1. Google Driveアプリで競合ファイルを確認
2. 「ファイル名 (1).py」のような重複ファイルを確認
3. 正しいバージョンを選んで、不要なものを削除
4. Gitで正しい状態に戻す：
   ```bash
   git status
   git checkout -- 競合したファイル名
   ```

### 同期が遅い場合
- Google Driveアプリの設定で同期優先度を上げる
- 大きなファイルは.gitignoreに追加
- 必要に応じてGitHubも併用

### Pythonパスエラー
各PCで仮想環境は別々に作成する必要があります：
```bash
# 仮想環境を削除して再作成
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## ベストプラクティス

1. **重要な変更はGitにもプッシュ**
   - Google Drive + GitHubの二重バックアップ
   
2. **大きなファイルは除外**
   - 音声ファイルや大きなデータは.gitignoreに追加

3. **定期的な同期確認**
   - Google Driveアイコンで同期状態を確認

4. **.envファイルは各PCで管理**
   - セキュリティのため同期しない
   - 各PCで個別に作成

5. **コンフリクト防止**
   - 同時に両方のPCで編集しない
   - 作業開始前にgit pullを実行