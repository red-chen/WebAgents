"""
配置管理模块
管理项目的所有配置参数
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    项目配置类
    """
    
    # 基础配置
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    # 网络请求配置
    timeout: int = field(default_factory=lambda: int(os.getenv('REQUEST_TIMEOUT', '30')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('MAX_RETRIES', '3')))
    min_request_interval: float = field(default_factory=lambda: float(os.getenv('MIN_REQUEST_INTERVAL', '1.0')))
    
    # User-Agent配置
    user_agent: str = field(default_factory=lambda: os.getenv(
        'USER_AGENT', 
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ))
    
    # 缓存配置
    cache_enabled: bool = field(default_factory=lambda: os.getenv('CACHE_ENABLED', 'True').lower() == 'true')
    cache_ttl: int = field(default_factory=lambda: int(os.getenv('CACHE_TTL', '3600')))  # 1小时
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    
    # API配置
    api_host: str = field(default_factory=lambda: os.getenv('API_HOST', '0.0.0.0'))
    api_port: int = field(default_factory=lambda: int(os.getenv('API_PORT', '8000')))
    
    # Agent启用/禁用配置
    google_news_enabled: bool = field(default_factory=lambda: os.getenv('GOOGLE_NEWS_ENABLED', 'True').lower() == 'true')
    x_twitter_enabled: bool = field(default_factory=lambda: os.getenv('X_TWITTER_ENABLED', 'True').lower() == 'true')
    reddit_enabled: bool = field(default_factory=lambda: os.getenv('REDDIT_ENABLED', 'True').lower() == 'true')
    jin10_enabled: bool = field(default_factory=lambda: os.getenv('JIN10_ENABLED', 'True').lower() == 'true')
    tiger_enabled: bool = field(default_factory=lambda: os.getenv('TIGER_ENABLED', 'True').lower() == 'true')
    tradingview_enabled: bool = field(default_factory=lambda: os.getenv('TRADINGVIEW_ENABLED', 'True').lower() == 'true')
    
    # Google News配置
    google_news_rss_base: str = "https://news.google.com/rss"
    google_news_languages: Dict[str, str] = field(default_factory=lambda: {
        'en': 'English',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    })
    
    # X (Twitter) API配置
    twitter_api_key: Optional[str] = field(default_factory=lambda: os.getenv('TWITTER_API_KEY'))
    twitter_api_secret: Optional[str] = field(default_factory=lambda: os.getenv('TWITTER_API_SECRET'))
    twitter_access_token: Optional[str] = field(default_factory=lambda: os.getenv('TWITTER_ACCESS_TOKEN'))
    twitter_access_token_secret: Optional[str] = field(default_factory=lambda: os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
    twitter_bearer_token: Optional[str] = field(default_factory=lambda: os.getenv('TWITTER_BEARER_TOKEN'))
    
    # Reddit API配置
    reddit_client_id: Optional[str] = field(default_factory=lambda: os.getenv('REDDIT_CLIENT_ID'))
    reddit_client_secret: Optional[str] = field(default_factory=lambda: os.getenv('REDDIT_CLIENT_SECRET'))
    reddit_user_agent: str = field(default_factory=lambda: os.getenv('REDDIT_USER_AGENT', 'WebAgents/1.0'))
    
    # 金融网站配置
    jin10_base_url: str = "https://www.jin10.com"
    tiger_base_url: str = "https://www.itiger.com"
    tradingview_base_url: str = "https://www.tradingview.com"
    
    def __post_init__(self):
        """初始化后的验证"""
        self._validate_config()
    
    def _validate_config(self):
        """验证配置参数的有效性"""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        
        if self.min_request_interval < 0:
            raise ValueError("Min request interval cannot be negative")
    
    def get_twitter_config(self) -> Dict[str, Optional[str]]:
        """获取Twitter API配置"""
        return {
            'api_key': self.twitter_api_key,
            'api_secret': self.twitter_api_secret,
            'access_token': self.twitter_access_token,
            'access_token_secret': self.twitter_access_token_secret,
            'bearer_token': self.twitter_bearer_token
        }
    
    def get_reddit_config(self) -> Dict[str, Optional[str]]:
        """获取Reddit API配置"""
        return {
            'client_id': self.reddit_client_id,
            'client_secret': self.reddit_client_secret,
            'user_agent': self.reddit_user_agent
        }
    
    def is_twitter_configured(self) -> bool:
        """检查Twitter API是否已配置"""
        return all([
            self.twitter_api_key,
            self.twitter_api_secret,
            self.twitter_bearer_token
        ])
    
    def is_reddit_configured(self) -> bool:
        """检查Reddit API是否已配置"""
        return all([
            self.reddit_client_id,
            self.reddit_client_secret
        ])
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        # 将键名转换为小写并替换下划线为属性名格式
        attr_name = key.lower()
        
        # 如果是agent启用配置，转换为对应的属性名
        if attr_name.endswith('_enabled'):
            agent_name = attr_name.replace('_enabled', '')
            if agent_name == 'google_news':
                attr_name = 'google_news_enabled'
            elif agent_name == 'x_twitter':
                attr_name = 'x_twitter_enabled'
            elif agent_name == 'reddit':
                attr_name = 'reddit_enabled'
            elif agent_name == 'jin10':
                attr_name = 'jin10_enabled'
            elif agent_name == 'tiger':
                attr_name = 'tiger_enabled'
            elif agent_name == 'tradingview':
                attr_name = 'tradingview_enabled'
        
        return getattr(self, attr_name, default)
    
    def is_agent_enabled(self, agent_type: str) -> bool:
        """
        检查指定agent是否启用
        
        Args:
            agent_type: agent类型
            
        Returns:
            是否启用
        """
        enabled_key = f"{agent_type}_enabled"
        return self.get(enabled_key, True)
    
    def get_enabled_agents(self) -> Dict[str, bool]:
        """
        获取所有agent的启用状态
        
        Returns:
            agent启用状态字典
        """
        return {
            'google_news': self.google_news_enabled,
            'x_twitter': self.x_twitter_enabled,
            'reddit': self.reddit_enabled,
            'jin10': self.jin10_enabled,
            'tiger': self.tiger_enabled,
            'tradingview': self.tradingview_enabled
        }


# 全局配置实例
config = Config()