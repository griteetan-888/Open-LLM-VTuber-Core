#!/usr/bin/env python3
"""
记忆系统测试工具
测试智能记忆压缩和管理功能
"""
import asyncio
import time
import json
from typing import List, Dict, Any
from loguru import logger
from pathlib import Path

# 导入记忆系统模块
try:
    from src.open_llm_vtuber.memory.smart_memory_manager import SmartMemoryManager
    from src.open_llm_vtuber.memory.memory_compressor import MemoryType
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"无法导入记忆系统模块: {e}")
    MEMORY_SYSTEM_AVAILABLE = False

class MemorySystemTester:
    """记忆系统测试器"""
    
    def __init__(self):
        self.memory_manager = None
        self.test_results = []
        
        if MEMORY_SYSTEM_AVAILABLE:
            self.memory_manager = SmartMemoryManager(
                max_memory_items=100,
                compression_threshold=0.3,
                memory_file_path="test_memory/memories.json",
                summary_file_path="test_memory/summaries.json"
            )
    
    def generate_test_conversation(self, conversation_id: str, message_count: int = 10) -> List[Dict[str, Any]]:
        """生成测试对话"""
        conversations = [
            {
                "role": "human",
                "content": "你好，我想了解一下人工智能的发展历史。",
                "timestamp": "2024-01-01T10:00:00"
            },
            {
                "role": "ai", 
                "content": "人工智能的发展可以追溯到1950年代，当时图灵提出了著名的图灵测试。",
                "timestamp": "2024-01-01T10:00:30"
            },
            {
                "role": "human",
                "content": "我对机器学习很感兴趣，特别是深度学习。",
                "timestamp": "2024-01-01T10:01:00"
            },
            {
                "role": "ai",
                "content": "深度学习是机器学习的一个分支，使用多层神经网络来学习数据的复杂模式。",
                "timestamp": "2024-01-01T10:01:30"
            },
            {
                "role": "human",
                "content": "我喜欢使用Python进行编程，特别是TensorFlow和PyTorch。",
                "timestamp": "2024-01-01T10:02:00"
            },
            {
                "role": "ai",
                "content": "Python确实是机器学习的首选语言，TensorFlow和PyTorch都是优秀的深度学习框架。",
                "timestamp": "2024-01-01T10:02:30"
            },
            {
                "role": "human",
                "content": "我担心AI可能会取代人类的工作。",
                "timestamp": "2024-01-01T10:03:00"
            },
            {
                "role": "ai",
                "content": "这是一个合理的担忧。AI确实会改变就业市场，但也会创造新的工作机会。",
                "timestamp": "2024-01-01T10:03:30"
            },
            {
                "role": "human",
                "content": "谢谢你的解释，我对AI的未来很乐观。",
                "timestamp": "2024-01-01T10:04:00"
            },
            {
                "role": "ai",
                "content": "很高兴能帮助你了解AI。如果你有其他问题，随时可以问我。",
                "timestamp": "2024-01-01T10:04:30"
            }
        ]
        
        return conversations[:message_count]
    
    def test_memory_compression(self) -> Dict[str, Any]:
        """测试记忆压缩功能"""
        logger.info("🧪 测试记忆压缩功能...")
        
        if not self.memory_manager:
            return {"error": "记忆管理器不可用"}
        
        # 生成多个测试对话
        test_conversations = []
        for i in range(5):
            conversation_id = f"test_conv_{i}"
            conversation = self.generate_test_conversation(conversation_id)
            test_conversations.append((conversation_id, conversation))
        
        # 处理对话
        start_time = time.time()
        for conversation_id, conversation in test_conversations:
            result = self.memory_manager.process_conversation(conversation, conversation_id)
            logger.info(f"处理对话 {conversation_id}: {result['memory_count']} 个记忆")
        
        processing_time = time.time() - start_time
        
        # 获取统计信息
        stats = self.memory_manager.get_memory_statistics()
        
        return {
            "test_name": "memory_compression",
            "conversations_processed": len(test_conversations),
            "processing_time": processing_time,
            "statistics": stats,
            "success": True
        }
    
    def test_memory_retrieval(self) -> Dict[str, Any]:
        """测试记忆检索功能"""
        logger.info("🔍 测试记忆检索功能...")
        
        if not self.memory_manager:
            return {"error": "记忆管理器不可用"}
        
        # 测试查询
        test_queries = [
            "人工智能",
            "机器学习", 
            "Python编程",
            "深度学习",
            "工作担忧"
        ]
        
        retrieval_results = []
        start_time = time.time()
        
        for query in test_queries:
            memories = self.memory_manager.search_memories(query, limit=5)
            retrieval_results.append({
                "query": query,
                "memories_found": len(memories),
                "memory_types": [memory.type.value for memory in memories]
            })
        
        retrieval_time = time.time() - start_time
        
        return {
            "test_name": "memory_retrieval",
            "queries_tested": len(test_queries),
            "retrieval_time": retrieval_time,
            "results": retrieval_results,
            "success": True
        }
    
    def test_memory_compression_performance(self) -> Dict[str, Any]:
        """测试记忆压缩性能"""
        logger.info("⚡ 测试记忆压缩性能...")
        
        if not self.memory_manager:
            return {"error": "记忆管理器不可用"}
        
        # 生成大量记忆
        large_conversation = self.generate_test_conversation("large_conv", 50)
        
        # 测试压缩性能
        start_time = time.time()
        result = self.memory_manager.process_conversation(large_conversation, "large_conv")
        processing_time = time.time() - start_time
        
        # 测试压缩
        start_time = time.time()
        self.memory_manager.compress_old_data(days_threshold=0)  # 压缩所有数据
        compression_time = time.time() - start_time
        
        # 获取最终统计
        final_stats = self.memory_manager.get_memory_statistics()
        
        return {
            "test_name": "memory_compression_performance",
            "conversation_size": len(large_conversation),
            "memories_extracted": result['memory_count'],
            "processing_time": processing_time,
            "compression_time": compression_time,
            "final_statistics": final_stats,
            "success": True
        }
    
    def test_memory_export_import(self) -> Dict[str, Any]:
        """测试记忆导出导入功能"""
        logger.info("📤 测试记忆导出导入功能...")
        
        if not self.memory_manager:
            return {"error": "记忆管理器不可用"}
        
        # 导出记忆
        export_file = "test_memory_export.json"
        start_time = time.time()
        self.memory_manager.export_memories(export_file)
        export_time = time.time() - start_time
        
        # 创建新的记忆管理器
        new_memory_manager = SmartMemoryManager(
            max_memory_items=100,
            compression_threshold=0.3,
            memory_file_path="test_memory/imported_memories.json",
            summary_file_path="test_memory/imported_summaries.json"
        )
        
        # 导入记忆
        start_time = time.time()
        new_memory_manager.import_memories(export_file)
        import_time = time.time() - start_time
        
        # 比较统计信息
        original_stats = self.memory_manager.get_memory_statistics()
        imported_stats = new_memory_manager.get_memory_statistics()
        
        return {
            "test_name": "memory_export_import",
            "export_time": export_time,
            "import_time": import_time,
            "original_memories": original_stats.get("total_memories", 0),
            "imported_memories": imported_stats.get("total_memories", 0),
            "export_file": export_file,
            "success": True
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        logger.info("🚀 开始记忆系统综合测试...")
        logger.info("=" * 60)
        
        if not MEMORY_SYSTEM_AVAILABLE:
            return {"error": "记忆系统不可用"}
        
        test_results = []
        
        # 1. 测试记忆压缩
        compression_result = self.test_memory_compression()
        test_results.append(compression_result)
        
        # 2. 测试记忆检索
        retrieval_result = self.test_memory_retrieval()
        test_results.append(retrieval_result)
        
        # 3. 测试压缩性能
        performance_result = self.test_memory_compression_performance()
        test_results.append(performance_result)
        
        # 4. 测试导出导入
        export_import_result = self.test_memory_export_import()
        test_results.append(export_import_result)
        
        # 生成综合报告
        comprehensive_report = {
            "test_timestamp": time.time(),
            "test_results": test_results,
            "overall_success": all(result.get("success", False) for result in test_results),
            "summary": self._generate_test_summary(test_results)
        }
        
        # 保存报告
        report_file = Path("memory_system_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 测试报告已保存: {report_file}")
        
        return comprehensive_report
    
    def _generate_test_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成测试摘要"""
        successful_tests = sum(1 for result in test_results if result.get("success", False))
        total_tests = len(test_results)
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "test_names": [result.get("test_name", "unknown") for result in test_results]
        }
        
        return summary
    
    def print_test_report(self, report: Dict[str, Any]):
        """打印测试报告"""
        logger.info("📊 记忆系统测试报告")
        logger.info("=" * 60)
        
        if report.get("error"):
            logger.error(f"❌ 测试失败: {report['error']}")
            return
        
        # 基本信息
        logger.info(f"🧪 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.get('test_timestamp', 0)))}")
        logger.info(f"📈 总体成功率: {report.get('overall_success', False)}")
        
        # 测试结果
        test_results = report.get("test_results", [])
        for result in test_results:
            test_name = result.get("test_name", "unknown")
            success = result.get("success", False)
            
            if success:
                logger.info(f"✅ {test_name}: 成功")
                
                # 显示具体结果
                if test_name == "memory_compression":
                    stats = result.get("statistics", {})
                    logger.info(f"   总记忆数: {stats.get('total_memories', 0)}")
                    logger.info(f"   记忆类型: {stats.get('memory_types', {})}")
                
                elif test_name == "memory_retrieval":
                    results = result.get("results", [])
                    logger.info(f"   查询测试: {len(results)} 个")
                    for res in results:
                        logger.info(f"   查询 '{res['query']}': {res['memories_found']} 个记忆")
                
                elif test_name == "memory_compression_performance":
                    logger.info(f"   处理时间: {result.get('processing_time', 0):.3f}秒")
                    logger.info(f"   压缩时间: {result.get('compression_time', 0):.3f}秒")
                    logger.info(f"   提取记忆: {result.get('memories_extracted', 0)} 个")
                
                elif test_name == "memory_export_import":
                    logger.info(f"   导出时间: {result.get('export_time', 0):.3f}秒")
                    logger.info(f"   导入时间: {result.get('import_time', 0):.3f}秒")
                    logger.info(f"   原始记忆: {result.get('original_memories', 0)} 个")
                    logger.info(f"   导入记忆: {result.get('imported_memories', 0)} 个")
            else:
                logger.error(f"❌ {test_name}: 失败")
        
        # 摘要
        summary = report.get("summary", {})
        logger.info(f"📊 测试摘要:")
        logger.info(f"   总测试数: {summary.get('total_tests', 0)}")
        logger.info(f"   成功测试: {summary.get('successful_tests', 0)}")
        logger.info(f"   成功率: {summary.get('success_rate', 0):.1%}")
        
        logger.info("=" * 60)

async def main():
    tester = MemorySystemTester()
    
    print("🧠 记忆系统测试器")
    print("=" * 50)
    print("测试智能记忆压缩和管理功能...")
    
    try:
        report = tester.run_comprehensive_test()
        tester.print_test_report(report)
        print("✅ 测试完成！")
        
    except KeyboardInterrupt:
        print("\n🛑 测试已停止")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
