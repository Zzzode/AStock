"""自定义异常类型"""

from typing import Optional, Any


class AstockError(Exception):
    """A股分析工具基础异常"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.insert(0, f"[{self.code}]")
        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典，用于 API 响应"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class DataSourceError(AstockError):
    """数据源异常"""

    def __init__(self, message: str, source: Optional[str] = None, **kwargs: Any):
        self.source = source
        details = kwargs.pop("details", {})
        if source:
            details["source"] = source
        super().__init__(message, details=details, **kwargs)


class ValidationError(AstockError):
    """验证异常"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs: Any,
    ):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details=details, **kwargs)


class DatabaseError(AstockError):
    """数据库异常"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ):
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        super().__init__(message, details=details, **kwargs)


class ConfigError(AstockError):
    """配置异常"""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs: Any):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details=details, **kwargs)


class StrategyError(AstockError):
    """策略异常"""

    def __init__(self, message: str, strategy: Optional[str] = None, **kwargs: Any):
        details = kwargs.pop("details", {})
        if strategy:
            details["strategy"] = strategy
        super().__init__(message, details=details, **kwargs)


class BacktestError(AstockError):
    """回测异常"""

    def __init__(self, message: str, backtest_id: Optional[str] = None, **kwargs: Any):
        details = kwargs.pop("details", {})
        if backtest_id:
            details["backtest_id"] = backtest_id
        super().__init__(message, details=details, **kwargs)


class AlertError(AstockError):
    """告警异常"""

    def __init__(self, message: str, channel: Optional[str] = None, **kwargs: Any):
        details = kwargs.pop("details", {})
        if channel:
            details["channel"] = channel
        super().__init__(message, details=details, **kwargs)
