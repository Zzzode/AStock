"""多渠道告警引擎"""

import asyncio
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..storage import AlertRecord

# 尝试导入 aiohttp，如果不存在则使用 placeholder
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class AlertEngine:
    """多渠道告警引擎

    支持的告警渠道:
    - terminal: 终端输出
    - system: 系统通知 (macOS)
    - wechat: 微信推送 (Server酱)
    - dingtalk: 钉钉推送
    """

    def __init__(self, config_path: Optional[Path] = None):
        """初始化告警引擎

        Args:
            config_path: 配置文件路径，默认为 data/config.json
        """
        self.config_path = config_path or Path("data/config.json")
        self.config = self._load_config()

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
        """邮件推送 (预留接口)

        Args:
            alert: 告警记录
        """
        # TODO: 实现邮件推送
        raise RuntimeError("邮件推送尚未实现")
