#!/usr/bin/env python3
"""
基础系统测试脚本
测试系统是否可以正常运行，不依赖记忆系统
"""
import sys
import os
from loguru import logger

def test_basic_imports():
    """测试基础导入"""
    logger.info("🧪 测试基础导入...")
    
    try:
        # 测试基础模块导入
        from src.open_llm_vtuber.agent.agents.basic_memory_agent import BasicMemoryAgent
        logger.info("✅ BasicMemoryAgent 导入成功")
        
        from src.open_llm_vtuber.agent.agents.memory_enhanced_agent import MemoryEnhancedAgent
        logger.info("✅ MemoryEnhancedAgent 导入成功")
        
        from src.open_llm_vtuber.chat_history_manager import get_history, store_message
        logger.info("✅ 聊天历史管理器 导入成功")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ 导入失败: {e}")
        return False

def test_memory_system_availability():
    """测试记忆系统可用性"""
    logger.info("🧠 测试记忆系统可用性...")
    
    try:
        from src.open_llm_vtuber.memory import MEMORY_AVAILABLE
        if MEMORY_AVAILABLE:
            logger.info("✅ 记忆系统可用")
            return True
        else:
            logger.warning("⚠️ 记忆系统不可用，将使用基本功能")
            return True
            
    except ImportError as e:
        logger.warning(f"⚠️ 记忆系统不可用: {e}")
        return True

def test_agent_creation():
    """测试Agent创建"""
    logger.info("🤖 测试Agent创建...")
    
    try:
        # 模拟LLM接口
        class MockLLM:
            def generate(self, prompt, **kwargs):
                return "测试响应"
        
        # 测试BasicMemoryAgent
        from src.open_llm_vtuber.agent.agents.basic_memory_agent import BasicMemoryAgent
        
        mock_llm = MockLLM()
        agent = BasicMemoryAgent(
            llm=mock_llm,
            system="你是一个测试助手",
            live2d_model=None
        )
        
        logger.info("✅ BasicMemoryAgent 创建成功")
        
        # 测试MemoryEnhancedAgent
        from src.open_llm_vtuber.agent.agents.memory_enhanced_agent import MemoryEnhancedAgent
        
        enhanced_agent = MemoryEnhancedAgent(
            llm=mock_llm,
            system="你是一个测试助手",
            live2d_model=None,
            enable_memory_compression=False  # 禁用记忆压缩以避免依赖问题
        )
        
        logger.info("✅ MemoryEnhancedAgent 创建成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent创建失败: {e}")
        return False

def test_chat_history():
    """测试聊天历史功能"""
    logger.info("💬 测试聊天历史功能...")
    
    try:
        from src.open_llm_vtuber.chat_history_manager import create_new_history, store_message, get_history
        
        # 创建测试历史
        conf_uid = "test_conf"
        history_uid = create_new_history(conf_uid)
        
        if history_uid:
            logger.info(f"✅ 创建历史成功: {history_uid}")
            
            # 存储测试消息
            store_message(conf_uid, history_uid, "human", "测试消息", "测试用户")
            store_message(conf_uid, history_uid, "ai", "测试回复", "AI助手")
            
            # 获取历史
            messages = get_history(conf_uid, history_uid)
            logger.info(f"✅ 获取历史成功: {len(messages)} 条消息")
            
            return True
        else:
            logger.error("❌ 创建历史失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 聊天历史测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始基础系统测试...")
    logger.info("=" * 50)
    
    test_results = []
    
    # 1. 测试基础导入
    result1 = test_basic_imports()
    test_results.append(("基础导入", result1))
    
    # 2. 测试记忆系统可用性
    result2 = test_memory_system_availability()
    test_results.append(("记忆系统", result2))
    
    # 3. 测试Agent创建
    result3 = test_agent_creation()
    test_results.append(("Agent创建", result3))
    
    # 4. 测试聊天历史
    result4 = test_chat_history()
    test_results.append(("聊天历史", result4))
    
    # 生成测试报告
    logger.info("📊 测试报告")
    logger.info("=" * 50)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 所有测试通过！系统可以正常运行")
        return True
    else:
        logger.error("❌ 部分测试失败，系统可能存在问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
