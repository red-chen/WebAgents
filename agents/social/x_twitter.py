"""
X (Twitter) 代理
实现X/Twitter API v2的内容获取和解析
"""

import tweepy
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.base_agent import BaseAgent
from ...core.config import Config
from ...core.exceptions import NetworkError, ParseError, AuthenticationError


class XTwitterAgent(BaseAgent):
    """
    X (Twitter) 代理类
    通过Twitter API v2获取推文内容
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Twitter API客户端"""
        if not self.config.is_twitter_configured():
            raise AuthenticationError(
                "Twitter API credentials not configured", 
                service="Twitter"
            )
        
        try:
            self.client = tweepy.Client(
                bearer_token=self.config.twitter_bearer_token,
                consumer_key=self.config.twitter_api_key,
                consumer_secret=self.config.twitter_api_secret,
                access_token=self.config.twitter_access_token,
                access_token_secret=self.config.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Twitter client: {str(e)}")
    
    def fetch_content(self, query: str = None, tweet_type: str = 'recent', 
                     limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        获取Twitter内容
        
        Args:
            query: 搜索关键词或话题标签
            tweet_type: 推文类型 ('recent', 'popular', 'mixed')
            limit: 返回结果数量限制
            
        Returns:
            Dict: 包含推文列表的字典
            
        Raises:
            NetworkError: API请求失败
        """
        try:
            self.rate_limit_check()
            
            if query:
                # 搜索推文
                tweets = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(limit, 100),  # API限制
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                    user_fields=['username', 'name', 'verified'],
                    expansions=['author_id']
                )
            else:
                # 获取热门推文 (需要实现其他逻辑)
                raise ValueError("Query parameter is required for Twitter search")
            
            parsed_data = self.parse_content(tweets, limit=limit)
            
            return {
                'status': 'success',
                'data': parsed_data,
                'metadata': {
                    'query': query,
                    'tweet_type': tweet_type,
                    'total_count': len(parsed_data.get('tweets', [])),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except tweepy.TweepyException as e:
            raise NetworkError(f"Twitter API error: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Failed to fetch Twitter content: {str(e)}")
    
    def parse_content(self, tweets_response, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        解析Twitter API响应
        
        Args:
            tweets_response: Twitter API响应对象
            limit: 返回结果数量限制
            
        Returns:
            Dict: 结构化的推文数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            if not tweets_response.data:
                return {'tweets': []}
            
            # 构建用户信息映射
            users_map = {}
            if tweets_response.includes and 'users' in tweets_response.includes:
                for user in tweets_response.includes['users']:
                    users_map[user.id] = user
            
            tweets = []
            for tweet in tweets_response.data[:limit]:
                # 获取作者信息
                author = users_map.get(tweet.author_id, {})
                
                tweet_data = {
                    'title': tweet.text[:100] + '...' if len(tweet.text) > 100 else tweet.text,
                    'content': tweet.text,
                    'url': f"https://twitter.com/i/status/{tweet.id}",
                    'source': 'Twitter',
                    'timestamp': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                    'tweet_id': tweet.id,
                    'author': {
                        'id': tweet.author_id,
                        'username': getattr(author, 'username', 'unknown'),
                        'name': getattr(author, 'name', 'Unknown User'),
                        'verified': getattr(author, 'verified', False)
                    },
                    'metrics': {
                        'retweet_count': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                        'like_count': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                        'reply_count': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                        'quote_count': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0
                    },
                    'context_annotations': tweet.context_annotations or []
                }
                
                tweets.append(tweet_data)
            
            return {
                'tweets': tweets,
                'api_info': {
                    'result_count': len(tweets),
                    'newest_id': tweets_response.meta.get('newest_id') if tweets_response.meta else None,
                    'oldest_id': tweets_response.meta.get('oldest_id') if tweets_response.meta else None
                }
            }
            
        except Exception as e:
            raise ParseError(f"Failed to parse Twitter response: {str(e)}", source="Twitter")
    
    def search_tweets(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        搜索推文
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量
            
        Returns:
            Dict: 搜索结果
        """
        return self.fetch_content(query=query, limit=limit)
    
    def get_trending_hashtags(self, woeid: int = 1) -> Dict[str, Any]:
        """
        获取热门话题标签
        
        Args:
            woeid: Where On Earth ID (1为全球)
            
        Returns:
            Dict: 热门话题数据
        """
        try:
            # 注意: 这个功能需要Twitter API v1.1
            # 这里提供一个基础实现框架
            return {
                'status': 'success',
                'data': {'trends': []},
                'metadata': {
                    'woeid': woeid,
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Trending topics require Twitter API v1.1 access'
                }
            }
        except Exception as e:
            raise NetworkError(f"Failed to get trending hashtags: {str(e)}")
    
    def get_user_tweets(self, username: str, limit: int = 10) -> Dict[str, Any]:
        """
        获取用户推文
        
        Args:
            username: 用户名
            limit: 返回结果数量
            
        Returns:
            Dict: 用户推文数据
        """
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                raise ValueError(f"User {username} not found")
            
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'public_metrics'],
                exclude=['retweets', 'replies']
            )
            
            return self.parse_content(tweets, limit=limit)
            
        except tweepy.TweepyException as e:
            raise NetworkError(f"Failed to get user tweets: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Error getting user tweets: {str(e)}")