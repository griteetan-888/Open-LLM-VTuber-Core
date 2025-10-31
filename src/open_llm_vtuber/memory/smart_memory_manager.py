"""
智能记忆管理器
集成记忆压缩、检索和管理的完整系统
"""
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass, asdict
from .memory_compressor import MemoryCompressor, MemoryItem, MemoryType

@dataclass
class ConversationSummary:
    """对话摘要"""
    conversation_id: str
    summary: str
    key_points: List[str]
    participants: List[str]
    timestamp: datetime
    duration_minutes: float
    memory_count: int

class SmartMemoryManager:
    """智能记忆管理器"""
    
    def __init__(self, 
                 max_memory_items: int = 1000,
                 compression_threshold: float = 0.3,
                 memory_file_path: str = "memory/memories.json",
                 summary_file_path: str = "memory/summaries.json"):
        self.memory_compressor = MemoryCompressor(max_memory_items, compression_threshold)
        self.memory_file_path = memory_file_path
        self.summary_file_path = summary_file_path
        self.conversation_summaries: Dict[str, ConversationSummary] = {}
        
        # 确保目录存在
        os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(summary_file_path), exist_ok=True)
        
        # 加载现有记忆
        self._load_existing_memories()
    
    def _load_existing_memories(self):
        """加载现有记忆"""
        if os.path.exists(self.memory_file_path):
            self.memory_compressor.load_memories(self.memory_file_path)
        
        if os.path.exists(self.summary_file_path):
            self._load_conversation_summaries()
    
    def _load_conversation_summaries(self):
        """加载对话摘要"""
        try:
            with open(self.summary_file_path, 'r', encoding='utf-8') as f:
                summaries_data = json.load(f)
            
            for summary_data in summaries_data.get("summaries", []):
                summary = ConversationSummary(
                    conversation_id=summary_data["conversation_id"],
                    summary=summary_data["summary"],
                    key_points=summary_data["key_points"],
                    participants=summary_data["participants"],
                    timestamp=datetime.fromisoformat(summary_data["timestamp"]),
                    duration_minutes=summary_data["duration_minutes"],
                    memory_count=summary_data["memory_count"]
                )
                self.conversation_summaries[summary.conversation_id] = summary
            
            logger.info(f"加载了 {len(self.conversation_summaries)} 个对话摘要")
            
        except Exception as e:
            logger.error(f"加载对话摘要失败: {e}")
            self.conversation_summaries = {}
    
    def process_conversation(self, 
                           conversation: List[Dict[str, Any]], 
                           conversation_id: str,
                           participants: List[str] = None) -> Dict[str, Any]:
        """处理对话，提取记忆和生成摘要"""
        logger.info(f"处理对话: {conversation_id}")
        
        # 计算对话时长
        start_time = None
        end_time = None
        
        for message in conversation:
            if message.get("role") != "metadata":
                if not start_time:
                    start_time = datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat()))
                end_time = datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat()))
        
        duration_minutes = 0
        if start_time and end_time:
            duration_minutes = (end_time - start_time).total_seconds() / 60
        
        # 提取记忆
        memory_ids = self.memory_compressor.add_conversation_memory(conversation, conversation_id)
        
        # 生成对话摘要
        summary = self._generate_conversation_summary(conversation, conversation_id, participants or ["User", "AI"])
        
        # 保存摘要
        conversation_summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary["summary"],
            key_points=summary["key_points"],
            participants=participants or ["User", "AI"],
            timestamp=datetime.now(),
            duration_minutes=duration_minutes,
            memory_count=len(memory_ids)
        )
        
        self.conversation_summaries[conversation_id] = conversation_summary
        
        # 保存记忆和摘要
        self._save_memories()
        self._save_conversation_summaries()
        
        return {
            "conversation_id": conversation_id,
            "memory_count": len(memory_ids),
            "summary": summary,
            "duration_minutes": duration_minutes
        }
    
    def _generate_conversation_summary(self, 
                                     conversation: List[Dict[str, Any]], 
                                     conversation_id: str) -> Dict[str, Any]:
        """生成对话摘要"""
        # 提取关键信息
        user_messages = [msg for msg in conversation if msg.get("role") == "human"]
        ai_messages = [msg for msg in conversation if msg.get("role") == "ai"]
        
        # 生成摘要
        summary_text = f"对话 {conversation_id} 包含 {len(user_messages)} 条用户消息和 {len(ai_messages)} 条AI回复。"
        
        # 提取关键点
        key_points = []
        
        # 从用户消息中提取关键点
        for msg in user_messages[-5:]:  # 最近5条用户消息
            content = msg.get("content", "")
            if len(content) > 20:  # 只考虑较长的消息
                key_points.append(f"用户: {content[:50]}...")
        
        # 从AI消息中提取关键点
        for msg in ai_messages[-3:]:  # 最近3条AI回复
            content = msg.get("content", "")
            if len(content) > 20:
                key_points.append(f"AI: {content[:50]}...")
        
        return {
            "summary": summary_text,
            "key_points": key_points[:5]  # 最多5个关键点
        }
    
    def get_contextual_memories(self, 
                              current_conversation: List[Dict[str, Any]], 
                              limit: int = 5) -> List[MemoryItem]:
        """获取上下文相关记忆"""
        # 从当前对话中提取关键词
        keywords = self._extract_keywords_from_conversation(current_conversation)
        
        # 构建查询
        query = " ".join(keywords)
        
        # 获取相关记忆
        relevant_memories = self.memory_compressor.get_relevant_memories(query, limit)
        
        logger.info(f"找到 {len(relevant_memories)} 个相关记忆")
        return relevant_memories
    
    def _extract_keywords_from_conversation(self, conversation: List[Dict[str, Any]]) -> List[str]:
        """从对话中提取关键词"""
        keywords = []
        
        for message in conversation[-10:]:  # 最近10条消息
            if message.get("role") == "metadata":
                continue
                
            content = message.get("content", "")
            if content:
                # 简单的关键词提取（可以后续优化为更复杂的NLP）
                words = content.split()
                # 过滤短词和常见词
                filtered_words = [word for word in words if len(word) > 2 and word.lower() not in ["的", "了", "是", "在", "有", "和", "与", "或"]]
                keywords.extend(filtered_words[:3])  # 每条消息最多3个关键词
        
        return list(set(keywords))  # 去重
    
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationSummary]:
        """获取对话历史摘要"""
        return self.conversation_summaries.get(conversation_id)
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10) -> List[MemoryItem]:
        """搜索记忆"""
        memories = self.memory_compressor.get_relevant_memories(query, limit)
        
        # 按类型过滤
        if memory_type:
            memories = [memory for memory in memories if memory.type == memory_type]
        
        return memories
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        base_stats = self.memory_compressor.get_memory_statistics()
        
        # 添加对话摘要统计
        summary_stats = {
            "total_conversations": len(self.conversation_summaries),
            "average_memories_per_conversation": 0,
            "total_duration_minutes": 0
        }
        
        if self.conversation_summaries:
            total_memories = sum(summary.memory_count for summary in self.conversation_summaries.values())
            total_duration = sum(summary.duration_minutes for summary in self.conversation_summaries.values())
            
            summary_stats.update({
                "average_memories_per_conversation": total_memories / len(self.conversation_summaries),
                "total_duration_minutes": total_duration
            })
        
        return {**base_stats, **summary_stats}
    
    def compress_old_data(self, days_threshold: int = 30):
        """压缩旧数据"""
        # 压缩旧记忆
        self.memory_compressor.compress_old_memories(days_threshold)
        
        # 压缩旧对话摘要
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        old_summaries = [
            conv_id for conv_id, summary in self.conversation_summaries.items()
            if summary.timestamp < cutoff_date
        ]
        
        for conv_id in old_summaries:
            del self.conversation_summaries[conv_id]
        
        logger.info(f"压缩了 {len(old_summaries)} 个旧对话摘要")
        
        # 保存更新后的数据
        self._save_memories()
        self._save_conversation_summaries()
    
    def _save_memories(self):
        """保存记忆"""
        self.memory_compressor.save_memories(self.memory_file_path)
    
    def _save_conversation_summaries(self):
        """保存对话摘要"""
        summaries_data = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "total_summaries": len(self.conversation_summaries)
            },
            "summaries": []
        }
        
        for summary in self.conversation_summaries.values():
            summary_data = asdict(summary)
            summary_data["timestamp"] = summary.timestamp.isoformat()
            summaries_data["summaries"].append(summary_data)
        
        with open(self.summary_file_path, 'w', encoding='utf-8') as f:
            json.dump(summaries_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"对话摘要已保存到: {self.summary_file_path}")
    
    def export_memories(self, filepath: str, format: str = "json"):
        """导出记忆数据"""
        if format == "json":
            export_data = {
                "memories": [asdict(memory) for memory in self.memory_compressor.memories.values()],
                "conversation_summaries": [asdict(summary) for summary in self.conversation_summaries.values()],
                "statistics": self.get_memory_statistics(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"记忆数据已导出到: {filepath}")
    
    def import_memories(self, filepath: str):
        """导入记忆数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 导入记忆
            if "memories" in import_data:
                for memory_data in import_data["memories"]:
                    memory = MemoryItem(
                        id=memory_data["id"],
                        type=MemoryType(memory_data["type"]),
                        content=memory_data["content"],
                        importance=memory_data["importance"],
                        timestamp=datetime.fromisoformat(memory_data["timestamp"]),
                        source_conversation=memory_data["source_conversation"],
                        tags=memory_data["tags"],
                        compressed=memory_data.get("compressed", False),
                        access_count=memory_data.get("access_count", 0),
                        last_accessed=datetime.fromisoformat(memory_data["last_accessed"]) if memory_data.get("last_accessed") else None
                    )
                    self.memory_compressor.memories[memory.id] = memory
            
            # 导入对话摘要
            if "conversation_summaries" in import_data:
                for summary_data in import_data["conversation_summaries"]:
                    summary = ConversationSummary(
                        conversation_id=summary_data["conversation_id"],
                        summary=summary_data["summary"],
                        key_points=summary_data["key_points"],
                        participants=summary_data["participants"],
                        timestamp=datetime.fromisoformat(summary_data["timestamp"]),
                        duration_minutes=summary_data["duration_minutes"],
                        memory_count=summary_data["memory_count"]
                    )
                    self.conversation_summaries[summary.conversation_id] = summary
            
            logger.info(f"成功导入记忆数据: {filepath}")
            
        except Exception as e:
            logger.error(f"导入记忆数据失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        self._save_memories()
        self._save_conversation_summaries()
        logger.info("记忆管理器清理完成")
