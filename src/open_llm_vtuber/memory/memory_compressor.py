"""
智能记忆压缩引擎
实现聊天历史的智能压缩和记忆管理
"""
import json
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class MemoryType(Enum):
    """记忆类型枚举"""
    CONVERSATION = "conversation"  # 对话记忆
    FACT = "fact"                  # 事实记忆
    PREFERENCE = "preference"      # 偏好记忆
    EMOTION = "emotion"            # 情感记忆
    CONTEXT = "context"            # 上下文记忆

@dataclass
class MemoryItem:
    """记忆项数据结构"""
    id: str
    type: MemoryType
    content: str
    importance: float  # 重要性评分 (0-1)
    timestamp: datetime
    source_conversation: str  # 来源对话ID
    tags: List[str]  # 标签
    compressed: bool = False
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class MemoryCompressor:
    """智能记忆压缩器"""
    
    def __init__(self, max_memory_items: int = 1000, compression_threshold: float = 0.3):
        self.max_memory_items = max_memory_items
        self.compression_threshold = compression_threshold
        self.memories: Dict[str, MemoryItem] = {}
        self.compression_rules = self._initialize_compression_rules()
        
    def _initialize_compression_rules(self) -> Dict[str, Any]:
        """初始化压缩规则"""
        return {
            "importance_threshold": 0.5,  # 重要性阈值
            "age_decay_factor": 0.1,     # 年龄衰减因子
            "access_frequency_weight": 0.3,  # 访问频率权重
            "compression_ratio": 0.7,      # 压缩比例
            "retention_period_days": 30,  # 保留期（天）
        }
    
    def add_conversation_memory(self, conversation: List[Dict[str, Any]], conversation_id: str) -> List[str]:
        """添加对话记忆"""
        memory_ids = []
        
        # 分析对话内容
        conversation_analysis = self._analyze_conversation(conversation)
        
        # 提取不同类型的记忆
        for analysis in conversation_analysis:
            memory_item = MemoryItem(
                id=self._generate_memory_id(analysis["content"]),
                type=MemoryType(analysis["type"]),
                content=analysis["content"],
                importance=analysis["importance"],
                timestamp=datetime.now(),
                source_conversation=conversation_id,
                tags=analysis["tags"]
            )
            
            self.memories[memory_item.id] = memory_item
            memory_ids.append(memory_item.id)
        
        # 检查是否需要压缩
        if len(self.memories) > self.max_memory_items:
            self._compress_memories()
        
        logger.info(f"添加了 {len(memory_ids)} 个记忆项")
        return memory_ids
    
    def _analyze_conversation(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析对话内容，提取记忆"""
        memories = []
        
        for i, message in enumerate(conversation):
            if message.get("role") == "metadata":
                continue
                
            content = message.get("content", "")
            if not content:
                continue
            
            # 分析消息类型和重要性
            analysis = self._analyze_message_content(content, i, len(conversation))
            if analysis:
                memories.append(analysis)
        
        return memories
    
    def _analyze_message_content(self, content: str, position: int, total_length: int) -> Optional[Dict[str, Any]]:
        """分析消息内容，确定记忆类型和重要性"""
        content_lower = content.lower()
        
        # 重要性评分基础
        importance = 0.5
        
        # 位置权重（对话开始和结束更重要）
        if position < 3 or position > total_length - 3:
            importance += 0.2
        
        # 内容长度权重
        if len(content) > 100:
            importance += 0.1
        
        # 关键词检测
        memory_type = MemoryType.CONVERSATION
        tags = []
        
        # 事实记忆检测
        fact_keywords = ["知道", "了解", "记得", "事实", "信息", "数据"]
        if any(keyword in content_lower for keyword in fact_keywords):
            memory_type = MemoryType.FACT
            importance += 0.2
            tags.append("fact")
        
        # 偏好记忆检测
        preference_keywords = ["喜欢", "不喜欢", "偏好", "习惯", "爱好", "兴趣"]
        if any(keyword in content_lower for keyword in preference_keywords):
            memory_type = MemoryType.PREFERENCE
            importance += 0.3
            tags.append("preference")
        
        # 情感记忆检测
        emotion_keywords = ["开心", "难过", "生气", "兴奋", "担心", "害怕", "爱", "恨"]
        if any(keyword in content_lower for keyword in emotion_keywords):
            memory_type = MemoryType.EMOTION
            importance += 0.2
            tags.append("emotion")
        
        # 上下文记忆检测
        context_keywords = ["之前", "刚才", "昨天", "明天", "计划", "安排"]
        if any(keyword in content_lower for keyword in context_keywords):
            memory_type = MemoryType.CONTEXT
            importance += 0.1
            tags.append("context")
        
        # 确保重要性在0-1范围内
        importance = min(1.0, max(0.0, importance))
        
        # 只有重要性超过阈值的才作为记忆
        if importance >= self.compression_threshold:
            return {
                "type": memory_type.value,
                "content": content,
                "importance": importance,
                "tags": tags
            }
        
        return None
    
    def _generate_memory_id(self, content: str) -> str:
        """生成记忆ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        return f"mem_{timestamp}_{content_hash}"
    
    def _compress_memories(self):
        """压缩记忆"""
        logger.info("开始记忆压缩...")
        
        # 计算每个记忆的压缩分数
        memory_scores = []
        for memory_id, memory in self.memories.items():
            score = self._calculate_compression_score(memory)
            memory_scores.append((memory_id, score))
        
        # 按分数排序，保留高分记忆
        memory_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 保留前N个记忆
        keep_count = int(len(self.memories) * self.compression_rules["compression_ratio"])
        memories_to_keep = memory_scores[:keep_count]
        memories_to_remove = memory_scores[keep_count:]
        
        # 移除低分记忆
        for memory_id, _ in memories_to_remove:
            del self.memories[memory_id]
        
        logger.info(f"压缩完成，保留了 {len(memories_to_keep)} 个记忆，移除了 {len(memories_to_remove)} 个记忆")
    
    def _calculate_compression_score(self, memory: MemoryItem) -> float:
        """计算记忆的压缩分数"""
        # 基础重要性
        score = memory.importance
        
        # 访问频率权重
        access_weight = min(1.0, memory.access_count * 0.1)
        score += access_weight * self.compression_rules["access_frequency_weight"]
        
        # 年龄衰减
        age_days = (datetime.now() - memory.timestamp).days
        age_decay = max(0.0, 1.0 - (age_days * self.compression_rules["age_decay_factor"]))
        score *= age_decay
        
        # 最近访问权重
        if memory.last_accessed:
            days_since_access = (datetime.now() - memory.last_accessed).days
            recent_access_weight = max(0.0, 1.0 - (days_since_access * 0.1))
            score += recent_access_weight * 0.2
        
        return score
    
    def get_relevant_memories(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """获取相关记忆"""
        # 简单的关键词匹配（可以后续优化为语义搜索）
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in self.memories.values():
            # 更新访问信息
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            
            # 计算相关性
            relevance_score = self._calculate_relevance(memory, query_lower)
            if relevance_score > 0.3:  # 相关性阈值
                relevant_memories.append((memory, relevance_score))
        
        # 按相关性排序
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        
        return [memory for memory, _ in relevant_memories[:limit]]
    
    def _calculate_relevance(self, memory: MemoryItem, query: str) -> float:
        """计算记忆与查询的相关性"""
        content_lower = memory.content.lower()
        
        # 直接关键词匹配
        keyword_matches = sum(1 for word in query.split() if word in content_lower)
        keyword_score = keyword_matches / len(query.split()) if query.split() else 0
        
        # 标签匹配
        tag_matches = sum(1 for tag in memory.tags if tag in query)
        tag_score = tag_matches / len(memory.tags) if memory.tags else 0
        
        # 类型匹配
        type_score = 0.1 if memory.type.value in query else 0
        
        return keyword_score * 0.6 + tag_score * 0.3 + type_score * 0.1
    
    def compress_old_memories(self, days_threshold: int = 30):
        """压缩旧记忆"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        old_memories = [
            memory_id for memory_id, memory in self.memories.items()
            if memory.timestamp < cutoff_date and memory.access_count < 2
        ]
        
        for memory_id in old_memories:
            del self.memories[memory_id]
        
        logger.info(f"压缩了 {len(old_memories)} 个旧记忆")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        if not self.memories:
            return {"total_memories": 0}
        
        memory_types = {}
        for memory in self.memories.values():
            memory_types[memory.type.value] = memory_types.get(memory.type.value, 0) + 1
        
        total_importance = sum(memory.importance for memory in self.memories.values())
        avg_importance = total_importance / len(self.memories)
        
        return {
            "total_memories": len(self.memories),
            "memory_types": memory_types,
            "average_importance": avg_importance,
            "compression_ratio": len(self.memories) / self.max_memory_items,
            "oldest_memory": min(memory.timestamp for memory in self.memories.values()).isoformat(),
            "newest_memory": max(memory.timestamp for memory in self.memories.values()).isoformat()
        }
    
    def save_memories(self, filepath: str):
        """保存记忆到文件"""
        memories_data = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "total_memories": len(self.memories)
            },
            "memories": []
        }
        
        for memory in self.memories.values():
            memory_data = {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "importance": memory.importance,
                "timestamp": memory.timestamp.isoformat(),
                "source_conversation": memory.source_conversation,
                "tags": memory.tags,
                "compressed": memory.compressed,
                "access_count": memory.access_count,
                "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else None
            }
            memories_data["memories"].append(memory_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memories_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"记忆已保存到: {filepath}")
    
    def load_memories(self, filepath: str):
        """从文件加载记忆"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                memories_data = json.load(f)
            
            self.memories = {}
            for memory_data in memories_data.get("memories", []):
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
                self.memories[memory.id] = memory
            
            logger.info(f"从 {filepath} 加载了 {len(self.memories)} 个记忆")
            
        except Exception as e:
            logger.error(f"加载记忆失败: {e}")
            self.memories = {}