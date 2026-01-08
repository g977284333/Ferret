# 快速开始指南

## 项目结构说明

项目已重新组织，结构更加清晰：

```
Ferret/
├── docs/          # 所有文档
├── backend/       # 后端代码
├── frontend/      # 前端（预留）
├── apps/          # 应用（预留）
├── tests/         # 测试管理
└── data/          # 数据存储
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git
```

### 2. 运行系统

```bash
# 从项目根目录运行
python backend/src/main.py
```

### 3. 查看结果

- CSV文件：`data/processed/opportunities.csv`
- 数据库：`data/opportunities.db`

## 运行测试

```bash
# 功能验证
python backend/tests/validation/validate_system.py

# 全面测试
python backend/tests/validation/comprehensive_test.py
```

## 配置

编辑 `backend/config/config.yaml` 来调整参数。

## 更多文档

- [完整文档索引](../README.md)
- [开发者指南](developer_guide.md)
- [系统框架](../../design/framework/FRAMEWORK.md)
