# 快速开始指南

## 1. 安装依赖

```bash
# 安装基础依赖
pip install pandas numpy matplotlib seaborn python-dotenv tqdm pyyaml

# 安装App Store爬虫（从GitHub安装）
pip install git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git
```

**注意**: `itunes-app-scraper` 不在PyPI上，必须从GitHub安装。

## 2. 运行数据采集（测试）

```bash
# 测试App Store爬虫
python scrapers/app_store_scraper.py
```

## 3. 运行完整流程

```bash
python main.py
```

这会：
1. 采集App Store数据
2. 分析机会
3. 输出Top机会列表

## 4. 查看结果

结果会保存在：
- `data/processed/opportunities.csv` - CSV格式
- `data/opportunities.db` - SQLite数据库

## 5. 自定义配置

编辑 `config/config.yaml` 来调整：
- 数据源配置
- 机会评分权重
- 筛选阈值

编辑 `main.py` 来调整：
- 搜索关键词（第12行）
- 每个关键词的采集数量（limit参数）

## 测试结果

✅ **已测试通过**：
- 数据采集：成功采集52个App（3个关键词，已去重）
- 数据分析：发现46个潜在机会
- 完整流程：约2分钟完成

**Top机会示例**：
- Evernote: 评分4.41，机会分数0.950
- Trello: 评分4.38，机会分数0.860
- Asana: 评分4.69，机会分数0.790

## 下一步

1. **优化数据采集**：根据实际需求调整爬虫
2. **优化评分模型**：根据实际数据调整权重
3. **添加更多数据源**：Product Hunt、Google Play等
4. **快速试错**：选择Top机会，开发MVP验证

详细测试结果见 `TEST_RESULTS.md`
