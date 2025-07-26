"""
异常定义模块
定义项目中使用的所有自定义异常
"""


class WebAgentsException(Exception):
    """
    WebAgents项目的基础异常类
    """
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class NetworkError(WebAgentsException):
    """
    网络请求相关异常
    """
    
    def __init__(self, message: str, status_code: int = None, url: str = None):
        self.status_code = status_code
        self.url = url
        error_code = f"NET_{status_code}" if status_code else "NET_ERROR"
        super().__init__(message, error_code)


class ParseError(WebAgentsException):
    """
    内容解析相关异常
    """
    
    def __init__(self, message: str, source: str = None):
        self.source = source
        error_code = "PARSE_ERROR"
        super().__init__(message, error_code)


class RateLimitError(WebAgentsException):
    """
    请求频率限制异常
    """
    
    def __init__(self, message: str, retry_after: int = None):
        self.retry_after = retry_after
        error_code = "RATE_LIMIT"
        super().__init__(message, error_code)


class AuthenticationError(WebAgentsException):
    """
    认证相关异常
    """
    
    def __init__(self, message: str, service: str = None):
        self.service = service
        error_code = "AUTH_ERROR"
        super().__init__(message, error_code)


class ConfigurationError(WebAgentsException):
    """
    配置相关异常
    """
    
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        error_code = "CONFIG_ERROR"
        super().__init__(message, error_code)


class DataValidationError(WebAgentsException):
    """
    数据验证异常
    """
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        error_code = "VALIDATION_ERROR"
        super().__init__(message, error_code)


class CacheError(WebAgentsException):
    """
    缓存相关异常
    """
    
    def __init__(self, message: str, cache_key: str = None):
        self.cache_key = cache_key
        error_code = "CACHE_ERROR"
        super().__init__(message, error_code)