import discord
from typing import Optional, Dict, Any
import json
import os

class PermissionManager:
    """権限とユーザー管理"""
    
    def __init__(self, config_path: str = "config/permissions.json"):
        self.config_path = config_path
        self.permissions = self._load_permissions()
    
    def _load_permissions(self) -> Dict[str, Any]:
        """権限設定の読み込み"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # デフォルト設定
            default = {
                "premium_roles": ["Premium", "VIP", "Supporter"],
                "admin_roles": ["Admin", "Moderator"],
                "daily_limits": {
                    "free": 10,
                    "premium": -1  # 無制限
                },
                "blocked_users": []
            }
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default, f, indent=2)
            return default
    
    def is_premium(self, member: discord.Member) -> bool:
        """プレミアムユーザーかどうか"""
        if not member:
            return False
        
        user_roles = [role.name for role in member.roles]
        return any(role in self.permissions["premium_roles"] for role in user_roles)
    
    def is_admin(self, member: discord.Member) -> bool:
        """管理者かどうか"""
        if not member:
            return False
        
        # サーバー所有者は常に管理者
        if member.guild and member.guild.owner_id == member.id:
            return True
        
        # Discord権限チェック
        if member.guild_permissions.administrator:
            return True
        
        # カスタムロールチェック
        user_roles = [role.name for role in member.roles]
        return any(role in self.permissions["admin_roles"] for role in user_roles)
    
    def is_blocked(self, user_id: int) -> bool:
        """ブロックされているユーザーかどうか"""
        return str(user_id) in self.permissions.get("blocked_users", [])
    
    def get_daily_limit(self, member: Optional[discord.Member]) -> int:
        """日次利用制限を取得"""
        if member and self.is_premium(member):
            return self.permissions["daily_limits"]["premium"]
        return self.permissions["daily_limits"]["free"]
    
    def add_premium_role(self, role_name: str):
        """プレミアムロールを追加"""
        if role_name not in self.permissions["premium_roles"]:
            self.permissions["premium_roles"].append(role_name)
            self._save_permissions()
    
    def block_user(self, user_id: int):
        """ユーザーをブロック"""
        user_id_str = str(user_id)
        if user_id_str not in self.permissions["blocked_users"]:
            self.permissions["blocked_users"].append(user_id_str)
            self._save_permissions()
    
    def unblock_user(self, user_id: int):
        """ユーザーのブロックを解除"""
        user_id_str = str(user_id)
        if user_id_str in self.permissions["blocked_users"]:
            self.permissions["blocked_users"].remove(user_id_str)
            self._save_permissions()
    
    def _save_permissions(self):
        """権限設定を保存"""
        with open(self.config_path, 'w') as f:
            json.dump(self.permissions, f, indent=2)