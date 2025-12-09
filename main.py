#!/usr/bin/env python3
"""
Cursor Auto Login Tool - Main Entry Point

Cursor 全自动登录工具主入口
功能：
1. 自动获取 Cursor Token
2. 自动清理浏览器 Cookie
3. 自动设置新 Token
4. 自动打开并登录浏览器
5. 自动创建 API Key
6. 自动配置环境变量

使用方法：
  python3 main.py           # 无头模式（后台运行）
  python3 main.py --show    # 显示浏览器界面
  python3 main.py --visible # 显示浏览器界面（同 --show）
"""

import sys

from cursor_login import (
    get_cursor_token,
    auto_login_with_selenium,
    get_manual_login_script
)


def parse_arguments():
    """
    解析命令行参数

    Returns:
        headless: 是否使用无头模式
    """
    headless = True  # 默认无头模式
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--show', '--visible', '-v', '-s']:
            headless = False
    return headless


def print_header(headless: bool):
    """
    打印程序标题

    Args:
        headless: 是否为无头模式
    """
    print("\n" + "="*60)
    print("🔐 Cursor 全自动登录工具 v2.0")
    print("="*60)
    if headless:
        print("🔧 运行模式：后台无头模式（不显示浏览器）")
    else:
        print("🔧 运行模式：可视化模式（显示浏览器界面）")
    print("="*60)


def print_account_info(info: dict):
    """
    打印账户信息

    Args:
        info: 用户信息字典
    """
    print("\n" + "="*60)
    print("📋 账户信息")
    print("="*60)
    print(f"📧 邮箱: {info['email']}")
    print(f"👤 User ID: {info['user_id']}")
    print(f"🔑 Token: {info['token'][:50]}...")
    print(f"⏰ 过期时间: {info['expiry']}")
    print("="*60)


def print_manual_login_instructions(info: dict):
    """
    打印手动登录说明

    Args:
        info: 用户信息字典
    """
    print("\n❌ 自动登录失败")
    print("\n💡 手动登录方法：")
    print("1. 访问 https://www.cursor.com/")
    print("2. 按 F12 打开控制台")
    print("3. 粘贴以下代码：")
    print("\n" + "-"*60)
    print(get_manual_login_script(info))
    print("-"*60)


def main():
    """主函数"""
    try:
        # 解析命令行参数
        headless = parse_arguments()

        # 打印标题
        print_header(headless)

        # 获取 Token
        print("\n📥 正在获取 Cursor Token...")
        info = get_cursor_token()

        if not info:
            print("\n❌ 无法获取账户信息")
            print("💡 请确保：")
            print("   1. Cursor 客户端已安装")
            print("   2. 已经登录过 Cursor 客户端")
            print("   3. 数据库文件存在")
            return

        # 显示账户信息
        print_account_info(info)

        # 开始自动登录
        success = auto_login_with_selenium(info, headless=headless)

        if success:
            print("\n✅ 自动登录完成！")
        else:
            print_manual_login_instructions(info)

    except KeyboardInterrupt:
        print("\n\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
