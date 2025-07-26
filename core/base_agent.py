"""
基础代理类
定义所有网站代理的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
import time
import logging
from core.config import Config
from core.exceptions import NetworkError, ParseError, RateLimitError

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    所有网站代理的基础抽象类
    定义了通用的请求处理逻辑和数据格式规范
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.last_request_time = 0
        self.request_count = 0
        
    @abstractmethod
    def fetch_content(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        获取网站内容的抽象方法
        
        Args:
            url: 目标URL
            **kwargs: 额外参数
            
        Returns:
            Dict: 原始内容数据
            
        Raises:
            NetworkError: 网络请求失败
            RateLimitError: 请求频率超限
        """
        pass
    
    @abstractmethod
    def parse_content(self, raw_content: str, **kwargs) -> Dict[str, Any]:
        """
        解析网站内容的抽象方法
        
        Args:
            raw_content: 原始内容
            **kwargs: 解析参数
            
        Returns:
            Dict: 结构化数据
            
        Raises:
            ParseError: 内容解析失败
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性和有效性
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 验证结果
        """
        if not isinstance(data, dict):
            return False
            
        required_fields = ['title', 'content', 'timestamp', 'source']
        return all(field in data for field in required_fields)
    
    def cache_data(self, key: str, data: Dict[str, Any]) -> None:
        """
        缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
        """
        # TODO: 实现缓存逻辑
        logger.info(f"Caching data with key: {key}")
    
    def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Dict]: 缓存的数据，如果不存在则返回None
        """
        # TODO: 实现缓存获取逻辑
        logger.info(f"Getting cached data with key: {key}")
        return None
    
    def rate_limit_check(self) -> None:
        """
        检查请求频率限制
        
        Raises:
            RateLimitError: 请求频率超限
        """
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        
        if time_diff < self.config.min_request_interval:
            wait_time = self.config.min_request_interval - time_diff
            time.sleep(wait_time)
            
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            Dict: HTTP请求头
        """
        return {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }