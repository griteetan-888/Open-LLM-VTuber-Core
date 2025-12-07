# Windows 系统运行指南

本指南详细介绍如何在 Windows 系统上运行 Open-LLM-VTuber 项目。

## 📋 目录

1. [环境准备](#环境准备)
2. [安装步骤](#安装步骤)
3. [配置设置](#配置设置)
4. [启动运行](#启动运行)
5. [常见问题](#常见问题)

---

## 环境准备

### 1. 安装 Python

#### 检查是否已安装 Python

打开 **命令提示符（CMD）** 或 **PowerShell**，运行：

```cmd
python --version
```

或

```cmd
python3 --version
```

如果显示版本号（如 `Python 3.11.x`），说明已安装。

#### 如果没有安装 Python

1. 访问 Python 官网：https://www.python.org/downloads/
2. 下载最新版本的 Python 3.10 或更高版本（推荐 3.11 或 3.12）
3. 运行安装程序，**重要**：勾选 "Add Python to PATH"
4. 点击 "Install Now" 完成安装

#### 验证安装

重新打开命令提示符，运行：

```cmd
python --version
```

应该显示 Python 版本号。

### 2. 安装 Git（可选，如果需要从 Git 克隆）

如果项目是从 Git 仓库获取的，需要安装 Git：

1. 访问：https://git-scm.com/download/win
2. 下载并安装 Git for Windows
3. 安装时选择 "Git Bash Here" 选项

---

## 安装步骤

### 步骤 1：获取项目文件

确保你已经有了项目文件夹，包含以下文件：
- `start.py`
- `conf.yaml`
- `requirements.txt`
- `src/` 目录
- 其他项目文件

### 步骤 2：打开命令提示符

1. 在项目文件夹中，按住 `Shift` 键，右键点击空白处
2. 选择 "在此处打开 PowerShell 窗口" 或 "在此处打开命令提示符窗口"

或者：

1. 按 `Win + R`，输入 `cmd`，按回车
2. 使用 `cd` 命令进入项目目录：
   ```cmd
   cd C:\path\to\Open-LLM-VTuber-Core
   ```

### 步骤 3：创建虚拟环境（推荐）

**为什么要使用虚拟环境？**
- 避免与系统 Python 包冲突
- 保持项目依赖独立
- 便于管理不同项目的依赖

#### 创建虚拟环境

```cmd
python -m venv venv
```

#### 激活虚拟环境

```cmd
venv\Scripts\activate
```

激活后，命令提示符前面会显示 `(venv)`。

**注意**：每次打开新的命令提示符窗口都需要重新激活虚拟环境。

### 步骤 4：安装依赖

在激活虚拟环境后，运行：

```cmd
pip install -r requirements.txt
```

**如果下载慢**，可以使用国内镜像：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

安装过程可能需要几分钟，请耐心等待。

### 步骤 5：安装 FFmpeg（可选，但推荐）

如果看到 `ffmpeg` 相关的警告，可以安装 FFmpeg：

#### 使用 Chocolatey（推荐）

1. 以管理员身份打开 PowerShell
2. 安装 Chocolatey（如果还没有）：
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. 安装 FFmpeg：
   ```powershell
   choco install ffmpeg
   ```

#### 手动安装

1. 下载：https://www.gyan.dev/ffmpeg/builds/
2. 解压到 `C:\ffmpeg`
3. 添加到系统 PATH：
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 编辑"系统变量"中的 `Path`
   - 添加：`C:\ffmpeg\bin`

---

## 配置设置

### 1. 编辑配置文件

打开项目文件夹中的 `conf.yaml` 文件，使用记事本或其他文本编辑器。

### 2. 配置 API 密钥

找到 `openai_llm` 部分，填入你的 OpenAI API 密钥：

```yaml
llm_configs:
  openai_llm:
    base_url: 'https://api.openai.com/v1'
    llm_api_key: 'YOUR_OPENAI_API_KEY_HERE'  # 替换为你的真实 API 密钥
    model: 'gpt-3.5-turbo'  # 或使用其他模型
```

### 3. 配置服务器地址（如果需要外部访问）

找到 `system_config` 部分：

```yaml
system_config:
  host: '0.0.0.0'  # 改为 0.0.0.0 允许外部访问，localhost 只能本机访问
  port: 12393       # 端口号，如果被占用可以改为其他端口（如 12394）
```

**说明**：
- `host: 'localhost'`：只能本机访问
- `host: '0.0.0.0'`：允许局域网和公网访问
- `port: 12393`：如果端口被占用，改为其他端口（如 12394、8080 等）

### 4. 保存配置文件

保存 `conf.yaml` 文件。

---

## 启动运行

### 方法 1：使用 start.py（推荐）

在命令提示符中（确保已激活虚拟环境），运行：

```cmd
python start.py
```

如果需要指定主机和端口：

```cmd
python start.py --host 0.0.0.0 --port 12393
```

### 方法 2：使用 run_server.py

```cmd
python run_server.py
```

**注意**：`run_server.py` 需要 `upgrade_codes` 模块，如果报错，使用 `start.py`。

### 启动成功标志

如果看到类似以下输出，说明启动成功：

```
🚀 启动 Open-LLM-VTuber Core 服务器
✅ 配置文件加载成功
✅ 服务器初始化成功
🔄 正在初始化服务器上下文...
✅ 服务器上下文初始化成功
🌐 服务器启动在 0.0.0.0:12393
📱 请在浏览器中访问: http://0.0.0.0:12393
```

### 访问界面

打开浏览器，访问：

- **本机访问**：`http://localhost:12393`
- **局域网访问**：`http://你的IP地址:12393`（需要先配置 `host: '0.0.0.0'`）

### 停止服务器

在命令提示符中按 `Ctrl + C` 停止服务器。

---

## 常见问题

### Q1: `python: command not found` 或 `'python' 不是内部或外部命令`

**解决方案**：
1. 检查 Python 是否已安装：`python --version`
2. 如果没有安装，参考[环境准备](#环境准备)部分安装 Python
3. 如果已安装但找不到，检查 PATH 环境变量是否包含 Python 路径

### Q2: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
1. 确保已激活虚拟环境（命令提示符前有 `(venv)`）
2. 重新安装依赖：`pip install -r requirements.txt`
3. 如果某个包安装失败，单独安装：`pip install 包名`

### Q3: 端口被占用 `[WinError 10048]`

**解决方案**：

**查找并关闭占用端口的进程**：

在 PowerShell 中运行：

```powershell
Get-NetTCPConnection -LocalPort 12393 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

或在 CMD 中运行：

```cmd
for /f "tokens=5" %a in ('netstat -ano ^| findstr :12393') do taskkill /PID %a /F
```

**或更换端口**：

修改 `conf.yaml` 中的端口号，或使用命令行参数：

```cmd
python start.py --host 0.0.0.0 --port 12394
```

### Q4: `RuntimeWarning: couldn't find ffmpeg`

**解决方案**：
- 这是警告，不影响基本功能
- 如果需要音频处理功能，参考[安装 FFmpeg](#步骤-5安装-ffmpeg可选但推荐)部分

### Q5: 无法从其他设备访问

**检查清单**：
1. ✅ `conf.yaml` 中 `host` 是否设置为 `0.0.0.0`？
2. ✅ 防火墙是否允许端口访问？
3. ✅ 设备是否在同一网络？
4. ✅ IP 地址是否正确？

**配置防火墙**：

1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 选择"入站规则" → "新建规则"
4. 选择"端口" → TCP → 特定本地端口：`12393`
5. 允许连接 → 完成

### Q6: `Failed to start VAD: TypeError: Cannot read properties of undefined`

**解决方案**：
- 如果通过 HTTP 访问（非 localhost），需要使用 HTTPS
- 使用 ngrok 提供 HTTPS：`ngrok http 12393`
- 或只使用文本输入，不启用麦克风功能

### Q7: 依赖安装很慢

**解决方案**：使用国内镜像源

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q8: 虚拟环境激活失败

**解决方案**：

如果 `venv\Scripts\activate` 报错，尝试：

```cmd
.\venv\Scripts\activate
```

或使用 PowerShell：

```powershell
.\venv\Scripts\Activate.ps1
```

如果 PowerShell 提示"无法加载脚本"，运行：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 快速启动脚本

创建一个批处理文件 `start_server.bat`：

```batch
@echo off
echo 启动 Open-LLM-VTuber 服务器
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统 Python
)

REM 检查端口是否被占用
netstat -ano | findstr :12393 >nul
if %errorlevel% equ 0 (
    echo ⚠️  端口 12393 已被占用！
    echo.
    set /p choice="是否关闭占用端口的进程? (Y/N): "
    if /i "%choice%"=="Y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :12393') do (
            taskkill /PID %%a /F >nul 2>&1
        )
        echo ✅ 进程已关闭
        timeout /t 2 >nul
    ) else (
        echo 使用其他端口启动...
        python start.py --host 0.0.0.0 --port 12394
        pause
        exit /b
    )
)

echo.
echo 🚀 启动服务器...
echo 📱 访问地址: http://localhost:12393
echo.
echo 按 Ctrl+C 停止服务器
echo.

python start.py --host 0.0.0.0 --port 12393

pause
```

使用方法：
1. 将上述内容保存为 `start_server.bat`
2. 双击运行即可

---

## 完整安装流程总结

1. ✅ 安装 Python 3.10+（勾选 Add to PATH）
2. ✅ 打开命令提示符，进入项目目录
3. ✅ 创建虚拟环境：`python -m venv venv`
4. ✅ 激活虚拟环境：`venv\Scripts\activate`
5. ✅ 安装依赖：`pip install -r requirements.txt`
6. ✅ 配置 `conf.yaml`（API 密钥、host、port）
7. ✅ 启动服务器：`python start.py`
8. ✅ 浏览器访问：`http://localhost:12393`

---

## 获取帮助

如果遇到问题：

1. 查看日志文件：`logs/debug_YYYY-MM-DD.log`
2. 检查配置文件：`conf.yaml`
3. 确认依赖安装：`pip list`
4. 查看错误信息：仔细阅读控制台输出的错误信息

---

## 注意事项

1. **API 密钥安全**：不要将包含真实 API 密钥的 `conf.yaml` 提交到 Git
2. **端口占用**：如果端口被占用，更换端口或关闭占用进程
3. **防火墙**：允许外部访问需要配置防火墙
4. **虚拟环境**：每次打开新终端都需要重新激活虚拟环境
5. **Python 版本**：确保使用 Python 3.10 或更高版本

---

祝使用愉快！🎉

