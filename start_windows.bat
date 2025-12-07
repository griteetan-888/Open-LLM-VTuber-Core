@echo off
chcp 65001 >nul
echo ========================================
echo   Open-LLM-VTuber Windows 启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ 错误: 未找到 Python
        echo.
        echo 请先安装 Python 3.10 或更高版本
        echo 下载地址: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ 检测到 Python
%PYTHON_CMD% --version
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 📦 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  未找到虚拟环境
    echo.
    set /p create_venv="是否创建虚拟环境? (Y/N): "
    if /i "!create_venv!"=="Y" (
        echo 正在创建虚拟环境...
        %PYTHON_CMD% -m venv venv
        if %errorlevel% equ 0 (
            echo ✅ 虚拟环境创建成功
            call venv\Scripts\activate.bat
            echo.
            set /p install_deps="是否安装依赖? (Y/N): "
            if /i "!install_deps!"=="Y" (
                echo 正在安装依赖...
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
            )
        ) else (
            echo ❌ 虚拟环境创建失败
            pause
            exit /b 1
        )
    ) else (
        echo 使用系统 Python 继续...
    )
)

echo.

REM 检查端口是否被占用
netstat -ano | findstr :12393 >nul
if %errorlevel% equ 0 (
    echo ⚠️  端口 12393 已被占用！
    echo.
    echo 占用端口的进程:
    netstat -ano | findstr :12393
    echo.
    set /p choice="是否关闭占用端口的进程? (Y/N): "
    if /i "%choice%"=="Y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :12393') do (
            echo 正在关闭进程 %%a...
            taskkill /PID %%a /F >nul 2>&1
        )
        echo ✅ 进程已关闭
        timeout /t 2 >nul
    ) else (
        echo 使用其他端口启动...
        set PORT=12394
        goto :start_server
    )
)

set PORT=12393

:start_server
echo.
echo ========================================
echo   服务器信息
echo ========================================
echo   本机访问: http://localhost:%PORT%
echo.

REM 获取本机 IP（如果配置了 0.0.0.0）
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP:~1%

if not "%IP%"=="" (
    echo   局域网访问: http://%IP%:%PORT%
    echo.
)

echo ========================================
echo.
echo 💡 提示:
echo   - 确保 conf.yaml 中已配置 API 密钥
echo   - 按 Ctrl+C 停止服务器
echo.
echo 🚀 正在启动服务器...
echo.

%PYTHON_CMD% start.py --host 0.0.0.0 --port %PORT%

echo.
echo 服务器已停止
pause

