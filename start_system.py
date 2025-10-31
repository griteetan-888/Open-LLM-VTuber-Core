#!/usr/bin/env python3
"""
系统启动脚本
确保系统可以正常启动，包含记忆系统但不会因为记忆系统问题而崩溃
"""
import sys
import os
from loguru import logger

def check_system_health():
    """检查系统健康状态"""
    logger.info("🔍 检查系统健康状态...")
    
    try:
        # 测试基础导入
        from src.open_llm_vtuber.agent.agents.basic_memory_agent import BasicMemoryAgent
        from src.open_llm_vtuber.agent.agents.memory_enhanced_agent import MemoryEnhancedAgent
        from src.open_llm_vtuber.chat_history_manager import get_history, store_message
        
        logger.info("✅ 基础模块导入成功")
        
        # 测试记忆系统可用性
        try:
            from src.open_llm_vtuber.memory import MEMORY_AVAILABLE
            if MEMORY_AVAILABLE:
                logger.info("✅ 记忆系统可用")
            else:
                logger.warning("⚠️ 记忆系统不可用，将使用基本功能")
        except ImportError:
            logger.warning("⚠️ 记忆系统不可用，将使用基本功能")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 系统健康检查失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🚀 启动Open-LLM-VTuber系统...")
    logger.info("=" * 60)
    
    # 检查系统健康状态
    if not check_system_health():
        logger.error("❌ 系统健康检查失败，无法启动")
        return False
    
    logger.info("✅ 系统健康检查通过")
    logger.info("🎉 系统可以正常启动！")
    logger.info("=" * 60)
    
    # 显示系统状态
    logger.info("📊 系统状态:")
    logger.info("   • 基础Agent: ✅ 可用")
    logger.info("   • 记忆增强Agent: ✅ 可用")
    logger.info("   • 聊天历史管理: ✅ 可用")
    
    try:
        from src.open_llm_vtuber.memory import MEMORY_AVAILABLE
        if MEMORY_AVAILABLE:
            logger.info("   • 智能记忆系统: ✅ 可用")
        else:
            logger.info("   • 智能记忆系统: ⚠️ 不可用（使用基本功能）")
    except ImportError:
        logger.info("   • 智能记忆系统: ⚠️ 不可用（使用基本功能）")
    
    logger.info("=" * 60)
    logger.info("💡 使用建议:")
    logger.info("   1. 运行 python3 main.py 启动完整系统")
    logger.info("   2. 运行 python3 test_memory_system.py 测试记忆系统")
    logger.info("   3. 查看 conf.yaml 配置文件")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
