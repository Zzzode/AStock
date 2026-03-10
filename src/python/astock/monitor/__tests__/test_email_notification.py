"""邮件推送功能测试"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from astock.config import EmailConfig
from astock.storage import AlertRecord
from astock.monitor.alert_engine import send_email_notification, _send_email_sync


class TestEmailConfig:
    """EmailConfig 测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = EmailConfig()
        assert config.smtp_host == "smtp.qq.com"
        assert config.smtp_port == 465
        assert config.use_ssl is True
        assert config.use_tls is False
        assert config.sender_email == ""
        assert config.sender_password == ""
        assert config.recipients == []
        assert config.is_configured() is False

    def test_is_configured(self):
        """测试配置完整性检查"""
        # 未配置
        config = EmailConfig()
        assert config.is_configured() is False

        # 部分配置
        config = EmailConfig(sender_email="test@example.com")
        assert config.is_configured() is False

        config = EmailConfig(
            sender_email="test@example.com",
            sender_password="password",
        )
        assert config.is_configured() is False

        # 完整配置
        config = EmailConfig(
            sender_email="test@example.com",
            sender_password="password",
            recipients=["recipient@example.com"],
        )
        assert config.is_configured() is True

    def test_from_env(self, monkeypatch):
        """测试从环境变量加载配置"""
        monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.test.com")
        monkeypatch.setenv("EMAIL_SMTP_PORT", "587")
        monkeypatch.setenv("EMAIL_USE_SSL", "false")
        monkeypatch.setenv("EMAIL_USE_TLS", "true")
        monkeypatch.setenv("EMAIL_SENDER", "sender@test.com")
        monkeypatch.setenv("EMAIL_PASSWORD", "test_password")
        monkeypatch.setenv("EMAIL_SENDER_NAME", "测试发件人")
        monkeypatch.setenv("EMAIL_RECIPIENTS", "a@test.com,b@test.com")
        monkeypatch.setenv("EMAIL_SUBJECT_PREFIX", "[测试]")

        config = EmailConfig.from_env()
        assert config.smtp_host == "smtp.test.com"
        assert config.smtp_port == 587
        assert config.use_ssl is False
        assert config.use_tls is True
        assert config.sender_email == "sender@test.com"
        assert config.sender_password == "test_password"
        assert config.sender_name == "测试发件人"
        assert config.recipients == ["a@test.com", "b@test.com"]
        assert config.subject_prefix == "[测试]"

    def test_to_dict(self):
        """测试转换为字典"""
        config = EmailConfig(
            smtp_host="smtp.test.com",
            smtp_port=465,
            sender_email="test@example.com",
            sender_password="secret_password",
            recipients=["recipient@example.com"],
        )
        d = config.to_dict()
        assert d["smtp_host"] == "smtp.test.com"
        assert d["smtp_port"] == 465
        assert d["sender_email"] == "test@example.com"
        assert d["sender_password"] == "***"  # 密码应该被隐藏
        assert d["recipients"] == ["recipient@example.com"]


class TestSendEmailNotification:
    """send_email_notification 测试"""

    @pytest.fixture
    def sample_alert(self):
        """创建测试告警记录"""
        return AlertRecord(
            id=1,
            code="000001",
            signal_type="ma_cross",
            signal_name="MA金叉",
            message="MA5上穿MA20，形成金叉信号",
            level=2,
            triggered_at=datetime(2026, 3, 10, 10, 30, 0),
            status="pending",
            channels=["email"],
        )

    @pytest.fixture
    def sample_email_config(self):
        """创建测试邮件配置"""
        return EmailConfig(
            smtp_host="smtp.test.com",
            smtp_port=465,
            use_ssl=True,
            sender_email="sender@test.com",
            sender_password="test_password",
            sender_name="测试发件人",
            recipients=["recipient@test.com"],
            subject_prefix="[测试]",
        )

    @pytest.mark.asyncio
    async def test_send_email_notification_not_configured(self, sample_alert):
        """测试未配置时发送邮件"""
        config = EmailConfig()  # 未配置
        with pytest.raises(RuntimeError, match="邮件配置不完整"):
            await send_email_notification(sample_alert, config)

    @pytest.mark.asyncio
    async def test_send_email_notification_ssl(self, sample_alert, sample_email_config):
        """测试使用SSL发送邮件"""
        with patch("astock.monitor.alert_engine._send_email_sync") as mock_send:
            await send_email_notification(sample_alert, sample_email_config)
            mock_send.assert_called_once()
            # 检查参数
            call_args = mock_send.call_args
            assert call_args[0][0] == sample_email_config
            assert "[测试]" in call_args[0][1]
            assert "000001" in call_args[0][1]
            assert "MA金叉" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_send_email_notification_tls(self, sample_alert):
        """测试使用TLS发送邮件"""
        config = EmailConfig(
            smtp_host="smtp.test.com",
            smtp_port=587,
            use_ssl=False,
            use_tls=True,
            sender_email="sender@test.com",
            sender_password="test_password",
            recipients=["recipient@test.com"],
        )
        with patch("astock.monitor.alert_engine._send_email_sync") as mock_send:
            await send_email_notification(sample_alert, config)
            mock_send.assert_called_once()

    def test_send_email_sync_ssl(self, sample_email_config):
        """测试同步发送邮件(SSL)"""
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            subject = "[测试] 测试邮件"
            html_content = "<html><body>测试内容</body></html>"

            _send_email_sync(sample_email_config, subject, html_content)

            mock_smtp.assert_called_once_with(
                sample_email_config.smtp_host,
                sample_email_config.smtp_port
            )
            mock_server.login.assert_called_once_with(
                sample_email_config.sender_email,
                sample_email_config.sender_password
            )
            mock_server.sendmail.assert_called_once()

    def test_send_email_sync_tls(self):
        """测试同步发送邮件(TLS)"""
        config = EmailConfig(
            smtp_host="smtp.test.com",
            smtp_port=587,
            use_ssl=False,
            use_tls=True,
            sender_email="sender@test.com",
            sender_password="test_password",
            recipients=["recipient@test.com"],
        )

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            subject = "测试邮件"
            html_content = "<html><body>测试内容</body></html>"

            _send_email_sync(config, subject, html_content)

            mock_smtp.assert_called_once_with(
                config.smtp_host,
                config.smtp_port
            )
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()

    def test_send_email_sync_auth_error(self, sample_email_config):
        """测试邮件认证失败"""
        import smtplib

        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_server = MagicMock()
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
            mock_smtp.return_value.__enter__.return_value = mock_server

            with pytest.raises(RuntimeError, match="邮件认证失败"):
                _send_email_sync(sample_email_config, "测试", "<html></html>")


class TestAlertEngineEmailIntegration:
    """AlertEngine 邮件集成测试"""

    @pytest.fixture
    def email_config(self):
        """创建测试邮件配置"""
        return EmailConfig(
            smtp_host="smtp.test.com",
            smtp_port=465,
            use_ssl=True,
            sender_email="sender@test.com",
            sender_password="test_password",
            recipients=["recipient@test.com"],
        )

    @pytest.mark.asyncio
    async def test_send_email_via_alert_engine(self, email_config, tmp_path):
        """测试通过AlertEngine发送邮件"""
        from astock.monitor.alert_engine import AlertEngine

        # 创建测试配置文件
        config_file = tmp_path / "config.json"
        config_file.write_text('{}')

        engine = AlertEngine(config_path=config_file)
        engine.email_config = email_config

        alert = AlertRecord(
            id=1,
            code="000001",
            signal_type="test",
            signal_name="测试信号",
            message="测试消息",
            level=3,
            triggered_at=datetime.now(),
            status="pending",
            channels=["email"],
        )

        with patch("astock.monitor.alert_engine._send_email_sync") as mock_send:
            await engine._send_email(alert)
            mock_send.assert_called_once()
