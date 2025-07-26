"""
数据处理器
提供数据清洗、格式化、验证等功能
"""

import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
import hashlib
from urllib.parse import urlparse, urljoin
import html


class DataProcessor:
    """
    数据处理器类
    提供各种数据处理和格式化功能
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
        
        # HTML解码
        text = html.unescape(text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        从文本中提取URL
        
        Args:
            text: 包含URL的文本
            
        Returns:
            List[str]: URL列表
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    @staticmethod
    def normalize_url(url: str, base_url: str = None) -> str:
        """
        标准化URL
        
        Args:
            url: 原始URL
            base_url: 基础URL（用于相对路径）
            
        Returns:
            str: 标准化的URL
        """
        if not url:
            return ""
        
        # 如果是相对路径且提供了基础URL
        if base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        
        # 移除URL片段
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        return normalized
    
    @staticmethod
    def parse_timestamp(timestamp_str: str, formats: List[str] = None) -> Optional[datetime]:
        """
        解析时间戳字符串
        
        Args:
            timestamp_str: 时间戳字符串
            formats: 可能的时间格式列表
            
        Returns:
            Optional[datetime]: 解析后的datetime对象
        """
        if not timestamp_str:
            return None
        
        if formats is None:
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y'
            ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def format_timestamp(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        格式化时间戳
        
        Args:
            dt: datetime对象
            format_str: 格式字符串
            
        Returns:
            str: 格式化的时间字符串
        """
        if not dt:
            return ""
        
        return dt.strftime(format_str)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """
        提取文本中的标签
        
        Args:
            text: 包含标签的文本
            
        Returns:
            List[str]: 标签列表
        """
        if not text:
            return []
        
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """
        提取文本中的@提及
        
        Args:
            text: 包含@提及的文本
            
        Returns:
            List[str]: 提及用户列表
        """
        if not text:
            return []
        
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        return [mention.lower() for mention in mentions]
    
    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        生成内容哈希值
        
        Args:
            content: 内容字符串
            
        Returns:
            str: MD5哈希值
        """
        if not content:
            return ""
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 是否有效
        """
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: URL地址
            
        Returns:
            bool: 是否有效
        """
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 后缀
            
        Returns:
            str: 截断后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        从文本中提取数字
        
        Args:
            text: 包含数字的文本
            
        Returns:
            List[float]: 数字列表
        """
        if not text:
            return []
        
        number_pattern = r'-?\d+\.?\d*'
        numbers = re.findall(number_pattern, text)
        return [float(num) for num in numbers if num]
    
    @staticmethod
    def format_number(number: Union[int, float], decimal_places: int = 2) -> str:
        """
        格式化数字
        
        Args:
            number: 数字
            decimal_places: 小数位数
            
        Returns:
            str: 格式化的数字字符串
        """
        if number is None:
            return "0"
        
        if isinstance(number, int):
            return f"{number:,}"
        else:
            return f"{number:,.{decimal_places}f}"
    
    @staticmethod
    def parse_json_safely(json_str: str) -> Optional[Dict[str, Any]]:
        """
        安全解析JSON字符串
        
        Args:
            json_str: JSON字符串
            
        Returns:
            Optional[Dict]: 解析后的字典或None
        """
        if not json_str:
            return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并字典
        
        Args:
            dict1: 第一个字典
            dict2: 第二个字典
            
        Returns:
            Dict: 合并后的字典
        """
        result = dict1.copy()
        result.update(dict2)
        return result
    
    @staticmethod
    def filter_dict_by_keys(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
        """
        根据键过滤字典
        
        Args:
            data: 原始字典
            allowed_keys: 允许的键列表
            
        Returns:
            Dict: 过滤后的字典
        """
        return {k: v for k, v in data.items() if k in allowed_keys}
    
    @staticmethod
    def remove_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        移除字典中的空值
        
        Args:
            data: 原始字典
            
        Returns:
            Dict: 移除空值后的字典
        """
        return {k: v for k, v in data.items() if v is not None and v != ""}
    
    @staticmethod
    def convert_to_utc(dt: datetime) -> datetime:
        """
        转换为UTC时间
        
        Args:
            dt: datetime对象
            
        Returns:
            datetime: UTC时间
        """
        if not dt:
            return None
        
        if dt.tzinfo is None:
            # 假设是本地时间
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        if not filename:
            return "untitled"
        
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除首尾空白和点
        filename = filename.strip('. ')
        
        # 确保不为空
        if not filename:
            filename = "untitled"
        
        return filename