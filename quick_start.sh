#!/bin/bash
# Open-LLM-VTuber Core 快速启动脚本

echo "🚀 Open-LLM-VTuber Core 快速启动"
echo "=================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python 3.10+"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔄 激活虚拟环境..."
source venv/bin/activate

echo "📦 安装依赖..."
pip install -r requirements.txt

# 创建必要目录
mkdir -p logs models cache chat_history

# 检查配置文件
if [ ! -f "conf.yaml" ]; then
    if [ -f "conf.yaml.example" ]; then
        echo "⚙️  创建配置文件..."
        cp conf.yaml.example conf.yaml
    else
        echo "❌ 配置文件不存在"
        exit 1
    fi
fi

echo "🎭 启动服务器..."
echo "📱 请在浏览器中访问: http://localhost:12393"
echo "⚠️  按 Ctrl+C 停止服务器"
echo ""

python start.py
