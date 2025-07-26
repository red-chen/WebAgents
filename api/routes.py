"""
API路由定义

定义所有API端点的路由和处理逻辑。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import asyncio
from datetime import datetime

from api.models import (
    NewsRequest, NewsResponse, NewsItem,
    SocialRequest, SocialResponse, SocialPost,
    FinancialRequest, FinancialResponse, FinancialData,
    SearchRequest, SearchResponse, SearchResult,
    ErrorResponse
)
from agents import (
    GoogleNewsAgent,
    XTwitterAgent,
    RedditAgent,
    Jin10Agent,
    TigerAgent,
    TradingViewAgent
)
from core.config import Config
from core.exceptions import WebAgentsException
from utils.logger import Logger

router = APIRouter()
config = Config()
logger = Logger()

# 初始化代理实例
google_news_agent = GoogleNewsAgent(config)
x_twitter_agent = XTwitterAgent(config)
reddit_agent = RedditAgent(config)
jin10_agent = Jin10Agent(config)
tiger_agent = TigerAgent(config)
tradingview_agent = TradingViewAgent(config)


@router.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }


@router.get("/api/news/google", response_model=NewsResponse, summary="获取Google新闻")
async def get_google_news(
    query: Optional[str] = Query(None, description="搜索关键词"),
    lang: str = Query("zh", description="语言代码"),
    region: str = Query("CN", description="地区代码"),
    category: Optional[str] = Query(None, description="新闻分类"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取Google新闻数据"""
    try:
        logger.log_api_request("google_news", {"query": query, "lang": lang, "region": region})
        
        # 构建请求参数
        params = {
            "query": query,
            "lang": lang,
            "region": region,
            "category": category,
            "limit": limit,
            "page": page
        }
        
        # 获取新闻数据
        if query:
            raw_data = await google_news_agent.search_news(query, lang=lang, limit=limit)
        else:
            raw_data = await google_news_agent.get_trending_topics(lang=lang, region=region, limit=limit)
        
        # 解析数据
        parsed_data = google_news_agent.parse_content(raw_data)
        
        # 转换为响应格式
        news_items = []
        for item in parsed_data.get("articles", []):
            news_item = NewsItem(
                title=item.get("title", ""),
                summary=item.get("summary"),
                url=item.get("url", ""),
                source=item.get("source", ""),
                published_at=item.get("published_at", datetime.now()),
                image_url=item.get("image_url"),
                category=item.get("category"),
                tags=item.get("tags", []),
                language=lang,
                region=region
            )
            news_items.append(news_item)
        
        return NewsResponse(
            data=news_items,
            total=len(news_items),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"Google News API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in Google News API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/api/social/x", response_model=SocialResponse, summary="获取X(Twitter)内容")
async def get_x_content(
    query: Optional[str] = Query(None, description="搜索关键词"),
    type: str = Query("search", description="内容类型: search, trending, user"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取X(Twitter)内容"""
    try:
        logger.log_api_request("x_twitter", {"query": query, "type": type})
        
        # 根据类型获取数据
        if type == "search" and query:
            raw_data = await x_twitter_agent.search_tweets(query, limit=limit)
        elif type == "trending":
            raw_data = await x_twitter_agent.get_trending_hashtags(limit=limit)
        elif type == "user" and user_id:
            raw_data = await x_twitter_agent.get_user_tweets(user_id, limit=limit)
        else:
            raise HTTPException(status_code=400, detail="无效的请求参数")
        
        # 解析数据
        parsed_data = x_twitter_agent.parse_content(raw_data)
        
        # 转换为响应格式
        social_posts = []
        for item in parsed_data.get("tweets", []):
            social_post = SocialPost(
                id=item.get("id", ""),
                content=item.get("content", ""),
                author=item.get("author", ""),
                author_id=item.get("author_id", ""),
                platform="twitter",
                url=item.get("url", ""),
                created_at=item.get("created_at", datetime.now()),
                likes=item.get("likes", 0),
                shares=item.get("retweets", 0),
                comments=item.get("replies", 0),
                hashtags=item.get("hashtags", []),
                mentions=item.get("mentions", []),
                media_urls=item.get("media_urls", [])
            )
            social_posts.append(social_post)
        
        return SocialResponse(
            data=social_posts,
            total=len(social_posts),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"X Twitter API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in X Twitter API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/api/social/reddit", response_model=SocialResponse, summary="获取Reddit内容")
async def get_reddit_content(
    subreddit: str = Query("all", description="子版块名称"),
    sort: str = Query("hot", description="排序方式: hot, new, top"),
    time_filter: str = Query("day", description="时间过滤: hour, day, week, month, year, all"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取Reddit内容"""
    try:
        logger.log_api_request("reddit", {"subreddit": subreddit, "sort": sort})
        
        # 获取Reddit数据
        raw_data = await reddit_agent.get_subreddit_posts(
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            limit=limit
        )
        
        # 解析数据
        parsed_data = reddit_agent.parse_content(raw_data)
        
        # 转换为响应格式
        social_posts = []
        for item in parsed_data.get("posts", []):
            social_post = SocialPost(
                id=item.get("id", ""),
                content=item.get("content", ""),
                author=item.get("author", ""),
                author_id=item.get("author_id", ""),
                platform="reddit",
                url=item.get("url", ""),
                created_at=item.get("created_at", datetime.now()),
                likes=item.get("upvotes", 0),
                shares=0,  # Reddit没有分享概念
                comments=item.get("num_comments", 0),
                hashtags=[],  # Reddit使用flair而不是hashtag
                mentions=[],
                media_urls=item.get("media_urls", [])
            )
            social_posts.append(social_post)
        
        return SocialResponse(
            data=social_posts,
            total=len(social_posts),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"Reddit API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in Reddit API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/api/financial/jin10", response_model=FinancialResponse, summary="获取金十数据")
async def get_jin10_data(
    category: str = Query("news", description="数据类型: news, calendar, data"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取金十数据财经信息"""
    try:
        logger.log_api_request("jin10", {"category": category})
        
        # 根据类型获取数据
        if category == "news":
            raw_data = await jin10_agent.get_flash_news(limit=limit)
        elif category == "calendar":
            raw_data = await jin10_agent.get_economic_calendar(limit=limit)
        elif category == "data":
            raw_data = await jin10_agent.get_economic_data(limit=limit)
        else:
            raise HTTPException(status_code=400, detail="无效的数据类型")
        
        # 解析数据
        parsed_data = jin10_agent.parse_content(raw_data)
        
        # 转换为响应格式
        financial_data = []
        for item in parsed_data.get("data", []):
            financial_item = FinancialData(
                title=item.get("title", ""),
                content=item.get("content", ""),
                data_type=category,
                source="jin10",
                timestamp=item.get("timestamp", datetime.now()),
                url=item.get("url"),
                metadata=item.get("metadata", {})
            )
            financial_data.append(financial_item)
        
        return FinancialResponse(
            data=financial_data,
            total=len(financial_data),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"Jin10 API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in Jin10 API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/api/financial/tiger", response_model=FinancialResponse, summary="获取老虎证券数据")
async def get_tiger_data(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("US", description="市场: US, HK, CN"),
    data_type: str = Query("quote", description="数据类型: quote, profile, financials, news"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取老虎证券股票数据"""
    try:
        logger.log_api_request("tiger", {"symbol": symbol, "market": market, "data_type": data_type})
        
        # 根据类型获取数据
        if data_type == "quote":
            raw_data = await tiger_agent.get_stock_quote(symbol, market=market)
        elif data_type == "profile":
            raw_data = await tiger_agent.get_company_profile(symbol, market=market)
        elif data_type == "financials":
            raw_data = await tiger_agent.get_financial_data(symbol, market=market)
        elif data_type == "news":
            raw_data = await tiger_agent.get_stock_news(symbol, market=market, limit=limit)
        else:
            raise HTTPException(status_code=400, detail="无效的数据类型")
        
        # 解析数据
        parsed_data = tiger_agent.parse_content(raw_data)
        
        # 转换为响应格式
        financial_data = []
        for item in parsed_data.get("data", []):
            financial_item = FinancialData(
                symbol=symbol,
                title=item.get("title", ""),
                content=item.get("content", ""),
                data_type=data_type,
                source="tiger",
                timestamp=item.get("timestamp", datetime.now()),
                url=item.get("url"),
                price=item.get("price"),
                change=item.get("change"),
                change_percent=item.get("change_percent"),
                volume=item.get("volume"),
                market_cap=item.get("market_cap"),
                metadata=item.get("metadata", {})
            )
            financial_data.append(financial_item)
        
        return FinancialResponse(
            data=financial_data,
            total=len(financial_data),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"Tiger API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in Tiger API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/api/financial/tradingview", response_model=FinancialResponse, summary="获取TradingView数据")
async def get_tradingview_data(
    symbol: str = Query(..., description="交易品种代码"),
    data_type: str = Query("chart", description="数据类型: chart, ideas, analysis, screener"),
    interval: str = Query("1d", description="时间间隔: 1m, 5m, 15m, 1h, 1d, 1w, 1M"),
    indicators: List[str] = Query([], description="技术指标列表"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    page: int = Query(1, ge=1, description="页码")
):
    """获取TradingView数据"""
    try:
        logger.log_api_request("tradingview", {"symbol": symbol, "data_type": data_type})
        
        # 根据类型获取数据
        if data_type == "chart":
            raw_data = await tradingview_agent.get_chart_data(symbol, interval=interval, indicators=indicators)
        elif data_type == "ideas":
            raw_data = await tradingview_agent.get_trading_ideas(symbol, limit=limit)
        elif data_type == "analysis":
            raw_data = await tradingview_agent.get_technical_analysis(symbol)
        elif data_type == "screener":
            raw_data = await tradingview_agent.get_screener_data(limit=limit)
        else:
            raise HTTPException(status_code=400, detail="无效的数据类型")
        
        # 解析数据
        parsed_data = tradingview_agent.parse_content(raw_data)
        
        # 转换为响应格式
        financial_data = []
        for item in parsed_data.get("data", []):
            financial_item = FinancialData(
                symbol=symbol,
                title=item.get("title", ""),
                content=item.get("content", ""),
                data_type=data_type,
                source="tradingview",
                timestamp=item.get("timestamp", datetime.now()),
                url=item.get("url"),
                metadata=item.get("metadata", {})
            )
            financial_data.append(financial_item)
        
        return FinancialResponse(
            data=financial_data,
            total=len(financial_data),
            page=page,
            page_size=limit
        )
        
    except WebAgentsException as e:
        logger.log_error(f"TradingView API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.log_error(f"Unexpected error in TradingView API: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/api/search", response_model=SearchResponse, summary="综合搜索")
async def search_content(request: SearchRequest):
    """跨平台综合搜索"""
    try:
        logger.log_api_request("search", {"query": request.query, "sources": request.sources})
        
        search_results = []
        tasks = []
        
        # 根据指定的数据源创建搜索任务
        if "google_news" in request.sources and "news" in request.data_types:
            tasks.append(("google_news", google_news_agent.search_news(request.query, limit=request.limit)))
        
        if "twitter" in request.sources and "social" in request.data_types:
            tasks.append(("twitter", x_twitter_agent.search_tweets(request.query, limit=request.limit)))
        
        if "reddit" in request.sources and "social" in request.data_types:
            tasks.append(("reddit", reddit_agent.search_posts(request.query, limit=request.limit)))
        
        if "jin10" in request.sources and "financial" in request.data_types:
            tasks.append(("jin10", jin10_agent.get_flash_news(limit=request.limit)))
        
        # 并发执行搜索任务
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        # 处理搜索结果
        for i, (source, result) in enumerate(zip([task[0] for task in tasks], results)):
            if isinstance(result, Exception):
                logger.log_error(f"Search error in {source}: {str(result)}")
                continue
            
            # 根据数据源解析结果
            if source == "google_news":
                parsed_data = google_news_agent.parse_content(result)
                for item in parsed_data.get("articles", []):
                    search_result = SearchResult(
                        title=item.get("title", ""),
                        content=item.get("summary", ""),
                        url=item.get("url", ""),
                        source=item.get("source", ""),
                        platform="google_news",
                        timestamp=item.get("published_at", datetime.now()),
                        data_type="news",
                        metadata=item
                    )
                    search_results.append(search_result)
            
            elif source == "twitter":
                parsed_data = x_twitter_agent.parse_content(result)
                for item in parsed_data.get("tweets", []):
                    search_result = SearchResult(
                        title=f"@{item.get('author', '')}的推文",
                        content=item.get("content", ""),
                        url=item.get("url", ""),
                        source=item.get("author", ""),
                        platform="twitter",
                        timestamp=item.get("created_at", datetime.now()),
                        data_type="social",
                        metadata=item
                    )
                    search_results.append(search_result)
            
            # 可以继续添加其他数据源的处理逻辑...
        
        # 按时间戳排序
        search_results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 分页处理
        start_idx = (request.page - 1) * request.limit
        end_idx = start_idx + request.limit
        paginated_results = search_results[start_idx:end_idx]
        
        return SearchResponse(
            data=paginated_results,
            total=len(search_results),
            query=request.query,
            sources=request.sources,
            page=request.page,
            page_size=request.limit
        )
        
    except Exception as e:
        logger.log_error(f"Search API error: {str(e)}")
        raise HTTPException(status_code=500, detail="搜索服务错误")