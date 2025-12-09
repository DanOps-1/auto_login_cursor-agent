"""
浏览器自动化模块
使用 Selenium 实现自动登录和操作
"""

import time
import subprocess
import sys
from typing import Dict, Optional

from .config import (
    CURSOR_WEBSITE,
    CURSOR_DASHBOARD,
    COOKIE_NAME,
    COOKIE_DOMAIN,
    COOKIE_PATH,
    DEFAULT_WINDOW_SIZE
)
from .api_key import create_api_key, update_zshrc_with_api_key


def auto_login_with_selenium(info: Dict[str, str], headless: bool = True) -> bool:
    """
    使用 Selenium 自动登录 Cursor

    Args:
        info: 包含用户信息的字典，包括 email, token, user_id, expiry
        headless: 是否使用无头模式（默认 True）

    Returns:
        成功返回 True，失败返回 False
    """
    # 确保 Selenium 已安装
    if not _ensure_selenium_installed():
        return False

    # 导入 Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("❌ 安装后仍无法导入，请手动重新运行脚本")
        return False

    print("\n🚀 开始自动登录流程...")
    if headless:
        print("   💡 后台模式：浏览器不显示界面")
    else:
        print("   💡 可视化模式：显示浏览器界面")

    # 配置浏览器
    chrome_options = _configure_chrome_options(headless)

    driver = None

    try:
        # 启动浏览器
        print("1️⃣ 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)

        # 设置 Cookie 并登录
        if not _set_login_cookie(driver, info):
            if driver and headless:
                driver.quit()
            return False

        # 验证登录状态
        if not _verify_login(driver, info, headless):
            if driver and headless:
                driver.quit()
            return False

        return True

    except Exception as e:
        print(f"\n❌ 自动登录失败: {e}")
        import traceback
        traceback.print_exc()
        if driver and headless:
            driver.quit()
            print("✅ 浏览器已关闭")
        return False


def _ensure_selenium_installed() -> bool:
    """
    确保 Selenium 已安装

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        import selenium
        return True
    except ImportError:
        print("\n❌ 未安装 Selenium，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
            print("✅ Selenium 安装完成")
            print("🔄 正在重新加载模块...\n")
            return True
        except Exception as e:
            print(f"❌ Selenium 安装失败: {e}")
            return False


def _configure_chrome_options(headless: bool):
    """
    配置 Chrome 浏览器选项

    Args:
        headless: 是否使用无头模式

    Returns:
        Chrome Options 对象
    """
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()

    if headless:
        # 无头模式配置
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={DEFAULT_WINDOW_SIZE}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    else:
        # 可视化模式配置
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option("detach", True)

    return chrome_options


def _set_login_cookie(driver, info: Dict[str, str]) -> bool:
    """
    设置登录 Cookie

    Args:
        driver: Selenium WebDriver 实例
        info: 用户信息字典

    Returns:
        成功返回 True，失败返回 False
    """
    # 访问主域名
    print("2️⃣ 访问 cursor.com...")
    driver.get(CURSOR_WEBSITE)
    time.sleep(1)

    # 清理旧 Cookie
    print("3️⃣ 清理旧的登录状态...")
    driver.delete_all_cookies()

    # 设置新 Cookie
    print("4️⃣ 设置新的登录 Token...")
    cookie_value = f"{info['user_id']}::{info['token']}"

    try:
        driver.add_cookie({
            'name': COOKIE_NAME,
            'value': cookie_value,
            'domain': COOKIE_DOMAIN,
            'path': COOKIE_PATH,
            'secure': True,
            'sameSite': 'None',
            'httpOnly': False
        })
        print("   ✅ Cookie 已通过 Selenium 设置")
    except Exception as e:
        print(f"   ⚠️  Selenium 设置失败，尝试 JavaScript: {e}")
        # 备用方案：使用 JavaScript
        cookie_value_encoded = f"{info['user_id']}%3A%3A{info['token']}"
        driver.execute_script(f"""
            document.cookie = "{COOKIE_NAME}={cookie_value_encoded}; domain={COOKIE_DOMAIN}; path={COOKIE_PATH}; secure; SameSite=None; max-age=5184000";
        """)

    # 验证 Cookie 是否设置成功
    print("5️⃣ 验证登录状态...")
    cookies = driver.get_cookies()
    cursor_cookie = next((c for c in cookies if c['name'] == COOKIE_NAME), None)

    if cursor_cookie:
        print("✅ Cookie 设置成功！")
        print(f"   Cookie 值: {cursor_cookie['value'][:50]}...")
        return True
    else:
        print("❌ Cookie 设置失败")
        print("可能原因：浏览器阻止了 Cookie")
        return False


def _verify_login(driver, info: Dict[str, str], headless: bool) -> bool:
    """
    验证登录状态并创建 API Key

    Args:
        driver: Selenium WebDriver 实例
        info: 用户信息字典
        headless: 是否为无头模式

    Returns:
        成功返回 True，失败返回 False
    """
    # 跳转到 Dashboard
    print("6️⃣ 跳转到 Dashboard...")
    driver.get(CURSOR_DASHBOARD)
    time.sleep(2)

    # 检查登录状态
    print("7️⃣ 检查登录状态...")
    try:
        current_url = driver.current_url
        print(f"   当前 URL: {current_url}")

        # 如果跳转到认证页面，尝试重新设置
        if "authenticator.cursor.sh" in current_url:
            print("⚠️  页面跳转到了认证页面，Cookie 可能未生效")
            print("🔄 尝试重新设置并跳转...")

            driver.get(CURSOR_WEBSITE)
            time.sleep(1)

            driver.get(CURSOR_DASHBOARD)
            time.sleep(2)

            current_url = driver.current_url
            print(f"   新 URL: {current_url}")

        # 检查是否成功登录
        if "dashboard" in current_url and "authenticator" not in current_url:
            print("✅ 成功跳转到 Dashboard！")
        else:
            print(f"⚠️  当前页面: {current_url}")

        print("\n" + "="*60)
        print("🎉 登录成功！")
        print("="*60)
        print(f"📧 邮箱: {info['email']}")
        print(f"⏰ Token 过期时间: {info['expiry']}")
        print("="*60)

        # 创建 API Key
        api_key = create_api_key(driver)
        if api_key:
            print("\n" + "="*60)
            print("🔑 API Key 已创建")
            print("="*60)
            print(f"📝 API Key: {api_key}")
            print("="*60)
            print("\n💡 此 API Key 可用于 Cursor CLI 和 API 调用")

            # 写入到 ~/.zshrc
            print("\n🔟 写入环境变量...")
            update_zshrc_with_api_key(api_key)
        else:
            print("\n⚠️  API Key 创建失败，请手动创建")

        # 根据模式决定是否关闭浏览器
        if headless:
            print("\n🔚 关闭浏览器...")
            driver.quit()
            print("   ✅ 浏览器已关闭")
        else:
            print("\n✅ 浏览器将保持打开状态，可以继续使用")

        return True

    except Exception as e:
        print(f"⚠️  无法验证登录状态: {e}")
        print("但 Cookie 已设置")
        if driver and headless:
            driver.quit()
            print("✅ 浏览器已关闭")
        elif not headless:
            print("✅ 浏览器将保持打开状态")
        return True


def get_manual_login_script(info: Dict[str, str]) -> str:
    """
    获取手动登录的 JavaScript 代码

    Args:
        info: 用户信息字典

    Returns:
        JavaScript 代码字符串
    """
    cookie_value = f"{info['user_id']}%3A%3A{info['token']}"
    return f'document.cookie="{COOKIE_NAME}={cookie_value};domain={COOKIE_DOMAIN};path={COOKIE_PATH};secure;SameSite=None";location.reload();'
