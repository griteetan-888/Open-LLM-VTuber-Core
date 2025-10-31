#!/bin/bash

# LLM-VTuber快速性能优化脚本
echo "🚀 开始LLM-VTuber性能优化..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip install psutil loguru pyyaml

# 运行性能优化
echo "🔧 运行性能优化..."
python3 optimize_performance.py

# 检查优化结果
if [ -f "optimization_report.json" ]; then
    echo "✅ 优化完成！查看报告: optimization_report.json"
else
    echo "❌ 优化失败"
    exit 1
fi

# 启动优化后的系统
echo "🎯 启动优化后的VTuber系统..."
python3 start.py

echo "🎉 优化完成！系统已启动"
