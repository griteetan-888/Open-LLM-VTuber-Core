"""
流式OpenAI LLM实现 - 支持真正的流式API和加速首句
"""
import asyncio
import time
from typing import AsyncIterator, List, Dict, Any, Optional
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk
from loguru import logger

from .stateless_llm_interface import StatelessLLMInterface


class StreamingOpenAILLM(StatelessLLMInterface):
    """支持流式API和加速首句的OpenAI LLM实现"""
    
    def __init__(
        self,
        model: str,
        base_url: str,
        llm_api_key: str,
        temperature: float = 0.6,
        max_tokens: int = 500,
        timeout: int = 10,
        retry_count: int = 1,
        # 流式API配置
        stream: bool = True,
        stream_chunk_size: int = 8,
        stream_buffer_size: int = 3,
        first_response_timeout: int = 200,
        enable_streaming_tts: bool = True,
        tts_stream_delay: int = 50,
        # 流式优化
        streaming_optimization: bool = True,
        chunk_processing_parallel: bool = True,
        immediate_audio_playback: bool = True,
        # 性能优化
        max_wait_time: int = 3,
        connection_pool_size: int = 5,
        keep_alive: bool = True,
    ):
        """初始化流式OpenAI LLM"""
        self.model = model
        self.base_url = base_url
        self.llm_api_key = llm_api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_count = retry_count
        
        # 流式配置
        self.stream = stream
        self.stream_chunk_size = stream_chunk_size
        self.stream_buffer_size = stream_buffer_size
        self.first_response_timeout = first_response_timeout
        self.enable_streaming_tts = enable_streaming_tts
        self.tts_stream_delay = tts_stream_delay
        
        # 流式优化
        self.streaming_optimization = streaming_optimization
        self.chunk_processing_parallel = chunk_processing_parallel
        self.immediate_audio_playback = immediate_audio_playback
        
        # 性能优化
        self.max_wait_time = max_wait_time
        self.connection_pool_size = connection_pool_size
        self.keep_alive = keep_alive
        
        # 初始化客户端
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=llm_api_key,
            timeout=timeout,
        )
        
        # 性能指标
        self.first_response_times = []
        self.total_response_times = []
        self.streaming_metrics = {
            'chunks_processed': 0,
            'first_response_achieved': 0,
            'streaming_success_rate': 0.0
        }
        
        logger.info(f"🚀 流式OpenAI LLM初始化完成")
        logger.info(f"   模型: {model}")
        logger.info(f"   流式API: {stream}")
        logger.info(f"   首句响应超时: {first_response_timeout}ms")
        logger.info(f"   流式优化: {streaming_optimization}")

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        system: str = None,
        tools: List[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """流式聊天完成 - 支持加速首句"""
        start_time = time.time()
        first_response_time = None
        
        try:
            # 准备消息
            messages_with_system = messages
            if system:
                messages_with_system = [
                    {"role": "system", "content": system},
                    *messages,
                ]
            
            logger.debug(f"📡 开始流式聊天完成，消息数: {len(messages_with_system)}")
            
            # 创建流式请求
            stream: AsyncStream[ChatCompletionChunk] = await self.client.chat.completions.create(
                messages=messages_with_system,
                model=self.model,
                stream=True,  # 强制启用流式
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools if tools else None,
            )
            
            chunk_count = 0
            accumulated_text = ""
            
            async for chunk in stream:
                chunk_count += 1
                current_time = time.time()
                
                # 记录首句响应时间
                if first_response_time is None and chunk.choices:
                    first_response_time = (current_time - start_time) * 1000
                    self.first_response_times.append(first_response_time)
                    self.streaming_metrics['first_response_achieved'] += 1
                    
                    logger.info(f"⚡ 首句响应时间: {first_response_time:.2f}ms")
                    
                    # 检查是否达到加速首句目标
                    if first_response_time <= self.first_response_timeout:
                        logger.info(f"✅ 加速首句成功: {first_response_time:.2f}ms <= {self.first_response_timeout}ms")
                    else:
                        logger.warning(f"⚠️ 首句响应较慢: {first_response_time:.2f}ms > {self.first_response_timeout}ms")
                
                # 处理文本内容
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_text += content
                    
                    # 发送流式文本事件
                    yield {
                        "type": "text_delta",
                        "text": content,
                        "timestamp": current_time,
                        "chunk_id": chunk_count,
                        "first_response_time": first_response_time,
                        "accumulated_text": accumulated_text
                    }
                    
                    # 如果启用流式优化，立即处理小块
                    if self.streaming_optimization and len(content.strip()) >= self.stream_chunk_size:
                        yield {
                            "type": "streaming_chunk_ready",
                            "text": content,
                            "chunk_id": chunk_count,
                            "ready_for_tts": True
                        }
            
            # 记录总响应时间
            total_time = (time.time() - start_time) * 1000
            self.total_response_times.append(total_time)
            self.streaming_metrics['chunks_processed'] += chunk_count
            
            # 计算流式成功率
            if first_response_time and first_response_time <= self.first_response_timeout:
                self.streaming_metrics['streaming_success_rate'] = (
                    self.streaming_metrics['first_response_achieved'] / 
                    max(1, len(self.first_response_times))
                )
            
            logger.info(f"📊 流式完成统计:")
            logger.info(f"   总响应时间: {total_time:.2f}ms")
            logger.info(f"   首句响应时间: {first_response_time:.2f}ms" if first_response_time else "   首句响应时间: 未记录")
            logger.info(f"   处理块数: {chunk_count}")
            logger.info(f"   流式成功率: {self.streaming_metrics['streaming_success_rate']:.2%}")
            
            # 发送完成事件
            yield {
                "type": "completion",
                "total_time": total_time,
                "first_response_time": first_response_time,
                "chunk_count": chunk_count,
                "final_text": accumulated_text,
                "streaming_success": first_response_time and first_response_time <= self.first_response_timeout
            }
            
        except Exception as e:
            logger.error(f"❌ 流式聊天完成失败: {e}")
            yield {
                "type": "error",
                "message": str(e),
                "timestamp": time.time()
            }

    def get_streaming_metrics(self) -> Dict[str, Any]:
        """获取流式性能指标"""
        if not self.first_response_times:
            return {
                "status": "no_data",
                "message": "暂无流式数据"
            }
        
        avg_first_response = sum(self.first_response_times) / len(self.first_response_times)
        avg_total_response = sum(self.total_response_times) / len(self.total_response_times)
        
        return {
            "status": "active",
            "first_response_times": {
                "average": avg_first_response,
                "min": min(self.first_response_times),
                "max": max(self.first_response_times),
                "count": len(self.first_response_times)
            },
            "total_response_times": {
                "average": avg_total_response,
                "min": min(self.total_response_times),
                "max": max(self.total_response_times),
                "count": len(self.total_response_times)
            },
            "streaming_metrics": self.streaming_metrics,
            "performance_grade": self._calculate_performance_grade(avg_first_response)
        }
    
    def _calculate_performance_grade(self, avg_first_response: float) -> str:
        """计算性能等级"""
        if avg_first_response <= 200:
            return "A+ (优秀)"
        elif avg_first_response <= 500:
            return "A (良好)"
        elif avg_first_response <= 1000:
            return "B (一般)"
        else:
            return "C (需要优化)"
    
    async def test_streaming_performance(self, test_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """测试流式性能"""
        logger.info("🧪 开始流式性能测试...")
        
        start_time = time.time()
        test_results = []
        
        for i, message in enumerate(test_messages, 1):
            logger.info(f"测试 {i}: {message.get('content', '')[:50]}...")
            
            test_start = time.time()
            first_response_time = None
            chunk_count = 0
            
            try:
                async for event in self.chat_completion([message]):
                    if event.get("type") == "text_delta":
                        if first_response_time is None:
                            first_response_time = event.get("first_response_time", 0)
                        chunk_count += 1
                    elif event.get("type") == "completion":
                        total_time = event.get("total_time", 0)
                        test_results.append({
                            "test_id": i,
                            "first_response_time": first_response_time,
                            "total_time": total_time,
                            "chunk_count": chunk_count,
                            "success": event.get("streaming_success", False)
                        })
                        break
                        
            except Exception as e:
                logger.error(f"测试 {i} 失败: {e}")
                test_results.append({
                    "test_id": i,
                    "error": str(e),
                    "success": False
                })
        
        total_test_time = time.time() - start_time
        
        # 分析测试结果
        successful_tests = [r for r in test_results if r.get("success", False)]
        avg_first_response = sum(r["first_response_time"] for r in successful_tests) / len(successful_tests) if successful_tests else 0
        
        return {
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(test_results) if test_results else 0,
            "average_first_response_time": avg_first_response,
            "total_test_time": total_test_time,
            "performance_grade": self._calculate_performance_grade(avg_first_response),
            "test_results": test_results
        }

