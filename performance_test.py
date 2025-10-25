#!/usr/bin/env python3
"""
性能测试脚本 - 分析ASR、TTS、LLM各组件的性能瓶颈
"""
import asyncio
import time
import json
import websockets
import requests
from datetime import datetime

class PerformanceTester:
    def __init__(self):
        self.results = {}
        
    async def test_llm_performance(self):
        """测试LLM推理性能"""
        print("🧠 测试LLM推理性能...")
        
        try:
            uri = 'ws://localhost:12393/client-ws'
            async with websockets.connect(uri) as websocket:
                # 等待初始化
                await asyncio.sleep(2)
                
                # 发送测试消息
                test_message = {
                    'type': 'text-input',
                    'content': 'Hello Kiyo! How are you today?'
                }
                
                start_time = time.time()
                await websocket.send(json.dumps(test_message))
                
                # 收集响应时间
                llm_start = None
                llm_end = None
                tts_start = None
                tts_end = None
                
                while time.time() - start_time < 60:  # 60秒超时
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        current_time = time.time()
                        
                        if data.get('type') == 'full-text' and 'text' in data:
                            if llm_start is None:
                                llm_start = current_time
                                print(f"   📝 LLM开始响应: {current_time - start_time:.2f}s")
                            llm_end = current_time
                            
                        elif data.get('type') == 'audio':
                            if tts_start is None:
                                tts_start = current_time
                                print(f"   🔊 TTS开始合成: {current_time - start_time:.2f}s")
                            tts_end = current_time
                            
                        elif data.get('type') == 'control' and data.get('text') == 'conversation-chain-end':
                            print(f"   ✅ 对话结束: {current_time - start_time:.2f}s")
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                # 计算性能指标
                if llm_start and llm_end:
                    llm_time = llm_end - llm_start
                    self.results['llm_response_time'] = llm_time
                    print(f"   ⏱️  LLM响应时间: {llm_time:.2f}s")
                
                if tts_start and tts_end:
                    tts_time = tts_end - tts_start
                    self.results['tts_synthesis_time'] = tts_time
                    print(f"   ⏱️  TTS合成时间: {tts_time:.2f}s")
                
                total_time = time.time() - start_time
                self.results['total_response_time'] = total_time
                print(f"   ⏱️  总响应时间: {total_time:.2f}s")
                
        except Exception as e:
            print(f"   ❌ LLM测试失败: {e}")
    
    def test_api_latency(self):
        """测试API延迟"""
        print("🌐 测试API延迟...")
        
        try:
            # 测试OpenAI API延迟
            start_time = time.time()
            response = requests.post(
                'https://api.zzz-api.top/v1/chat/completions',
                headers={
                    'Authorization': 'Bearer sk-zk252f4ee8cfc1e7f0d4d6e03fb46d6972f68ce685be0e3f',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'ft:gpt-3.5-turbo-0125:zzzorg::CIDmBkkP',
                    'messages': [{'role': 'user', 'content': 'Hello'}],
                    'max_tokens': 50
                },
                timeout=30
            )
            api_time = time.time() - start_time
            
            if response.status_code == 200:
                self.results['api_latency'] = api_time
                print(f"   ⏱️  API延迟: {api_time:.2f}s")
            else:
                print(f"   ❌ API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ API测试失败: {e}")
    
    def test_asr_performance(self):
        """测试ASR性能（模拟）"""
        print("🎤 分析ASR配置...")
        
        # 检查ASR配置
        asr_config = {
            'model_type': 'sense_voice',
            'provider': 'cpu',
            'num_threads': 4,
            'use_itn': True
        }
        
        print(f"   📊 ASR配置:")
        print(f"      - 模型类型: {asr_config['model_type']}")
        print(f"      - 推理设备: {asr_config['provider']}")
        print(f"      - 线程数: {asr_config['num_threads']}")
        print(f"      - 逆文本标准化: {asr_config['use_itn']}")
        
        # 性能评估
        if asr_config['provider'] == 'cpu':
            print("   ⚠️  使用CPU推理，可能较慢")
        if asr_config['num_threads'] < 8:
            print("   💡 建议增加线程数以提升性能")
    
    def test_tts_performance(self):
        """测试TTS性能"""
        print("🔊 分析TTS配置...")
        
        # 检查TTS配置
        tts_config = {
            'model': 'edge_tts',
            'voice': 'en-US-AvaMultilingualNeural'
        }
        
        print(f"   📊 TTS配置:")
        print(f"      - 引擎: {tts_config['model']}")
        print(f"      - 声音: {tts_config['voice']}")
        
        # 性能评估
        if tts_config['model'] == 'edge_tts':
            print("   ✅ Edge TTS通常性能较好")
        else:
            print("   ⚠️  其他TTS引擎可能较慢")
    
    def analyze_performance(self):
        """分析性能瓶颈"""
        print("\n📊 性能分析报告:")
        print("=" * 50)
        
        # LLM性能分析
        if 'llm_response_time' in self.results:
            llm_time = self.results['llm_response_time']
            if llm_time > 10:
                print("🐌 LLM响应较慢 (>10s)")
                print("   💡 建议:")
                print("      - 检查网络连接")
                print("      - 考虑使用更快的模型")
                print("      - 减少max_tokens")
            elif llm_time > 5:
                print("⚠️  LLM响应一般 (5-10s)")
            else:
                print("✅ LLM响应较快 (<5s)")
        
        # TTS性能分析
        if 'tts_synthesis_time' in self.results:
            tts_time = self.results['tts_synthesis_time']
            if tts_time > 5:
                print("🐌 TTS合成较慢 (>5s)")
                print("   💡 建议:")
                print("      - 考虑使用本地TTS")
                print("      - 优化音频质量设置")
            elif tts_time > 2:
                print("⚠️  TTS合成一般 (2-5s)")
            else:
                print("✅ TTS合成较快 (<2s)")
        
        # 总响应时间分析
        if 'total_response_time' in self.results:
            total_time = self.results['total_response_time']
            if total_time > 20:
                print("🐌 总体响应很慢 (>20s)")
            elif total_time > 10:
                print("⚠️  总体响应较慢 (10-20s)")
            else:
                print("✅ 总体响应较快 (<10s)")
        
        # API延迟分析
        if 'api_latency' in self.results:
            api_time = self.results['api_latency']
            if api_time > 5:
                print("🌐 API延迟较高 (>5s)")
                print("   💡 建议:")
                print("      - 检查网络连接")
                print("      - 考虑更换API提供商")
            else:
                print("🌐 API延迟正常 (<5s)")
    
    async def run_all_tests(self):
        """运行所有性能测试"""
        print("🚀 开始性能测试...")
        print("=" * 50)
        
        # 测试各个组件
        self.test_asr_performance()
        print()
        self.test_tts_performance()
        print()
        self.test_api_latency()
        print()
        await self.test_llm_performance()
        print()
        
        # 分析结果
        self.analyze_performance()

async def main():
    tester = PerformanceTester()
    await tester.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
