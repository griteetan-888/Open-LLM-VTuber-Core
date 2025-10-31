#!/usr/bin/env python3
"""
2-3秒响应时间测试脚本
专门测试和验证2-3秒响应时间目标
"""
import asyncio
import time
import json
import websockets
import statistics
from typing import List, Dict, Any
from loguru import logger

class ResponseTimeTester:
    def __init__(self):
        self.test_results = []
        self.target_time = 3.0  # 目标响应时间3秒
        self.success_threshold = 0.8  # 80%成功率
        
    async def test_single_response(self, test_input: str) -> Dict[str, Any]:
        """测试单个响应"""
        logger.info(f"🧪 测试输入: '{test_input}'")
        
        start_time = time.time()
        
        try:
            uri = 'ws://localhost:12393/client-ws'
            async with websockets.connect(uri) as websocket:
                # 等待连接建立
                await asyncio.sleep(0.5)
                
                # 发送测试消息
                test_message = {
                    'type': 'text-input',
                    'content': test_input
                }
                
                await websocket.send(json.dumps(test_message))
                
                # 记录关键时间点
                llm_start = None
                llm_end = None
                tts_start = None
                tts_end = None
                total_end = None
                
                # 监听响应
                timeout = 10  # 10秒总超时
                while time.time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(response)
                        current_time = time.time()
                        
                        # 记录LLM开始响应
                        if data.get('type') == 'full-text' and llm_start is None:
                            llm_start = current_time
                            llm_response_time = llm_start - start_time
                            logger.info(f"📝 LLM开始响应: {llm_response_time:.2f}s")
                        
                        # 记录TTS开始合成
                        elif data.get('type') == 'audio' and tts_start is None:
                            tts_start = current_time
                            tts_response_time = tts_start - start_time
                            logger.info(f"🔊 TTS开始合成: {tts_response_time:.2f}s")
                        
                        # 记录对话结束
                        elif data.get('type') == 'control' and data.get('text') == 'conversation-chain-end':
                            total_end = current_time
                            total_time = total_end - start_time
                            logger.info(f"✅ 对话完成: {total_time:.2f}s")
                            break
                            
                    except asyncio.TimeoutError:
                        logger.warning("响应超时")
                        break
                
                # 计算时间指标
                total_time = time.time() - start_time
                llm_time = (llm_start - start_time) if llm_start else None
                tts_time = (tts_start - llm_start) if tts_start and llm_start else None
                
                result = {
                    "test_input": test_input,
                    "total_time": total_time,
                    "llm_response_time": llm_time,
                    "tts_generation_time": tts_time,
                    "success": total_time <= self.target_time,
                    "timestamp": time.time()
                }
                
                # 评估结果
                if result["success"]:
                    logger.info(f"✅ 测试成功: {total_time:.2f}s <= {self.target_time}s")
                else:
                    logger.warning(f"❌ 测试失败: {total_time:.2f}s > {self.target_time}s")
                
                return result
                
        except Exception as e:
            logger.error(f"测试失败: {e}")
            return {
                "test_input": test_input,
                "error": str(e),
                "success": False,
                "total_time": None
            }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        logger.info("🚀 开始2-3秒响应时间综合测试...")
        logger.info("=" * 60)
        
        # 测试用例
        test_cases = [
            "Hello!",
            "How are you?",
            "What's your name?",
            "Tell me a joke.",
            "What's the weather like?",
            "How old are you?",
            "What do you like to do?",
            "Do you have any hobbies?",
            "What's your favorite color?",
            "Can you help me?"
        ]
        
        # 运行测试
        for i, test_input in enumerate(test_cases, 1):
            logger.info(f"📋 测试 {i}/{len(test_cases)}")
            result = await self.test_single_response(test_input)
            self.test_results.append(result)
            
            # 测试间隔
            await asyncio.sleep(1)
        
        # 分析结果
        return self.analyze_test_results()
    
    def analyze_test_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        if not self.test_results:
            return {"error": "no_test_results"}
        
        # 基本统计
        successful_tests = [r for r in self.test_results if r.get("success", False)]
        failed_tests = [r for r in self.test_results if not r.get("success", False)]
        
        success_rate = len(successful_tests) / len(self.test_results)
        
        # 时间统计
        total_times = [r["total_time"] for r in self.test_results if r.get("total_time")]
        llm_times = [r["llm_response_time"] for r in self.test_results if r.get("llm_response_time")]
        tts_times = [r["tts_generation_time"] for r in self.test_results if r.get("tts_generation_time")]
        
        analysis = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": success_rate,
                "target_achieved": success_rate >= self.success_threshold
            },
            "response_times": {
                "average_total_time": statistics.mean(total_times) if total_times else None,
                "median_total_time": statistics.median(total_times) if total_times else None,
                "min_total_time": min(total_times) if total_times else None,
                "max_total_time": max(total_times) if total_times else None,
                "average_llm_time": statistics.mean(llm_times) if llm_times else None,
                "average_tts_time": statistics.mean(tts_times) if tts_times else None
            },
            "performance_grade": self._calculate_performance_grade(success_rate),
            "recommendations": self._generate_recommendations(success_rate, total_times),
            "detailed_results": self.test_results
        }
        
        return analysis
    
    def _calculate_performance_grade(self, success_rate: float) -> str:
        """计算性能等级"""
        if success_rate >= 0.9:
            return "A+ (优秀)"
        elif success_rate >= 0.8:
            return "A (良好)"
        elif success_rate >= 0.7:
            return "B (一般)"
        elif success_rate >= 0.6:
            return "C (需要改进)"
        else:
            return "D (需要大幅优化)"
    
    def _generate_recommendations(self, success_rate: float, total_times: List[float]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append("💡 成功率低于80%，需要优化系统性能")
        
        if total_times:
            avg_time = statistics.mean(total_times)
            if avg_time > 3.0:
                recommendations.append("💡 平均响应时间超过3秒，需要进一步优化")
            
            max_time = max(total_times)
            if max_time > 5.0:
                recommendations.append("💡 最大响应时间超过5秒，检查系统瓶颈")
        
        if success_rate >= 0.8:
            recommendations.append("✅ 系统性能良好，已达到2-3秒响应目标")
        
        return recommendations
    
    def print_test_report(self, analysis: Dict[str, Any]):
        """打印测试报告"""
        logger.info("📊 2-3秒响应时间测试报告")
        logger.info("=" * 60)
        
        # 测试摘要
        summary = analysis["test_summary"]
        logger.info(f"📋 测试摘要:")
        logger.info(f"   总测试数: {summary['total_tests']}")
        logger.info(f"   成功测试: {summary['successful_tests']}")
        logger.info(f"   失败测试: {summary['failed_tests']}")
        logger.info(f"   成功率: {summary['success_rate']:.1%}")
        logger.info(f"   目标达成: {'✅' if summary['target_achieved'] else '❌'}")
        
        # 响应时间统计
        times = analysis["response_times"]
        logger.info(f"⏱️ 响应时间统计:")
        logger.info(f"   平均总时间: {times['average_total_time']:.2f}s")
        logger.info(f"   中位数时间: {times['median_total_time']:.2f}s")
        logger.info(f"   最短时间: {times['min_total_time']:.2f}s")
        logger.info(f"   最长时间: {times['max_total_time']:.2f}s")
        logger.info(f"   平均LLM时间: {times['average_llm_time']:.2f}s")
        logger.info(f"   平均TTS时间: {times['average_tts_time']:.2f}s")
        
        # 性能等级
        logger.info(f"🏆 性能等级: {analysis['performance_grade']}")
        
        # 优化建议
        recommendations = analysis["recommendations"]
        logger.info(f"💡 优化建议:")
        for rec in recommendations:
            logger.info(f"   {rec}")
        
        logger.info("=" * 60)
    
    async def run_continuous_monitoring(self, duration_minutes: int = 5):
        """运行持续监控"""
        logger.info(f"🔄 开始持续监控 {duration_minutes} 分钟...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # 随机测试
            test_inputs = [
                "Hello!", "How are you?", "What's up?", "Tell me something interesting"
            ]
            
            import random
            test_input = random.choice(test_inputs)
            
            result = await self.test_single_response(test_input)
            self.test_results.append(result)
            
            # 每30秒测试一次
            await asyncio.sleep(30)
        
        # 分析持续监控结果
        analysis = self.analyze_test_results()
        self.print_test_report(analysis)
        
        return analysis

async def main():
    tester = ResponseTimeTester()
    
    print("🚀 2-3秒响应时间测试器")
    print("=" * 50)
    print("选择测试模式:")
    print("1. 综合测试 (10个测试用例)")
    print("2. 持续监控 (5分钟)")
    print("3. 自定义测试")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            analysis = await tester.run_comprehensive_test()
            tester.print_test_report(analysis)
            
        elif choice == "2":
            analysis = await tester.run_continuous_monitoring(5)
            
        elif choice == "3":
            test_input = input("请输入测试文本: ").strip()
            result = await tester.test_single_response(test_input)
            print(f"测试结果: {result}")
            
        else:
            print("无效选择，运行综合测试...")
            analysis = await tester.run_comprehensive_test()
            tester.print_test_report(analysis)
            
    except KeyboardInterrupt:
        print("\n🛑 测试已停止")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
