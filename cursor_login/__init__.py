"""
Cursor Auto Login Tool

Cursor 全自动登录工具
- 自动获取 Token、清理 Cookie、设置新 Token 并自动登录浏览器
"""

__version__ = "2.0.0"
__author__ = "DanOps-1"

from .database import get_cursor_token
from .browser import auto_login_with_selenium, get_manual_login_script
from .api_key import create_api_key, update_zshrc_with_api_key

__all__ = [
    'get_cursor_token',
    'auto_login_with_selenium',
    'get_manual_login_script',
    'create_api_key',
    'update_zshrc_with_api_key',
]
