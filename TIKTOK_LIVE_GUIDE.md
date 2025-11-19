# TikTok 直播弹幕抓取集成指南

本指南介绍如何将 Open-LLM-VTuber 框架接入 TikTok 直播平台并抓取弹幕。

## 📋 目录

1. [概述](#概述)
2. [安装依赖](#安装依赖)
3. [配置设置](#配置设置)
4. [使用方法](#使用方法)
5. [实现方式](#实现方式)
6. [常见问题](#常见问题)

## 概述

TikTok 直播弹幕抓取支持多种方式：

1. **TikTokLive 库**（推荐）：使用第三方 Python 库
2. **WebSocket 直连**：直接连接 TikTok 的 WebSocket（需要协议知识）
3. **HTTP 轮询**：通过 HTTP 请求轮询（可能被限流）

## 安装依赖

### 方法 1：使用 TikTokLive 库（推荐）

```bash
pip install TikTokLive
```

这个库提供了完整的 TikTok Live API，支持：
- 实时评论抓取
- 礼物、关注等事件
- 自动重连
- 事件处理

### 方法 2：手动实现

如果不使用库，需要：
- 逆向工程 TikTok 的 WebSocket 协议
- 或使用浏览器自动化（Selenium/Playwright）

## 配置设置

在 `conf.yaml` 中配置 TikTok Live：

```yaml
live_config:
  tiktok_live:
    username: 'your_tiktok_username'  # TikTok用户名（不带@）
    room_id: ''                        # 可选：直播间ID
    use_library: true                  # 是否使用TikTokLive库
    session_id: ''                     # 可选：会话ID
    cookie: ''                         # 可选：Cookie字符串
```

### 配置说明

- **username**: TikTok 用户名（必需），例如：`username123`
- **room_id**: 直播间 ID（可选），如果已知可以填写
- **use_library**: 是否使用 TikTokLive 库（推荐设为 `true`）
- **session_id**: 用于认证的会话 ID（可选，某些功能可能需要）
- **cookie**: 用于认证的 Cookie 字符串（可选）

### 获取 Cookie（可选）

如果需要认证，可以从浏览器获取 Cookie：

1. 打开 TikTok 网站并登录
2. 打开开发者工具（F12）
3. 进入 Network 标签
4. 刷新页面
5. 找到任意请求，复制 Cookie 值
6. 粘贴到配置文件的 `cookie` 字段

## 使用方法

### 方法 1：使用启动脚本

```bash
python start_tiktok_live.py
```

### 方法 2：在代码中使用

```python
import asyncio
from open_llm_vtuber.live.tiktok_live import TikTokLivePlatform

async def main():
    platform = TikTokLivePlatform(
        username='your_username',
        use_library=True
    )
    await platform.run()

asyncio.run(main())
```

## 实现方式

### 1. TikTokLive 库方式（推荐）

代码会自动使用 TikTokLive 库连接：

```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent

client = TikTokLiveClient(unique_id='username')
@client.on(CommentEvent)
async def on_comment(event):
    print(f"{event.user.nickname}: {event.comment}")
```

### 2. WebSocket 直连方式

需要了解 TikTok 的 WebSocket 协议格式。目前代码中提供了框架，但需要实现具体的协议解析。

### 3. HTTP 轮询方式

作为备选方案，通过 HTTP 请求定期获取评论。可能被限流，不推荐。

## 架构说明

```
TikTok Live → TikTokLivePlatform → Proxy WebSocket → VTuber Server
                ↓
           弹幕消息处理
                ↓
           转发到VTuber
```

1. **TikTokLivePlatform** 连接到 TikTok 直播
2. 抓取弹幕/评论
3. 通过 WebSocket 发送到代理服务器（`ws://localhost:12393/proxy-ws`）
4. 代理服务器转发到 VTuber 服务器
5. VTuber 处理消息并生成回复

## 常见问题

### Q1: 提示 "TikTokLive library is required"

**A**: 需要安装 TikTokLive 库：
```bash
pip install TikTokLive
```

### Q2: 连接失败

**A**: 检查：
1. 用户名是否正确（不带 @）
2. 网络连接是否正常
3. TikTok 是否在直播
4. 是否需要认证（cookie/session_id）

### Q3: 抓取不到弹幕

**A**: 
1. 确认直播间正在直播
2. 检查是否有弹幕发送
3. 查看日志中的错误信息
4. 尝试使用认证（cookie）

### Q4: 如何同时支持多个平台？

**A**: 可以同时运行多个平台客户端，每个平台使用不同的代理连接。

### Q5: 支持其他直播平台吗？

**A**: 可以！参考 `bilibili_live.py` 和 `tiktok_live.py` 的实现，创建新的平台集成。

## 扩展开发

### 添加新的事件处理

在 `tiktok_live.py` 中，可以添加更多事件处理：

```python
from TikTokLive.events import GiftEvent, FollowEvent

@self._client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    logger.info(f"收到礼物: {event.gift.name} x{event.gift.count}")

@self._client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    logger.info(f"新关注: {event.user.nickname}")
```

### 自定义消息处理

可以修改 `_handle_comment` 方法来自定义消息处理逻辑：

```python
async def _handle_comment(self, comment_text: str, user_info: Optional[Dict] = None):
    # 过滤特定消息
    if comment_text.startswith('!'):
        # 处理命令
        pass
    
    # 转发到VTuber
    await self._send_to_proxy(comment_text)
```

## 注意事项

1. **合规性**: 确保遵守 TikTok 的服务条款和使用政策
2. **速率限制**: 注意 API 调用频率，避免被限流
3. **稳定性**: 网络不稳定时可能需要重连机制
4. **隐私**: 不要泄露用户的 Cookie 或会话信息

## 相关资源

- [TikTokLive 库文档](https://github.com/isaackogan/TikTokLive)
- [Bilibili 直播集成参考](src/open_llm_vtuber/live/bilibili_live.py)
- [直播平台接口定义](src/open_llm_vtuber/live/live_interface.py)

## 贡献

欢迎提交 PR 来改进 TikTok 直播集成功能！

