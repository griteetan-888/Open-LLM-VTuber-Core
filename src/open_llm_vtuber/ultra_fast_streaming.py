"""
超快速流式处理系统 - 实现2-3秒响应时间
"""
import asyncio
import time
import json
import hashlib
from typing import AsyncIterator, Dict, Any, Optional, List
from loguru import logger
from pathlib import Path
import aiofiles

class UltraFastStreamingProcessor:
    """超快速流式处理器 - 专门为2-3秒响应时间优化"""
    
    def __init__(self, cache_dir: str = "cache/ultra_fast"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 预计算缓存
        self.precomputed_responses = {}
        self.common_phrases_cache = {}
        
        # 性能指标
        self.response_times = []
        self.cache_hit_rate = 0.0
        
        # 超快速配置
        self.max_response_time = 3.0  # 最大响应时间3秒
        self.chunk_size = 5           # 超小块处理
        self.parallel_limit = 5       # 并行处理限制
        
    async def process_ultra_fast_response(
        self, 
        user_input: str, 
        llm_engine, 
        tts_engine,
        websocket_send
    ) -> str:
        """超快速响应处理 - 目标2-3秒"""
        start_time = time.time()
        
        # 1. 检查预计算缓存 (0.1秒内)
        cached_response = await self._check_precomputed_cache(user_input)
        if cached_response:
            logger.info("⚡ 使用预计算缓存响应")
            await self._send_cached_response(cached_response, websocket_send)
            return cached_response["text"]
        
        # 2. 并行启动LLM和TTS准备 (0.2秒内)
        llm_task = asyncio.create_task(
            self._ultra_fast_llm_generation(user_input, llm_engine)
        )
        
        # 3. 流式处理LLM响应 (1-2秒内)
        response_text = ""
        tts_tasks = []
        
        async for chunk in self._stream_llm_response(llm_task):
            if chunk:
                response_text += chunk
                
                # 立即发送文本到前端
                await websocket_send(json.dumps({
                    "type": "text-stream",
                    "text": chunk,
                    "timestamp": time.time()
                }))
                
                # 并行启动TTS生成
                if len(chunk.strip()) > 3:  # 只对有意义的内容生成TTS
                    tts_task = asyncio.create_task(
                        self._ultra_fast_tts_generation(chunk, tts_engine)
                    )
                    tts_tasks.append(tts_task)
        
        # 4. 并行处理所有TTS任务 (1秒内)
        if tts_tasks:
            await self._process_parallel_tts(tts_tasks, websocket_send)
        
        # 5. 缓存响应
        await self._cache_response(user_input, response_text)
        
        total_time = time.time() - start_time
        self.response_times.append(total_time)
        
        logger.info(f"⚡ 超快速响应完成: {total_time:.2f}秒")
        
        if total_time > self.max_response_time:
            logger.warning(f"⚠️ 响应时间超过目标: {total_time:.2f}s > {self.max_response_time}s")
        
        return response_text
    
    async def _check_precomputed_cache(self, user_input: str) -> Optional[Dict]:
        """检查预计算缓存"""
        cache_key = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    return json.loads(content)
            except Exception as e:
                logger.warning(f"读取缓存失败: {e}")
        
        return None
    
    async def _ultra_fast_llm_generation(self, user_input: str, llm_engine) -> AsyncIterator[str]:
        """超快速LLM生成"""
        try:
            # 使用最小化配置
            messages = [
                {"role": "user", "content": user_input}
            ]
            
            # 流式生成，小块处理
            async for chunk in llm_engine.chat_completion(messages, stream=True):
                if chunk and len(chunk.strip()) > 0:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"LLM生成失败: {e}")
            yield "Sorry, I need a moment to think..."
    
    async def _stream_llm_response(self, llm_task) -> AsyncIterator[str]:
        """流式处理LLM响应"""
        try:
            # 等待LLM任务完成，但设置超时
            response = await asyncio.wait_for(llm_task, timeout=self.max_response_time)
            
            # 如果LLM返回完整响应，则分块发送
            if isinstance(response, str):
                words = response.split()
                for i in range(0, len(words), self.chunk_size):
                    chunk = " ".join(words[i:i+self.chunk_size])
                    if chunk.strip():
                        yield chunk
                        await asyncio.sleep(0.05)  # 短暂延迟以模拟流式效果
            else:
                # 如果已经是流式响应
                async for chunk in response:
                    yield chunk
                    
        except asyncio.TimeoutError:
            logger.warning("LLM响应超时，使用默认响应")
            yield "Let me think about that..."
        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            yield "I'm processing your request..."
    
    async def _ultra_fast_tts_generation(self, text: str, tts_engine) -> Optional[str]:
        """超快速TTS生成"""
        try:
            # 检查TTS缓存
            tts_cache_key = hashlib.md5(text.encode()).hexdigest()
            cached_audio = self.cache_dir / f"tts_{tts_cache_key}.mp3"
            
            if cached_audio.exists():
                return str(cached_audio)
            
            # 生成新音频
            audio_path = await tts_engine.async_generate_audio(
                text=text,
                file_name_no_ext=f"ultra_fast_{int(time.time())}"
            )
            
            # 缓存音频
            if audio_path:
                import shutil
                shutil.copy2(audio_path, cached_audio)
            
            return audio_path
            
        except Exception as e:
            logger.error(f"TTS生成失败: {e}")
            return None
    
    async def _process_parallel_tts(self, tts_tasks: List[asyncio.Task], websocket_send):
        """并行处理TTS任务"""
        try:
            # 等待所有TTS任务完成
            results = await asyncio.gather(*tts_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, str) and result:
                    # 发送音频到前端
                    await websocket_send(json.dumps({
                        "type": "audio",
                        "audio_path": result,
                        "sequence": i,
                        "timestamp": time.time()
                    }))
                    
        except Exception as e:
            logger.error(f"并行TTS处理失败: {e}")
    
    async def _send_cached_response(self, cached_data: Dict, websocket_send):
        """发送缓存响应"""
        try:
            # 发送文本
            await websocket_send(json.dumps({
                "type": "cached-text",
                "text": cached_data["text"],
                "timestamp": time.time()
            }))
            
            # 发送音频
            if cached_data.get("audio_path"):
                await websocket_send(json.dumps({
                    "type": "cached-audio",
                    "audio_path": cached_data["audio_path"],
                    "timestamp": time.time()
                }))
                
        except Exception as e:
            logger.error(f"发送缓存响应失败: {e}")
    
    async def _cache_response(self, user_input: str, response_text: str):
        """缓存响应"""
        try:
            cache_key = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
            cache_data = {
                "text": response_text,
                "timestamp": time.time(),
                "user_input": user_input
            }
            
            cache_file = self.cache_dir / f"{cache_key}.json"
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, ensure_ascii=False, indent=2))
                
        except Exception as e:
            logger.error(f"缓存响应失败: {e}")
    
    def precompute_common_responses(self):
        """预计算常见响应"""
        common_inputs = [
            "Hello", "Hi", "How are you?", "What's up?", "Good morning",
            "Good afternoon", "Good evening", "Thank you", "Thanks",
            "You're welcome", "Nice to meet you", "See you later"
        ]
        
        logger.info("🔄 预计算常见响应...")
        # 这里可以预先生成常见响应的缓存
        # 实际实现需要根据具体的LLM和TTS引擎来调整
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.response_times:
            return {"error": "no_data"}
        
        avg_time = sum(self.response_times) / len(self.response_times)
        max_time = max(self.response_times)
        min_time = min(self.response_times)
        
        success_rate = len([t for t in self.response_times if t <= self.max_response_time]) / len(self.response_times)
        
        return {
            "average_response_time": avg_time,
            "max_response_time": max_time,
            "min_response_time": min_time,
            "success_rate": success_rate,
            "target_achieved": success_rate >= 0.8,  # 80%的请求在目标时间内完成
            "total_requests": len(self.response_times)
        }

class UltraFastTTSManager:
    """超快速TTS管理器"""
    
    def __init__(self):
        self.audio_cache = {}
        self.preloaded_phrases = {}
        self.parallel_semaphore = asyncio.Semaphore(3)  # 限制并行TTS任务
    
    async def generate_audio_ultra_fast(self, text: str, tts_engine) -> Optional[str]:
        """超快速音频生成"""
        async with self.parallel_semaphore:
            # 检查缓存
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self.audio_cache:
                return self.audio_cache[cache_key]
            
            try:
                # 生成音频
                audio_path = await tts_engine.async_generate_audio(
                    text=text,
                    file_name_no_ext=f"ultra_fast_{cache_key[:8]}"
                )
                
                # 缓存结果
                if audio_path:
                    self.audio_cache[cache_key] = audio_path
                
                return audio_path
                
            except Exception as e:
                logger.error(f"超快速TTS生成失败: {e}")
                return None
    
    def preload_common_phrases(self, phrases: List[str], tts_engine):
        """预加载常见短语"""
        logger.info(f"🔄 预加载 {len(phrases)} 个常见短语...")
        
        async def _preload():
            tasks = []
            for phrase in phrases:
                task = asyncio.create_task(
                    self.generate_audio_ultra_fast(phrase, tts_engine)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("✅ 常见短语预加载完成")
        
        # 在后台运行预加载
        asyncio.create_task(_preload())
