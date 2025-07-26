"""
Reddit 代理
实现Reddit API (PRAW)的内容获取和解析
"""

import praw
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.base_agent import BaseAgent
from ...core.config import Config
from ...core.exceptions import NetworkError, ParseError, AuthenticationError


class RedditAgent(BaseAgent):
    """
    Reddit 代理类
    通过Reddit API (PRAW)获取Reddit内容
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.reddit = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Reddit API客户端"""
        if not self.config.is_reddit_configured():
            raise AuthenticationError(
                "Reddit API credentials not configured", 
                service="Reddit"
            )
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.config.reddit_client_id,
                client_secret=self.config.reddit_client_secret,
                user_agent=self.config.reddit_user_agent
            )
            
            # 测试连接
            self.reddit.user.me()
            
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Reddit client: {str(e)}")
    
    def fetch_content(self, subreddit: str = 'all', sort: str = 'hot', 
                     limit: int = 10, time_filter: str = 'day', **kwargs) -> Dict[str, Any]:
        """
        获取Reddit内容
        
        Args:
            subreddit: 子版块名称
            sort: 排序方式 ('hot', 'new', 'top', 'rising')
            limit: 返回结果数量限制
            time_filter: 时间过滤 ('hour', 'day', 'week', 'month', 'year', 'all')
            
        Returns:
            Dict: 包含帖子列表的字典
            
        Raises:
            NetworkError: API请求失败
        """
        try:
            self.rate_limit_check()
            
            # 获取子版块
            sub = self.reddit.subreddit(subreddit)
            
            # 根据排序方式获取帖子
            if sort == 'hot':
                submissions = sub.hot(limit=limit)
            elif sort == 'new':
                submissions = sub.new(limit=limit)
            elif sort == 'top':
                submissions = sub.top(time_filter=time_filter, limit=limit)
            elif sort == 'rising':
                submissions = sub.rising(limit=limit)
            else:
                submissions = sub.hot(limit=limit)
            
            parsed_data = self.parse_content(submissions, limit=limit)
            
            return {
                'status': 'success',
                'data': parsed_data,
                'metadata': {
                    'subreddit': subreddit,
                    'sort': sort,
                    'time_filter': time_filter,
                    'total_count': len(parsed_data.get('posts', [])),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise NetworkError(f"Failed to fetch Reddit content: {str(e)}")
    
    def parse_content(self, submissions, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        解析Reddit API响应
        
        Args:
            submissions: Reddit submissions迭代器
            limit: 返回结果数量限制
            
        Returns:
            Dict: 结构化的帖子数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            posts = []
            count = 0
            
            for submission in submissions:
                if count >= limit:
                    break
                
                # 获取帖子内容
                post_data = {
                    'title': submission.title,
                    'content': submission.selftext or submission.url,
                    'url': f"https://reddit.com{submission.permalink}",
                    'source': 'Reddit',
                    'timestamp': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'post_id': submission.id,
                    'subreddit': submission.subreddit.display_name,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'is_video': submission.is_video,
                    'is_self': submission.is_self,
                    'over_18': submission.over_18,
                    'spoiler': submission.spoiler,
                    'stickied': submission.stickied,
                    'flair': {
                        'text': submission.link_flair_text,
                        'css_class': submission.link_flair_css_class
                    },
                    'awards': self._extract_awards(submission),
                    'media_type': self._determine_media_type(submission)
                }
                
                posts.append(post_data)
                count += 1
            
            return {
                'posts': posts,
                'subreddit_info': {
                    'name': posts[0]['subreddit'] if posts else None,
                    'total_posts': len(posts)
                }
            }
            
        except Exception as e:
            raise ParseError(f"Failed to parse Reddit response: {str(e)}", source="Reddit")
    
    def _extract_awards(self, submission) -> List[Dict[str, Any]]:
        """提取帖子奖励信息"""
        awards = []
        try:
            for award in submission.all_awardings:
                awards.append({
                    'name': award.get('name', ''),
                    'count': award.get('count', 0),
                    'icon_url': award.get('icon_url', '')
                })
        except:
            pass
        return awards
    
    def _determine_media_type(self, submission) -> str:
        """确定媒体类型"""
        if submission.is_video:
            return 'video'
        elif submission.is_self:
            return 'text'
        elif any(ext in submission.url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return 'image'
        elif 'youtube.com' in submission.url or 'youtu.be' in submission.url:
            return 'youtube'
        else:
            return 'link'
    
    def get_subreddit_posts(self, subreddit: str, sort: str = 'hot', 
                           limit: int = 10, time_filter: str = 'day') -> Dict[str, Any]:
        """
        获取特定子版块的帖子
        
        Args:
            subreddit: 子版块名称
            sort: 排序方式
            limit: 返回结果数量
            time_filter: 时间过滤
            
        Returns:
            Dict: 子版块帖子数据
        """
        return self.fetch_content(subreddit=subreddit, sort=sort, limit=limit, time_filter=time_filter)
    
    def search_posts(self, query: str, subreddit: str = 'all', 
                    sort: str = 'relevance', limit: int = 10) -> Dict[str, Any]:
        """
        搜索Reddit帖子
        
        Args:
            query: 搜索关键词
            subreddit: 搜索范围的子版块
            sort: 排序方式 ('relevance', 'hot', 'top', 'new', 'comments')
            limit: 返回结果数量
            
        Returns:
            Dict: 搜索结果
        """
        try:
            sub = self.reddit.subreddit(subreddit)
            submissions = sub.search(query, sort=sort, limit=limit)
            
            parsed_data = self.parse_content(submissions, limit=limit)
            
            return {
                'status': 'success',
                'data': parsed_data,
                'metadata': {
                    'query': query,
                    'subreddit': subreddit,
                    'sort': sort,
                    'total_count': len(parsed_data.get('posts', [])),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise NetworkError(f"Failed to search Reddit posts: {str(e)}")
    
    def get_post_comments(self, post_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        获取帖子评论
        
        Args:
            post_id: 帖子ID
            limit: 返回评论数量
            
        Returns:
            Dict: 评论数据
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # 展开所有评论
            
            comments = []
            count = 0
            
            for comment in submission.comments.list()[:limit]:
                if count >= limit:
                    break
                
                comment_data = {
                    'id': comment.id,
                    'body': comment.body,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                    'is_submitter': comment.is_submitter,
                    'stickied': comment.stickied,
                    'parent_id': comment.parent_id,
                    'depth': comment.depth if hasattr(comment, 'depth') else 0
                }
                
                comments.append(comment_data)
                count += 1
            
            return {
                'status': 'success',
                'data': {
                    'post_id': post_id,
                    'comments': comments,
                    'total_comments': len(comments)
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise NetworkError(f"Failed to get post comments: {str(e)}")
    
    def get_trending_subreddits(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取热门子版块
        
        Args:
            limit: 返回结果数量
            
        Returns:
            Dict: 热门子版块数据
        """
        try:
            # 获取热门子版块
            popular_subreddits = []
            
            # 这里可以实现获取热门子版块的逻辑
            # Reddit API可能需要特殊权限来获取这些数据
            
            return {
                'status': 'success',
                'data': {
                    'subreddits': popular_subreddits
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Trending subreddits feature requires additional implementation'
                }
            }
            
        except Exception as e:
            raise NetworkError(f"Failed to get trending subreddits: {str(e)}")