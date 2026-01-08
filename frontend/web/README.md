# Ferret Web前端

基于Flask + Tailwind CSS + Flowbite的Web前端应用。

## 技术栈

- **后端**：Flask
- **前端**：Tailwind CSS + Flowbite
- **图表**：Chart.js
- **表格**：DataTables
- **JavaScript**：jQuery

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 项目根目录的依赖也需要安装
cd ../..
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

访问：http://localhost:5000

## 项目结构

```
frontend/web/
├── app.py              # Flask应用主文件
├── requirements.txt    # Python依赖
├── templates/          # HTML模板
│   ├── base.html      # 基础模板
│   ├── index.html     # 首页
│   ├── scrape.html    # 采集页面
│   ├── opportunities.html # 机会列表
│   ├── detail.html    # 详情页面
│   └── config.html    # 配置页面
├── static/            # 静态文件
│   ├── css/          # 样式文件
│   ├── js/           # JavaScript文件
│   └── img/          # 图片资源
└── api/              # API路由
    ├── scrape.py     # 采集API
    ├── opportunities.py # 机会API
    ├── config.py     # 配置API
    └── stats.py      # 统计API
```

## 功能

- ✅ 数据采集控制
- ✅ 机会列表查看
- ✅ 机会详情展示
- ✅ 配置管理
- ✅ 统计信息

## 开发

### 添加新页面

1. 在 `templates/` 创建HTML模板
2. 在 `app.py` 添加路由
3. 在 `static/js/` 添加JavaScript

### API开发

在 `api/` 目录下创建新的蓝图文件。

## 部署

生产环境建议使用：
- Gunicorn + Nginx
- 或 Docker
