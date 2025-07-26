# WebAgents

WebAgents是一个为大模型提供实时网站内容获取能力的代理服务系统。通过统一的API接口，支持从多个主流网站获取新闻、社交媒体内容、金融数据等信息。

## 功能特性

- **多网站支持**: 支持Google News、X (Twitter)、Reddit、金十数据、老虎证券、TradingView等主流网站
- **统一API接口**: 提供RESTful API，方便集成到各种应用中
- **智能缓存**: 内置缓存机制，提高响应速度，减少重复请求
- **频率限制**: 内置频率限制功能，避免触发网站的反爬虫机制
- **数据处理**: 提供数据清洗、格式化、验证等功能
- **异步支持**: 支持异步请求，提高并发处理能力
- **日志记录**: 完整的日志记录系统，便于调试和监控

## 项目结构

```
WebAgents/
├── agents/                 # 网站代理模块
│   ├── news/              # 新闻类网站代理
│   ├── social/            # 社交媒体代理
│   └── financial/         # 金融数据代理
├── core/                  # 核心模块
│   ├── base_agent.py      # 基础代理类
│   ├── config.py          # 配置管理
│   └── exceptions.py      # 异常定义
├── utils/                 # 工具模块
│   ├── data_processor.py  # 数据处理
│   ├── cache_manager.py   # 缓存管理
│   ├── logger.py          # 日志记录
│   └── rate_limiter.py    # 频率限制
├── api/                   # API接口
│   ├── routes.py          # 路由定义
│   └── models.py          # 数据模型
├── tests/                 # 测试模块
├── main.py               # 主程序入口
├── requirements.txt      # 依赖文件
└── .env.example         # 配置文件模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 为 `.env` 并配置相应的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入相应的API密钥和配置信息。

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 4. 查看API文档

访问 `http://localhost:8000/docs` 查看自动生成的API文档。

## API使用示例

### 获取Google新闻

```bash
curl -X POST "http://localhost:8000/api/news/google" \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能", "language": "zh-CN", "limit": 10}'
```

### 获取X (Twitter)内容

```bash
curl -X POST "http://localhost:8000/api/social/twitter" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI", "result_type": "recent", "limit": 20}'
```

### 获取Reddit内容

```bash
curl -X POST "http://localhost:8000/api/social/reddit" \
  -H "Content-Type: application/json" \
  -d '{"subreddit": "MachineLearning", "sort": "hot", "limit": 15}'
```

### 获取金融数据

```bash
curl -X POST "http://localhost:8000/api/financial/jin10" \
  -H "Content-Type: application/json" \
  -d '{"data_type": "flash", "limit": 20}'
```

## 配置说明

主要配置项说明：

- `DEBUG`: 调试模式开关
- `LOG_LEVEL`: 日志级别
- `CACHE_TTL`: 缓存过期时间
- `REQUEST_TIMEOUT`: 请求超时时间
- `RATE_LIMIT_*`: 各网站的频率限制设置
- API密钥配置（需要申请相应网站的API访问权限）

## 开发指南

### 添加新的网站代理

1. 在相应的 `agents` 子目录下创建新的代理类
2. 继承 `BaseAgent` 类
3. 实现 `fetch_content` 和 `parse_content` 方法
4. 在 `api/routes.py` 中添加相应的API端点

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black .
flake8 .
```

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 注意事项

1. 使用本项目时请遵守各网站的使用条款和robots.txt规则
2. 合理设置频率限制，避免对目标网站造成过大压力
3. 某些功能需要相应的API密钥，请确保已正确配置
4. 在生产环境中使用时，请注意安全性和稳定性配置