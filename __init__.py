"""
WebAgents - 智能网站代理系统
一个强大的多网站数据抓取和分析平台
"""

from .core import BaseAgent, Config
from .agents import (
    GoogleNewsAgent, 
    XTwitterAgent, 
    RedditAgent, 
    Jin10Agent, 
    TigerAgent, 
    TradingViewAgent
)
from .utils import DataProcessor, CacheManager, Logger, RateLimiter

__version__ = "1.0.0"
__author__ = "WebAgents Team"

__all__ = [
    # 核心模块
    'BaseAgent',
    'Config',
    
    # 代理类
    'GoogleNewsAgent',
    'XTwitterAgent', 
    'RedditAgent',
    'Jin10Agent',
    'TigerAgent',
    'TradingViewAgent',
    
    # 工具类
    'DataProcessor',
    'CacheManager', 
    'Logger',
    'RateLimiter'
]