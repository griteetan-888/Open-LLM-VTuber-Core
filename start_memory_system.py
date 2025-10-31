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
