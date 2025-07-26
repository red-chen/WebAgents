"""
老虎证券代理
实现老虎证券股票数据的获取和解析
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from ...core.base_agent import BaseAgent
from ...core.config import Config
from ...core.exceptions import NetworkError, ParseError


class TigerAgent(BaseAgent):
    """
    老虎证券代理类
    获取美股、港股、A股等市场数据
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.tiger_base_url
        
    def fetch_content(self, symbol: str, market: str = 'US', 
                     data_type: str = 'quote', **kwargs) -> Dict[str, Any]:
        """
        获取老虎证券数据
        
        Args:
            symbol: 股票代码
            market: 市场类型 ('US', 'HK', 'CN')
            data_type: 数据类型 ('quote', 'profile', 'financials', 'news')
            
        Returns:
            Dict: 包含股票数据的字典
            
        Raises:
            NetworkError: 网络请求失败
        """
        try:
            self.rate_limit_check()
            
            if data_type == 'quote':
                return self._fetch_quote_data(symbol, market)
            elif data_type == 'profile':
                return self._fetch_company_profile(symbol, market)
            elif data_type == 'financials':
                return self._fetch_financial_data(symbol, market)
            elif data_type == 'news':
                return self._fetch_stock_news(symbol, market)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch Tiger data: {str(e)}")
    
    def _fetch_quote_data(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取股票报价数据"""
        url = f"{self.base_url}/api/quote/{market}/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='quote', symbol=symbol, market=market)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'market': market,
                'data_type': 'quote',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_company_profile(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取公司基本信息"""
        url = f"{self.base_url}/api/profile/{market}/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='profile', symbol=symbol, market=market)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'market': market,
                'data_type': 'profile',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_financial_data(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取财务数据"""
        url = f"{self.base_url}/api/financials/{market}/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='financials', symbol=symbol, market=market)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'market': market,
                'data_type': 'financials',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_stock_news(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取股票相关新闻"""
        url = f"{self.base_url}/api/news/{market}/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='news', symbol=symbol, market=market)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'market': market,
                'data_type': 'news',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def parse_content(self, raw_content: str, content_type: str = 'quote', 
                     symbol: str = '', market: str = '', **kwargs) -> Dict[str, Any]:
        """
        解析老虎证券内容
        
        Args:
            raw_content: 原始内容
            content_type: 内容类型
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Dict: 结构化的股票数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            if content_type == 'quote':
                return self._parse_quote_data(raw_content, symbol, market)
            elif content_type == 'profile':
                return self._parse_company_profile(raw_content, symbol, market)
            elif content_type == 'financials':
                return self._parse_financial_data(raw_content, symbol, market)
            elif content_type == 'news':
                return self._parse_stock_news(raw_content, symbol, market)
            else:
                raise ParseError(f"Unsupported content type: {content_type}", source="Tiger")
                
        except Exception as e:
            raise ParseError(f"Failed to parse Tiger content: {str(e)}", source="Tiger")
    
    def _parse_quote_data(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析股票报价数据"""
        try:
            # 尝试解析JSON响应
            data = json.loads(content)
            
            quote_data = {
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'price': data.get('price', 0),
                'change': data.get('change', 0),
                'change_percent': data.get('changePercent', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('marketCap', 0),
                'pe_ratio': data.get('peRatio', 0),
                'high_52w': data.get('high52w', 0),
                'low_52w': data.get('low52w', 0),
                'dividend_yield': data.get('dividendYield', 0),
                'last_updated': data.get('lastUpdated', datetime.now().isoformat())
            }
            
            return {'quote': quote_data}
            
        except json.JSONDecodeError:
            # 如果不是JSON，尝试HTML解析
            return self._parse_html_quote(content, symbol, market)
    
    def _parse_company_profile(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析公司基本信息"""
        try:
            data = json.loads(content)
            
            profile_data = {
                'symbol': symbol,
                'market': market,
                'company_name': data.get('companyName', ''),
                'industry': data.get('industry', ''),
                'sector': data.get('sector', ''),
                'description': data.get('description', ''),
                'employees': data.get('employees', 0),
                'headquarters': data.get('headquarters', ''),
                'website': data.get('website', ''),
                'ceo': data.get('ceo', ''),
                'founded': data.get('founded', '')
            }
            
            return {'profile': profile_data}
            
        except json.JSONDecodeError:
            return self._parse_html_profile(content, symbol, market)
    
    def _parse_financial_data(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析财务数据"""
        try:
            data = json.loads(content)
            
            financial_data = {
                'symbol': symbol,
                'market': market,
                'revenue': data.get('revenue', 0),
                'net_income': data.get('netIncome', 0),
                'total_assets': data.get('totalAssets', 0),
                'total_debt': data.get('totalDebt', 0),
                'cash': data.get('cash', 0),
                'eps': data.get('eps', 0),
                'roe': data.get('roe', 0),
                'roa': data.get('roa', 0),
                'debt_to_equity': data.get('debtToEquity', 0),
                'quarter': data.get('quarter', ''),
                'year': data.get('year', '')
            }
            
            return {'financials': financial_data}
            
        except json.JSONDecodeError:
            return self._parse_html_financials(content, symbol, market)
    
    def _parse_stock_news(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析股票新闻"""
        try:
            data = json.loads(content)
            news_items = []
            
            items = data.get('news', [])
            
            for item in items:
                news_item = {
                    'title': item.get('title', ''),
                    'content': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Tiger'),
                    'timestamp': item.get('publishTime', datetime.now().isoformat()),
                    'symbol': symbol,
                    'market': market
                }
                news_items.append(news_item)
            
            return {'news': news_items}
            
        except json.JSONDecodeError:
            return self._parse_html_news(content, symbol, market)
    
    def _parse_html_quote(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析HTML格式的报价数据"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 这里需要根据实际的HTML结构来实现
        quote_data = {
            'symbol': symbol,
            'market': market,
            'name': '',
            'price': 0,
            'change': 0,
            'change_percent': 0,
            'volume': 0
        }
        
        # 示例解析逻辑
        price_elem = soup.find('span', class_='price')
        if price_elem:
            quote_data['price'] = self._extract_number(price_elem.get_text())
        
        return {'quote': quote_data}
    
    def _parse_html_profile(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析HTML格式的公司信息"""
        soup = BeautifulSoup(content, 'html.parser')
        
        profile_data = {
            'symbol': symbol,
            'market': market,
            'company_name': '',
            'industry': '',
            'sector': '',
            'description': ''
        }
        
        return {'profile': profile_data}
    
    def _parse_html_financials(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析HTML格式的财务数据"""
        soup = BeautifulSoup(content, 'html.parser')
        
        financial_data = {
            'symbol': symbol,
            'market': market,
            'revenue': 0,
            'net_income': 0,
            'eps': 0
        }
        
        return {'financials': financial_data}
    
    def _parse_html_news(self, content: str, symbol: str, market: str) -> Dict[str, Any]:
        """解析HTML格式的新闻数据"""
        soup = BeautifulSoup(content, 'html.parser')
        news_items = []
        
        return {'news': news_items}
    
    def _extract_number(self, text: str) -> float:
        """从文本中提取数字"""
        try:
            # 移除非数字字符，保留小数点和负号
            cleaned = re.sub(r'[^\d.-]', '', text)
            return float(cleaned) if cleaned else 0
        except:
            return 0
    
    def get_stock_quote(self, symbol: str, market: str = 'US') -> Dict[str, Any]:
        """
        获取股票报价
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Dict: 股票报价数据
        """
        return self.fetch_content(symbol=symbol, market=market, data_type='quote')
    
    def get_company_profile(self, symbol: str, market: str = 'US') -> Dict[str, Any]:
        """
        获取公司基本信息
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Dict: 公司信息数据
        """
        return self.fetch_content(symbol=symbol, market=market, data_type='profile')
    
    def get_financial_data(self, symbol: str, market: str = 'US') -> Dict[str, Any]:
        """
        获取财务数据
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Dict: 财务数据
        """
        return self.fetch_content(symbol=symbol, market=market, data_type='financials')
    
    def get_stock_news(self, symbol: str, market: str = 'US') -> Dict[str, Any]:
        """
        获取股票相关新闻
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Dict: 股票新闻数据
        """
        return self.fetch_content(symbol=symbol, market=market, data_type='news')