#!/usr/bin/env python3
"""
启动脚本：连接 TikTok 直播并抓取弹幕

使用方法:
1. 安装 TikTokLive 库（推荐）:
   pip install TikTokLive

2. 配置 conf.yaml 中的 tiktok_live 部分

3. 运行此脚本:
   python start_tiktok_live.py

注意：
- TikTok 没有官方公开 API，需要使用第三方库或逆向工程
- 推荐使用 TikTokLive 库：https://github.com/isaackogan/TikTokLive
- 某些功能可能需要认证（cookie/session_id）
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from open_llm_vtuber.config_manager.main import Config
from open_llm_vtuber.config_manager.utils import read_yaml, validate_config
from open_llm_vtuber.live.tiktok_live import TikTokLivePlatform


async def main():
    """主函数：启动 TikTok 直播弹幕抓取"""
    logger.info("🚀 启动 TikTok 直播弹幕抓取服务")
    
    # 加载配置
    try:
        config: Config = validate_config(read_yaml("conf.yaml"))
        live_config = config.live_config.tiktok_live
        logger.info("✅ 配置文件加载成功")
    except Exception as e:
        logger.error(f"❌ 配置文件加载失败: {e}")
        sys.exit(1)
    
    # 检查配置
    if not live_config.username:
        logger.error("❌ 请在 conf.yaml 中配置 tiktok_live.username")
        sys.exit(1)
    
    # 创建 TikTok Live 平台实例
    try:
        platform = TikTokLivePlatform(
            username=live_config.username,
            room_id=live_config.room_id if live_config.room_id else None,
            use_library=live_config.use_library,
            session_id=live_config.session_id if live_config.session_id else None,
            cookie=live_config.cookie if live_config.cookie else None,
        )
        logger.info(f"✅ TikTok Live 平台初始化成功: @{live_config.username}")
    except Exception as e:
        logger.error(f"❌ TikTok Live 平台初始化失败: {e}")
        logger.info("💡 提示：如果使用库模式，请先安装: pip install TikTokLive")
        sys.exit(1)
    
    # 运行平台
    try:
        logger.info("🔄 开始连接 TikTok 直播...")
        await platform.run()
    except KeyboardInterrupt:
        logger.info("🛑 收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"❌ 运行错误: {e}")
        import traceback
        logger.debug(traceback.format_exc())
    finally:
        await platform.disconnect()
        logger.info("✅ 已断开连接")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 程序已停止")

