# 前端实现计划

## 技术栈

### 后端
- **Flask**：轻量级Web框架
- **Flask-CORS**：跨域支持
- **现有代码复用**：直接调用backend/src中的模块

### 前端
- **Bootstrap 5**：UI框架
- **jQuery**：DOM操作和AJAX
- **Chart.js**：数据可视化
- **DataTables**：表格功能

## 实现步骤

### 阶段1：基础框架（1-2天）

#### 1.1 创建Flask应用
- [ ] 创建 `frontend/web/app.py`
- [ ] 配置路由
- [ ] 集成现有后端代码
- [ ] 测试基础功能

#### 1.2 创建基础模板
- [ ] 创建 `base.html` 基础模板
- [ ] 集成Bootstrap
- [ ] 创建导航栏
- [ ] 创建布局结构

### 阶段2：核心页面（3-5天）

#### 2.1 首页/仪表板
- [ ] 创建首页模板
- [ ] 实现快速采集表单
- [ ] 显示统计信息
- [ ] 显示最近机会列表

#### 2.2 数据采集页面
- [ ] 创建采集页面
- [ ] 实现关键词管理
- [ ] 实现采集控制
- [ ] 实现进度显示
- [ ] 实现结果预览

#### 2.3 机会列表页面
- [ ] 创建列表页面
- [ ] 集成DataTables
- [ ] 实现搜索和筛选
- [ ] 实现排序和分页
- [ ] 实现详情跳转

#### 2.4 机会详情页面
- [ ] 创建详情页面
- [ ] 显示完整信息
- [ ] 实现评分可视化
- [ ] 实现图表展示

#### 2.5 配置页面
- [ ] 创建配置页面
- [ ] 实现权重调整（滑块）
- [ ] 实现阈值设置
- [ ] 实现配置保存

### 阶段3：API实现（2-3天）

#### 3.1 采集API
- [ ] `/api/v1/scrape/start` - 启动采集
- [ ] `/api/v1/scrape/status` - 获取状态
- [ ] `/api/v1/scrape/stop` - 停止采集

#### 3.2 机会API
- [ ] `/api/v1/opportunities` - 获取列表
- [ ] `/api/v1/opportunities/<id>` - 获取详情

#### 3.3 配置API
- [ ] `/api/v1/config` - 获取/更新配置

#### 3.4 统计API
- [ ] `/api/v1/stats` - 获取统计信息

### 阶段4：优化和测试（1-2天）

- [ ] UI优化
- [ ] 交互优化
- [ ] 错误处理
- [ ] 性能优化
- [ ] 测试和修复

## 文件结构

```
frontend/web/
├── app.py                    # Flask应用主文件
├── requirements.txt          # 依赖文件
├── config.py                 # 配置文件
│
├── templates/                # HTML模板
│   ├── base.html            # 基础模板
│   ├── index.html           # 首页
│   ├── scrape.html          # 采集页面
│   ├── opportunities.html   # 机会列表
│   ├── detail.html          # 详情页面
│   └── config.html          # 配置页面
│
├── static/                   # 静态文件
│   ├── css/
│   │   └── style.css        # 自定义样式
│   ├── js/
│   │   ├── main.js         # 主JavaScript
│   │   ├── scrape.js       # 采集相关
│   │   ├── opportunities.js # 机会列表
│   │   └── config.js       # 配置管理
│   └── img/                 # 图片资源
│
└── api/                      # API路由
    ├── __init__.py
    ├── scrape.py            # 采集API
    ├── opportunities.py     # 机会API
    ├── config.py            # 配置API
    └── stats.py             # 统计API
```

## 关键技术点

### 1. 后端集成

```python
# 在Flask中调用现有模块
import sys
from pathlib import Path

# 添加backend/src到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "src"))

from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
```

### 2. 异步任务处理

```python
# 使用Flask的线程或Celery处理长时间任务
from threading import Thread

def run_scrape_task(keywords, limit):
    # 在后台线程运行
    pass
```

### 3. 实时进度更新

**方案1：轮询（简单）**
```javascript
// 每2秒查询一次状态
setInterval(function() {
    $.get('/api/v1/scrape/status/' + taskId, updateProgress);
}, 2000);
```

**方案2：WebSocket（复杂但更好）**
```python
# 使用Flask-SocketIO
from flask_socketio import SocketIO
```

### 4. 数据可视化

```javascript
// 使用Chart.js
const ctx = document.getElementById('scoreChart');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['市场规模', '竞争程度', '用户满意度', '增长趋势', '变现潜力'],
        datasets: [{
            data: [1.0, 1.0, 1.0, 1.0, 0.5]
        }]
    }
});
```

## 开发优先级

### MVP功能（必须）
1. ✅ 数据采集控制
2. ✅ 机会列表查看
3. ✅ 机会详情查看
4. ✅ 基础配置管理

### 增强功能（重要）
5. 实时进度显示
6. 数据可视化
7. 搜索和筛选
8. 导出功能

### 优化功能（可选）
9. 历史记录
10. 批量操作
11. 数据对比
12. 高级筛选

## 开发时间估算

- **阶段1**：1-2天（基础框架）
- **阶段2**：3-5天（核心页面）
- **阶段3**：2-3天（API实现）
- **阶段4**：1-2天（优化测试）

**总计**：7-12天（1-2周）

## 下一步

1. 确认设计方案
2. 开始实现基础框架
3. 逐步实现各功能模块

---

**准备开始实现了吗？**
