"""
WebAgents Core Module
核心模块，包含基础代理类、配置管理和异常定义
"""

__version__ = "0.1.0"
__author__ = "WebAgents Team"

from .base_agent import BaseAgent
from .config import Config
from .exceptions import WebAgentsException, NetworkError, ParseError, RateLimitError

__all__ = [
    "BaseAgent",
    "Config", 
    "WebAgentsException",
    "NetworkError",
    "ParseError", 
    "RateLimitError"
]