# Cursor Auto Login Tool

Cursor 全自动登录工具 - 自动获取 Token、清理 Cookie、设置新 Token 并自动登录浏览器。

## 功能特性

- 🔐 **自动获取 Cursor Token** - 从本地数据库自动提取登录凭证
- 🧹 **自动清理浏览器 Cookie** - 清除旧的登录状态
- 🔑 **自动设置新 Token** - 在浏览器中自动配置登录凭证
- 🌐 **自动打开并登录浏览器** - 一键完成整个登录流程
- 🔧 **API Key 自动创建** - 自动创建并保存 Cursor API Key
- 📝 **环境变量自动配置** - 自动更新 `~/.zshrc` 中的 `CURSOR_API_KEY`
- 👁️ **支持无头/可视化模式** - 可选择后台运行或显示浏览器界面

## 系统要求

- macOS（理论上支持其他系统，需要修改数据库路径）
- Python 3.6+
- Chrome/Chromium 浏览器
- 已安装并登录过 Cursor 客户端

## 安装

### 1. 克隆仓库

```bash
git clone git@github.com:DanOps-1/auto_login_cursor-agent.git
cd auto_login_cursor-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 如果未安装 Selenium，脚本会自动安装。

## 项目结构

```
auto_login_cursor-agent/
├── cursor_login/           # 核心包
│   ├── __init__.py        # 包初始化
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库操作
│   ├── api_key.py         # API Key 管理
│   └── browser.py         # 浏览器自动化
├── main.py                # 主入口（推荐使用）
├── cursor_auto_login.py   # 兼容旧版的单文件脚本
├── requirements.txt       # 依赖配置
├── LICENSE               # MIT 许可证
└── README.md             # 项目文档
```

## 使用方法

### 基础用法（推荐使用新入口）

```bash
# 无头模式（后台运行，不显示浏览器界面）
python3 main.py

# 显示浏览器界面
python3 main.py --show
python3 main.py --visible
```

### 兼容旧版（单文件方式）

```bash
# 仍然支持原有的单文件脚本
python3 cursor_auto_login.py
python3 cursor_auto_login.py --show
```

### 命令行参数

- **无参数** / **默认**: 无头模式，浏览器在后台运行
- `--show` / `-s`: 显示浏览器界面
- `--visible` / `-v`: 显示浏览器界面（同 `--show`）

### 运行模式对比

| 模式 | 命令 | 特点 |
|------|------|------|
| 无头模式 | `python3 main.py` | 后台运行，自动关闭浏览器 |
| 可视化模式 | `python3 main.py --show` | 显示浏览器，保持打开状态 |

### 作为 Python 模块使用

```python
from cursor_login import get_cursor_token, auto_login_with_selenium

# 获取 Token
info = get_cursor_token()

# 自动登录（无头模式）
success = auto_login_with_selenium(info, headless=True)

# 自动登录（显示浏览器）
success = auto_login_with_selenium(info, headless=False)
```

## 工作流程

1. 📥 从本地数据库读取 Cursor Token
2. 🚀 启动 Chrome 浏览器
3. 🌐 访问 cursor.com
4. 🧹 清理所有旧 Cookie
5. 🔑 设置新的登录 Token
6. ✅ 验证登录状态
7. 🔐 自动创建 API Key
8. 📝 更新 `~/.zshrc` 环境变量
9. 🎉 完成登录

## 数据库路径

脚本默认从以下路径读取 Cursor 数据库：

```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

如果使用其他操作系统，请修改 `cursor_login/config.py` 中的 `DB_PATH` 变量。

## API Key 配置

脚本会自动：
1. 在 Cursor Dashboard 中创建新的 API Key
2. 将 API Key 写入 `~/.zshrc` 文件
3. 配置为环境变量 `CURSOR_API_KEY`

使用 API Key：

```bash
# 重新加载配置
source ~/.zshrc

# 验证 API Key
echo $CURSOR_API_KEY
```

## 故障排除

### 问题：无法获取 Cursor Token

**解决方案**:
- 确保 Cursor 客户端已安装
- 确保已经登录过 Cursor 客户端
- 检查数据库文件是否存在

### 问题：Cookie 设置失败

**解决方案**:
- 使用可视化模式运行查看详细过程
- 手动登录方法见脚本输出提示

### 问题：Chrome 驱动问题

**解决方案**:
- 确保 Chrome/Chromium 浏览器已安装
- Selenium 会自动管理 ChromeDriver

## 手动登录方法

如果自动登录失败，可以手动执行：

1. 访问 https://www.cursor.com/
2. 按 F12 打开浏览器控制台
3. 粘贴脚本输出的 JavaScript 代码
4. 刷新页面

## 安全说明

- 本工具仅在本地操作，不会上传任何数据
- Token 和 API Key 仅保存在本地
- 建议在个人设备上使用

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

DanOps-1

## 更新日志

### v2.0.0 (2025-12-09)
- 重构为模块化架构
- 将代码拆分为多个模块：config, database, api_key, browser
- 添加 main.py 作为新的主入口
- 保留 cursor_auto_login.py 以兼容旧版
- 支持作为 Python 包导入使用
- 改进代码组织和可维护性

### v1.0.0 (2024-10-24)
- 初始版本发布
- 支持自动登录功能
- 支持 API Key 自动创建
- 支持环境变量自动配置
