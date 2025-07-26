#!/usr/bin/env python3
"""
WebAgents 主程序入口

启动WebAgents服务，提供RESTful API接口。
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.routes import router
from core.config import Config
from core.exceptions import WebAgentsException
from utils.logger import Logger

# 初始化配置和日志
config = Config()
logger = Logger()

# 创建FastAPI应用
app = FastAPI(
    title="WebAgents API",
    description="为大模型提供实时网站内容获取能力的代理服务系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

# 全局异常处理器
@app.exception_handler(WebAgentsException)
async def webagents_exception_handler(request, exc):
    """处理WebAgents自定义异常"""
    logger.log_error(f"WebAgents exception: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": str(exc),
            "error_code": exc.__class__.__name__
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """处理HTTP异常"""
    logger.log_error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTPException"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理通用异常"""
    logger.log_error(f"Unexpected exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "内部服务器错误",
            "error_code": "InternalServerError"
        }
    )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    logger.log_info("WebAgents服务启动中...")
    
    # 验证配置
    try:
        config.validate()
        logger.log_info("配置验证通过")
    except Exception as e:
        logger.log_error(f"配置验证失败: {str(e)}")
        raise
    
    # 创建必要的目录
    os.makedirs(config.cache_dir, exist_ok=True)
    os.makedirs(config.log_dir, exist_ok=True)
    
    logger.log_info("WebAgents服务启动完成")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    logger.log_info("WebAgents服务正在关闭...")
    # 这里可以添加清理缓存、关闭数据库连接等操作
    logger.log_info("WebAgents服务已关闭")

# 根路径
@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "WebAgents API",
        "version": "1.0.0",
        "description": "为大模型提供实时网站内容获取能力的代理服务系统",
        "docs_url": "/docs",
        "health_check": "/health"
    }

def main():
    """主函数，启动服务"""
    # 从环境变量或配置文件读取服务器配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.log_info(f"启动WebAgents服务: http://{host}:{port}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )

if __name__ == "__main__":
    main()