"""
WebAgents Core Module
核心模块，包含基础代理类、配置管理和异常定义
"""

__version__ = "0.1.0"
__author__ = "WebAgents Team"

from core.base_agent import BaseAgent
from core.config import Config
from core.exceptions import WebAgentsException, NetworkError, ParseError, RateLimitError

__all__ = [
    "BaseAgent",
    "Config", 
    "WebAgentsException",
    "NetworkError",
    "ParseError", 
    "RateLimitError"
]