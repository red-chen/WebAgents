"""
日志记录器
提供结构化日志记录功能
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


class Logger:
    """
    日志记录器类
    提供结构化日志记录和文件轮转功能
    """
    
    def __init__(self, name: str = "WebAgents", log_dir: str = None, 
                 log_level: str = "INFO", max_file_size: int = 10*1024*1024, 
                 backup_count: int = 5):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录
            log_level: 日志级别
            max_file_size: 最大文件大小（字节）
            backup_count: 备份文件数量
        """
        self.name = name
        self.log_dir = log_dir or os.path.join(os.getcwd(), 'logs')
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 设置日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 文件处理器
        log_file = os.path.join(self.log_dir, f"{self.name.lower()}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _log_structured(self, level: str, message: str, extra_data: Dict[str, Any] = None):
        """
        记录结构化日志
        
        Args:
            level: 日志级别
            message: 日志消息
            extra_data: 额外数据
        """
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'logger': self.name
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        # 记录JSON格式的结构化日志
        json_log = json.dumps(log_data, ensure_ascii=False)
        
        # 根据级别记录日志
        if level == 'DEBUG':
            self.logger.debug(f"STRUCTURED: {json_log}")
        elif level == 'INFO':
            self.logger.info(f"STRUCTURED: {json_log}")
        elif level == 'WARNING':
            self.logger.warning(f"STRUCTURED: {json_log}")
        elif level == 'ERROR':
            self.logger.error(f"STRUCTURED: {json_log}")
        elif level == 'CRITICAL':
            self.logger.critical(f"STRUCTURED: {json_log}")
    
    def debug(self, message: str, extra_data: Dict[str, Any] = None):
        """记录DEBUG级别日志"""
        self.logger.debug(message)
        if extra_data:
            self._log_structured('DEBUG', message, extra_data)
    
    def info(self, message: str, extra_data: Dict[str, Any] = None):
        """记录INFO级别日志"""
        self.logger.info(message)
        if extra_data:
            self._log_structured('INFO', message, extra_data)
    
    def warning(self, message: str, extra_data: Dict[str, Any] = None):
        """记录WARNING级别日志"""
        self.logger.warning(message)
        if extra_data:
            self._log_structured('WARNING', message, extra_data)
    
    def error(self, message: str, extra_data: Dict[str, Any] = None):
        """记录ERROR级别日志"""
        self.logger.error(message)
        if extra_data:
            self._log_structured('ERROR', message, extra_data)
    
    def critical(self, message: str, extra_data: Dict[str, Any] = None):
        """记录CRITICAL级别日志"""
        self.logger.critical(message)
        if extra_data:
            self._log_structured('CRITICAL', message, extra_data)
    
    def log_request(self, url: str, method: str = 'GET', status_code: int = None, 
                   response_time: float = None, error: str = None):
        """
        记录HTTP请求日志
        
        Args:
            url: 请求URL
            method: 请求方法
            status_code: 响应状态码
            response_time: 响应时间（秒）
            error: 错误信息
        """
        extra_data = {
            'type': 'http_request',
            'url': url,
            'method': method,
            'status_code': status_code,
            'response_time': response_time,
            'error': error
        }
        
        if error:
            self.error(f"HTTP request failed: {method} {url}", extra_data)
        else:
            self.info(f"HTTP request: {method} {url} - {status_code}", extra_data)
    
    def log_agent_activity(self, agent_name: str, action: str, target: str = None, 
                          result: str = None, duration: float = None, error: str = None):
        """
        记录代理活动日志
        
        Args:
            agent_name: 代理名称
            action: 执行的动作
            target: 目标（如URL、用户等）
            result: 执行结果
            duration: 执行时长（秒）
            error: 错误信息
        """
        extra_data = {
            'type': 'agent_activity',
            'agent': agent_name,
            'action': action,
            'target': target,
            'result': result,
            'duration': duration,
            'error': error
        }
        
        if error:
            self.error(f"Agent {agent_name} failed: {action}", extra_data)
        else:
            self.info(f"Agent {agent_name}: {action}", extra_data)
    
    def log_data_processing(self, data_type: str, source: str, count: int = None, 
                           processing_time: float = None, error: str = None):
        """
        记录数据处理日志
        
        Args:
            data_type: 数据类型
            source: 数据源
            count: 处理的数据条数
            processing_time: 处理时间（秒）
            error: 错误信息
        """
        extra_data = {
            'type': 'data_processing',
            'data_type': data_type,
            'source': source,
            'count': count,
            'processing_time': processing_time,
            'error': error
        }
        
        if error:
            self.error(f"Data processing failed: {data_type} from {source}", extra_data)
        else:
            self.info(f"Data processed: {count} {data_type} from {source}", extra_data)
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None, 
                           cache_type: str = 'memory', error: str = None):
        """
        记录缓存操作日志
        
        Args:
            operation: 操作类型（get, set, delete, clear）
            key: 缓存键
            hit: 是否命中（仅get操作）
            cache_type: 缓存类型
            error: 错误信息
        """
        extra_data = {
            'type': 'cache_operation',
            'operation': operation,
            'key': key,
            'hit': hit,
            'cache_type': cache_type,
            'error': error
        }
        
        if error:
            self.error(f"Cache operation failed: {operation} {key}", extra_data)
        else:
            self.debug(f"Cache {operation}: {key} ({'hit' if hit else 'miss' if hit is not None else 'N/A'})", extra_data)
    
    def log_rate_limit(self, source: str, limit: int, current: int, reset_time: datetime = None):
        """
        记录频率限制日志
        
        Args:
            source: 限制源
            limit: 限制数量
            current: 当前使用量
            reset_time: 重置时间
        """
        extra_data = {
            'type': 'rate_limit',
            'source': source,
            'limit': limit,
            'current': current,
            'reset_time': reset_time.isoformat() if reset_time else None
        }
        
        if current >= limit:
            self.warning(f"Rate limit reached for {source}: {current}/{limit}", extra_data)
        else:
            self.debug(f"Rate limit status for {source}: {current}/{limit}", extra_data)
    
    def log_configuration(self, config_name: str, config_value: Any = None, 
                         action: str = 'loaded', error: str = None):
        """
        记录配置相关日志
        
        Args:
            config_name: 配置名称
            config_value: 配置值（敏感信息会被隐藏）
            action: 动作（loaded, updated, validated）
            error: 错误信息
        """
        # 隐藏敏感配置值
        sensitive_keys = ['password', 'token', 'key', 'secret', 'api_key']
        display_value = config_value
        
        if config_value and any(key in config_name.lower() for key in sensitive_keys):
            display_value = "***HIDDEN***"
        
        extra_data = {
            'type': 'configuration',
            'config_name': config_name,
            'config_value': display_value,
            'action': action,
            'error': error
        }
        
        if error:
            self.error(f"Configuration {action} failed: {config_name}", extra_data)
        else:
            self.info(f"Configuration {action}: {config_name}", extra_data)
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别字符串
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
    
    def get_log_file_path(self) -> str:
        """
        获取日志文件路径
        
        Returns:
            str: 日志文件路径
        """
        return os.path.join(self.log_dir, f"{self.name.lower()}.log")


# 创建默认日志记录器实例
default_logger = Logger()

# 便捷函数
def debug(message: str, extra_data: Dict[str, Any] = None):
    """记录DEBUG日志"""
    default_logger.debug(message, extra_data)

def info(message: str, extra_data: Dict[str, Any] = None):
    """记录INFO日志"""
    default_logger.info(message, extra_data)

def warning(message: str, extra_data: Dict[str, Any] = None):
    """记录WARNING日志"""
    default_logger.warning(message, extra_data)

def error(message: str, extra_data: Dict[str, Any] = None):
    """记录ERROR日志"""
    default_logger.error(message, extra_data)

def critical(message: str, extra_data: Dict[str, Any] = None):
    """记录CRITICAL日志"""
    default_logger.critical(message, extra_data)