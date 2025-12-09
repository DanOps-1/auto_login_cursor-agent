"""
数据库操作模块
负责从 Cursor 数据库中读取用户信息和 Token
"""

import sqlite3
import json
import base64
from datetime import datetime
from typing import Optional, Dict

from .config import DB_PATH


def get_cursor_token() -> Optional[Dict[str, str]]:
    """
    从 Cursor 数据库获取 Token 和用户信息

    Returns:
        包含用户信息的字典，格式：
        {
            'email': str,      # 用户邮箱
            'token': str,      # Refresh Token
            'user_id': str,    # 用户 ID
            'expiry': str      # Token 过期时间
        }
        如果失败返回 None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 获取邮箱
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursorAuth/cachedEmail'")
        email_result = cursor.fetchone()
        email = email_result[0] if email_result else None

        # 获取 Token
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursorAuth/refreshToken'")
        token_result = cursor.fetchone()
        token = token_result[0] if token_result else None

        conn.close()

        if not email or not token:
            print("❌ 无法获取 Cursor 账户信息")
            return None

        # 从 Token 中解析 User ID
        try:
            user_id, expiry = _parse_jwt_token(token)
        except Exception as e:
            print(f"⚠️  Token 解析失败: {e}")
            user_id = "unknown"
            expiry = "未知"

        return {
            'email': email,
            'token': token,
            'user_id': user_id,
            'expiry': expiry
        }

    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return None


def _parse_jwt_token(token: str) -> tuple[str, str]:
    """
    解析 JWT Token，提取 User ID 和过期时间

    Args:
        token: JWT Token 字符串

    Returns:
        (user_id, expiry) 元组
    """
    # JWT Token 格式: header.payload.signature
    payload = token.split('.')[1]

    # 添加必要的填充
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += '=' * padding

    # 解码 Base64
    decoded = base64.urlsafe_b64decode(payload)
    payload_data = json.loads(decoded)

    # 提取 User ID（移除 auth0| 前缀）
    user_id = payload_data['sub'].replace('auth0|', '')

    # 获取过期时间
    exp_time = datetime.fromtimestamp(payload_data['exp'])
    expiry = exp_time.strftime('%Y-%m-%d %H:%M:%S')

    return user_id, expiry
