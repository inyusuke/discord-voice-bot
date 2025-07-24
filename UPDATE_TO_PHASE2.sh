#!/bin/bash

# Phase 1からPhase 2 Simpleへの更新スクリプト

echo "🚀 Phase 1 → Phase 2 Simple 更新開始"

# 更新対象のディレクトリ
UPDATE_DIR="phase1_to_phase2_update"

# 一時ディレクトリ作成
echo "📁 一時ディレクトリを作成..."
mkdir -p $UPDATE_DIR
cd $UPDATE_DIR

# Phase 2 Simpleのファイルをコピー
echo "📋 Phase 2 Simpleのファイルをコピー..."
cp -r ../phase2_simple/* .

# 不要なファイルを削除（もしあれば）
echo "🗑️  不要なファイルを削除..."
rm -f bot.py bot_legacy.py

# ディレクトリ構造を確認
echo "📂 新しいディレクトリ構造:"
ls -la

echo ""
echo "✅ 更新準備完了！"
echo ""
echo "次の手順:"
echo "1. cd $UPDATE_DIR"
echo "2. 既存のGitリポジトリにこれらのファイルをコピー"
echo "3. git add ."
echo "4. git commit -m 'Upgrade to Phase 2 Simple - Add reaction features'"
echo "5. git push"
echo ""
echo "📝 注意: 環境変数（.env）は変更不要です"