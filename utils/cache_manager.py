"""
缓存管理器
提供内存缓存和文件缓存功能
"""

import json
import pickle
import os
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import hashlib
import threading


class CacheManager:
    """
    缓存管理器类
    支持内存缓存和文件缓存
    """
    
    def __init__(self, cache_dir: str = None, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            default_ttl: 默认缓存时间（秒）
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), '.cache')
        self.default_ttl = default_ttl
        self._memory_cache = {}
        self._cache_lock = threading.RLock()
        
        # 创建缓存目录
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _generate_cache_key(self, key: str) -> str:
        """
        生成缓存键的哈希值
        
        Args:
            key: 原始键
            
        Returns:
            str: 哈希后的键
        """
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            str: 文件路径
        """
        cache_key = self._generate_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.cache")
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """
        检查缓存是否过期
        
        Args:
            timestamp: 缓存时间戳
            ttl: 生存时间
            
        Returns:
            bool: 是否过期
        """
        return time.time() - timestamp > ttl
    
    def set_memory_cache(self, key: str, value: Any, ttl: int = None) -> None:
        """
        设置内存缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self._cache_lock:
            self._memory_cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
    
    def get_memory_cache(self, key: str) -> Optional[Any]:
        """
        获取内存缓存
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        with self._cache_lock:
            if key not in self._memory_cache:
                return None
            
            cache_item = self._memory_cache[key]
            
            # 检查是否过期
            if self._is_expired(cache_item['timestamp'], cache_item['ttl']):
                del self._memory_cache[key]
                return None
            
            return cache_item['value']
    
    def set_file_cache(self, key: str, value: Any, ttl: int = None, use_json: bool = True) -> None:
        """
        设置文件缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            use_json: 是否使用JSON格式（否则使用pickle）
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_file = self._get_cache_file_path(key)
        
        cache_data = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        try:
            with open(cache_file, 'w' if use_json else 'wb') as f:
                if use_json:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                else:
                    pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Failed to write cache file {cache_file}: {e}")
    
    def get_file_cache(self, key: str, use_json: bool = True) -> Optional[Any]:
        """
        获取文件缓存
        
        Args:
            key: 缓存键
            use_json: 是否使用JSON格式
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        cache_file = self._get_cache_file_path(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r' if use_json else 'rb') as f:
                if use_json:
                    cache_data = json.load(f)
                else:
                    cache_data = pickle.load(f)
            
            # 检查是否过期
            if self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                os.remove(cache_file)
                return None
            
            return cache_data['value']
            
        except Exception as e:
            print(f"Failed to read cache file {cache_file}: {e}")
            # 删除损坏的缓存文件
            try:
                os.remove(cache_file)
            except:
                pass
            return None
    
    def set(self, key: str, value: Any, ttl: int = None, use_file: bool = False, use_json: bool = True) -> None:
        """
        设置缓存（统一接口）
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            use_file: 是否使用文件缓存
            use_json: 是否使用JSON格式（仅文件缓存）
        """
        if use_file:
            self.set_file_cache(key, value, ttl, use_json)
        else:
            self.set_memory_cache(key, value, ttl)
    
    def get(self, key: str, use_file: bool = False, use_json: bool = True) -> Optional[Any]:
        """
        获取缓存（统一接口）
        
        Args:
            key: 缓存键
            use_file: 是否使用文件缓存
            use_json: 是否使用JSON格式（仅文件缓存）
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        if use_file:
            return self.get_file_cache(key, use_json)
        else:
            return self.get_memory_cache(key)
    
    def delete(self, key: str, use_file: bool = False) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            use_file: 是否删除文件缓存
            
        Returns:
            bool: 是否成功删除
        """
        success = True
        
        # 删除内存缓存
        with self._cache_lock:
            if key in self._memory_cache:
                del self._memory_cache[key]
        
        # 删除文件缓存
        if use_file:
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except Exception as e:
                    print(f"Failed to delete cache file {cache_file}: {e}")
                    success = False
        
        return success
    
    def clear_memory_cache(self) -> None:
        """清空内存缓存"""
        with self._cache_lock:
            self._memory_cache.clear()
    
    def clear_file_cache(self) -> None:
        """清空文件缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
        except Exception as e:
            print(f"Failed to clear file cache: {e}")
    
    def clear_all(self) -> None:
        """清空所有缓存"""
        self.clear_memory_cache()
        self.clear_file_cache()
    
    def cleanup_expired(self) -> None:
        """清理过期缓存"""
        # 清理内存缓存
        with self._cache_lock:
            expired_keys = []
            for key, cache_item in self._memory_cache.items():
                if self._is_expired(cache_item['timestamp'], cache_item['ttl']):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
        
        # 清理文件缓存
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        # 尝试读取缓存文件检查是否过期
                        with open(file_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        if self._is_expired(cache_data['timestamp'], cache_data['ttl']):
                            os.remove(file_path)
                    except:
                        # 如果读取失败，删除损坏的文件
                        os.remove(file_path)
        except Exception as e:
            print(f"Failed to cleanup expired file cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计信息
        """
        with self._cache_lock:
            memory_count = len(self._memory_cache)
        
        file_count = 0
        total_file_size = 0
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_count += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    total_file_size += os.path.getsize(file_path)
        except Exception:
            pass
        
        return {
            'memory_cache_count': memory_count,
            'file_cache_count': file_count,
            'total_file_size_bytes': total_file_size,
            'cache_directory': self.cache_dir
        }
    
    def exists(self, key: str, use_file: bool = False) -> bool:
        """
        检查缓存是否存在且未过期
        
        Args:
            key: 缓存键
            use_file: 是否检查文件缓存
            
        Returns:
            bool: 是否存在
        """
        if use_file:
            return self.get_file_cache(key) is not None
        else:
            return self.get_memory_cache(key) is not None