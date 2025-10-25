#!/usr/bin/env python3
"""
Open-LLM-VTuber Core 启动脚本
简化版本，专注于核心功能
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
import uvicorn
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from open_llm_vtuber.server import WebSocketServer
from open_llm_vtuber.config_manager import Config, read_yaml, validate_config

def init_logger(console_log_level: str = "INFO") -> None:
    """初始化日志系统"""
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=console_log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {message}",
        colorize=True,
    )

    # 文件输出
    logger.add(
        "logs/debug_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
    )

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Open-LLM-VTuber Core Server")
    parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=12393, help="服务器端口")
    return parser.parse_args()

@logger.catch
def main():
    """主函数"""
    args = parse_args()
    console_log_level = "DEBUG" if args.verbose else "INFO"
    
    # 初始化日志
    init_logger(console_log_level)
    logger.info("🚀 启动 Open-LLM-VTuber Core 服务器")
    
    # 设置环境变量
    os.environ["HF_HOME"] = str(Path(__file__).parent / "models")
    os.environ["MODELSCOPE_CACHE"] = str(Path(__file__).parent / "models")
    
    # 加载配置
    try:
        config: Config = validate_config(read_yaml("conf.yaml"))
        server_config = config.system_config
        logger.info("✅ 配置文件加载成功")
    except Exception as e:
        logger.error(f"❌ 配置文件加载失败: {e}")
        sys.exit(1)
    
    # 初始化WebSocket服务器
    try:
        server = WebSocketServer(config=config)
        logger.info("✅ 服务器初始化成功")
    except Exception as e:
        logger.error(f"❌ 服务器初始化失败: {e}")
        sys.exit(1)
    
    # 异步初始化
    logger.info("🔄 正在初始化服务器上下文...")
    try:
        asyncio.run(server.initialize())
        logger.info("✅ 服务器上下文初始化成功")
    except Exception as e:
        logger.error(f"❌ 服务器上下文初始化失败: {e}")
        sys.exit(1)
    
    # 启动服务器
    logger.info(f"🌐 服务器启动在 {args.host}:{args.port}")
    logger.info("📱 请在浏览器中访问: http://{}:{}".format(args.host, args.port))
    
    try:
        uvicorn.run(
            app=server.app,
            host=args.host,
            port=args.port,
            log_level=console_log_level.lower(),
        )
    except KeyboardInterrupt:
        logger.info("🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器运行错误: {e}")

if __name__ == "__main__":
    main()
