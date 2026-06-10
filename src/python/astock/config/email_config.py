"""Email configuration model"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class EmailConfig(BaseModel):
    """Email configuration"""

    # SMTP server settings
    smtp_host: str = Field(default="smtp.qq.com", description="SMTP server address")
    smtp_port: int = Field(default=465, description="SMTP port")
    use_ssl: bool = Field(default=True, description="Whether to use SSL encryption")
    use_tls: bool = Field(default=False, description="Whether to use TLS encryption")

    # Sender information
    sender_email: str = Field(default="", description="Sender email address")
    sender_password: str = Field(default="", description="Sender password/auth code")
    sender_name: str = Field(default="A股交易告警系统", description="Sender display name")

    # Recipient list
    recipients: list[str] = Field(default_factory=list, description="Recipient email list")

    # Email content settings
    subject_prefix: str = Field(default="[A股告警]", description="Email subject prefix")

    def is_configured(self) -> bool:
        """Check whether email is fully configured

        Returns:
            Whether configured
        """
        return bool(self.sender_email and self.sender_password and self.recipients)

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Load email configuration from environment variables

        Environment variables:
            EMAIL_SMTP_HOST: SMTP server address
            EMAIL_SMTP_PORT: SMTP port
            EMAIL_USE_SSL: Whether to use SSL
            EMAIL_USE_TLS: Whether to use TLS
            EMAIL_SENDER: Sender email
            EMAIL_PASSWORD: Sender password/auth code
            EMAIL_SENDER_NAME: Sender display name
            EMAIL_RECIPIENTS: Recipient list (comma-separated)
            EMAIL_SUBJECT_PREFIX: Email subject prefix

        Returns:
            EmailConfig instance
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
        """Convert to dictionary format

        Returns:
            Configuration dictionary
        """
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "use_ssl": self.use_ssl,
            "use_tls": self.use_tls,
            "sender_email": self.sender_email,
            "sender_password": "***",  # Hide password
            "sender_name": self.sender_name,
            "recipients": self.recipients,
            "subject_prefix": self.subject_prefix,
        }
