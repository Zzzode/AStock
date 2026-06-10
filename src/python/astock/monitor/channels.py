"""Alert channels - WeCom/DingTalk/Telegram/Email/Terminal"""

import asyncio
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiohttp

from ..utils import get_logger, AlertError

logger = get_logger("alert_channel")


@dataclass
class AlertMessage:
    """Alert message"""

    title: str
    content: str
    level: int = 3  # 1=Critical, 2=Important, 3=Normal
    code: Optional[str] = None
    signal_name: Optional[str] = None


class AlertChannel(ABC):
    """Alert channel base class"""

    name: str = "base"

    @abstractmethod
    async def send(self, message: AlertMessage) -> bool:
        """Send alert"""
        pass


class TerminalChannel(AlertChannel):
    """Terminal output channel"""

    name = "terminal"

    def __init__(self) -> None:
        self.colors = {
            1: "\033[91m",  # Red - Critical
            2: "\033[93m",  # Yellow - Important
            3: "\033[92m",  # Green - Normal
        }
        self.reset = "\033[0m"

    async def send(self, message: AlertMessage) -> bool:
        color = self.colors.get(message.level, self.reset)
        level_text = {1: "Critical", 2: "Important", 3: "Normal"}.get(message.level, "Unknown")

        output = f"""
{color}{"=" * 50}{self.reset}
{color}[{level_text} Alert] {message.title}{self.reset}
{color}{"=" * 50}{self.reset}
{message.content}
{color}{"=" * 50}{self.reset}
"""
        print(output)
        return True


class WeChatWorkChannel(AlertChannel):
    """WeCom (WeChat Work) channel"""

    name = "wechat_work"

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url

    async def send(self, message: AlertMessage) -> bool:
        if not self.webhook_url:
            logger.warning("WeCom webhook not configured")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"### {message.title}\n\n{message.content}"
                    },
                }
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("errcode") == 0:
                            logger.info(f"WeCom alert sent successfully: {message.title}")
                            return True
                        else:
                            logger.error(f"WeCom alert failed: {result}")
                            return False
                    else:
                        logger.error(f"WeCom request failed: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"WeCom send error: {e}", exc_info=True)
            return False


class DingTalkChannel(AlertChannel):
    """DingTalk channel"""

    name = "dingtalk"

    def __init__(self, webhook_url: Optional[str] = None, secret: Optional[str] = None) -> None:
        self.webhook_url = webhook_url
        self.secret = secret

    def _sign(self, timestamp: int) -> str:
        """Generate signature"""
        import hmac
        import hashlib
        import base64
        import urllib.parse

        secret = self.secret
        if secret is None:
            raise ValueError("DingTalk secret not configured")
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    async def send(self, message: AlertMessage) -> bool:
        if not self.webhook_url:
            logger.warning("DingTalk webhook not configured")
            return False

        try:
            import time

            timestamp = int(time.time() * 1000)

            url = self.webhook_url
            if self.secret:
                sign = self._sign(timestamp)
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": message.title,
                        "text": f"### {message.title}\n\n{message.content}",
                    },
                }
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("errcode") == 0:
                            logger.info(f"DingTalk alert sent successfully: {message.title}")
                            return True
                        else:
                            logger.error(f"DingTalk alert failed: {result}")
                            return False
                    else:
                        logger.error(f"DingTalk request failed: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"DingTalk send error: {e}", exc_info=True)
            return False


class TelegramChannel(AlertChannel):
    """Telegram channel"""

    name = "telegram"

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send(self, message: AlertMessage) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram configuration incomplete")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": self.chat_id,
                    "text": f"*{message.title}*\n\n{message.content}",
                    "parse_mode": "Markdown",
                }
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("ok"):
                            logger.info(f"Telegram alert sent successfully: {message.title}")
                            return True
                        else:
                            logger.error(f"Telegram alert failed: {result}")
                            return False
                    else:
                        logger.error(f"Telegram request failed: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Telegram send error: {e}", exc_info=True)
            return False


class EmailChannel(AlertChannel):
    """Email channel"""

    name = "email"

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 465,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_addr: Optional[str] = None,
        to_addrs: Optional[list[str]] = None,
    ) -> None:
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_addr = from_addr or smtp_user
        self.to_addrs = to_addrs or []

    async def send(self, message: AlertMessage) -> bool:
        smtp_server = self.smtp_server
        smtp_user = self.smtp_user
        smtp_password = self.smtp_password
        to_addrs = self.to_addrs

        if smtp_server is None or smtp_user is None or smtp_password is None or not to_addrs:
            logger.warning("Email configuration incomplete")
            return False
        from_addr = self.from_addr or smtp_user

        try:
            # Create email
            msg = MIMEMultipart()
            msg["From"] = from_addr
            msg["To"] = ", ".join(to_addrs)
            msg["Subject"] = f"[A-Share Alert] {message.title}"

            body = f"""
Alert Title: {message.title}
Alert Level: {message.level}
Stock Code: {message.code or "N/A"}
Signal Name: {message.signal_name or "N/A"}

Details:
{message.content}
"""
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Send email (executed in background thread)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email_sync, msg)

            logger.info(f"Email alert sent successfully: {message.title}")
            return True

        except Exception as e:
            logger.error(f"Email send error: {e}", exc_info=True)
            return False

    def _send_email_sync(self, msg: MIMEMultipart) -> None:
        """Send email synchronously"""
        smtp_server = self.smtp_server
        smtp_user = self.smtp_user
        smtp_password = self.smtp_password
        from_addr = self.from_addr or smtp_user
        to_addrs = self.to_addrs
        if smtp_server is None or smtp_user is None or smtp_password is None or from_addr is None:
            raise RuntimeError("Email configuration incomplete")
        with smtplib.SMTP_SSL(smtp_server, self.smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, to_addrs, msg.as_string())


class PushPlusChannel(AlertChannel):
    """PushPlus channel (WeChat push)"""

    name = "pushplus"

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token

    async def send(self, message: AlertMessage) -> bool:
        if not self.token:
            logger.warning("PushPlus token not configured")
            return False

        try:
            url = "http://www.pushplus.plus/send"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "token": self.token,
                    "title": message.title,
                    "content": message.content,
                    "template": "html",
                }
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("code") == 200:
                            logger.info(f"PushPlus alert sent successfully: {message.title}")
                            return True
                        else:
                            logger.error(f"PushPlus alert failed: {result}")
                            return False
                    else:
                        logger.error(f"PushPlus request failed: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"PushPlus send error: {e}", exc_info=True)
            return False


# Channel registry
CHANNEL_REGISTRY: dict[str, type[AlertChannel]] = {
    "terminal": TerminalChannel,
    "wechat_work": WeChatWorkChannel,
    "dingtalk": DingTalkChannel,
    "telegram": TelegramChannel,
    "email": EmailChannel,
    "pushplus": PushPlusChannel,
}


def get_channel(name: str, **config: object) -> AlertChannel:
    """Get alert channel instance"""
    if name not in CHANNEL_REGISTRY:
        raise AlertError(f"Unknown alert channel: {name}", channel=name)
    return CHANNEL_REGISTRY[name](**config)


def list_channels() -> list[str]:
    """List all available channels"""
    return list(CHANNEL_REGISTRY.keys())
