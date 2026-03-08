"""统一日志配置"""

import logging
import sys
from pathlib import Path
from typing import Optional


# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    console: bool = True,
) -> None:
    """配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件名，None 表示不写入文件
        log_dir: 日志文件目录
        console: 是否输出到控制台
    """
    # 获取根日志器
    root_logger = logging.getLogger("astock")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除已有处理器
    root_logger.handlers.clear()

    # 创建格式器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_dir) / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str = "astock") -> logging.Logger:
    """获取日志器

    Args:
        name: 日志器名称

    Returns:
        配置好的日志器实例
    """
    # 确保以 astock 为前缀
    if not name.startswith("astock"):
        name = f"astock.{name}"
    return logging.getLogger(name)


# 默认配置
setup_logging()
