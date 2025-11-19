from pydantic import Field
from typing import Dict, ClassVar, List
from .i18n import I18nMixin, Description


class BiliBiliLiveConfig(I18nMixin):
    """Configuration for BiliBili Live platform."""

    room_ids: List[int] = Field([], alias="room_ids")
    sessdata: str = Field("", alias="sessdata")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "room_ids": Description(
            en="List of BiliBili live room IDs to monitor", zh="要监控的B站直播间ID列表"
        ),
        "sessdata": Description(
            en="SESSDATA cookie value for authenticated requests (optional)",
            zh="用于认证请求的SESSDATA cookie值（可选）",
        ),
    }


class TikTokLiveConfig(I18nMixin):
    """Configuration for TikTok Live platform."""

    username: str = Field("", alias="username")
    room_id: str = Field("", alias="room_id")
    use_library: bool = Field(True, alias="use_library")
    session_id: str = Field("", alias="session_id")
    cookie: str = Field("", alias="cookie")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "username": Description(
            en="TikTok username (without @)", zh="TikTok用户名（不带@）"
        ),
        "room_id": Description(
            en="TikTok room ID (optional, if known)", zh="TikTok直播间ID（可选，如果已知）"
        ),
        "use_library": Description(
            en="Whether to use TikTokLive library if available", zh="是否使用TikTokLive库（如果可用）"
        ),
        "session_id": Description(
            en="Session ID for authentication (optional)", zh="用于认证的会话ID（可选）"
        ),
        "cookie": Description(
            en="Cookie string for authentication (optional)", zh="用于认证的Cookie字符串（可选）"
        ),
    }


class LiveConfig(I18nMixin):
    """Configuration for live streaming platforms integration."""

    bilibili_live: BiliBiliLiveConfig = Field(
        BiliBiliLiveConfig(), alias="bilibili_live"
    )
    tiktok_live: TikTokLiveConfig = Field(
        TikTokLiveConfig(), alias="tiktok_live"
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "bilibili_live": Description(
            en="Configuration for BiliBili Live platform", zh="B站直播平台配置"
        ),
        "tiktok_live": Description(
            en="Configuration for TikTok Live platform", zh="TikTok直播平台配置"
        ),
    }
