"""
配置管理模块
存储全局配置信息
"""

import os

# Cursor 数据库路径
DB_PATH = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")

# Cursor 网站相关
CURSOR_WEBSITE = "https://cursor.com/"
CURSOR_DASHBOARD = "https://www.cursor.com/dashboard"
CURSOR_INTEGRATIONS = "https://www.cursor.com/dashboard?tab=integrations"

# Cookie 配置
COOKIE_NAME = "WorkosCursorSessionToken"
COOKIE_DOMAIN = ".cursor.com"
COOKIE_PATH = "/"

# 浏览器配置
DEFAULT_WINDOW_SIZE = "1920,1080"
DEFAULT_TIMEOUT = 15  # 默认超时时间（秒）

# API Key 配置
API_KEY_PREFIX = "auto_key_"
ZSHRC_PATH = os.path.expanduser("~/.zshrc")
ENV_VAR_NAME = "CURSOR_API_KEY"
