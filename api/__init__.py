"""
WebAgents API模块

提供RESTful API接口，用于访问各种网站代理服务。
"""

from .routes import router
from .models import (
    NewsResponse,
    SocialResponse,
    FinancialResponse,
    SearchResponse,
    ErrorResponse
)

__all__ = [
    'router',
    'NewsResponse',
    'SocialResponse', 
    'FinancialResponse',
    'SearchResponse',
    'ErrorResponse'
]