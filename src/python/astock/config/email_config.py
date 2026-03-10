"""邮件配置模型"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class EmailConfig(BaseModel):
    """邮件配置"""

    # SMTP 服务器设置
    smtp_host: str = Field(default="smtp.qq.com", description="SMTP服务器地址")
    smtp_port: int = Field(default=465, description="SMTP端口")
    use_ssl: bool = Field(default=True, description="是否使用SSL加密")
    use_tls: bool = Field(default=False, description="是否使用TLS加密")

    # 发件人信息
    sender_email: str = Field(default="", description="发件人邮箱地址")
    sender_password: str = Field(default="", description="发件人密码/授权码")
    sender_name: str = Field(default="A股交易告警系统", description="发件人显示名称")

    # 收件人列表
    recipients: list[str] = Field(default_factory=list, description="收件人邮箱列表")

    # 邮件内容设置
    subject_prefix: str = Field(default="[A股告警]", description="邮件主题前缀")

    def is_configured(self) -> bool:
        """检查邮件是否已配置完整

        Returns:
            是否已配置
        """
        return bool(self.sender_email and self.sender_password and self.recipients)

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """从环境变量加载邮件配置

        环境变量:
            EMAIL_SMTP_HOST: SMTP服务器地址
            EMAIL_SMTP_PORT: SMTP端口
            EMAIL_USE_SSL: 是否使用SSL
            EMAIL_USE_TLS: 是否使用TLS
            EMAIL_SENDER: 发件人邮箱
            EMAIL_PASSWORD: 发件人密码/授权码
            EMAIL_SENDER_NAME: 发件人显示名称
            EMAIL_RECIPIENTS: 收件人列表(逗号分隔)
            EMAIL_SUBJECT_PREFIX: 邮件主题前缀

        Returns:
            EmailConfig 实例
        """
        recipients_str = os.getenv("EMAIL_RECIPIENTS", "")
        recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

        return cls(
            smtp_host=os.getenv("EMAIL_SMTP_HOST", "smtp.qq.com"),
            smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "465")),
            use_ssl=os.getenv("EMAIL_USE_SSL", "true").lower() == "true",
            use_tls=os.getenv("EMAIL_USE_TLS", "false").lower() == "true",
            sender_email=os.getenv("EMAIL_SENDER", ""),
            sender_password=os.getenv("EMAIL_PASSWORD", ""),
            sender_name=os.getenv("EMAIL_SENDER_NAME", "A股交易告警系统"),
            recipients=recipients,
            subject_prefix=os.getenv("EMAIL_SUBJECT_PREFIX", "[A股告警]"),
        )

    def to_dict(self) -> dict:
        """转换为字典格式

        Returns:
            配置字典
        """
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "use_ssl": self.use_ssl,
            "use_tls": self.use_tls,
            "sender_email": self.sender_email,
            "sender_password": "***",  # 隐藏密码
            "sender_name": self.sender_name,
            "recipients": self.recipients,
            "subject_prefix": self.subject_prefix,
        }
