"""多渠道告警引擎"""

import asyncio
import json
import subprocess
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

from ..storage import AlertRecord
from ..config import EmailConfig

# 尝试导入 aiohttp，如果不存在则使用 placeholder
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


async def send_email_notification(alert: AlertRecord, email_config: EmailConfig) -> None:
    """发送邮件告警通知

    使用 Python 标准库 smtplib 发送 HTML 格式的邮件通知

    Args:
        alert: 告警记录
        email_config: 邮件配置

    Raises:
        RuntimeError: 邮件发送失败
    """
    if not email_config.is_configured():
        raise RuntimeError("邮件配置不完整")

    # 构建邮件内容
    level_names = {1: "紧急", 2: "重要", 3: "一般"}
    level_name = level_names.get(alert.level, "未知")
    level_colors = {1: "#FF0000", 2: "#FFA500", 3: "#008000"}
    level_color = level_colors.get(alert.level, "#808080")

    # HTML 邮件模板
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            border-bottom: 2px solid {level_color};
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .level-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: {level_color};
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .info-table td {{
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}
        .info-table td:first-child {{
            font-weight: 600;
            color: #666;
            width: 100px;
        }}
        .info-table td:last-child {{
            color: #333;
        }}
        .code {{
            font-family: "SF Mono", Consolas, monospace;
            background-color: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .message {{
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 4px;
            margin-top: 16px;
            border-left: 4px solid {level_color};
        }}
        .footer {{
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #999;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="level-badge">{level_name}</span>
            <h2 style="margin: 12px 0 0 0;">股票告警通知</h2>
        </div>
        <table class="info-table">
            <tr>
                <td>股票代码</td>
                <td><span class="code">{alert.code}</span></td>
            </tr>
            <tr>
                <td>信号类型</td>
                <td>{alert.signal_name}</td>
            </tr>
            <tr>
                <td>触发时间</td>
                <td>{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
        <div class="message">
            <strong>告警详情:</strong><br>
            {alert.message}
        </div>
        <div class="footer">
            此邮件由 A股交易告警系统自动发送，请勿回复。
        </div>
    </div>
</body>
</html>
"""

    # 构建邮件主题
    subject = f"{email_config.subject_prefix} [{level_name}] {alert.code} - {alert.signal_name}"

    # 在线程池中执行同步的 SMTP 操作
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _send_email_sync,
        email_config,
        subject,
        html_content,
    )


def _send_email_sync(email_config: EmailConfig, subject: str, html_content: str) -> None:
    """同步发送邮件

    Args:
        email_config: 邮件配置
        subject: 邮件主题
        html_content: HTML 邮件内容

    Raises:
        RuntimeError: 邮件发送失败
    """
    try:
        # 创建邮件对象
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{email_config.sender_name} <{email_config.sender_email}>"
        msg["To"] = ", ".join(email_config.recipients)

        # 添加 HTML 内容
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        # 连接 SMTP 服务器并发送
        if email_config.use_ssl:
            # SSL 连接
            with smtplib.SMTP_SSL(email_config.smtp_host, email_config.smtp_port) as server:
                server.login(email_config.sender_email, email_config.sender_password)
                server.sendmail(
                    email_config.sender_email,
                    email_config.recipients,
                    msg.as_string()
                )
        else:
            # TLS 或普通连接
            with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port) as server:
                if email_config.use_tls:
                    server.starttls()
                server.login(email_config.sender_email, email_config.sender_password)
                server.sendmail(
                    email_config.sender_email,
                    email_config.recipients,
                    msg.as_string()
                )

        print(f"[AlertEngine] 邮件发送成功: {', '.join(email_config.recipients)}")

    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(f"邮件认证失败，请检查邮箱和密码/授权码: {e}")
    except smtplib.SMTPConnectError as e:
        raise RuntimeError(f"SMTP 服务器连接失败: {e}")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"邮件发送失败: {e}")
    except Exception as e:
        raise RuntimeError(f"邮件发送异常: {e}")


class AlertEngine:
    """多渠道告警引擎

    支持的告警渠道:
    - terminal: 终端输出
    - system: 系统通知 (macOS)
    - wechat: 微信推送 (Server酱)
    - dingtalk: 钉钉推送
    - email: 邮件推送
    """

    def __init__(self, config_path: Optional[Path] = None):
        """初始化告警引擎

        Args:
            config_path: 配置文件路径，默认为 data/config.json
        """
        self.config_path = config_path or Path("data/config.json")
        self.config = self._load_config()
        self.email_config = self._load_email_config()

    def _load_config(self) -> dict[str, Any]:
        """加载配置文件

        Returns:
            配置字典
        """
        if not self.config_path.exists():
            print(f"[AlertEngine] 配置文件不存在: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"[AlertEngine] 已加载配置文件")
                if isinstance(config, dict):
                    return config
                return {}
        except Exception as e:
            print(f"[AlertEngine] 加载配置失败: {e}")
            return {}

    def _load_email_config(self) -> EmailConfig:
        """加载邮件配置

        优先从环境变量加载，其次从配置文件加载

        Returns:
            EmailConfig 实例
        """
        # 首先尝试从环境变量加载
        email_config = EmailConfig.from_env()
        if email_config.is_configured():
            print(f"[AlertEngine] 已从环境变量加载邮件配置")
            return email_config

        # 从配置文件加载
        email_config_data = self.config.get("email", {})
        if email_config_data:
            try:
                email_config = EmailConfig(**email_config_data)
                if email_config.is_configured():
                    print(f"[AlertEngine] 已从配置文件加载邮件配置")
                    return email_config
            except Exception as e:
                print(f"[AlertEngine] 加载邮件配置失败: {e}")

        # 返回空配置
        return EmailConfig()

    async def send(self, alert: AlertRecord, channels: Optional[list[str]] = None) -> dict[str, bool]:
        """发送告警到多个渠道

        Args:
            alert: 告警记录
            channels: 指定渠道列表，默认使用 alert.channels

        Returns:
            各渠道发送结果 {channel: success}
        """
        channels = channels or alert.channels or ["terminal"]
        results: dict[str, bool] = {}

        for channel in channels:
            try:
                method_name = f"_send_{channel}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    await method(alert)
                    results[channel] = True
                    print(f"[AlertEngine] {channel} 发送成功")
                else:
                    print(f"[AlertEngine] 不支持的渠道: {channel}")
                    results[channel] = False
            except Exception as e:
                print(f"[AlertEngine] {channel} 发送失败: {e}")
                results[channel] = False

        return results

    async def _send_terminal(self, alert: AlertRecord) -> None:
        """终端输出告警

        Args:
            alert: 告警记录
        """
        level_names = {1: "紧急", 2: "重要", 3: "一般"}
        level_name = level_names.get(alert.level, "未知")

        border = "=" * 60
        output = f"""
{border}
[{level_name}] 告警通知
{border}
股票代码: {alert.code}
信号类型: {alert.signal_name}
告警详情: {alert.message}
触发时间: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
{border}
"""
        print(output)

    async def _send_system(self, alert: AlertRecord) -> None:
        """系统通知 (macOS)

        使用 osascript 发送 macOS 系统通知

        Args:
            alert: 告警记录
        """
        level_names = {1: "紧急", 2: "重要", 3: "一般"}
        level_name = level_names.get(alert.level, "未知")

        title = f"[{level_name}] {alert.code}"
        message = f"{alert.signal_name}: {alert.message}"

        # 使用 osascript 发送通知
        script = f'''
        display notification "{message}" with title "{title}"
        '''

        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"系统通知发送失败: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("osascript 不可用，系统通知仅支持 macOS")

    async def _send_wechat(self, alert: AlertRecord) -> None:
        """微信推送 (Server酱)

        需要在配置文件中设置 wechat.webhook_url

        Args:
            alert: 告警记录
        """
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp 未安装，请运行: pip install aiohttp")

        wechat_config = self.config.get("wechat", {})
        webhook_url = wechat_config.get("webhook_url")

        if not webhook_url:
            raise RuntimeError("未配置微信 webhook_url")

        level_names = {1: "紧急", 2: "重要", 3: "一般"}
        level_name = level_names.get(alert.level, "未知")

        # Server酱 API 格式
        title = f"[{level_name}] {alert.code} {alert.signal_name}"
        desp = f"""
**股票代码**: {alert.code}

**信号类型**: {alert.signal_name}

**告警详情**: {alert.message}

**触发时间**: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

        payload = {
            "title": title,
            "desp": desp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"微信推送失败: {response.status} - {text}")

    async def _send_dingtalk(self, alert: AlertRecord) -> None:
        """钉钉推送

        需要在配置文件中设置 dingtalk.webhook_url

        Args:
            alert: 告警记录
        """
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp 未安装，请运行: pip install aiohttp")

        dingtalk_config = self.config.get("dingtalk", {})
        webhook_url = dingtalk_config.get("webhook_url")

        if not webhook_url:
            raise RuntimeError("未配置钉钉 webhook_url")

        level_names = {1: "紧急", 2: "重要", 3: "一般"}
        level_name = level_names.get(alert.level, "未知")

        # 钉钉消息格式
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"[{level_name}] {alert.code}",
                "text": f"""
### [{level_name}] {alert.code}

**信号类型**: {alert.signal_name}

**告警详情**: {alert.message}

**触发时间**: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"钉钉推送失败: {response.status} - {text}")

    async def _send_email(self, alert: AlertRecord) -> None:
        """邮件推送

        Args:
            alert: 告警记录
        """
        if not self.email_config.is_configured():
            raise RuntimeError("邮件推送未配置，请设置邮箱信息")

        await send_email_notification(alert, self.email_config)
