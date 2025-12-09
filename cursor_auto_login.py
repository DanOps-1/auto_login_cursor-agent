#!/usr/bin/env python3
"""
Cursor 全自动登录工具
功能：
1. 自动获取 Cursor Token
2. 自动清理浏览器 Cookie
3. 自动设置新 Token
4. 自动打开并登录浏览器

使用方法：
  python3 cursor_auto_login.py           # 无头模式（后台运行）
  python3 cursor_auto_login.py --show    # 显示浏览器界面
  python3 cursor_auto_login.py --visible # 显示浏览器界面（同 --show）
"""

import sqlite3
import json
import base64
import os
import sys
import time
from datetime import datetime

# 数据库路径
DB_PATH = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")


def get_cursor_token():
    """获取 Cursor Token 和用户信息"""
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
            # JWT Token 格式: header.payload.signature
            payload = token.split('.')[1]
            # 添加必要的填充
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            user_id = payload_data['sub'].replace('auth0|', '')
            
            # 获取过期时间
            exp_time = datetime.fromtimestamp(payload_data['exp'])
            expiry = exp_time.strftime('%Y-%m-%d %H:%M:%S')
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


def create_api_key(driver):
    """自动创建 API Key"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print("\n8️⃣ 正在创建 API Key...")
        
        # 导航到 Integrations 页面
        print("   → 跳转到 Integrations 页面...")
        driver.get("https://www.cursor.com/dashboard?tab=integrations")
        time.sleep(2)  # 缩短等待时间
        
        # 等待并点击 "New API Key" 或 "New User API Key" 按钮
        print("   → 查找 API Key 创建按钮...")
        try:
            # 等待按钮出现（增加超时时间）
            wait = WebDriverWait(driver, 15)
            
            # 使用更通用的 XPath 匹配包含 "API Key" 的按钮
            new_api_key_button = None
            button_texts = [
                "New User API Key",
                "New API Key",
                "User API Key"
            ]
            
            for button_text in button_texts:
                try:
                    print(f"   → 尝试查找 '{button_text}' 按钮...")
                    new_api_key_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{button_text}')]"))
                    )
                    print(f"   ✅ 找到按钮: {button_text}")
                    break
                except:
                    continue
            
            if not new_api_key_button:
                raise Exception("找不到 API Key 创建按钮")
            
            print("   → 点击按钮...")
            new_api_key_button.click()
            
            # 填写 API Key 名称（等待输入框出现）
            print("   → 填写 API Key 名称...")
            name_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter User API Key Name...']"))
            )
            
            # 生成一个唯一的名称
            from datetime import datetime
            api_key_name = f"auto_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            name_input.send_keys(api_key_name)
            print(f"   → API Key 名称: {api_key_name}")
            
            # 查找并点击保存/创建按钮（通常是 "Save" 或 "Create" 按钮）
            print("   → 点击保存按钮...")
            try:
                # 尝试多种可能的按钮文本
                save_button = None
                for button_text in ["Save", "Create", "确认", "保存", "创建"]:
                    try:
                        save_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                        if save_button.is_displayed():
                            break
                    except:
                        continue
                
                if save_button:
                    save_button.click()
                else:
                    # 如果找不到按钮，尝试按回车键
                    from selenium.webdriver.common.keys import Keys
                    name_input.send_keys(Keys.RETURN)
                
                time.sleep(1)
            except Exception as e:
                print(f"   ⚠️  点击保存按钮失败，尝试按回车: {e}")
                from selenium.webdriver.common.keys import Keys
                name_input.send_keys(Keys.RETURN)
                time.sleep(1)
            
            # 等待 API Key 生成
            print("   → 等待 API Key 生成...")
            time.sleep(3)  # 缩短等待时间
            
            # 尝试多种方式提取 API Key
            api_key = None
            import re
            
            # 方法1：从页面源代码中提取 key_ 格式（最可靠）
            try:
                print("   → 从页面源代码提取...")
                page_source = driver.page_source
                # 匹配 key_ 开头的 API Key
                matches = re.findall(r'key_[a-zA-Z0-9]{32,}', page_source)
                if matches:
                    api_key = matches[0]
                    print(f"   ✅ 找到 API Key")
            except Exception as e:
                print(f"   ⚠️  方法1失败: {e}")
            
            # 方法2：查找所有可能包含 API Key 的元素（备用）
            if not api_key:
                try:
                    print("   → 查找文本元素（备用方法）...")
                    all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                    for elem in all_elements:
                        text = elem.text.strip()
                        if 'key_' in text and len(text) > 20:
                            # 提取其中的 key_xxx 部分
                            match = re.search(r'key_[a-zA-Z0-9]{32,}', text)
                            if match:
                                api_key = match.group(0)
                                print(f"   ✅ 找到 API Key（备用方法）")
                                break
                except Exception as e:
                    print(f"   ⚠️  备用方法失败: {e}")
            
            if api_key:
                print("   ✅ API Key 创建成功！")
                return api_key
            else:
                print("   ⚠️  无法自动提取 API Key，请在页面上手动复制")
                return None
                
        except Exception as e:
            print(f"   ⚠️  查找按钮失败: {e}")
            return None
            
    except Exception as e:
        print(f"   ❌ 创建 API Key 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_zshrc_with_api_key(api_key):
    """更新 ~/.zshrc 中的 CURSOR_API_KEY 环境变量"""
    try:
        zshrc_path = os.path.expanduser("~/.zshrc")
        
        # 读取现有内容
        if os.path.exists(zshrc_path):
            with open(zshrc_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # 查找并更新 CURSOR_API_KEY
        api_key_line = f'export CURSOR_API_KEY="{api_key}"\n'
        found = False
        updated_lines = []
        
        for line in lines:
            # 如果找到 CURSOR_API_KEY 的行，替换它
            if line.strip().startswith('export CURSOR_API_KEY='):
                updated_lines.append(api_key_line)
                found = True
                print(f"   → 更新现有的 CURSOR_API_KEY")
            else:
                updated_lines.append(line)
        
        # 如果没找到，添加到文件末尾
        if not found:
            # 确保文件末尾有换行
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'
            updated_lines.append('\n')
            updated_lines.append('# Cursor API Key (自动添加)\n')
            updated_lines.append(api_key_line)
            print(f"   → 添加新的 CURSOR_API_KEY")
        
        # 写回文件
        with open(zshrc_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print(f"   ✅ 已写入 ~/.zshrc")
        print(f"   💡 运行 'source ~/.zshrc' 或重启终端以生效")
        return True
        
    except Exception as e:
        print(f"   ❌ 写入 ~/.zshrc 失败: {e}")
        return False


def auto_login_with_selenium(info, headless=True):
    """使用 Selenium 自动登录
    
    Args:
        info: 账户信息字典
        headless: 是否使用无头模式（默认 True，后台运行）
    """
    import subprocess
    import sys as system
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("\n❌ 未安装 Selenium，正在安装...")
        subprocess.check_call([system.executable, "-m", "pip", "install", "selenium"])
        print("✅ Selenium 安装完成")
        print("🔄 正在重新加载模块...\n")
        
        # 重新导入
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
    
    # 配置 Chrome
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器界面
        chrome_options.add_argument('--no-sandbox')  # 提高兼容性
        chrome_options.add_argument('--disable-dev-shm-usage')  # 避免内存问题
        chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
        chrome_options.add_argument('--window-size=1920,1080')  # 设置虚拟窗口大小
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 隐藏自动化特征
    else:
        chrome_options.add_argument('--start-maximized')  # 最大化窗口
        chrome_options.add_experimental_option("detach", True)  # 浏览器不随脚本退出而关闭
    
    driver = None
    
    try:
        # 启动浏览器
        print("1️⃣ 启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 先访问主域名以设置 Cookie
        print("2️⃣ 访问 cursor.com...")
        driver.get("https://cursor.com/")
        time.sleep(1)  # 缩短等待时间
        
        # 清理所有旧 Cookie
        print("3️⃣ 清理旧的登录状态...")
        driver.delete_all_cookies()
        
        # 使用 Selenium 的 add_cookie 方法设置 Cookie（更可靠）
        print("4️⃣ 设置新的登录 Token...")
        cookie_value = f"{info['user_id']}::{info['token']}"
        
        try:
            driver.add_cookie({
                'name': 'WorkosCursorSessionToken',
                'value': cookie_value,
                'domain': '.cursor.com',
                'path': '/',
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
                document.cookie = "WorkosCursorSessionToken={cookie_value_encoded}; domain=.cursor.com; path=/; secure; SameSite=None; max-age=5184000";
            """)
        
        # 验证 Cookie 是否设置成功
        print("5️⃣ 验证登录状态...")
        cookies = driver.get_cookies()
        cursor_cookie = next((c for c in cookies if c['name'] == 'WorkosCursorSessionToken'), None)
        
        if cursor_cookie:
            print("✅ Cookie 设置成功！")
            print(f"   Cookie 值: {cursor_cookie['value'][:50]}...")
            
            # 跳转到 Dashboard 以验证登录
            print("6️⃣ 跳转到 Dashboard...")
            driver.get("https://www.cursor.com/dashboard")
            time.sleep(2)  # 缩短等待时间
            
            # 验证登录
            print("7️⃣ 检查登录状态...")
            try:
                # 检查当前 URL 是否跳转到认证页面
                current_url = driver.current_url
                print(f"   当前 URL: {current_url}")
                
                if "authenticator.cursor.sh" in current_url:
                    print("⚠️  页面跳转到了认证页面，Cookie 可能未生效")
                    print("🔄 尝试重新设置并跳转...")
                    
                    # 重新跳转回主页
                    driver.get("https://www.cursor.com/")
                    time.sleep(1)
                    
                    # 再次跳转到 dashboard
                    driver.get("https://www.cursor.com/dashboard")
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
                
            except Exception as e:
                print(f"⚠️  无法验证登录状态: {e}")
                print("但 Cookie 已设置")
                if driver and headless:
                    driver.quit()
                    print("✅ 浏览器已关闭")
                elif not headless:
                    print("✅ 浏览器将保持打开状态")
        else:
            print("❌ Cookie 设置失败")
            print("可能原因：浏览器阻止了 Cookie")
            if driver and headless:
                driver.quit()
                print("✅ 浏览器已关闭")
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


def main():
    """主函数"""
    # 解析命令行参数
    headless = True  # 默认无头模式
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--show', '--visible', '-v', '-s']:
            headless = False
    
    print("\n" + "="*60)
    print("🔐 Cursor 全自动登录工具")
    print("="*60)
    if headless:
        print("🔧 运行模式：后台无头模式（不显示浏览器）")
    else:
        print("🔧 运行模式：可视化模式（显示浏览器界面）")
    print("="*60)
    
    # 1. 获取 Token
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
    print("\n" + "="*60)
    print("📋 账户信息")
    print("="*60)
    print(f"📧 邮箱: {info['email']}")
    print(f"👤 User ID: {info['user_id']}")
    print(f"🔑 Token: {info['token'][:50]}...")
    print(f"⏰ 过期时间: {info['expiry']}")
    print("="*60)
    
    # 2. 开始自动登录
    success = auto_login_with_selenium(info, headless=headless)
    
    if success:
        print("\n✅ 自动登录完成！")
    else:
        print("\n❌ 自动登录失败")
        print("\n💡 手动登录方法：")
        print("1. 访问 https://www.cursor.com/")
        print("2. 按 F12 打开控制台")
        print("3. 粘贴以下代码：")
        print("\n" + "-"*60)
        cookie_value = f"{info['user_id']}%3A%3A{info['token']}"
        print(f'document.cookie="WorkosCursorSessionToken={cookie_value};domain=.cursor.com;path=/;secure;SameSite=None";location.reload();')
        print("-"*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

