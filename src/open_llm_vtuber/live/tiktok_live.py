import asyncio
import json
import traceback
from typing import Callable, Dict, Any, List, Optional
from loguru import logger
import aiohttp
import websockets
from .live_interface import LivePlatformInterface

# Try to import TikTok Live libraries (if available)
TIKTOK_LIVE_AVAILABLE = False
try:
    # Option 1: Try TikTokLive library (if installed)
    # pip install TikTokLive
    try:
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent
        TIKTOK_LIVE_AVAILABLE = True
        TIKTOK_LIBRARY = "TikTokLive"
    except ImportError:
        pass
    
    # Option 2: Try other TikTok libraries
    # You can add more libraries here
    if not TIKTOK_LIVE_AVAILABLE:
        try:
            # Add other TikTok library imports here if needed
            pass
        except ImportError:
            pass
            
except Exception as e:
    logger.warning(f"TikTok Live libraries not available: {e}")


class TikTokLivePlatform(LivePlatformInterface):
    """
    Implementation of LivePlatformInterface for TikTok Live platform.
    Connects to a TikTok live room and forwards comments/messages to the VTuber.
    
    Supports multiple connection methods:
    1. TikTokLive library (recommended)
    2. WebSocket direct connection
    3. HTTP polling (fallback)
    """

    def __init__(
        self,
        username: str,
        room_id: Optional[str] = None,
        use_library: bool = True,
        session_id: Optional[str] = None,
        cookie: Optional[str] = None,
    ):
        """
        Initialize the TikTok Live platform client.

        Args:
            username: TikTok username (without @)
            room_id: Optional room ID (if known)
            use_library: Whether to use TikTokLive library if available
            session_id: Optional session ID for authentication
            cookie: Optional cookie string for authentication
        """
        self._username = username
        self._room_id = room_id
        self._use_library = use_library and TIKTOK_LIVE_AVAILABLE
        self._session_id = session_id
        self._cookie = cookie
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._client: Optional[Any] = None  # TikTokLive client if using library
        self._connected = False
        self._running = False
        self._message_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._polling_task: Optional[asyncio.Task] = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to the proxy server."""
        try:
            if self._use_library and self._client:
                # Check TikTokLive client connection
                return self._connected and hasattr(self._client, 'is_connected') and self._client.is_connected
            elif self._websocket:
                if hasattr(self._websocket, "closed"):
                    return self._connected and not self._websocket.closed
                elif hasattr(self._websocket, "open"):
                    return self._connected and self._websocket.open
                else:
                    return self._connected
            else:
                return self._connected
        except Exception:
            return False

    def _init_session(self):
        """Initialize HTTP session with cookies if provided."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        cookies = {}
        if self._cookie:
            # Parse cookie string
            for item in self._cookie.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookies[key] = value
        
        self._session = aiohttp.ClientSession(headers=headers, cookies=cookies)

    async def connect(self, proxy_url: str) -> bool:
        """
        Connect to the proxy WebSocket server.

        Args:
            proxy_url: The WebSocket URL of the proxy

        Returns:
            bool: True if connection successful
        """
        try:
            # Connect to the proxy WebSocket
            self._websocket = await websockets.connect(
                proxy_url, ping_interval=20, ping_timeout=10, close_timeout=5
            )
            self._connected = True
            logger.info(f"Connected to proxy at {proxy_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to proxy: {e}")
            return False

    async def disconnect(self) -> None:
        """
        Disconnect from the proxy server and stop the TikTok client.
        """
        self._running = False

        # Stop TikTok client if running
        if self._client:
            try:
                if hasattr(self._client, 'disconnect'):
                    await self._client.disconnect()
                elif hasattr(self._client, 'stop'):
                    await self._client.stop()
                self._client = None
            except Exception as e:
                logger.warning(f"Error while stopping TikTok client: {e}")

        # Cancel polling task if running
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket connection
        if self._websocket:
            try:
                await self._websocket.close()
            except Exception as e:
                logger.warning(f"Error while closing WebSocket: {e}")

        # Close HTTP session
        if self._session:
            try:
                await self._session.close()
                self._session = None
            except Exception as e:
                logger.warning(f"Error while closing HTTP session: {e}")

        self._connected = False
        logger.info("Disconnected from TikTok Live and proxy server")

    async def send_message(self, text: str) -> bool:
        """
        Send a text message to the VTuber through the proxy.
        TikTok Live doesn't support sending messages back to the live room.

        Args:
            text: The message text

        Returns:
            bool: True if sent successfully
        """
        # TikTok Live platform only receives messages, doesn't send them back
        logger.warning(
            "TikTok Live platform doesn't support sending messages back to the live room"
        )
        return False

    async def register_message_handler(
        self, handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Register a callback for handling incoming messages.

        Args:
            handler: Function to call when a message is received
        """
        self._message_handlers.append(handler)
        logger.debug("Registered new message handler")

    async def _handle_comment(self, comment_text: str, user_info: Optional[Dict] = None):
        """
        Process received comment message and forward it to VTuber.

        Args:
            comment_text: The comment text received from TikTok
            user_info: Optional user information (username, etc.)
        """
        try:
            # Send comment directly to proxy
            await self._send_to_proxy(comment_text)
            if user_info:
                logger.debug(f"[TikTok] {user_info.get('username', 'Unknown')}: {comment_text}")
            else:
                logger.debug(f"[TikTok] Comment: {comment_text}")
        except Exception as e:
            logger.error(f"Error forwarding comment to proxy: {e}")

    async def _send_to_proxy(self, text: str) -> bool:
        """
        Send comment text to the proxy.

        Args:
            text: The comment text to send

        Returns:
            bool: True if sent successfully
        """
        if not self.is_connected or not self._websocket:
            logger.error("Cannot send message: Not connected to proxy")
            return False

        try:
            message = {"type": "text-input", "text": text}
            await self._websocket.send(json.dumps(message))
            logger.info(f"Sent TikTok comment to VTuber: {text}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to proxy: {e}")
            self._connected = False
            return False

    async def start_receiving(self) -> None:
        """
        Start receiving messages from the proxy WebSocket.
        This runs in the background to receive messages from the VTuber.
        """
        if not self.is_connected:
            logger.error("Cannot start receiving: Not connected to proxy")
            return

        try:
            logger.info("Started receiving messages from proxy")
            while self._running and self.is_connected:
                try:
                    message = await self._websocket.recv()
                    data = json.loads(message)

                    # Log received message (truncate audio data for readability)
                    if "audio" in data:
                        log_data = data.copy()
                        log_data["audio"] = (
                            f"[Audio data, length: {len(data['audio'])}]"
                        )
                        logger.debug(f"Received message from VTuber: {log_data}")
                    else:
                        logger.debug(f"Received message from VTuber: {data}")

                    # Process the message
                    await self.handle_incoming_messages(data)

                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed by server")
                    self._connected = False
                    break
                except Exception as e:
                    logger.error(f"Error receiving message from proxy: {e}")
                    await asyncio.sleep(1)

            logger.info("Stopped receiving messages from proxy")
        except Exception as e:
            logger.error(f"Error in message receiving loop: {e}")

    async def handle_incoming_messages(self, message: Dict[str, Any]) -> None:
        """
        Process messages received from the VTuber.

        Args:
            message: The message received from the VTuber
        """
        # Process the message with all registered handlers
        for handler in self._message_handlers:
            try:
                await asyncio.to_thread(handler, message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

    async def _run_with_library(self) -> None:
        """Run using TikTokLive library (recommended method)."""
        if not TIKTOK_LIVE_AVAILABLE:
            raise ImportError("TikTokLive library is required. Install with: pip install TikTokLive")
        
        try:
            # Initialize TikTokLive client
            self._client = TikTokLiveClient(unique_id=self._username)
            
            # Register event handlers
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
                """Handle comment events from TikTok Live."""
                comment_text = event.comment
                user_info = {
                    "username": event.user.nickname,
                    "user_id": event.user.user_id,
                }
                await self._handle_comment(comment_text, user_info)
            
            # Start the client
            await self._client.start()
            
            # Keep running
            while self._running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error running TikTok Live with library: {e}")
            raise

    async def _run_with_websocket(self) -> None:
        """Run using direct WebSocket connection (requires protocol knowledge)."""
        logger.warning("Direct WebSocket connection not fully implemented. Using HTTP polling fallback.")
        await self._run_with_polling()

    async def _run_with_polling(self) -> None:
        """Run using HTTP polling (fallback method)."""
        logger.info("Using HTTP polling method (may be rate-limited)")
        
        # This is a placeholder - you'll need to implement the actual TikTok API polling
        # TikTok doesn't have a public API, so this would require:
        # 1. Reverse engineering TikTok's internal API
        # 2. Using browser automation (Selenium/Playwright)
        # 3. Using third-party services
        
        while self._running:
            try:
                # Placeholder: Implement actual polling logic here
                # This would typically involve:
                # - Making HTTP requests to TikTok's internal API
                # - Parsing the response for new comments
                # - Calling _handle_comment() for each new comment
                
                await asyncio.sleep(5)  # Poll every 5 seconds
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(10)

    async def run(self) -> None:
        """
        Main entry point for running the TikTok Live platform client.
        Connects to TikTok Live and the proxy, and starts monitoring comments.
        """
        proxy_url = "ws://localhost:12393/proxy-ws"

        try:
            self._running = True

            # Initialize HTTP session
            self._init_session()

            # Connect to the proxy
            if not await self.connect(proxy_url):
                logger.error("Failed to connect to proxy, exiting")
                return

            # Start background task for receiving messages from the proxy
            receive_task = asyncio.create_task(self.start_receiving())

            # Start TikTok Live connection based on available method
            if self._use_library:
                logger.info(f"Connecting to TikTok Live using library: @{self._username}")
                tiktok_task = asyncio.create_task(self._run_with_library())
            else:
                logger.info(f"Connecting to TikTok Live using WebSocket: @{self._username}")
                tiktok_task = asyncio.create_task(self._run_with_websocket())

            # Wait for tasks
            try:
                await tiktok_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"TikTok Live task error: {e}")

            # Clean up receive task if necessary
            if not receive_task.done():
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            logger.error(f"Error in TikTok Live run loop: {e}")
            logger.debug(traceback.format_exc())
        finally:
            # Ensure clean disconnect
            await self.disconnect()

