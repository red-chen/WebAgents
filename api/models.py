"""
API数据模型定义

定义API请求和响应的数据结构。
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = False
    error_code: str
    error_details: Optional[Dict[str, Any]] = None


class NewsItem(BaseModel):
    """新闻条目模型"""
    title: str
    summary: Optional[str] = None
    url: str
    source: str
    published_at: datetime
    image_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "zh"
    region: str = "CN"


class NewsResponse(BaseResponse):
    """新闻响应模型"""
    data: List[NewsItem]
    total: int
    page: int = 1
    page_size: int = 20


class SocialPost(BaseModel):
    """社交媒体帖子模型"""
    id: str
    content: str
    author: str
    author_id: str
    platform: str  # twitter, reddit
    url: str
    created_at: datetime
    likes: int = 0
    shares: int = 0
    comments: int = 0
    hashtags: List[str] = []
    mentions: List[str] = []
    media_urls: List[str] = []


class SocialResponse(BaseResponse):
    """社交媒体响应模型"""
    data: List[SocialPost]
    total: int
    page: int = 1
    page_size: int = 20


class FinancialData(BaseModel):
    """金融数据模型"""
    symbol: Optional[str] = None
    title: str
    content: str
    data_type: str  # news, quote, analysis, calendar
    source: str  # jin10, tiger, tradingview
    timestamp: datetime
    url: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    metadata: Dict[str, Any] = {}


class FinancialResponse(BaseResponse):
    """金融数据响应模型"""
    data: List[FinancialData]
    total: int
    page: int = 1
    page_size: int = 20


class SearchResult(BaseModel):
    """搜索结果模型"""
    title: str
    content: str
    url: str
    source: str
    platform: str
    timestamp: datetime
    relevance_score: float = 0.0
    data_type: str
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseResponse):
    """搜索响应模型"""
    data: List[SearchResult]
    total: int
    query: str
    sources: List[str]
    page: int = 1
    page_size: int = 20


class NewsRequest(BaseModel):
    """新闻请求模型"""
    query: Optional[str] = None
    lang: str = "zh"
    region: str = "CN"
    category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SocialRequest(BaseModel):
    """社交媒体请求模型"""
    query: Optional[str] = None
    platform: str = "twitter"  # twitter, reddit
    subreddit: Optional[str] = None
    sort: str = "hot"  # hot, new, top
    limit: int = Field(default=20, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class FinancialRequest(BaseModel):
    """金融数据请求模型"""
    symbol: Optional[str] = None
    market: str = "US"  # US, HK, CN
    data_type: str = "news"  # news, quote, analysis, calendar
    category: Optional[str] = None
    interval: str = "1d"  # 1m, 5m, 15m, 1h, 1d, 1w, 1M
    indicators: List[str] = []
    limit: int = Field(default=20, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    sources: List[str] = ["google_news", "twitter", "reddit", "jin10", "tiger", "tradingview"]
    data_types: List[str] = ["news", "social", "financial"]
    lang: str = "zh"
    limit: int = Field(default=20, ge=1, le=100)
    page: int = Field(default=1, ge=1)