"""
Google News 代理
实现Google News RSS/API的内容获取和解析
"""

import feedparser
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
from datetime import datetime

from core.base_agent import BaseAgent
from core.config import Config
from core.exceptions import NetworkError, ParseError


class GoogleNewsAgent(BaseAgent):
    """
    Google News代理类
    通过RSS接口获取Google News的新闻内容
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.google_news_rss_base
        
    def fetch_content(self, query: str = None, lang: str = 'en', 
                     region: str = 'US', limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        获取Google News内容
        
        Args:
            query: 搜索关键词
            lang: 语言代码 (en, zh, ja, ko等)
            region: 地区代码 (US, CN, JP等)
            limit: 返回结果数量限制
            
        Returns:
            Dict: 包含新闻列表的字典
            
        Raises:
            NetworkError: 网络请求失败
        """
        try:
            self.rate_limit_check()
            
            # 构建RSS URL
            url = self._build_rss_url(query, lang, region)
            
            # 发送请求
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            # 解析RSS内容
            parsed_data = self.parse_content(response.text, limit=limit)
            
            return {
                'status': 'success',
                'data': parsed_data,
                'metadata': {
                    'query': query,
                    'lang': lang,
                    'region': region,
                    'total_count': len(parsed_data.get('articles', [])),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch Google News: {str(e)}", url=url)
    
    def parse_content(self, raw_content: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        解析Google News RSS内容
        
        Args:
            raw_content: RSS XML内容
            limit: 返回结果数量限制
            
        Returns:
            Dict: 结构化的新闻数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            # 使用feedparser解析RSS
            feed = feedparser.parse(raw_content)
            
            if feed.bozo:
                raise ParseError("Invalid RSS format", source="Google News")
            
            articles = []
            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'source': self._extract_source(entry),
                    'timestamp': self._parse_timestamp(entry.get('published')),
                    'guid': entry.get('id', ''),
                    'tags': self._extract_tags(entry)
                }
                
                if self.validate_data(article):
                    articles.append(article)
            
            return {
                'articles': articles,
                'feed_info': {
                    'title': feed.feed.get('title', ''),
                    'description': feed.feed.get('description', ''),
                    'language': feed.feed.get('language', ''),
                    'updated': feed.feed.get('updated', '')
                }
            }
            
        except Exception as e:
            raise ParseError(f"Failed to parse Google News RSS: {str(e)}", source="Google News")
    
    def _build_rss_url(self, query: str = None, lang: str = 'en', region: str = 'US') -> str:
        """
        构建Google News RSS URL
        
        Args:
            query: 搜索关键词
            lang: 语言代码
            region: 地区代码
            
        Returns:
            str: 完整的RSS URL
        """
        if query:
            # 搜索特定关键词
            params = {
                'q': query,
                'hl': lang,
                'gl': region,
                'ceid': f"{region}:{lang}"
            }
            return f"{self.base_url}/search?" + urlencode(params)
        else:
            # 获取头条新闻
            params = {
                'hl': lang,
                'gl': region,
                'ceid': f"{region}:{lang}"
            }
            return f"{self.base_url}?" + urlencode(params)
    
    def _extract_source(self, entry) -> str:
        """从RSS条目中提取新闻源"""
        source = entry.get('source', {})
        if isinstance(source, dict):
            return source.get('title', 'Unknown')
        return str(source) if source else 'Unknown'
    
    def _parse_timestamp(self, published: str) -> str:
        """解析发布时间"""
        if not published:
            return datetime.now().isoformat()
        
        try:
            # feedparser通常会解析时间为time.struct_time
            import time
            if hasattr(published, 'tm_year'):
                return datetime(*published[:6]).isoformat()
            else:
                return published
        except:
            return datetime.now().isoformat()
    
    def _extract_tags(self, entry) -> List[str]:
        """提取标签"""
        tags = []
        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term'):
                    tags.append(tag.term)
        return tags
    
    def get_trending_topics(self, lang: str = 'en', region: str = 'US') -> Dict[str, Any]:
        """
        获取热门话题
        
        Args:
            lang: 语言代码
            region: 地区代码
            
        Returns:
            Dict: 热门话题数据
        """
        return self.fetch_content(lang=lang, region=region, limit=20)
    
    def search_news(self, query: str, lang: str = 'en', region: str = 'US', 
                   limit: int = 10) -> Dict[str, Any]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            lang: 语言代码
            region: 地区代码
            limit: 返回结果数量
            
        Returns:
            Dict: 搜索结果
        """
        return self.fetch_content(query=query, lang=lang, region=region, limit=limit)