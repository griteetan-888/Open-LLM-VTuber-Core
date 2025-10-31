"""
记忆增强的Agent
集成智能记忆管理的Agent实现
"""
import time
from typing import Union, List, Dict, Any, Optional, Literal
from loguru import logger

from .agent_interface import AgentInterface
from .basic_memory_agent import BasicMemoryAgent
from ..stateless_llm.stateless_llm_interface import StatelessLLMInterface
from ...config_manager.tts_preprocessor import TTSPreprocessorConfig
from ...mcpp.tool_manager import ToolManager
from ...mcpp.tool_executor import ToolExecutor
# 可选导入记忆系统
try:
    from ...memory.smart_memory_manager import SmartMemoryManager
    from ...memory.memory_compressor import MemoryType
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError:
    SmartMemoryManager = None
    MemoryType = None
    MEMORY_SYSTEM_AVAILABLE = False
from ...chat_history_manager import get_history

class MemoryEnhancedAgent(BasicMemoryAgent):
    """记忆增强的Agent，继承BasicMemoryAgent并添加智能记忆管理"""
    
    def __init__(
        self,
        llm: StatelessLLMInterface,
        system: str,
        live2d_model,
        tts_preprocessor_config: TTSPreprocessorConfig = None,
        faster_first_response: bool = True,
        segment_method: str = "pysbd",
        use_mcpp: bool = False,
        interrupt_method: Literal["system", "user"] = "user",
        tool_prompts: Dict[str, str] = None,
        tool_manager: Optional[ToolManager] = None,
        tool_executor: Optional[ToolExecutor] = None,
        mcp_prompt_string: str = "",
        # 记忆管理相关参数
        max_memory_items: int = 1000,
        compression_threshold: float = 0.3,
        memory_file_path: str = "memory/memories.json",
        summary_file_path: str = "memory/summaries.json",
        enable_memory_compression: bool = True,
        memory_context_limit: int = 5,
    ):
        """初始化记忆增强Agent"""
        super().__init__(
            llm=llm,
            system=system,
            live2d_model=live2d_model,
            tts_preprocessor_config=tts_preprocessor_config,
            faster_first_response=faster_first_response,
            segment_method=segment_method,
            use_mcpp=use_mcpp,
            interrupt_method=interrupt_method,
            tool_prompts=tool_prompts,
            tool_manager=tool_manager,
            tool_executor=tool_executor,
            mcp_prompt_string=mcp_prompt_string,
        )
        
        # 初始化智能记忆管理器（如果可用）
        if MEMORY_SYSTEM_AVAILABLE:
            self.memory_manager = SmartMemoryManager(
                max_memory_items=max_memory_items,
                compression_threshold=compression_threshold,
                memory_file_path=memory_file_path,
                summary_file_path=summary_file_path
            )
        else:
            self.memory_manager = None
            logger.warning("记忆系统不可用，将使用基本记忆功能")
        
        self.enable_memory_compression = enable_memory_compression
        self.memory_context_limit = memory_context_limit
        
        logger.info("✅ 记忆增强Agent初始化完成")
    
    def set_memory_from_history(self, conf_uid: str, history_uid: str) -> None:
        """从历史记录加载记忆"""
        # 调用父类方法加载基本记忆
        super().set_memory_from_history(conf_uid, history_uid)
        
        # 获取历史记录
        messages = get_history(conf_uid, history_uid)
        
        if messages:
            # 处理历史记录，提取记忆
            conversation_id = f"{conf_uid}_{history_uid}"
            self.memory_manager.process_conversation(messages, conversation_id)
            
            logger.info(f"从历史记录中提取了记忆: {conversation_id}")
    
    def _add_message(
        self,
        message: Union[str, List[Dict[str, Any]]],
        role: str,
        display_text: Any = None,
        skip_memory: bool = False,
    ):
        """添加消息到记忆"""
        # 调用父类方法添加基本消息
        super()._add_message(message, role, display_text, skip_memory)
        
        # 如果启用了记忆压缩且记忆系统可用，处理记忆
        if self.enable_memory_compression and not skip_memory and self.memory_manager:
            self._process_message_for_memory(message, role)
    
    def _process_message_for_memory(self, message: Union[str, List[Dict[str, Any]]], role: str):
        """处理消息以提取记忆"""
        try:
            # 构建消息数据
            message_data = {
                "role": role,
                "content": message if isinstance(message, str) else str(message),
                "timestamp": time.time()
            }
            
            # 获取相关记忆
            relevant_memories = self.memory_manager.get_contextual_memories([message_data], self.memory_context_limit)
            
            # 如果有相关记忆，可以在这里使用它们来增强响应
            if relevant_memories:
                logger.debug(f"找到 {len(relevant_memories)} 个相关记忆")
                
        except Exception as e:
            logger.error(f"处理消息记忆失败: {e}")
    
    def _to_text_prompt(self, input_data) -> str:
        """构建包含记忆上下文的文本提示"""
        # 获取基础提示
        base_prompt = super()._to_text_prompt(input_data)
        
        # 获取相关记忆（如果记忆系统可用）
        if self.enable_memory_compression and self.memory_manager:
            try:
                # 从当前对话中获取相关记忆
                current_conversation = self._memory[-10:] if len(self._memory) > 10 else self._memory
                relevant_memories = self.memory_manager.get_contextual_memories(current_conversation, self.memory_context_limit)
                
                if relevant_memories:
                    # 构建记忆上下文
                    memory_context = self._build_memory_context(relevant_memories)
                    
                    # 将记忆上下文添加到提示中
                    enhanced_prompt = f"{base_prompt}\n\n[相关记忆上下文]\n{memory_context}"
                    
                    logger.debug(f"添加了 {len(relevant_memories)} 个相关记忆到提示中")
                    return enhanced_prompt
                    
            except Exception as e:
                logger.error(f"构建记忆上下文失败: {e}")
        
        return base_prompt
    
    def _build_memory_context(self, memories) -> str:
        """构建记忆上下文"""
        if not memories:
            return ""
        
        context_parts = []
        
        for memory in memories:
            # 根据记忆类型构建上下文
            if memory.type == MemoryType.FACT:
                context_parts.append(f"事实记忆: {memory.content}")
            elif memory.type == MemoryType.PREFERENCE:
                context_parts.append(f"偏好记忆: {memory.content}")
            elif memory.type == MemoryType.EMOTION:
                context_parts.append(f"情感记忆: {memory.content}")
            elif memory.type == MemoryType.CONTEXT:
                context_parts.append(f"上下文记忆: {memory.content}")
            else:
                context_parts.append(f"对话记忆: {memory.content}")
        
        return "\n".join(context_parts)
    
    def process_conversation_end(self, conversation_id: str, participants: List[str] = None):
        """处理对话结束，提取和压缩记忆"""
        if self.enable_memory_compression and self.memory_manager:
            try:
                # 处理当前对话
                result = self.memory_manager.process_conversation(
                    self._memory, 
                    conversation_id, 
                    participants or ["User", "AI"]
                )
                
                logger.info(f"对话结束处理完成: {conversation_id}, 提取了 {result['memory_count']} 个记忆")
                
                # 定期压缩旧数据
                if len(self.memory_manager.memory_compressor.memories) > self.memory_manager.memory_compressor.max_memory_items * 0.8:
                    self.memory_manager.compress_old_data(days_threshold=7)
                    
            except Exception as e:
                logger.error(f"处理对话结束失败: {e}")
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10):
        """搜索记忆"""
        if self.memory_manager:
            return self.memory_manager.search_memories(query, memory_type, limit)
        return []
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        if self.memory_manager:
            return self.memory_manager.get_memory_statistics()
        return {"error": "记忆系统不可用"}
    
    def export_memories(self, filepath: str, format: str = "json"):
        """导出记忆数据"""
        if self.memory_manager:
            self.memory_manager.export_memories(filepath, format)
        else:
            logger.warning("记忆系统不可用，无法导出记忆")
    
    def import_memories(self, filepath: str):
        """导入记忆数据"""
        if self.memory_manager:
            self.memory_manager.import_memories(filepath)
        else:
            logger.warning("记忆系统不可用，无法导入记忆")
    
    def cleanup(self):
        """清理资源"""
        super().cleanup()
        if self.memory_manager:
            self.memory_manager.cleanup()
        logger.info("记忆增强Agent清理完成")
