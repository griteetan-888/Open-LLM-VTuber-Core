#!/usr/bin/env python3
"""
Open-LLM-VTuber Core 安装脚本
自动安装依赖和设置环境
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python版本过低，需要Python 3.10或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装Python依赖"""
    print("📦 安装Python依赖...")
    
    # 检查是否有pip
    if not run_command("pip --version", "检查pip"):
        print("❌ pip未安装，请先安装pip")
        return False
    
    # 升级pip
    run_command("pip install --upgrade pip", "升级pip")
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装项目依赖"):
        print("❌ 依赖安装失败")
        return False
    
    return True

def setup_directories():
    """创建必要的目录"""
    print("📁 创建必要目录...")
    
    directories = [
        "logs",
        "models", 
        "cache",
        "chat_history"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True

def download_models():
    """下载必要的模型文件"""
    print("🤖 下载模型文件...")
    
    # 这里可以添加模型下载逻辑
    # 由于模型文件较大，建议用户手动下载
    print("ℹ️  模型文件需要手动下载，请参考README.md中的说明")
    
    return True

def create_config():
    """创建配置文件"""
    print("⚙️  设置配置文件...")
    
    if not Path("conf.yaml").exists():
        if Path("conf_simple.yaml").exists():
            # 复制简化配置作为默认配置
            import shutil
            shutil.copy("conf_simple.yaml", "conf.yaml")
            print("✅ 已创建默认配置文件 conf.yaml")
        else:
            print("⚠️  未找到配置文件模板")
            return False
    else:
        print("✅ 配置文件已存在")
    
    return True

def main():
    """主安装流程"""
    print("🚀 Open-LLM-VTuber Core 安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建目录
    if not setup_directories():
        print("❌ 目录创建失败")
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 创建配置
    if not create_config():
        print("❌ 配置创建失败")
        sys.exit(1)
    
    # 下载模型（可选）
    download_models()
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("\n📋 下一步操作:")
    print("1. 编辑 conf.yaml 文件，配置你的API密钥")
    print("2. 运行 python start.py 启动服务器")
    print("3. 在浏览器中访问 http://localhost:12393")
    print("\n💡 提示:")
    print("- 首次运行需要下载模型文件，请确保网络连接正常")
    print("- 查看 README.md 获取详细使用说明")
    print("- 如有问题，请查看日志文件 logs/")

if __name__ == "__main__":
    main()
