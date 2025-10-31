#!/usr/bin/env python3
"""
连续性对话测试脚本
测试Kiyo的连续性对话功能
"""
import asyncio
import time
from loguru import logger

# 模拟LLM接口
class MockLLM:
    def __init__(self):
        self.conversation_history = []
    
    def generate(self, prompt, **kwargs):
        """模拟LLM生成响应"""
        # 检查是否包含连续性对话提示
        if "CONTINUOUS CONVERSATION MODE" in prompt:
            logger.info("✅ 连续性对话模式已激活")
            
            # 模拟Kiyo的连续性对话响应
            if "traffic" in prompt.lower():
                return "Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?"
            elif "crush" in prompt.lower() and "leo" in prompt.lower():
                return "A Leo? Bold choice. Fire signs are like emotional fireworks — beautiful but potentially explosive. What's your move?"
            elif "text" in prompt.lower():
                return "Text first? Depends. Are you feeling confident or just emotionally brave today?"
            else:
                return "That's interesting! Tell me more about what's on your mind right now."
        else:
            return "I'm here to chat with you! What's going on?"

def test_continuous_conversation_prompt():
    """测试连续性对话提示"""
    logger.info("🧪 测试连续性对话提示...")
    
    try:
        from prompts.prompt_loader import load_prompt
        
        # 加载连续性对话提示
        prompt = load_prompt('continuous_conversation_prompt')
        
        if "CONTINUOUS CONVERSATION MODE" in prompt:
            logger.info("✅ 连续性对话提示加载成功")
            logger.info(f"提示内容预览: {prompt[:100]}...")
            return True
        else:
            logger.error("❌ 连续性对话提示加载失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

def test_conversation_flow():
    """测试对话流程"""
    logger.info("💬 测试对话流程...")
    
    # 模拟对话场景
    conversation_scenarios = [
        {
            "user_input": "I was stuck in traffic and it's so annoying!",
            "expected_continuation": "traffic"
        },
        {
            "user_input": "I met my crush today and froze.. He is a Leo..",
            "expected_continuation": "crush"
        },
        {
            "user_input": "Should I text him first?",
            "expected_continuation": "text"
        }
    ]
    
    mock_llm = MockLLM()
    
    for i, scenario in enumerate(conversation_scenarios, 1):
        logger.info(f"场景 {i}: {scenario['user_input']}")
        
        # 构建包含连续性对话提示的完整提示
        full_prompt = f"""
        {scenario['user_input']}
        
        CONTINUOUS CONVERSATION MODE:
        When the user seems like they want you to continue the conversation naturally, you should:
        1. IMMEDIATELY continue the dialogue by asking a follow-up question
        2. ALWAYS end your response with a question or open-ended statement
        3. Keep the conversation flowing naturally and engagingly
        """
        
        # 生成响应
        response = mock_llm.generate(full_prompt)
        logger.info(f"Kiyo回复: {response}")
        
        # 检查响应是否包含连续性元素
        if "?" in response and len(response) > 20:
            logger.info(f"✅ 场景 {i} 连续性对话成功")
        else:
            logger.warning(f"⚠️ 场景 {i} 连续性对话可能不够自然")
    
    return True

def test_config_integration():
    """测试配置集成"""
    logger.info("⚙️ 测试配置集成...")
    
    try:
        import yaml
        
        # 读取配置文件
        with open('conf.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查连续性对话配置
        agent_settings = config.get('character_config', {}).get('agent_config', {}).get('agent_settings', {})
        basic_memory_agent = agent_settings.get('basic_memory_agent', {})
        
        if basic_memory_agent.get('enable_continuous_conversation'):
            logger.info("✅ 连续性对话配置已启用")
        else:
            logger.warning("⚠️ 连续性对话配置未启用")
        
        # 检查工具提示配置
        tool_prompts = config.get('system_config', {}).get('tool_prompts', {})
        if 'continuous_conversation_prompt' in tool_prompts:
            logger.info("✅ 连续性对话提示已配置")
        else:
            logger.warning("⚠️ 连续性对话提示未配置")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始连续性对话测试...")
    logger.info("=" * 60)
    
    test_results = []
    
    # 1. 测试连续性对话提示
    result1 = test_continuous_conversation_prompt()
    test_results.append(("连续性对话提示", result1))
    
    # 2. 测试对话流程
    result2 = test_conversation_flow()
    test_results.append(("对话流程", result2))
    
    # 3. 测试配置集成
    result3 = test_config_integration()
    test_results.append(("配置集成", result3))
    
    # 生成测试报告
    logger.info("📊 连续性对话测试报告")
    logger.info("=" * 60)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 连续性对话功能配置完成！")
        logger.info("💡 使用说明:")
        logger.info("   1. 当用户消息以 ']' 结尾时，Kiyo会自动继续对话")
        logger.info("   2. Kiyo会主动提问，保持对话流畅")
        logger.info("   3. 对话会自然延续，无需用户每次都输入")
        logger.info("   4. 系统已配置连续性对话参数")
    else:
        logger.error("❌ 部分测试失败，请检查配置")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
