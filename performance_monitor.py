#!/usr/bin/env python3
"""
实时性能监控脚本
监控LLM-VTuber系统的各项性能指标
"""
import asyncio
import time
import psutil
import json
import websockets
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

class RealTimePerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            "llm_response_time": 5.0,    # LLM响应时间阈值(秒)
            "tts_generation_time": 3.0,  # TTS生成时间阈值(秒)
            "asr_processing_time": 2.0,   # ASR处理时间阈值(秒)
            "cpu_usage": 80.0,           # CPU使用率阈值(%)
            "memory_usage": 85.0,         # 内存使用率阈值(%)
            "disk_usage": 90.0           # 磁盘使用率阈值(%)
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统性能指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "process_count": len(psutil.pids())
        }
    
    def check_performance_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """检查性能告警"""
        alerts = []
        
        if metrics["cpu_percent"] > self.performance_thresholds["cpu_usage"]:
            alerts.append(f"⚠️  CPU使用率过高: {metrics['cpu_percent']:.1f}%")
        
        if metrics["memory_percent"] > self.performance_thresholds["memory_usage"]:
            alerts.append(f"⚠️  内存使用率过高: {metrics['memory_percent']:.1f}%")
        
        if metrics["disk_percent"] > self.performance_thresholds["disk_usage"]:
            alerts.append(f"⚠️  磁盘使用率过高: {metrics['disk_percent']:.1f}%")
        
        return alerts
    
    async def test_llm_performance(self) -> Dict[str, Any]:
        """测试LLM性能"""
        logger.info("🧠 测试LLM性能...")
        
        try:
            uri = 'ws://localhost:12393/client-ws'
            async with websockets.connect(uri) as websocket:
                # 等待连接建立
                await asyncio.sleep(1)
                
                # 发送测试消息
                test_message = {
                    'type': 'text-input',
                    'content': 'Hello! How are you?'
                }
                
                start_time = time.time()
                await websocket.send(json.dumps(test_message))
                
                # 监听响应
                response_times = []
                llm_start = None
                tts_start = None
                
                timeout = 30
                while time.time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(response)
                        current_time = time.time()
                        
                        if data.get('type') == 'full-text' and llm_start is None:
                            llm_start = current_time
                            logger.info(f"📝 LLM开始响应: {current_time - start_time:.2f}s")
                        
                        elif data.get('type') == 'audio' and tts_start is None:
                            tts_start = current_time
                            logger.info(f"🔊 TTS开始合成: {current_time - start_time:.2f}s")
                        
                        elif data.get('type') == 'control' and data.get('text') == 'conversation-chain-end':
                            total_time = current_time - start_time
                            logger.info(f"✅ 对话完成: {total_time:.2f}s")
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                # 计算性能指标
                llm_response_time = (llm_start - start_time) if llm_start else None
                tts_generation_time = (tts_start - llm_start) if tts_start and llm_start else None
                total_response_time = time.time() - start_time
                
                return {
                    "llm_response_time": llm_response_time,
                    "tts_generation_time": tts_generation_time,
                    "total_response_time": total_response_time,
                    "success": llm_start is not None
                }
                
        except Exception as e:
            logger.error(f"❌ LLM性能测试失败: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(self.metrics_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_metrics = self.metrics_history[-5:]  # 最近5次记录
        
        # 计算趋势
        cpu_trend = self._calculate_trend([m["cpu_percent"] for m in recent_metrics])
        memory_trend = self._calculate_trend([m["memory_percent"] for m in recent_metrics])
        
        return {
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "sample_count": len(recent_metrics)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.metrics_history:
            return {"error": "no_data"}
        
        latest_metrics = self.metrics_history[-1]
        trends = self.analyze_performance_trends()
        alerts = self.check_performance_alerts(latest_metrics)
        
        # 性能评分
        performance_score = self._calculate_performance_score(latest_metrics)
        
        return {
            "timestamp": latest_metrics["timestamp"],
            "current_metrics": latest_metrics,
            "performance_score": performance_score,
            "trends": trends,
            "alerts": alerts,
            "recommendations": self._generate_recommendations(latest_metrics, trends)
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> int:
        """计算性能评分 (0-100)"""
        score = 100
        
        # CPU使用率评分
        if metrics["cpu_percent"] > 80:
            score -= 20
        elif metrics["cpu_percent"] > 60:
            score -= 10
        
        # 内存使用率评分
        if metrics["memory_percent"] > 85:
            score -= 20
        elif metrics["memory_percent"] > 70:
            score -= 10
        
        # 磁盘使用率评分
        if metrics["disk_percent"] > 90:
            score -= 15
        elif metrics["disk_percent"] > 80:
            score -= 5
        
        return max(0, score)
    
    def _generate_recommendations(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if metrics["cpu_percent"] > 70:
            recommendations.append("💡 考虑优化CPU密集型任务或增加处理核心")
        
        if metrics["memory_percent"] > 75:
            recommendations.append("💡 考虑增加内存或优化内存使用")
        
        if metrics["disk_percent"] > 85:
            recommendations.append("💡 清理磁盘空间或增加存储容量")
        
        if trends.get("cpu_trend") == "increasing":
            recommendations.append("💡 CPU使用率呈上升趋势，建议监控系统负载")
        
        if trends.get("memory_trend") == "increasing":
            recommendations.append("💡 内存使用率呈上升趋势，建议检查内存泄漏")
        
        return recommendations
    
    async def monitor_loop(self, interval: int = 30):
        """监控循环"""
        logger.info("📊 开始实时性能监控...")
        logger.info(f"监控间隔: {interval}秒")
        
        while True:
            try:
                # 收集系统指标
                system_metrics = self.get_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # 保持历史记录在合理范围内
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-50:]
                
                # 检查告警
                alerts = self.check_performance_alerts(system_metrics)
                if alerts:
                    for alert in alerts:
                        logger.warning(alert)
                
                # 每5分钟进行一次LLM性能测试
                if len(self.metrics_history) % 10 == 0:
                    llm_performance = await self.test_llm_performance()
                    if llm_performance.get("success"):
                        logger.info(f"🧠 LLM响应时间: {llm_performance.get('llm_response_time', 'N/A'):.2f}s")
                        logger.info(f"🔊 TTS生成时间: {llm_performance.get('tts_generation_time', 'N/A'):.2f}s")
                
                # 每10分钟生成性能报告
                if len(self.metrics_history) % 20 == 0:
                    report = self.generate_performance_report()
                    logger.info(f"📊 性能评分: {report.get('performance_score', 'N/A')}/100")
                    
                    # 保存报告
                    report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report, f, ensure_ascii=False, indent=2)
                    logger.info(f"📄 性能报告已保存: {report_file}")
                
                # 显示当前状态
                logger.info(f"💻 CPU: {system_metrics['cpu_percent']:.1f}% | "
                          f"内存: {system_metrics['memory_percent']:.1f}% | "
                          f"磁盘: {system_metrics['disk_percent']:.1f}%")
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 监控已停止")
                break
            except Exception as e:
                logger.error(f"❌ 监控错误: {e}")
                await asyncio.sleep(interval)

async def main():
    monitor = RealTimePerformanceMonitor()
    
    print("🚀 LLM-VTuber性能监控器")
    print("=" * 50)
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    
    await monitor.monitor_loop(interval=30)

if __name__ == "__main__":
    asyncio.run(main())
