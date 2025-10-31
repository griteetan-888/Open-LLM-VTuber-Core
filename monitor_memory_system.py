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
