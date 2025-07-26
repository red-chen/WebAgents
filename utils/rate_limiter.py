"""
频率限制器
提供API调用频率限制功能
"""

import time
import threading
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque


class RateLimiter:
    """
    频率限制器类
    支持多种限制策略：令牌桶、滑动窗口、固定窗口
    """
    
    def __init__(self, strategy: str = 'token_bucket'):
        """
        初始化频率限制器
        
        Args:
            strategy: 限制策略 ('token_bucket', 'sliding_window', 'fixed_window')
        """
        self.strategy = strategy
        self.limits = {}  # 存储各个源的限制配置
        self.buckets = {}  # 令牌桶状态
        self.windows = defaultdict(deque)  # 滑动窗口记录
        self.fixed_windows = {}  # 固定窗口状态
        self.lock = threading.RLock()
    
    def set_limit(self, source: str, limit: int, window: int, burst: int = None):
        """
        设置频率限制
        
        Args:
            source: 限制源标识
            limit: 限制数量
            window: 时间窗口（秒）
            burst: 突发限制（仅令牌桶策略）
        """
        with self.lock:
            self.limits[source] = {
                'limit': limit,
                'window': window,
                'burst': burst or limit
            }
            
            # 初始化对应策略的状态
            if self.strategy == 'token_bucket':
                self.buckets[source] = {
                    'tokens': limit,
                    'last_refill': time.time(),
                    'capacity': burst or limit
                }
            elif self.strategy == 'fixed_window':
                self.fixed_windows[source] = {
                    'count': 0,
                    'window_start': time.time()
                }
    
    def check_limit(self, source: str, tokens: int = 1) -> bool:
        """
        检查是否超过频率限制
        
        Args:
            source: 限制源标识
            tokens: 请求的令牌数量
            
        Returns:
            bool: True表示允许请求，False表示超过限制
        """
        if source not in self.limits:
            return True  # 没有设置限制，允许请求
        
        with self.lock:
            if self.strategy == 'token_bucket':
                return self._check_token_bucket(source, tokens)
            elif self.strategy == 'sliding_window':
                return self._check_sliding_window(source, tokens)
            elif self.strategy == 'fixed_window':
                return self._check_fixed_window(source, tokens)
            else:
                return True
    
    def _check_token_bucket(self, source: str, tokens: int) -> bool:
        """令牌桶策略检查"""
        config = self.limits[source]
        bucket = self.buckets[source]
        
        current_time = time.time()
        time_passed = current_time - bucket['last_refill']
        
        # 计算应该添加的令牌数
        tokens_to_add = time_passed * (config['limit'] / config['window'])
        bucket['tokens'] = min(bucket['capacity'], bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        
        # 检查是否有足够的令牌
        if bucket['tokens'] >= tokens:
            bucket['tokens'] -= tokens
            return True
        else:
            return False
    
    def _check_sliding_window(self, source: str, tokens: int) -> bool:
        """滑动窗口策略检查"""
        config = self.limits[source]
        window = self.windows[source]
        
        current_time = time.time()
        window_start = current_time - config['window']
        
        # 移除窗口外的记录
        while window and window[0] < window_start:
            window.popleft()
        
        # 检查当前窗口内的请求数
        current_count = len(window)
        
        if current_count + tokens <= config['limit']:
            # 添加当前请求的时间戳
            for _ in range(tokens):
                window.append(current_time)
            return True
        else:
            return False
    
    def _check_fixed_window(self, source: str, tokens: int) -> bool:
        """固定窗口策略检查"""
        config = self.limits[source]
        window_state = self.fixed_windows[source]
        
        current_time = time.time()
        window_elapsed = current_time - window_state['window_start']
        
        # 检查是否需要重置窗口
        if window_elapsed >= config['window']:
            window_state['count'] = 0
            window_state['window_start'] = current_time
        
        # 检查当前窗口内的请求数
        if window_state['count'] + tokens <= config['limit']:
            window_state['count'] += tokens
            return True
        else:
            return False
    
    def get_remaining_quota(self, source: str) -> Optional[int]:
        """
        获取剩余配额
        
        Args:
            source: 限制源标识
            
        Returns:
            Optional[int]: 剩余配额，None表示无限制
        """
        if source not in self.limits:
            return None
        
        with self.lock:
            config = self.limits[source]
            
            if self.strategy == 'token_bucket':
                bucket = self.buckets[source]
                current_time = time.time()
                time_passed = current_time - bucket['last_refill']
                tokens_to_add = time_passed * (config['limit'] / config['window'])
                current_tokens = min(bucket['capacity'], bucket['tokens'] + tokens_to_add)
                return int(current_tokens)
            
            elif self.strategy == 'sliding_window':
                window = self.windows[source]
                current_time = time.time()
                window_start = current_time - config['window']
                
                # 计算窗口内的请求数
                valid_requests = sum(1 for timestamp in window if timestamp >= window_start)
                return max(0, config['limit'] - valid_requests)
            
            elif self.strategy == 'fixed_window':
                window_state = self.fixed_windows[source]
                current_time = time.time()
                window_elapsed = current_time - window_state['window_start']
                
                if window_elapsed >= config['window']:
                    return config['limit']
                else:
                    return max(0, config['limit'] - window_state['count'])
            
            return None
    
    def get_reset_time(self, source: str) -> Optional[datetime]:
        """
        获取限制重置时间
        
        Args:
            source: 限制源标识
            
        Returns:
            Optional[datetime]: 重置时间，None表示无限制
        """
        if source not in self.limits:
            return None
        
        with self.lock:
            config = self.limits[source]
            
            if self.strategy == 'token_bucket':
                bucket = self.buckets[source]
                if bucket['tokens'] >= config['limit']:
                    return datetime.now()  # 已经有足够令牌
                
                # 计算恢复到满令牌需要的时间
                tokens_needed = config['limit'] - bucket['tokens']
                time_needed = tokens_needed / (config['limit'] / config['window'])
                return datetime.now() + timedelta(seconds=time_needed)
            
            elif self.strategy == 'sliding_window':
                window = self.windows[source]
                if not window:
                    return datetime.now()
                
                # 最早的请求时间 + 窗口时间
                earliest_request = min(window)
                return datetime.fromtimestamp(earliest_request + config['window'])
            
            elif self.strategy == 'fixed_window':
                window_state = self.fixed_windows[source]
                window_end = window_state['window_start'] + config['window']
                return datetime.fromtimestamp(window_end)
            
            return None
    
    def wait_if_needed(self, source: str, tokens: int = 1, max_wait: float = None) -> bool:
        """
        如果需要等待，则等待直到可以执行请求
        
        Args:
            source: 限制源标识
            tokens: 请求的令牌数量
            max_wait: 最大等待时间（秒），None表示无限等待
            
        Returns:
            bool: True表示成功获得许可，False表示超时
        """
        start_time = time.time()
        
        while not self.check_limit(source, tokens):
            if max_wait and (time.time() - start_time) >= max_wait:
                return False
            
            # 计算需要等待的时间
            reset_time = self.get_reset_time(source)
            if reset_time:
                wait_time = min(1.0, (reset_time - datetime.now()).total_seconds())
                if wait_time > 0:
                    time.sleep(wait_time)
            else:
                time.sleep(0.1)  # 默认等待时间
        
        return True
    
    def reset_limit(self, source: str):
        """
        重置指定源的限制状态
        
        Args:
            source: 限制源标识
        """
        with self.lock:
            if source in self.limits:
                config = self.limits[source]
                
                if self.strategy == 'token_bucket' and source in self.buckets:
                    self.buckets[source] = {
                        'tokens': config['limit'],
                        'last_refill': time.time(),
                        'capacity': config['burst']
                    }
                
                elif self.strategy == 'sliding_window' and source in self.windows:
                    self.windows[source].clear()
                
                elif self.strategy == 'fixed_window' and source in self.fixed_windows:
                    self.fixed_windows[source] = {
                        'count': 0,
                        'window_start': time.time()
                    }
    
    def get_status(self, source: str) -> Dict:
        """
        获取限制状态信息
        
        Args:
            source: 限制源标识
            
        Returns:
            Dict: 状态信息
        """
        if source not in self.limits:
            return {'error': 'No limit configured for this source'}
        
        config = self.limits[source]
        remaining = self.get_remaining_quota(source)
        reset_time = self.get_reset_time(source)
        
        return {
            'source': source,
            'strategy': self.strategy,
            'limit': config['limit'],
            'window': config['window'],
            'remaining': remaining,
            'reset_time': reset_time.isoformat() if reset_time else None,
            'burst': config.get('burst')
        }
    
    def cleanup_expired(self):
        """清理过期的限制状态"""
        current_time = time.time()
        
        with self.lock:
            # 清理滑动窗口中的过期记录
            for source, window in self.windows.items():
                if source in self.limits:
                    window_start = current_time - self.limits[source]['window']
                    while window and window[0] < window_start:
                        window.popleft()
            
            # 清理固定窗口中的过期状态
            for source, window_state in list(self.fixed_windows.items()):
                if source in self.limits:
                    window_elapsed = current_time - window_state['window_start']
                    if window_elapsed >= self.limits[source]['window']:
                        window_state['count'] = 0
                        window_state['window_start'] = current_time