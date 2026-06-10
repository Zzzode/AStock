"""Multi-channel alert engine"""

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

# Try to import aiohttp, use placeholder if not available
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


async def send_email_notification(alert: AlertRecord, email_config: EmailConfig) -> None:
    """Send email alert notification

    Uses Python standard library smtplib to send HTML-formatted email notifications

    Args:
        alert: Alert record
        email_config: Email configuration

    Raises:
        RuntimeError: Email sending failed
    """
    if not email_config.is_configured():
        raise RuntimeError("Email configuration is incomplete")

    # Build email content
    level_names = {1: "Critical", 2: "Important", 3: "Normal"}
    level_name = level_names.get(alert.level, "Unknown")
    level_colors = {1: "#FF0000", 2: "#FFA500", 3: "#008000"}
    level_color = level_colors.get(alert.level, "#808080")

    # HTML email template
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
            <h2 style="margin: 12px 0 0 0;">Stock Alert Notification</h2>
        </div>
        <table class="info-table">
            <tr>
                <td>Stock Code</td>
                <td><span class="code">{alert.code}</span></td>
            </tr>
            <tr>
                <td>Signal Type</td>
                <td>{alert.signal_name}</td>
            </tr>
            <tr>
                <td>Trigger Time</td>
                <td>{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
        <div class="message">
            <strong>Alert Details:</strong><br>
            {alert.message}
        </div>
        <div class="footer">
            This email is automatically sent by the A-Share Trading Alert System. Please do not reply.
        </div>
    </div>
</body>
</html>
"""

    # Build email subject
    subject = f"{email_config.subject_prefix} [{level_name}] {alert.code} - {alert.signal_name}"

    # Execute synchronous SMTP operations in thread pool
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _send_email_sync,
        email_config,
        subject,
        html_content,
    )


def _send_email_sync(email_config: EmailConfig, subject: str, html_content: str) -> None:
    """Send email synchronously

    Args:
        email_config: Email configuration
        subject: Email subject
        html_content: HTML email content

    Raises:
        RuntimeError: Email sending failed
    """
    try:
        # Create email object
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{email_config.sender_name} <{email_config.sender_email}>"
        msg["To"] = ", ".join(email_config.recipients)

        # Add HTML content
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        # Connect to SMTP server and send
        if email_config.use_ssl:
            # SSL connection
            with smtplib.SMTP_SSL(email_config.smtp_host, email_config.smtp_port) as server:
                server.login(email_config.sender_email, email_config.sender_password)
                server.sendmail(
                    email_config.sender_email,
                    email_config.recipients,
                    msg.as_string()
                )
        else:
            # TLS or plain connection
            with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port) as server:
                if email_config.use_tls:
                    server.starttls()
                server.login(email_config.sender_email, email_config.sender_password)
                server.sendmail(
                    email_config.sender_email,
                    email_config.recipients,
                    msg.as_string()
                )

        print(f"[AlertEngine] Email sent successfully: {', '.join(email_config.recipients)}")

    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(f"Email authentication failed, please check email and password/auth code: {e}")
    except smtplib.SMTPConnectError as e:
        raise RuntimeError(f"SMTP server connection failed: {e}")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Email sending failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Email sending exception: {e}")


class AlertEngine:
    """Multi-channel alert engine

    Supported alert channels:
    - terminal: Terminal output
    - system: System notification (macOS)
    - wechat: WeChat push (ServerChan)
    - dingtalk: DingTalk push
    - email: Email push
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize alert engine

        Args:
            config_path: Configuration file path, defaults to data/config.json
        """
        self.config_path = config_path or Path("data/config.json")
        self.config = self._load_config()
        self.email_config = self._load_email_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration file

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            print(f"[AlertEngine] Configuration file not found: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"[AlertEngine] Configuration file loaded")
                if isinstance(config, dict):
                    return config
                return {}
        except Exception as e:
            print(f"[AlertEngine] Failed to load configuration: {e}")
            return {}

    def _load_email_config(self) -> EmailConfig:
        """Load email configuration

        Prioritizes loading from environment variables, then from configuration file

        Returns:
            EmailConfig instance
        """
        # First try to load from environment variables
        email_config = EmailConfig.from_env()
        if email_config.is_configured():
            print(f"[AlertEngine] Email configuration loaded from environment variables")
            return email_config

        # Load from configuration file
        email_config_data = self.config.get("email", {})
        if email_config_data:
            try:
                email_config = EmailConfig(**email_config_data)
                if email_config.is_configured():
                    print(f"[AlertEngine] Email configuration loaded from config file")
                    return email_config
            except Exception as e:
                print(f"[AlertEngine] Failed to load email configuration: {e}")

        # Return empty configuration
        return EmailConfig()

    async def send(self, alert: AlertRecord, channels: Optional[list[str]] = None) -> dict[str, bool]:
        """Send alert to multiple channels

        Args:
            alert: Alert record
            channels: Specified channel list, defaults to alert.channels

        Returns:
            Send results per channel {channel: success}
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
                    print(f"[AlertEngine] {channel} sent successfully")
                else:
                    print(f"[AlertEngine] Unsupported channel: {channel}")
                    results[channel] = False
            except Exception as e:
                print(f"[AlertEngine] {channel} send failed: {e}")
                results[channel] = False

        return results

    async def _send_terminal(self, alert: AlertRecord) -> None:
        """Terminal alert output

        Args:
            alert: Alert record
        """
        level_names = {1: "Critical", 2: "Important", 3: "Normal"}
        level_name = level_names.get(alert.level, "Unknown")

        border = "=" * 60
        output = f"""
{border}
[{level_name}] Alert Notification
{border}
Stock Code: {alert.code}
Signal Type: {alert.signal_name}
Alert Details: {alert.message}
Trigger Time: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
{border}
"""
        print(output)

    async def _send_system(self, alert: AlertRecord) -> None:
        """System notification (macOS)

        Uses osascript to send macOS system notifications

        Args:
            alert: Alert record
        """
        level_names = {1: "Critical", 2: "Important", 3: "Normal"}
        level_name = level_names.get(alert.level, "Unknown")

        title = f"[{level_name}] {alert.code}"
        message = f"{alert.signal_name}: {alert.message}"

        # Use osascript to send notification
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
            raise RuntimeError(f"System notification send failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("osascript not available, system notifications only supported on macOS")

    async def _send_wechat(self, alert: AlertRecord) -> None:
        """WeChat push (ServerChan)

        Requires wechat.webhook_url to be set in configuration file

        Args:
            alert: Alert record
        """
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp not installed, please run: pip install aiohttp")

        wechat_config = self.config.get("wechat", {})
        webhook_url = wechat_config.get("webhook_url")

        if not webhook_url:
            raise RuntimeError("WeChat webhook_url not configured")

        level_names = {1: "Critical", 2: "Important", 3: "Normal"}
        level_name = level_names.get(alert.level, "Unknown")

        # ServerChan API format
        title = f"[{level_name}] {alert.code} {alert.signal_name}"
        desp = f"""
**Stock Code**: {alert.code}

**Signal Type**: {alert.signal_name}

**Alert Details**: {alert.message}

**Trigger Time**: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

        payload = {
            "title": title,
            "desp": desp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"WeChat push failed: {response.status} - {text}")

    async def _send_dingtalk(self, alert: AlertRecord) -> None:
        """DingTalk push

        Requires dingtalk.webhook_url to be set in configuration file

        Args:
            alert: Alert record
        """
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp not installed, please run: pip install aiohttp")

        dingtalk_config = self.config.get("dingtalk", {})
        webhook_url = dingtalk_config.get("webhook_url")

        if not webhook_url:
            raise RuntimeError("DingTalk webhook_url not configured")

        level_names = {1: "Critical", 2: "Important", 3: "Normal"}
        level_name = level_names.get(alert.level, "Unknown")

        # DingTalk message format
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"[{level_name}] {alert.code}",
                "text": f"""
### [{level_name}] {alert.code}

**Signal Type**: {alert.signal_name}

**Alert Details**: {alert.message}

**Trigger Time**: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"DingTalk push failed: {response.status} - {text}")

    async def _send_email(self, alert: AlertRecord) -> None:
        """Email push

        Args:
            alert: Alert record
        """
        if not self.email_config.is_configured():
            raise RuntimeError("Email push not configured, please set email information")

        await send_email_notification(alert, self.email_config)
