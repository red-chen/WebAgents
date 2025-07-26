"""
TradingView 代理
实现TradingView图表和技术分析数据的获取
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from core.base_agent import BaseAgent
from core.config import Config
from core.exceptions import NetworkError, ParseError


class TradingViewAgent(BaseAgent):
    """
    TradingView 代理类
    获取技术指标、图表数据和交易想法
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.tradingview_base_url
        
    def fetch_content(self, symbol: str, interval: str = '1D', 
                     indicators: List[str] = None, data_type: str = 'chart', **kwargs) -> Dict[str, Any]:
        """
        获取TradingView数据
        
        Args:
            symbol: 交易品种代码 (如 'AAPL', 'BTCUSD')
            interval: 时间间隔 ('1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M')
            indicators: 技术指标列表
            data_type: 数据类型 ('chart', 'ideas', 'analysis', 'screener')
            
        Returns:
            Dict: 包含TradingView数据的字典
            
        Raises:
            NetworkError: 网络请求失败
        """
        try:
            self.rate_limit_check()
            
            if data_type == 'chart':
                return self._fetch_chart_data(symbol, interval, indicators)
            elif data_type == 'ideas':
                return self._fetch_trading_ideas(symbol)
            elif data_type == 'analysis':
                return self._fetch_technical_analysis(symbol)
            elif data_type == 'screener':
                return self._fetch_screener_data(symbol)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch TradingView data: {str(e)}")
    
    def _fetch_chart_data(self, symbol: str, interval: str, indicators: List[str] = None) -> Dict[str, Any]:
        """获取图表数据"""
        url = f"{self.base_url}/api/chart/{symbol}"
        
        params = {
            'interval': interval,
            'indicators': ','.join(indicators) if indicators else ''
        }
        
        response = requests.get(
            url,
            params=params,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='chart', symbol=symbol, interval=interval)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'interval': interval,
                'indicators': indicators,
                'data_type': 'chart',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_trading_ideas(self, symbol: str) -> Dict[str, Any]:
        """获取交易想法"""
        url = f"{self.base_url}/api/ideas/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='ideas', symbol=symbol)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'data_type': 'ideas',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """获取技术分析"""
        url = f"{self.base_url}/api/analysis/{symbol}"
        
        response = requests.get(
            url,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='analysis', symbol=symbol)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'data_type': 'analysis',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _fetch_screener_data(self, symbol: str) -> Dict[str, Any]:
        """获取筛选器数据"""
        url = f"{self.base_url}/api/screener"
        
        params = {'symbol': symbol}
        
        response = requests.get(
            url,
            params=params,
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        parsed_data = self.parse_content(response.text, content_type='screener', symbol=symbol)
        
        return {
            'status': 'success',
            'data': parsed_data,
            'metadata': {
                'symbol': symbol,
                'data_type': 'screener',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def parse_content(self, raw_content: str, content_type: str = 'chart', 
                     symbol: str = '', interval: str = '', **kwargs) -> Dict[str, Any]:
        """
        解析TradingView内容
        
        Args:
            raw_content: 原始内容
            content_type: 内容类型
            symbol: 交易品种代码
            interval: 时间间隔
            
        Returns:
            Dict: 结构化的TradingView数据
            
        Raises:
            ParseError: 内容解析失败
        """
        try:
            if content_type == 'chart':
                return self._parse_chart_data(raw_content, symbol, interval)
            elif content_type == 'ideas':
                return self._parse_trading_ideas(raw_content, symbol)
            elif content_type == 'analysis':
                return self._parse_technical_analysis(raw_content, symbol)
            elif content_type == 'screener':
                return self._parse_screener_data(raw_content, symbol)
            else:
                raise ParseError(f"Unsupported content type: {content_type}", source="TradingView")
                
        except Exception as e:
            raise ParseError(f"Failed to parse TradingView content: {str(e)}", source="TradingView")
    
    def _parse_chart_data(self, content: str, symbol: str, interval: str) -> Dict[str, Any]:
        """解析图表数据"""
        try:
            # 尝试解析JSON响应
            data = json.loads(content)
            
            chart_data = {
                'symbol': symbol,
                'interval': interval,
                'ohlcv': data.get('ohlcv', []),  # Open, High, Low, Close, Volume
                'indicators': data.get('indicators', {}),
                'last_price': data.get('lastPrice', 0),
                'change': data.get('change', 0),
                'change_percent': data.get('changePercent', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('marketCap', 0),
                'technical_rating': data.get('technicalRating', 'NEUTRAL')
            }
            
            return {'chart': chart_data}
            
        except json.JSONDecodeError:
            # 如果不是JSON，尝试HTML解析
            return self._parse_html_chart(content, symbol, interval)
    
    def _parse_trading_ideas(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析交易想法"""
        try:
            data = json.loads(content)
            ideas = []
            
            items = data.get('ideas', [])
            
            for item in items:
                idea = {
                    'title': item.get('title', ''),
                    'content': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': 'TradingView',
                    'timestamp': item.get('publishTime', datetime.now().isoformat()),
                    'author': item.get('author', ''),
                    'symbol': symbol,
                    'direction': item.get('direction', 'NEUTRAL'),  # LONG, SHORT, NEUTRAL
                    'timeframe': item.get('timeframe', ''),
                    'likes': item.get('likes', 0),
                    'comments': item.get('comments', 0),
                    'tags': item.get('tags', [])
                }
                ideas.append(idea)
            
            return {'ideas': ideas}
            
        except json.JSONDecodeError:
            return self._parse_html_ideas(content, symbol)
    
    def _parse_technical_analysis(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析技术分析"""
        try:
            data = json.loads(content)
            
            analysis_data = {
                'symbol': symbol,
                'overall_rating': data.get('overallRating', 'NEUTRAL'),
                'moving_averages': {
                    'rating': data.get('movingAverages', {}).get('rating', 'NEUTRAL'),
                    'signals': data.get('movingAverages', {}).get('signals', {})
                },
                'oscillators': {
                    'rating': data.get('oscillators', {}).get('rating', 'NEUTRAL'),
                    'signals': data.get('oscillators', {}).get('signals', {})
                },
                'pivot_points': data.get('pivotPoints', {}),
                'support_resistance': data.get('supportResistance', {}),
                'fibonacci': data.get('fibonacci', {}),
                'pattern_recognition': data.get('patternRecognition', [])
            }
            
            return {'analysis': analysis_data}
            
        except json.JSONDecodeError:
            return self._parse_html_analysis(content, symbol)
    
    def _parse_screener_data(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析筛选器数据"""
        try:
            data = json.loads(content)
            
            screener_data = {
                'symbol': symbol,
                'market_cap': data.get('marketCap', 0),
                'pe_ratio': data.get('peRatio', 0),
                'eps': data.get('eps', 0),
                'dividend_yield': data.get('dividendYield', 0),
                'rsi': data.get('rsi', 0),
                'beta': data.get('beta', 0),
                'volume': data.get('volume', 0),
                'avg_volume': data.get('avgVolume', 0),
                'price_to_book': data.get('priceToBook', 0),
                'debt_to_equity': data.get('debtToEquity', 0)
            }
            
            return {'screener': screener_data}
            
        except json.JSONDecodeError:
            return self._parse_html_screener(content, symbol)
    
    def _parse_html_chart(self, content: str, symbol: str, interval: str) -> Dict[str, Any]:
        """解析HTML格式的图表数据"""
        soup = BeautifulSoup(content, 'html.parser')
        
        chart_data = {
            'symbol': symbol,
            'interval': interval,
            'last_price': 0,
            'change': 0,
            'change_percent': 0
        }
        
        return {'chart': chart_data}
    
    def _parse_html_ideas(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析HTML格式的交易想法"""
        soup = BeautifulSoup(content, 'html.parser')
        ideas = []
        
        return {'ideas': ideas}
    
    def _parse_html_analysis(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析HTML格式的技术分析"""
        soup = BeautifulSoup(content, 'html.parser')
        
        analysis_data = {
            'symbol': symbol,
            'overall_rating': 'NEUTRAL'
        }
        
        return {'analysis': analysis_data}
    
    def _parse_html_screener(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析HTML格式的筛选器数据"""
        soup = BeautifulSoup(content, 'html.parser')
        
        screener_data = {
            'symbol': symbol,
            'market_cap': 0,
            'pe_ratio': 0
        }
        
        return {'screener': screener_data}
    
    def get_chart_data(self, symbol: str, interval: str = '1D', 
                      indicators: List[str] = None) -> Dict[str, Any]:
        """
        获取图表数据
        
        Args:
            symbol: 交易品种代码
            interval: 时间间隔
            indicators: 技术指标列表
            
        Returns:
            Dict: 图表数据
        """
        return self.fetch_content(symbol=symbol, interval=interval, 
                                indicators=indicators, data_type='chart')
    
    def get_trading_ideas(self, symbol: str) -> Dict[str, Any]:
        """
        获取交易想法
        
        Args:
            symbol: 交易品种代码
            
        Returns:
            Dict: 交易想法数据
        """
        return self.fetch_content(symbol=symbol, data_type='ideas')
    
    def get_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取技术分析
        
        Args:
            symbol: 交易品种代码
            
        Returns:
            Dict: 技术分析数据
        """
        return self.fetch_content(symbol=symbol, data_type='analysis')
    
    def get_screener_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取筛选器数据
        
        Args:
            symbol: 交易品种代码
            
        Returns:
            Dict: 筛选器数据
        """
        return self.fetch_content(symbol=symbol, data_type='screener')
    
    def get_popular_indicators(self) -> List[str]:
        """
        获取常用技术指标列表
        
        Returns:
            List: 技术指标名称列表
        """
        return [
            'RSI',          # 相对强弱指数
            'MACD',         # 移动平均收敛散度
            'SMA',          # 简单移动平均
            'EMA',          # 指数移动平均
            'BB',           # 布林带
            'STOCH',        # 随机指标
            'ADX',          # 平均趋向指数
            'CCI',          # 商品通道指数
            'WILLIAMS',     # 威廉指标
            'ATR',          # 平均真实范围
            'VOLUME',       # 成交量
            'OBV'           # 能量潮
        ]