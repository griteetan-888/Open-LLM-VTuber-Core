#!/bin/bash

# Open-LLM-VTuber 服务器部署脚本
# 使用方法: ./deploy.sh

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Open-LLM-VTuber 服务器部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${GREEN}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装/更新依赖
echo -e "${GREEN}安装依赖包...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 检查配置文件
if [ ! -f "conf.yaml" ]; then
    echo -e "${YELLOW}警告: 未找到 conf.yaml，请从 conf.yaml.example 创建${NC}"
    if [ -f "conf.yaml.example" ]; then
        cp conf.yaml.example conf.yaml
        echo -e "${GREEN}已从 conf.yaml.example 创建 conf.yaml${NC}"
    fi
fi

# 检查 host 配置
if grep -q "host: 'localhost'" conf.yaml; then
    echo -e "${YELLOW}检测到 host 配置为 localhost${NC}"
    echo -e "${YELLOW}是否要修改为 0.0.0.0 以允许外部访问? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # 使用 sed 修改配置（macOS 和 Linux 兼容）
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/host: 'localhost'/host: '0.0.0.0'/" conf.yaml
        else
            sed -i "s/host: 'localhost'/host: '0.0.0.0'/" conf.yaml
        fi
        echo -e "${GREEN}已修改 host 为 0.0.0.0${NC}"
    fi
fi

# 创建必要的目录
echo -e "${GREEN}创建必要的目录...${NC}"
mkdir -p logs
mkdir -p cache
mkdir -p models

# 检查前端文件
if [ ! -f "frontend/index.html" ]; then
    echo -e "${YELLOW}警告: 未找到前端文件${NC}"
    echo -e "${YELLOW}如果是 Git 子模块，请运行: git submodule update --init --recursive${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署准备完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "下一步："
echo "1. 编辑 conf.yaml 配置 API 密钥和其他设置"
echo "2. 运行服务器:"
echo "   source venv/bin/activate"
echo "   python run_server.py"
echo ""
echo "或使用 systemd 服务（见 SERVER_DEPLOYMENT_GUIDE.md）"
echo ""

