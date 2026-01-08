# 前端API设计

## API设计原则

- RESTful风格
- JSON数据格式
- 统一的错误处理
- 清晰的响应结构

## API端点

### 1. 数据采集API

#### POST /api/v1/scrape/start
启动数据采集

**请求**：
```json
{
  "keywords": ["productivity", "task management"],
  "data_source": "app_store",
  "limit_per_keyword": 20
}
```

**响应**：
```json
{
  "status": "success",
  "task_id": "task_123456",
  "message": "采集任务已启动"
}
```

#### GET /api/v1/scrape/status/<task_id>
获取采集状态

**响应**：
```json
{
  "status": "running",
  "progress": {
    "total": 40,
    "completed": 20,
    "current_keyword": "productivity",
    "current_progress": "10/20"
  },
  "results": {
    "apps_collected": 20,
    "opportunities_found": 15
  }
}
```

#### POST /api/v1/scrape/stop/<task_id>
停止采集

**响应**：
```json
{
  "status": "success",
  "message": "采集任务已停止"
}
```

### 2. 机会管理API

#### GET /api/v1/opportunities
获取机会列表

**查询参数**：
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）
- `sort_by`: 排序字段（score, rating, reviews）
- `order`: 排序方向（asc, desc）
- `min_score`: 最低分数
- `max_score`: 最高分数
- `category`: 分类筛选
- `search`: 搜索关键词

**响应**：
```json
{
  "status": "success",
  "data": {
    "opportunities": [
      {
        "app_id": 281796108,
        "name": "Evernote - Notes Organizer",
        "category": "Productivity",
        "rating": 4.41,
        "review_count": 73331,
        "price": 0.0,
        "opportunity_score": 0.950,
        "url": "https://apps.apple.com/..."
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 46,
      "pages": 3
    }
  }
}
```

#### GET /api/v1/opportunities/<app_id>
获取机会详情

**响应**：
```json
{
  "status": "success",
  "data": {
    "app_id": 281796108,
    "name": "Evernote - Notes Organizer",
    "category": "Productivity",
    "rating": 4.41,
    "review_count": 73331,
    "price": 0.0,
    "opportunity_score": 0.950,
    "scoring_details": {
      "market_size": 1.0,
      "competition": 1.0,
      "user_satisfaction": 1.0,
      "growth_trend": 1.0,
      "monetization": 0.5
    },
    "url": "https://apps.apple.com/...",
    "description": "..."
  }
}
```

### 3. 配置管理API

#### GET /api/v1/config
获取配置

**响应**：
```json
{
  "status": "success",
  "data": {
    "scoring": {
      "weights": {
        "market_size": 0.3,
        "competition": 0.25,
        "user_satisfaction": 0.2,
        "growth_trend": 0.15,
        "monetization": 0.1
      },
      "thresholds": {
        "min_score": 0.6,
        "min_reviews": 10,
        "max_competitors": 20
      }
    },
    "data_sources": {
      "app_store": {"enabled": true},
      "product_hunt": {"enabled": false}
    }
  }
}
```

#### POST /api/v1/config
更新配置

**请求**：
```json
{
  "scoring": {
    "weights": {
      "market_size": 0.35,
      "competition": 0.25,
      "user_satisfaction": 0.2,
      "growth_trend": 0.1,
      "monetization": 0.1
    },
    "thresholds": {
      "min_score": 0.65,
      "min_reviews": 10
    }
  }
}
```

**响应**：
```json
{
  "status": "success",
  "message": "配置已更新"
}
```

### 4. 统计信息API

#### GET /api/v1/stats
获取统计信息

**响应**：
```json
{
  "status": "success",
  "data": {
    "total_opportunities": 120,
    "today_collected": 52,
    "active_tasks": 0,
    "top_categories": [
      {"category": "Productivity", "count": 45},
      {"category": "Business", "count": 30}
    ]
  }
}
```

### 5. 导出API

#### GET /api/v1/opportunities/export
导出机会数据

**查询参数**：
- `format`: csv, json
- `filters`: 筛选条件（JSON字符串）

**响应**：文件下载

## 错误处理

### 统一错误格式

```json
{
  "status": "error",
  "error_code": "INVALID_PARAMETER",
  "message": "参数错误：limit必须大于0",
  "details": {}
}
```

### 错误码

- `INVALID_PARAMETER`: 参数错误
- `TASK_NOT_FOUND`: 任务不存在
- `TASK_ALREADY_RUNNING`: 任务已运行
- `CONFIG_INVALID`: 配置无效
- `INTERNAL_ERROR`: 内部错误

## WebSocket（可选）

### 实时进度更新

```javascript
// 连接WebSocket
ws = new WebSocket('ws://localhost:5000/ws/scrape/<task_id>');

// 接收进度更新
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  updateProgress(data);
};
```

---

**API设计完成，可以开始实现了！**
