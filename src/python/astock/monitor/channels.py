"""告警渠道 - 企业微信/钉钉/Telegram/Email/终端"""

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
    """告警消息"""

    title: str
    content: str
    level: int = 3  # 1=紧急, 2=重要, 3=一般
    code: Optional[str] = None
    signal_name: Optional[str] = None


class AlertChannel(ABC):
    """告警渠道基类"""

    name: str = "base"

    @abstractmethod
    async def send(self, message: AlertMessage) -> bool:
        """发送告警"""
        pass


class TerminalChannel(AlertChannel):
    """终端输出渠道"""

    name = "terminal"

    def __init__(self):
        self.colors = {
            1: "\033[91m",  # 红色 - 紧急
            2: "\033[93m",  # 黄色 - 重要
            3: "\033[92m",  # 绿色 - 一般
        }
        self.reset = "\033[0m"

    async def send(self, message: AlertMessage) -> bool:
        color = self.colors.get(message.level, self.reset)
        level_text = {1: "紧急", 2: "重要", 3: "一般"}.get(message.level, "未知")

        output = f"""
{color}{"=" * 50}{self.reset}
{color}【{level_text}告警】{message.title}{self.reset}
{color}{"=" * 50}{self.reset}
{message.content}
{color}{"=" * 50}{self.reset}
"""
        print(output)
        return True


class WeChatWorkChannel(AlertChannel):
    """企业微信渠道"""

    name = "wechat_work"

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    async def send(self, message: AlertMessage) -> bool:
        if not self.webhook_url:
            logger.warning("企业微信 webhook 未配置")
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
                            logger.info(f"企业微信告警发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"企业微信告警失败: {result}")
                            return False
                    else:
                        logger.error(f"企业微信请求失败: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"企业微信发送错误: {e}", exc_info=True)
            return False


class DingTalkChannel(AlertChannel):
    """钉钉渠道"""

    name = "dingtalk"

    def __init__(self, webhook_url: Optional[str] = None, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret

    def _sign(self, timestamp: int) -> str:
        """生成签名"""
        import hmac
        import hashlib
        import base64
        import urllib.parse

        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    async def send(self, message: AlertMessage) -> bool:
        if not self.webhook_url:
            logger.warning("钉钉 webhook 未配置")
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
                            logger.info(f"钉钉告警发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"钉钉告警失败: {result}")
                            return False
                    else:
                        logger.error(f"钉钉请求失败: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"钉钉发送错误: {e}", exc_info=True)
            return False


class TelegramChannel(AlertChannel):
    """Telegram渠道"""

    name = "telegram"

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send(self, message: AlertMessage) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram 配置不完整")
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
                            logger.info(f"Telegram告警发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"Telegram告警失败: {result}")
                            return False
                    else:
                        logger.error(f"Telegram请求失败: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Telegram发送错误: {e}", exc_info=True)
            return False


class EmailChannel(AlertChannel):
    """邮件渠道"""

    name = "email"

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 465,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_addr: Optional[str] = None,
        to_addrs: Optional[list[str]] = None,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_addr = from_addr or smtp_user
        self.to_addrs = to_addrs or []

    async def send(self, message: AlertMessage) -> bool:
        if not all(
            [self.smtp_server, self.smtp_user, self.smtp_password, self.to_addrs]
        ):
            logger.warning("邮件配置不完整")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Subject"] = f"[A股告警] {message.title}"

            body = f"""
告警标题: {message.title}
告警级别: {message.level}
股票代码: {message.code or "无"}
信号名称: {message.signal_name or "无"}

详细内容:
{message.content}
"""
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件（在后台线程中执行）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email_sync, msg)

            logger.info(f"邮件告警发送成功: {message.title}")
            return True

        except Exception as e:
            logger.error(f"邮件发送错误: {e}", exc_info=True)
            return False

    def _send_email_sync(self, msg: MIMEMultipart) -> None:
        """同步发送邮件"""
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_addr, self.to_addrs, msg.as_string())


class PushPlusChannel(AlertChannel):
    """PushPlus渠道 (微信推送)"""

    name = "pushplus"

    def __init__(self, token: Optional[str] = None):
        self.token = token

    async def send(self, message: AlertMessage) -> bool:
        if not self.token:
            logger.warning("PushPlus token 未配置")
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
                            logger.info(f"PushPlus告警发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"PushPlus告警失败: {result}")
                            return False
                    else:
                        logger.error(f"PushPlus请求失败: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"PushPlus发送错误: {e}", exc_info=True)
            return False


# 渠道注册表
CHANNEL_REGISTRY: dict[str, type[AlertChannel]] = {
    "terminal": TerminalChannel,
    "wechat_work": WeChatWorkChannel,
    "dingtalk": DingTalkChannel,
    "telegram": TelegramChannel,
    "email": EmailChannel,
    "pushplus": PushPlusChannel,
}


def get_channel(name: str, **config) -> AlertChannel:
    """获取告警渠道实例"""
    if name not in CHANNEL_REGISTRY:
        raise AlertError(f"未知告警渠道: {name}", channel=name)
    return CHANNEL_REGISTRY[name](**config)


def list_channels() -> list[str]:
    """列出所有可用渠道"""
    return list(CHANNEL_REGISTRY.keys())
