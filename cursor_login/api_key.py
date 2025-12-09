"""
API Key 管理模块
负责创建 API Key 并保存到环境变量
"""

import os
import re
import time
from datetime import datetime
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .config import (
    CURSOR_INTEGRATIONS,
    API_KEY_PREFIX,
    ZSHRC_PATH,
    ENV_VAR_NAME,
    DEFAULT_TIMEOUT
)


def create_api_key(driver) -> Optional[str]:
    """
    自动创建 Cursor API Key

    Args:
        driver: Selenium WebDriver 实例

    Returns:
        成功返回 API Key 字符串，失败返回 None
    """
    try:
        print("\n8️⃣ 正在创建 API Key...")

        # 导航到 Integrations 页面
        print("   → 跳转到 Integrations 页面...")
        driver.get(CURSOR_INTEGRATIONS)
        time.sleep(2)

        # 查找并点击创建按钮
        api_key = _click_create_button(driver)
        if not api_key:
            return None

        print("   ✅ API Key 创建成功！")
        return api_key

    except Exception as e:
        print(f"   ❌ 创建 API Key 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def _click_create_button(driver) -> Optional[str]:
    """
    查找并点击 API Key 创建按钮，填写表单并提取 API Key

    Args:
        driver: Selenium WebDriver 实例

    Returns:
        成功返回 API Key，失败返回 None
    """
    try:
        print("   → 查找 API Key 创建按钮...")
        wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

        # 尝试查找不同的按钮文本
        button_texts = [
            "New User API Key",
            "New API Key",
            "User API Key"
        ]

        new_api_key_button = None
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

        # 填写 API Key 名称
        api_key_name = _fill_api_key_name(driver, wait)

        # 提交表单
        _submit_form(driver, wait)

        # 等待 API Key 生成
        print("   → 等待 API Key 生成...")
        time.sleep(3)

        # 提取 API Key
        api_key = _extract_api_key(driver)
        return api_key

    except Exception as e:
        print(f"   ⚠️  查找按钮失败: {e}")
        return None


def _fill_api_key_name(driver, wait) -> str:
    """
    填写 API Key 名称

    Args:
        driver: Selenium WebDriver 实例
        wait: WebDriverWait 实例

    Returns:
        API Key 名称
    """
    print("   → 填写 API Key 名称...")
    name_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter User API Key Name...']"))
    )

    # 生成唯一名称
    api_key_name = f"{API_KEY_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    name_input.send_keys(api_key_name)
    print(f"   → API Key 名称: {api_key_name}")

    return api_key_name


def _submit_form(driver, wait):
    """
    提交 API Key 创建表单

    Args:
        driver: Selenium WebDriver 实例
        wait: WebDriverWait 实例
    """
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
            name_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter User API Key Name...']")
            name_input.send_keys(Keys.RETURN)

        time.sleep(1)

    except Exception as e:
        print(f"   ⚠️  点击保存按钮失败，尝试按回车: {e}")
        name_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter User API Key Name...']")
        name_input.send_keys(Keys.RETURN)
        time.sleep(1)


def _extract_api_key(driver) -> Optional[str]:
    """
    从页面中提取 API Key

    Args:
        driver: Selenium WebDriver 实例

    Returns:
        成功返回 API Key，失败返回 None
    """
    api_key = None

    # 方法1：从页面源代码中提取
    try:
        print("   → 从页面源代码提取...")
        page_source = driver.page_source
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
                    match = re.search(r'key_[a-zA-Z0-9]{32,}', text)
                    if match:
                        api_key = match.group(0)
                        print(f"   ✅ 找到 API Key（备用方法）")
                        break
        except Exception as e:
            print(f"   ⚠️  备用方法失败: {e}")

    if not api_key:
        print("   ⚠️  无法自动提取 API Key，请在页面上手动复制")

    return api_key


def update_zshrc_with_api_key(api_key: str) -> bool:
    """
    更新 ~/.zshrc 中的 CURSOR_API_KEY 环境变量

    Args:
        api_key: API Key 字符串

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        # 读取现有内容
        if os.path.exists(ZSHRC_PATH):
            with open(ZSHRC_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []

        # 查找并更新环境变量
        api_key_line = f'export {ENV_VAR_NAME}="{api_key}"\n'
        found = False
        updated_lines = []

        for line in lines:
            # 如果找到已存在的环境变量，替换它
            if line.strip().startswith(f'export {ENV_VAR_NAME}='):
                updated_lines.append(api_key_line)
                found = True
                print(f"   → 更新现有的 {ENV_VAR_NAME}")
            else:
                updated_lines.append(line)

        # 如果没找到，添加到文件末尾
        if not found:
            # 确保文件末尾有换行
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'
            updated_lines.append('\n')
            updated_lines.append(f'# Cursor API Key (自动添加)\n')
            updated_lines.append(api_key_line)
            print(f"   → 添加新的 {ENV_VAR_NAME}")

        # 写回文件
        with open(ZSHRC_PATH, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        print(f"   ✅ 已写入 {ZSHRC_PATH}")
        print(f"   💡 运行 'source {ZSHRC_PATH}' 或重启终端以生效")
        return True

    except Exception as e:
        print(f"   ❌ 写入 {ZSHRC_PATH} 失败: {e}")
        return False
