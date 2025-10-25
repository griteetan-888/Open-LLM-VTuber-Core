#!/bin/bash

# Open-LLM-VTuber-Core GitHub 仓库设置脚本
# 使用方法: ./setup_github.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="Open-LLM-VTuber-Core"
GITHUB_USERNAME="griteetan-888"
REPO_NAME="Open-LLM-VTuber-Core"

echo -e "${BLUE}🚀 设置 Open-LLM-VTuber-Core GitHub 仓库${NC}"
echo "=================================================="

# 检查是否在正确的目录
if [ ! -f "conf.yaml" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查Git状态
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 错误: 未找到Git仓库，请先运行 git init${NC}"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  警告: 检测到未提交的更改${NC}"
    echo "请先提交所有更改，然后重新运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ Git仓库状态正常${NC}"

# 创建GitHub仓库（需要GitHub CLI）
if command -v gh &> /dev/null; then
    echo -e "${BLUE}📦 使用GitHub CLI创建仓库...${NC}"
    
    # 检查仓库是否已存在
    if gh repo view "$GITHUB_USERNAME/$REPO_NAME" &> /dev/null; then
        echo -e "${YELLOW}⚠️  仓库 $GITHUB_USERNAME/$REPO_NAME 已存在${NC}"
        read -p "是否要重新创建？这将删除现有仓库 (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}🗑️  删除现有仓库...${NC}"
            gh repo delete "$GITHUB_USERNAME/$REPO_NAME" --yes
        else
            echo -e "${BLUE}📝 使用现有仓库...${NC}"
        fi
    fi
    
    # 创建仓库
    echo -e "${BLUE}🆕 创建GitHub仓库...${NC}"
    gh repo create "$REPO_NAME" \
        --public \
        --description "Open-LLM-VTuber Core - 精简版VTuber AI聊天系统" \
        --add-readme \
        --clone=false
    
    echo -e "${GREEN}✅ GitHub仓库创建成功${NC}"
else
    echo -e "${YELLOW}⚠️  未找到GitHub CLI (gh)${NC}"
    echo "请手动在GitHub上创建仓库: https://github.com/new"
    echo "仓库名称: $REPO_NAME"
    echo "描述: Open-LLM-VTuber Core - 精简版VTuber AI聊天系统"
    echo "设置为公开仓库"
    echo ""
    read -p "创建完成后按Enter继续..."
fi

# 添加远程仓库
echo -e "${BLUE}🔗 添加远程仓库...${NC}"
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  远程仓库已存在，更新URL...${NC}"
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
}

# 推送代码到GitHub
echo -e "${BLUE}📤 推送代码到GitHub...${NC}"
git push -u origin main

# 创建初始标签
echo -e "${BLUE}🏷️  创建版本标签...${NC}"
git tag -a v1.2.0 -m "Release version 1.2.0 - 初始版本"
git push origin v1.2.0

# 创建develop分支
echo -e "${BLUE}🌿 创建develop分支...${NC}"
git checkout -b develop
git push -u origin develop
git checkout main

echo ""
echo -e "${GREEN}🎉 GitHub仓库设置完成！${NC}"
echo "=================================================="
echo -e "${BLUE}📋 仓库信息:${NC}"
echo "  • 仓库URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  • 主分支: main"
echo "  • 开发分支: develop"
echo "  • 当前版本: v1.2.0"
echo ""
echo -e "${BLUE}📝 下一步操作:${NC}"
echo "  1. 访问 https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  2. 配置仓库设置（分支保护、协作者等）"
echo "  3. 创建第一个Issue或Pull Request"
echo "  4. 开始开发新功能"
echo ""
echo -e "${BLUE}🔧 常用命令:${NC}"
echo "  • 查看状态: git status"
echo "  • 创建功能分支: git checkout -b feature/新功能名称"
echo "  • 提交更改: git add . && git commit -m 'feat: 描述'"
echo "  • 推送分支: git push origin 分支名称"
echo "  • 创建PR: 在GitHub网页上创建Pull Request"
echo ""
echo -e "${GREEN}✨ 版本控制管理系统已就绪！${NC}"
