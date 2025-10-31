#!/usr/bin/env python3
"""
真正的流式API测试脚本
测试实际的流式API实现和加速首句功能
"""
import asyncio
import time
import json
from loguru import logger

# 导入流式LLM
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from open_llm_vtuber.agent.stateless_llm.streaming_openai_llm import StreamingOpenAILLM

class RealStreamingAPITester:
    """真正的流式API测试器"""
    
    def __init__(self):
        self.test_results = []
        self.streaming_metrics = {}
    
    async def test_streaming_llm_creation(self) -> bool:
        """测试流式LLM创建"""
        logger.info("🧪 测试流式LLM创建...")
        
        try:
            # 创建流式LLM实例
            streaming_llm = StreamingOpenAILLM(
                model="ft:gpt-3.5-turbo-0125:zzzorg::CRpLnugB",
                base_url="https://api.zzz-api.top/v1",
                llm_api_key="sk-zk252f4ee8cfc1e7f0d4d6e03fb46d6972f68ce685be0e3f",
                temperature=0.6,
                max_tokens=500,
                timeout=10,
                retry_count=1,
                # 流式配置
                stream=True,
                stream_chunk_size=8,
                stream_buffer_size=3,
                first_response_timeout=200,
                enable_streaming_tts=True,
                tts_stream_delay=50,
                # 流式优化
                streaming_optimization=True,
                chunk_processing_parallel=True,
                immediate_audio_playback=True,
                # 性能优化
                max_wait_time=3,
                connection_pool_size=5,
                keep_alive=True,
            )
            
            logger.info("✅ 流式LLM创建成功")
            logger.info(f"   模型: {streaming_llm.model}")
            logger.info(f"   流式API: {streaming_llm.stream}")
            logger.info(f"   首句响应超时: {streaming_llm.first_response_timeout}ms")
            logger.info(f"   流式优化: {streaming_llm.streaming_optimization}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 流式LLM创建失败: {e}")
            return False
    
    async def test_streaming_chat_completion(self) -> bool:
        """测试流式聊天完成"""
        logger.info("💬 测试流式聊天完成...")
        
        try:
            # 创建流式LLM
            streaming_llm = StreamingOpenAILLM(
                model="ft:gpt-3.5-turbo-0125:zzzorg::CRpLnugB",
                base_url="https://api.zzz-api.top/v1",
                llm_api_key="sk-zk252f4ee8cfc1e7f0d4d6e03fb46d6972f68ce685be0e3f",
                temperature=0.6,
                max_tokens=500,
                timeout=10,
                retry_count=1,
                stream=True,
                first_response_timeout=200,
                streaming_optimization=True,
            )
            
            # 测试消息
            test_messages = [
                {"role": "user", "content": "Good morning! How are you today?"}
            ]
            
            logger.info("开始流式聊天完成测试...")
            start_time = time.time()
            
            first_response_time = None
            chunk_count = 0
            accumulated_text = ""
            
            async for event in streaming_llm.chat_completion(test_messages):
                current_time = time.time()
                
                if event.get("type") == "text_delta":
                    if first_response_time is None:
                        first_response_time = event.get("first_response_time", 0)
                        logger.info(f"⚡ 首句响应时间: {first_response_time:.2f}ms")
                    
                    chunk_count += 1
                    text_chunk = event.get("text", "")
                    accumulated_text += text_chunk
                    
                    logger.info(f"📡 流式块 {chunk_count}: {text_chunk}")
                    
                elif event.get("type") == "completion":
                    total_time = event.get("total_time", 0)
                    logger.info(f"✅ 流式完成:")
                    logger.info(f"   总响应时间: {total_time:.2f}ms")
                    logger.info(f"   首句响应时间: {first_response_time:.2f}ms")
                    logger.info(f"   处理块数: {chunk_count}")
                    logger.info(f"   最终文本: {accumulated_text}")
                    
                    # 检查是否达到加速首句目标
                    if first_response_time and first_response_time <= 200:
                        logger.info(f"🎉 加速首句成功: {first_response_time:.2f}ms <= 200ms")
                        return True
                    else:
                        logger.warning(f"⚠️ 首句响应较慢: {first_response_time:.2f}ms > 200ms")
                        return False
                        
                elif event.get("type") == "error":
                    logger.error(f"❌ 流式聊天失败: {event.get('message', '')}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 流式聊天完成测试失败: {e}")
            return False
    
    async def test_streaming_performance(self) -> bool:
        """测试流式性能"""
        logger.info("📊 测试流式性能...")
        
        try:
            # 创建流式LLM
            streaming_llm = StreamingOpenAILLM(
                model="ft:gpt-3.5-turbo-0125:zzzorg::CRpLnugB",
                base_url="https://api.zzz-api.top/v1",
                llm_api_key="sk-zk252f4ee8cfc1e7f0d4d6e03fb46d6972f68ce685be0e3f",
                temperature=0.6,
                max_tokens=500,
                timeout=10,
                retry_count=1,
                stream=True,
                first_response_timeout=200,
                streaming_optimization=True,
            )
            
            # 测试消息
            test_messages = [
                {"role": "user", "content": "Good morning! How are you today?"},
                {"role": "user", "content": "I was stuck in traffic and it's so annoying!"},
                {"role": "user", "content": "I met my crush today and froze.. He is a Leo.."}
            ]
            
            # 运行性能测试
            performance_results = await streaming_llm.test_streaming_performance(test_messages)
            
            logger.info("📈 流式性能测试结果:")
            logger.info(f"   总测试数: {performance_results['total_tests']}")
            logger.info(f"   成功测试数: {performance_results['successful_tests']}")
            logger.info(f"   成功率: {performance_results['success_rate']:.2%}")
            logger.info(f"   平均首句响应时间: {performance_results['average_first_response_time']:.2f}ms")
            logger.info(f"   性能等级: {performance_results['performance_grade']}")
            
            # 获取流式指标
            metrics = streaming_llm.get_streaming_metrics()
            logger.info("📊 流式指标:")
            logger.info(f"   状态: {metrics['status']}")
            if metrics['status'] == 'active':
                logger.info(f"   首句响应时间: {metrics['first_response_times']['average']:.2f}ms")
                logger.info(f"   总响应时间: {metrics['total_response_times']['average']:.2f}ms")
                logger.info(f"   性能等级: {metrics['performance_grade']}")
            
            return performance_results['success_rate'] >= 0.8
            
        except Exception as e:
            logger.error(f"❌ 流式性能测试失败: {e}")
            return False
    
    async def test_config_integration(self) -> bool:
        """测试配置集成"""
        logger.info("⚙️ 测试配置集成...")
        
        try:
            import yaml
            
            # 读取配置文件
            with open('conf.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查流式配置
            agent_settings = config.get('character_config', {}).get('agent_config', {}).get('agent_settings', {})
            basic_memory_agent = agent_settings.get('basic_memory_agent', {})
            
            # 检查关键配置
            streaming_configs = [
                ('enable_streaming', basic_memory_agent.get('enable_streaming')),
                ('stream_chunk_size', basic_memory_agent.get('stream_chunk_size')),
                ('first_response_threshold', basic_memory_agent.get('first_response_threshold')),
                ('streaming_optimization', basic_memory_agent.get('streaming_optimization'))
            ]
            
            configured_count = 0
            for config_name, config_value in streaming_configs:
                if config_value is not None:
                    logger.info(f"✅ {config_name}: {config_value}")
                    configured_count += 1
                else:
                    logger.warning(f"⚠️ {config_name}: 未配置")
            
            # 检查LLM流式配置
            llm_configs = config.get('character_config', {}).get('agent_config', {}).get('llm_configs', {})
            openai_llm = llm_configs.get('openai_llm', {})
            
            llm_streaming_configs = [
                ('stream', openai_llm.get('stream')),
                ('stream_chunk_size', openai_llm.get('stream_chunk_size')),
                ('first_response_timeout', openai_llm.get('first_response_timeout')),
                ('streaming_optimization', openai_llm.get('streaming_optimization'))
            ]
            
            for config_name, config_value in llm_streaming_configs:
                if config_value is not None:
                    logger.info(f"✅ LLM {config_name}: {config_value}")
                    configured_count += 1
                else:
                    logger.warning(f"⚠️ LLM {config_name}: 未配置")
            
            success_rate = configured_count / (len(streaming_configs) + len(llm_streaming_configs))
            
            if success_rate >= 0.8:
                logger.info(f"✅ 配置集成测试通过 ({configured_count}/{len(streaming_configs) + len(llm_streaming_configs)})")
                return True
            else:
                logger.error(f"❌ 配置集成测试失败 ({configured_count}/{len(streaming_configs) + len(llm_streaming_configs)})")
                return False
                
        except Exception as e:
            logger.error(f"❌ 配置集成测试失败: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("🚀 开始真正的流式API测试...")
        logger.info("=" * 60)
        
        test_results = []
        
        # 1. 测试流式LLM创建
        result1 = await self.test_streaming_llm_creation()
        test_results.append(("流式LLM创建", result1))
        
        # 2. 测试流式聊天完成
        result2 = await self.test_streaming_chat_completion()
        test_results.append(("流式聊天完成", result2))
        
        # 3. 测试流式性能
        result3 = await self.test_streaming_performance()
        test_results.append(("流式性能", result3))
        
        # 4. 测试配置集成
        result4 = await self.test_config_integration()
        test_results.append(("配置集成", result4))
        
        # 输出测试结果
        logger.info("📊 真正的流式API测试报告")
        logger.info("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"总体结果: {passed_tests}/{total_tests} 测试通过")
        
        if passed_tests == total_tests:
            logger.info("🎉 真正的流式API功能实现成功！")
            logger.info("💡 功能特性:")
            logger.info("   1. 真正的流式API响应 - 边生成边播放")
            logger.info("   2. 加速首句 - 200ms内听到回复")
            logger.info("   3. 流式性能监控 - 实时性能指标")
            logger.info("   4. 配置集成 - 完整的配置支持")
            logger.info("   5. 性能测试 - 自动化性能验证")
        else:
            logger.error("❌ 部分测试失败，请检查实现")
        
        logger.info("=" * 60)
        
        return passed_tests == total_tests

async def main():
    """主测试函数"""
    tester = RealStreamingAPITester()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("🎯 真正的流式API功能已成功实现！")
        logger.info("🚀 现在你的VTuber可以在200ms内开始回复！")
    else:
        logger.error("❌ 流式API实现需要进一步优化")

if __name__ == "__main__":
    asyncio.run(main())

