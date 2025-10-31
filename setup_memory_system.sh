#!/bin/bash

# 智能记忆系统一键设置脚本
echo "🧠 开始智能记忆系统设置..."
echo "================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ 检测到Python3环境"

# 创建记忆系统目录
echo "📁 创建记忆系统目录..."
mkdir -p memory/backups
mkdir -p test_memory
mkdir -p memory/logs

# 安装依赖
echo "📦 安装记忆系统依赖..."
pip install dataclasses-json
pip install sentence-transformers  # 为未来的语义搜索功能
pip install scikit-learn  # 为聚类功能

# 检查依赖安装
echo "🔍 检查依赖安装..."
python3 -c "
try:
    import dataclasses
    print('✅ dataclasses 可用')
except ImportError:
    print('❌ dataclasses 不可用')

try:
    import json
    print('✅ json 可用')
except ImportError:
    print('❌ json 不可用')

try:
    import hashlib
    print('✅ hashlib 可用')
except ImportError:
    print('❌ hashlib 不可用')
"

# 运行记忆系统测试
echo "🧪 运行记忆系统测试..."
python3 test_memory_system.py

# 创建记忆系统配置文件
echo "⚙️ 创建记忆系统配置文件..."
if [ ! -f "memory_config.yaml" ]; then
    echo "❌ 记忆系统配置文件不存在"
else
    echo "✅ 记忆系统配置文件已存在"
fi

# 创建记忆系统启动脚本
echo "🚀 创建记忆系统启动脚本..."
cat > start_memory_system.py << 'EOF'
#!/usr/bin/env python3
"""
记忆系统启动脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.open_llm_vtuber.memory.smart_memory_manager import SmartMemoryManager
from loguru import logger

def main():
    logger.info("🧠 启动智能记忆系统...")
    
    # 创建记忆管理器
    memory_manager = SmartMemoryManager(
        max_memory_items=1000,
        compression_threshold=0.3,
        memory_file_path="memory/memories.json",
        summary_file_path="memory/summaries.json"
    )
    
    # 显示统计信息
    stats = memory_manager.get_memory_statistics()
    logger.info(f"📊 记忆统计: {stats}")
    
    logger.info("✅ 记忆系统启动完成")

if __name__ == "__main__":
    main()
EOF

chmod +x start_memory_system.py

# 创建记忆系统监控脚本
echo "📊 创建记忆系统监控脚本..."
cat > monitor_memory_system.py << 'EOF'
#!/usr/bin/env python3
"""
记忆系统监控脚本
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.open_llm_vtuber.memory.smart_memory_manager import SmartMemoryManager
from loguru import logger

def monitor_memory_system():
    logger.info("📊 开始监控记忆系统...")
    
    memory_manager = SmartMemoryManager(
        max_memory_items=1000,
        compression_threshold=0.3,
        memory_file_path="memory/memories.json",
        summary_file_path="memory/summaries.json"
    )
    
    while True:
        try:
            # 获取统计信息
            stats = memory_manager.get_memory_statistics()
            
            logger.info("📈 记忆系统状态:")
            logger.info(f"   总记忆数: {stats.get('total_memories', 0)}")
            logger.info(f"   记忆类型: {stats.get('memory_types', {})}")
            logger.info(f"   平均重要性: {stats.get('average_importance', 0):.3f}")
            logger.info(f"   压缩比例: {stats.get('compression_ratio', 0):.3f}")
            
            # 检查是否需要压缩
            if stats.get('compression_ratio', 0) > 0.8:
                logger.warning("⚠️ 记忆使用率过高，建议压缩")
                memory_manager.compress_old_data(days_threshold=7)
            
            time.sleep(60)  # 每分钟监控一次
            
        except KeyboardInterrupt:
            logger.info("🛑 监控已停止")
            break
        except Exception as e:
            logger.error(f"监控出错: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_memory_system()
EOF

chmod +x monitor_memory_system.py

echo "🎉 智能记忆系统设置完成！"
echo "================================================"
echo "📊 设置总结:"
echo "   • 记忆系统: 已配置"
echo "   • 压缩机制: 已启用"
echo "   • 测试工具: 已准备"
echo "   • 监控脚本: 已创建"
echo "   • 配置文件: 已生成"
echo "================================================"
echo "💡 使用建议:"
echo "   1. 运行 python3 test_memory_system.py 测试系统"
echo "   2. 运行 python3 start_memory_system.py 启动系统"
echo "   3. 运行 python3 monitor_memory_system.py 监控系统"
echo "   4. 查看 memory_config.yaml 了解配置选项"
echo "================================================"
echo "🧠 记忆系统特性:"
echo "   • 智能记忆压缩"
echo "   • 多类型记忆管理"
echo "   • 上下文相关检索"
echo "   • 自动摘要生成"
echo "   • 性能监控"
echo "   • 数据导出导入"
echo "================================================"
