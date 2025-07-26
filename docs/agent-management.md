# Agent 管理功能

WebAgents 现在支持动态启用/禁用 Agent，避免在启动时初始化所有 Agent，解决 API 密钥未配置时的启动错误。

## 功能特性

### 1. 懒加载机制
- Agent 只在首次被访问时才进行初始化
- 避免启动时因为 API 密钥未配置导致的错误
- 提高应用启动速度

### 2. 动态启用/禁用
- 通过环境变量控制 Agent 的启用状态
- 禁用的 Agent 不会被初始化
- 访问禁用的 Agent 时返回友好的错误信息

### 3. 错误处理
- 提供详细的错误信息
- 区分不同类型的错误（认证、网络、配置等）
- 支持错误状态查询

## 配置方式

### 环境变量配置

在 `.env` 文件中设置以下变量来控制 Agent 的启用状态：

```bash
# Agent 启用/禁用配置
GOOGLE_NEWS_ENABLED=true      # Google News Agent
X_TWITTER_ENABLED=true        # X (Twitter) Agent  
REDDIT_ENABLED=true           # Reddit Agent
JIN10_ENABLED=true            # 金十数据 Agent
TIGER_ENABLED=true            # 老虎证券 Agent
TRADINGVIEW_ENABLED=true      # TradingView Agent
```

### 配置示例

#### 1. 只启用新闻相关的 Agent
```bash
GOOGLE_NEWS_ENABLED=true
X_TWITTER_ENABLED=false
REDDIT_ENABLED=false
JIN10_ENABLED=false
TIGER_ENABLED=false
TRADINGVIEW_ENABLED=false
```

#### 2. 只启用社交媒体 Agent
```bash
GOOGLE_NEWS_ENABLED=false
X_TWITTER_ENABLED=true
REDDIT_ENABLED=true
JIN10_ENABLED=false
TIGER_ENABLED=false
TRADINGVIEW_ENABLED=false
```

#### 3. 只启用金融数据 Agent
```bash
GOOGLE_NEWS_ENABLED=false
X_TWITTER_ENABLED=false
REDDIT_ENABLED=false
JIN10_ENABLED=true
TIGER_ENABLED=true
TRADINGVIEW_ENABLED=true
```

## API 端点

### 查看 Agent 状态

```http
GET /api/agents/status
```

返回所有 Agent 的状态信息：

```json
{
  "agents": {
    "google_news": {
      "enabled": true,
      "initialized": true,
      "error": null
    },
    "x_twitter": {
      "enabled": true,
      "initialized": false,
      "error": "x_twitter 代理的API凭证未配置或无效，请检查配置文件"
    },
    "reddit": {
      "enabled": false,
      "initialized": false,
      "error": null
    }
  },
  "total_agents": 6,
  "enabled_count": 4,
  "initialized_count": 2,
  "timestamp": "2024-01-01T12:00:00"
}
```

## 错误处理

当访问禁用或配置错误的 Agent 时，API 会返回相应的错误信息：

### 1. Agent 被禁用
```json
{
  "detail": "reddit 代理已被禁用，请在配置中启用后重试"
}
```

### 2. API 凭证未配置
```json
{
  "detail": "x_twitter 代理的API凭证未配置或无效，请检查配置文件"
}
```

### 3. 网络连接错误
```json
{
  "detail": "jin10 代理网络连接失败，请检查网络连接"
}
```

### 4. 其他错误
```json
{
  "detail": "tradingview 代理暂时不可用: 具体错误信息"
}
```

## 使用场景

### 1. 开发环境
在开发环境中，可能只需要测试特定的 Agent，可以禁用其他 Agent 来加快启动速度：

```bash
# 只启用 Google News 进行开发测试
GOOGLE_NEWS_ENABLED=true
X_TWITTER_ENABLED=false
REDDIT_ENABLED=false
JIN10_ENABLED=false
TIGER_ENABLED=false
TRADINGVIEW_ENABLED=false
```

### 2. 生产环境
在生产环境中，可以根据实际需要的功能启用相应的 Agent：

```bash
# 生产环境只提供新闻和社交媒体数据
GOOGLE_NEWS_ENABLED=true
X_TWITTER_ENABLED=true
REDDIT_ENABLED=true
JIN10_ENABLED=false
TIGER_ENABLED=false
TRADINGVIEW_ENABLED=false
```

### 3. API 密钥限制
当某些 API 密钥暂时不可用时，可以临时禁用对应的 Agent：

```bash
# Twitter API 密钥过期，临时禁用
X_TWITTER_ENABLED=false
```

## 技术实现

### 1. 懒加载机制
```python
def get_agent(agent_type: str):
    """获取代理实例，支持懒加载和错误处理"""
    if agent_type in _agent_cache:
        return _agent_cache[agent_type]
    
    # 检查代理是否启用
    if not config.get(f"{agent_type.upper()}_ENABLED", True):
        raise HTTPException(status_code=503, detail=f"{agent_type} 代理已被禁用")
    
    # 懒加载代理实例
    agent = create_agent(agent_type)
    _agent_cache[agent_type] = agent
    return agent
```

### 2. 配置管理
```python
class Config:
    # Agent启用/禁用配置
    google_news_enabled: bool = field(default_factory=lambda: os.getenv('GOOGLE_NEWS_ENABLED', 'True').lower() == 'true')
    x_twitter_enabled: bool = field(default_factory=lambda: os.getenv('X_TWITTER_ENABLED', 'True').lower() == 'true')
    # ... 其他配置
```

### 3. 错误分类
系统会根据错误类型提供不同的错误信息：
- 认证错误：API 密钥相关问题
- 网络错误：连接超时或网络不可达
- 配置错误：Agent 被禁用
- 其他错误：未知错误

## 注意事项

1. **默认启用**：所有 Agent 默认都是启用状态，只有明确设置为 `false` 才会禁用
2. **大小写不敏感**：环境变量值 `true`、`True`、`TRUE` 都表示启用
3. **缓存机制**：已初始化的 Agent 会被缓存，重复访问不会重新初始化
4. **状态查询**：可以通过 `/api/agents/status` 端点查看所有 Agent 的状态
5. **错误恢复**：修复配置后，重新访问 Agent 会自动重试初始化