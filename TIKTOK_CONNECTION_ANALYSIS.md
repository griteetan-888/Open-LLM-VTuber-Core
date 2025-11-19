# TikTok 连接与弹幕抓取代码分析

本文档详细分析现有代码中如何连接 TikTok 并抓取弹幕的实现机制。

## 📋 目录

1. [整体架构](#整体架构)
2. [核心组件分析](#核心组件分析)
3. [连接流程](#连接流程)
4. [弹幕抓取机制](#弹幕抓取机制)
5. [消息流转路径](#消息流转路径)
6. [代码实现细节](#代码实现细节)

---

## 整体架构

```
┌─────────────────┐
│  TikTok Live    │
│   (直播间)      │
└────────┬────────┘
         │ WebSocket/HTTP
         │ (弹幕数据)
         ▼
┌─────────────────────────┐
│  TikTokLivePlatform     │
│  (tiktok_live.py)      │
│  - 连接TikTok           │
│  - 抓取弹幕             │
│  - 处理事件             │
└────────┬────────────────┘
         │ WebSocket
         │ ws://localhost:12393/proxy-ws
         ▼
┌─────────────────────────┐
│  ProxyHandler           │
│  (proxy_handler.py)     │
│  - 代理转发              │
│  - 多客户端管理          │
└────────┬────────────────┘
         │ WebSocket
         │ ws://localhost:12393/client-ws
         ▼
┌─────────────────────────┐
│  VTuber Server          │
│  (主服务器)             │
│  - 处理消息              │
│  - 生成回复              │
│  - 返回响应              │
└─────────────────────────┘
```

---

## 核心组件分析

### 1. TikTokLivePlatform 类 (`src/open_llm_vtuber/live/tiktok_live.py`)

这是 TikTok 直播平台的核心实现类，继承自 `LivePlatformInterface`。

#### 关键属性

```python
class TikTokLivePlatform(LivePlatformInterface):
    def __init__(
        self,
        username: str,              # TikTok用户名（不带@）
        room_id: Optional[str],     # 直播间ID（可选）
        use_library: bool,          # 是否使用TikTokLive库
        session_id: Optional[str],  # 会话ID（可选）
        cookie: Optional[str],      # Cookie字符串（可选）
    ):
        self._username = username
        self._room_id = room_id
        self._use_library = use_library and TIKTOK_LIVE_AVAILABLE
        self._session: Optional[aiohttp.ClientSession] = None
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._client: Optional[TikTokLiveClient] = None  # TikTokLive客户端
        self._connected = False
        self._running = False
```

#### 连接方式

代码支持三种连接方式（按优先级排序）：

1. **TikTokLive 库方式（推荐）** ✅
   - 使用第三方库 `TikTokLive`
   - 安装：`pip install TikTokLive`
   - 优点：稳定、功能完整、自动重连
   - 实现方法：`_run_with_library()`

2. **WebSocket 直连方式** ⚠️
   - 直接连接 TikTok 的 WebSocket
   - 需要逆向工程协议
   - 当前状态：未完全实现（使用轮询作为后备）

3. **HTTP 轮询方式** ⚠️
   - 通过 HTTP 请求定期获取评论
   - 可能被限流
   - 当前状态：占位符实现

---

## 连接流程

### 步骤 1: 初始化平台实例

```python
# start_tiktok_live.py
platform = TikTokLivePlatform(
    username=live_config.username,        # 从 conf.yaml 读取
    room_id=live_config.room_id,
    use_library=live_config.use_library,
    session_id=live_config.session_id,
    cookie=live_config.cookie,
)
```

### 步骤 2: 启动运行 (`run()` 方法)

```python
async def run(self) -> None:
    # 1. 初始化 HTTP 会话（用于 Cookie 认证）
    self._init_session()
    
    # 2. 连接到代理服务器
    proxy_url = "ws://localhost:12393/proxy-ws"
    await self.connect(proxy_url)
    
    # 3. 启动后台任务接收消息
    receive_task = asyncio.create_task(self.start_receiving())
    
    # 4. 根据配置选择连接方式
    if self._use_library:
        tiktok_task = asyncio.create_task(self._run_with_library())
    else:
        tiktok_task = asyncio.create_task(self._run_with_websocket())
    
    # 5. 等待任务完成
    await tiktok_task
```

### 步骤 3: 连接 TikTok Live（使用库方式）

```python
async def _run_with_library(self) -> None:
    # 1. 创建 TikTokLive 客户端
    self._client = TikTokLiveClient(unique_id=self._username)
    
    # 2. 注册事件处理器
    @self._client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        logger.info(f"Connected to TikTok Live: @{self._username}")
        self._connected = True
    
    @self._client.on(DisconnectEvent)
    async def on_disconnect(event: DisconnectEvent):
        logger.info("Disconnected from TikTok Live")
        self._connected = False
    
    @self._client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        # 处理弹幕事件
        comment_text = event.comment
        user_info = {
            "username": event.user.nickname,
            "user_id": event.user.user_id,
        }
        await self._handle_comment(comment_text, user_info)
    
    # 3. 启动客户端
    await self._client.start()
    
    # 4. 保持运行
    while self._running:
        await asyncio.sleep(1)
```

---

## 弹幕抓取机制

### TikTokLive 库的事件驱动模型

TikTokLive 库使用事件驱动架构，当有弹幕时自动触发 `CommentEvent`：

```python
@self._client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    """
    当 TikTok 直播间有新评论时，此函数自动被调用
    
    event.comment: 评论文本内容
    event.user.nickname: 用户昵称
    event.user.user_id: 用户ID
    """
    comment_text = event.comment
    user_info = {
        "username": event.user.nickname,
        "user_id": event.user.user_id,
    }
    await self._handle_comment(comment_text, user_info)
```

### 弹幕处理流程

```
TikTok 直播间有新评论
        ↓
TikTokLive 库捕获 CommentEvent
        ↓
触发 on_comment() 回调
        ↓
调用 _handle_comment()
        ↓
调用 _send_to_proxy() 发送到代理
        ↓
通过 WebSocket 发送到 ws://localhost:12393/proxy-ws
```

### 代码实现

```python
async def _handle_comment(self, comment_text: str, user_info: Optional[Dict] = None):
    """处理收到的评论并转发到 VTuber"""
    try:
        # 发送评论到代理服务器
        await self._send_to_proxy(comment_text)
        
        # 记录日志
        if user_info:
            logger.debug(f"[TikTok] {user_info.get('username', 'Unknown')}: {comment_text}")
        else:
            logger.debug(f"[TikTok] Comment: {comment_text}")
    except Exception as e:
        logger.error(f"Error forwarding comment to proxy: {e}")

async def _send_to_proxy(self, text: str) -> bool:
    """发送评论文本到代理服务器"""
    if not self.is_connected or not self._websocket:
        logger.error("Cannot send message: Not connected to proxy")
        return False

    try:
        # 构造消息格式
        message = {"type": "text-input", "text": text}
        
        # 通过 WebSocket 发送 JSON 消息
        await self._websocket.send(json.dumps(message))
        logger.info(f"Sent TikTok comment to VTuber: {text}")
        return True
    except Exception as e:
        logger.error(f"Error sending message to proxy: {e}")
        self._connected = False
        return False
```

---

## 消息流转路径

### 1. 弹幕从 TikTok → VTuber

```
TikTok Live 直播间
    ↓ (WebSocket/HTTP)
TikTokLive 库捕获 CommentEvent
    ↓ (事件回调)
TikTokLivePlatform._handle_comment()
    ↓ (调用)
TikTokLivePlatform._send_to_proxy()
    ↓ (WebSocket JSON)
ws://localhost:12393/proxy-ws
    ↓ (ProxyHandler 转发)
ws://localhost:12393/client-ws
    ↓ (VTuber Server 处理)
生成回复、TTS、Live2D 动画
```

### 2. 响应从 VTuber → TikTok（可选）

```
VTuber Server 生成回复
    ↓ (WebSocket)
ws://localhost:12393/client-ws
    ↓ (ProxyHandler 广播)
ws://localhost:12393/proxy-ws
    ↓ (TikTokLivePlatform 接收)
start_receiving() 方法
    ↓ (处理)
handle_incoming_messages()
    ↓ (注册的处理器)
自定义消息处理逻辑
```

**注意**：TikTok Live 平台不支持直接发送消息回直播间，所以 `send_message()` 方法返回 `False`。

---

## 代码实现细节

### 1. 代理服务器连接

```python
async def connect(self, proxy_url: str) -> bool:
    """连接到代理 WebSocket 服务器"""
    try:
        self._websocket = await websockets.connect(
            proxy_url,
            ping_interval=20,    # 每20秒发送一次 ping
            ping_timeout=10,     # ping 超时10秒
            close_timeout=5      # 关闭超时5秒
        )
        self._connected = True
        logger.info(f"Connected to proxy at {proxy_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to proxy: {e}")
        return False
```

### 2. 消息接收循环

```python
async def start_receiving(self) -> None:
    """启动接收来自代理服务器的消息"""
    while self._running and self.is_connected:
        try:
            # 接收 WebSocket 消息
            message = await self._websocket.recv()
            data = json.loads(message)
            
            # 处理消息（可能是音频、文本等）
            await self.handle_incoming_messages(data)
            
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed by server")
            self._connected = False
            break
        except Exception as e:
            logger.error(f"Error receiving message from proxy: {e}")
            await asyncio.sleep(1)
```

### 3. HTTP 会话初始化（用于认证）

```python
def _init_session(self):
    """初始化 HTTP 会话，支持 Cookie 认证"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    cookies = {}
    if self._cookie:
        # 解析 Cookie 字符串
        for item in self._cookie.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
    
    self._session = aiohttp.ClientSession(headers=headers, cookies=cookies)
```

### 4. 断开连接清理

```python
async def disconnect(self) -> None:
    """断开连接并清理资源"""
    self._running = False
    
    # 停止 TikTok 客户端
    if self._client:
        if hasattr(self._client, 'disconnect'):
            await self._client.disconnect()
        self._client = None
    
    # 取消轮询任务
    if self._polling_task:
        self._polling_task.cancel()
    
    # 关闭 WebSocket
    if self._websocket:
        await self._websocket.close()
    
    # 关闭 HTTP 会话
    if self._session:
        await self._session.close()
        self._session = None
    
    self._connected = False
```

---

## 配置文件说明

### conf.yaml 中的 TikTok 配置

```yaml
live_config:
  tiktok_live:
    username: 'griteetan'      # TikTok用户名（必需，不带@）
    room_id: ''                 # 直播间ID（可选）
    use_library: true           # 是否使用TikTokLive库（推荐）
    session_id: ''              # 会话ID（可选，用于认证）
    cookie: ''                  # Cookie字符串（可选，用于认证）
```

### 配置项说明

- **username**: TikTok 用户名，例如 `griteetan`（不要带 `@` 符号）
- **room_id**: 直播间 ID，如果已知可以填写，否则留空
- **use_library**: 是否使用 TikTokLive 库，推荐设为 `true`
- **session_id**: 用于认证的会话 ID（某些功能可能需要）
- **cookie**: 用于认证的 Cookie 字符串（从浏览器开发者工具获取）

---

## 使用示例

### 方法 1: 使用启动脚本

```bash
# 1. 安装依赖
pip install TikTokLive

# 2. 配置 conf.yaml
# 编辑 conf.yaml，设置 tiktok_live.username

# 3. 运行启动脚本
python start_tiktok_live.py
```

### 方法 2: 在代码中使用

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

---

## 关键依赖

### 必需依赖

1. **TikTokLive** (推荐)
   ```bash
   pip install TikTokLive
   ```
   - 提供完整的 TikTok Live API
   - 支持实时评论、礼物、关注等事件
   - 自动重连机制

2. **websockets**
   - 用于连接代理服务器

3. **aiohttp**
   - 用于 HTTP 请求和 WebSocket 客户端

### 可选依赖

- **Cookie/Session ID**: 某些功能可能需要认证

---

## 错误处理与重连

### TikTokLive 库的自动重连

TikTokLive 库内置了自动重连机制，当连接断开时会自动尝试重连。

### 代理服务器重连

当前实现中，如果代理服务器连接断开，需要手动重启。可以添加自动重连逻辑：

```python
async def _reconnect_proxy(self):
    """自动重连代理服务器"""
    while self._running:
        if not self.is_connected:
            logger.info("Attempting to reconnect to proxy...")
            if await self.connect("ws://localhost:12393/proxy-ws"):
                logger.info("Reconnected to proxy")
                break
        await asyncio.sleep(5)
```

---

## 扩展功能

### 1. 添加更多事件处理

```python
from TikTokLive.events import GiftEvent, FollowEvent, LikeEvent

@self._client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    logger.info(f"收到礼物: {event.gift.name} x{event.gift.count}")

@self._client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    logger.info(f"新关注: {event.user.nickname}")

@self._client.on(LikeEvent)
async def on_like(event: LikeEvent):
    logger.info(f"收到点赞: {event.user.nickname}")
```

### 2. 消息过滤

```python
async def _handle_comment(self, comment_text: str, user_info: Optional[Dict] = None):
    # 过滤特定消息
    if comment_text.startswith('!'):
        # 处理命令
        await self._handle_command(comment_text)
        return
    
    # 过滤空消息
    if not comment_text.strip():
        return
    
    # 转发到VTuber
    await self._send_to_proxy(comment_text)
```

### 3. 自定义消息格式

```python
async def _send_to_proxy(self, text: str, user_info: Optional[Dict] = None) -> bool:
    message = {
        "type": "text-input",
        "text": text,
        "source": "tiktok",
        "user": user_info,  # 包含用户信息
        "timestamp": time.time()
    }
    await self._websocket.send(json.dumps(message))
```

---

## 注意事项

1. **合规性**: 确保遵守 TikTok 的服务条款和使用政策
2. **速率限制**: 注意 API 调用频率，避免被限流
3. **稳定性**: 网络不稳定时可能需要重连机制
4. **隐私**: 不要泄露用户的 Cookie 或会话信息
5. **依赖**: TikTok 没有官方公开 API，依赖第三方库或逆向工程

---

## 相关文件

- **核心实现**: `src/open_llm_vtuber/live/tiktok_live.py`
- **启动脚本**: `start_tiktok_live.py`
- **接口定义**: `src/open_llm_vtuber/live/live_interface.py`
- **代理处理**: `src/open_llm_vtuber/proxy_handler.py`
- **路由配置**: `src/open_llm_vtuber/routes.py`
- **配置文件**: `conf.yaml`
- **使用指南**: `TIKTOK_LIVE_GUIDE.md`

---

## 总结

TikTok 连接与弹幕抓取的实现基于以下核心机制：

1. **TikTokLive 库**: 使用第三方库连接 TikTok Live 并捕获事件
2. **事件驱动**: 通过事件回调机制实时接收弹幕
3. **代理转发**: 通过 WebSocket 代理服务器转发消息到 VTuber 服务器
4. **异步处理**: 使用 asyncio 实现异步并发处理

整个流程实现了从 TikTok 直播间到 VTuber 服务器的完整消息流转，支持实时弹幕抓取和响应处理。

