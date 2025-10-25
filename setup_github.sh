#!/bin/bash
set -e

REPO_NAME="Open-LLM-VTuber-Core"
REPO_DESC="Open-LLM-VTuber Core - 精简版VTuber AI聊天系统"
GITHUB_USER="griteetan-888"

echo "🚀 设置 $REPO_NAME GitHub 仓库"
echo "=================================================="

########################################
# 1. 确认当前目录是 git 仓库
########################################
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ 当前目录还不是 Git 仓库，正在初始化..."
  git init
  git add .
  git commit -m "Initial commit"
else
  echo "✅ Git 仓库状态正常"
fi

# 确保当前分支叫 main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "🔁 将当前分支重命名为 main..."
  git branch -M main
fi

########################################
# helper: 统一函数
########################################

set_remote_ssh () {
  echo "🔗 使用 SSH 配置远程仓库..."
  git remote remove origin 2>/dev/null || true
  git remote add origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
  echo "✅ origin -> git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
}

push_main () {
  echo "📤 推送 main 到 GitHub..."
  git push -u origin main
  echo "✨ 推送完成"
}

########################################
# 2. 优先使用 GitHub CLI (gh)
########################################
if command -v gh >/dev/null 2>&1; then
  echo "✅ 检测到 GitHub CLI (gh)"

  # 2.1 是否已经登录 gh
  if ! gh auth status >/dev/null 2>&1; then
    echo "⚠️  gh 还没有登录，开始登录流程..."
    gh auth login
  else
    echo "✅ gh 已登录"
  fi

  # 2.2 如果 GitHub 上还没有这个仓库，就创建它
  if ! gh repo view "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
    echo "📦 远程仓库不存在，正在创建 GitHub 仓库 ${GITHUB_USER}/${REPO_NAME} ..."
    gh repo create "${GITHUB_USER}/${REPO_NAME}" \
      --public \
      --description "${REPO_DESC}" \
      --source . \
      --remote origin \
      --push
    echo "✅ 仓库已创建并首次推送完成"
    exit 0
  else
    echo "ℹ️ 远程仓库已存在，跳过创建步骤"
  fi

  # 2.3 如果仓库已经存在：我们只需要把远程指到 SSH 并推送
  set_remote_ssh
  push_main
  exit 0
fi

########################################
# 3. 没有 gh → 使用 Personal Access Token 走 HTTPS
########################################
echo "⚠️  未检测到 gh (GitHub CLI)。"
echo "👉  两个选择："
echo "   (A) 推荐：安装 gh 再跑一次脚本，比如: brew install gh"
echo "   (B) 现在就推，用 Personal Access Token (PAT)"

read -p "是否现在使用 PAT 推送? [y/N]: " USE_PAT
if [[ "$USE_PAT" != "y" && "$USE_PAT" != "Y" ]]; then
  echo "❌ 已取消推送。安装 gh 后重新运行本脚本即可自动创建并推送。"
  exit 1
fi

echo ""
echo "🔐 请输入你的 GitHub Personal Access Token (PAT)"
echo "   生成方式: GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)"
echo "   需要至少勾选 repo 权限"
read -p "PAT: " PAT

if [ -z "$PAT" ]; then
  echo "❌ 没有输入 PAT，中止。"
  exit 1
fi

# 如果远程没建，你需要先在网页手动建一个空仓库：
# https://github.com/new  名称: $REPO_NAME  公开: Public
# 之后我们只负责设 remote+push
echo "🔗 配置 HTTPS 远程 (内嵌 Token，不会再问你密码)..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GITHUB_USER}:${PAT}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
echo "✅ origin -> https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

push_main