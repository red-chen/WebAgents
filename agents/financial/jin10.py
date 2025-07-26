"""
金十数据代理
实现金十数据网站的财经信息获取
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from core.base_agent import BaseAgent
from core.config import Config
from core.exceptions import NetworkError, ParseError


class Jin10Agent(BaseAgent):
    """
    金十数据代理类
    获取实时财经快讯、经济数据等信息
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.jin10_base_url
        
    def fetch_content(self, category: str = 'flash', limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        获取金十数据内容
        
        Args:
            category: 内容类别 ('flash', 'calendar', 'data')
            limit: 返回结果数量限制
            
        Returns:
            Dict: 包含财经信息的字典
            
        Raises:
            NetworkError: 网络请求失败
        """
        try:
            self.rate_limit_check()
            
            if category == 'flash':
                return self._fetch_flash_news(limit)
            elif category == 'calendar':
                return self._fetch_economic_calendar(limit)
            elif category == 'data':
                return self._fetch_economic_data(limit)
            else:
                raise ValueError(f"Unsupported category: {category}")
                
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch Jin10 data: {str(e)}")
    
    def _fetch_flash_news(self, limit: int) -> Dict[str, Any]:
        """获取财经快讯"""
        url = f"{self.base_url}/api/flash"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='flash', limit=limit)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'category': 'flash',
                'total_count': len(parsed_data.get('news', [])),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_economic_calendar(self, limit: int) -> Dict[str, Any]:
        """获取经济日历"""
        url = f"{self.base_url}/api/calendar"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='calendar', limit=limit)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'category': 'calendar',
                'total_count': len(parsed_data.get('events', [])),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_economic_data(self, limit: int) -> Dict[str, Any]:
        """获取经济数据"""
        url = f"{self.base_url}/api/data"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='data', limit=limit)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'category': 'data',
                'total_count': len(parsed_data.get('indicators', [])),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def parse_content(self, raw_content: str, content_type: str = 'flash', 
                     limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        解析金十数据内容
        
        Args:
            raw_content: 原始内容
            content_type: 内容类型
            limit: 返回结果数量限制
            
        Returns:
            Dict: 结构化的财经数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            if content_type == 'flash':
                return self._parse_flash_news(raw_content, limit)
            elif content_type == 'calendar':
                return self._parse_economic_calendar(raw_content, limit)
            elif content_type == 'data':
                return self._parse_economic_data(raw_content, limit)
            else:
                raise ParseError(f"Unsupported content type: {content_type}", source="Jin10")
                
        except Exception as e:
            raise ParseError(f"Failed to parse Jin10 content: {str(e)}", source="Jin10")
    
    def _parse_flash_news(self, content: str, limit: int) -> Dict[str, Any]:
        """解析财经快讯"""
        try:
            # 尝试解析JSON响应
            data = json.loads(content)
            news_items = []
            
            # 根据实际API响应结构调整
            items = data.get('data', [])[:limit]
            
            for item in items:
                news_item = {
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'timestamp': item.get('time', datetime.now().isoformat()),
                    'source': 'Jin10',
                    'importance': item.get('importance', 'medium'),
                    'category': item.get('category', 'general'),
                    'url': f"{self.base_url}/flash/{item.get('id', '')}"
                }
                news_items.append(news_item)
            
            return {'news': news_items}
            
        except json.JSONDecodeError:
            # 如果不是JSON，尝试HTML解析
            return self._parse_html_content(content, 'flash', limit)
    
    def _parse_economic_calendar(self, content: str, limit: int) -> Dict[str, Any]:
        """解析经济日历"""
        try:
            data = json.loads(content)
            events = []
            
            items = data.get('data', [])[:limit]
            
            for item in items:
                event = {
                    'title': item.get('event', ''),
                    'content': f"{item.get('country', '')} - {item.get('event', '')}",
                    'timestamp': item.get('time', datetime.now().isoformat()),
                    'source': 'Jin10',
                    'country': item.get('country', ''),
                    'importance': item.get('importance', 'medium'),
                    'previous': item.get('previous', ''),
                    'forecast': item.get('forecast', ''),
                    'actual': item.get('actual', ''),
                    'url': f"{self.base_url}/calendar"
                }
                events.append(event)
            
            return {'events': events}
            
        except json.JSONDecodeError:
            return self._parse_html_content(content, 'calendar', limit)
    
    def _parse_economic_data(self, content: str, limit: int) -> Dict[str, Any]:
        """解析经济数据"""
        try:
            data = json.loads(content)
            indicators = []
            
            items = data.get('data', [])[:limit]
            
            for item in items:
                indicator = {
                    'title': item.get('name', ''),
                    'content': f"{item.get('name', '')}: {item.get('value', '')}",
                    'timestamp': item.get('time', datetime.now().isoformat()),
                    'source': 'Jin10',
                    'value': item.get('value', ''),
                    'unit': item.get('unit', ''),
                    'change': item.get('change', ''),
                    'url': f"{self.base_url}/data"
                }
                indicators.append(indicator)
            
            return {'indicators': indicators}
            
        except json.JSONDecodeError:
            return self._parse_html_content(content, 'data', limit)
    
    def _parse_html_content(self, content: str, content_type: str, limit: int) -> Dict[str, Any]:
        """解析HTML内容（备用方案）"""
        soup = BeautifulSoup(content, 'html.parser')
        items = []
        
        # 这里需要根据实际的HTML结构来实现
        # 以下是示例代码
        news_elements = soup.find_all('div', class_='news-item')[:limit]
        
        for element in news_elements:
            title_elem = element.find('h3') or element.find('h2')
            content_elem = element.find('p')
            time_elem = element.find('time') or element.find('.time')
            
            item = {
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'content': content_elem.get_text(strip=True) if content_elem else '',
                'timestamp': time_elem.get_text(strip=True) if time_elem else datetime.now().isoformat(),
                'source': 'Jin10',
                'url': self.base_url
            }
            items.append(item)
        
        return {content_type: items}
    
    def get_flash_news(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取财经快讯
        
        Args:
            limit: 返回结果数量
            
        Returns:
            Dict: 财经快讯数据
        """
        return self.fetch_content(category='flash', limit=limit)
    
    def get_economic_calendar(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取经济日历
        
        Args:
            limit: 返回结果数量
            
        Returns:
            Dict: 经济日历数据
        """
        return self.fetch_content(category='calendar', limit=limit)
    
    def get_economic_data(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取经济数据
        
        Args:
            limit: 返回结果数量
            
        Returns:
            Dict: 经济数据
        """
        return self.fetch_content(category='data', limit=limit)