# 数据来源说明

## 数据真实性

### ✅ 数据来源：App Store官方API

所有数据均来自**App Store官方API**（通过`itunes-app-scraper`工具），数据**真实可靠**。

### 数据采集流程

1. **搜索关键词** → 使用App Store官方搜索API
2. **获取App ID列表** → 官方API返回
3. **获取App详情** → 官方API返回完整数据
4. **保存原始数据** → 完整保存到`raw_apps`表
5. **分析评分** → 基于真实数据计算机会分数

## 数据字段说明

### 基本信息（已显示）
- **名称** (trackName)
- **分类** (primaryGenreName)
- **评分** (averageUserRating)
- **评论数** (userRatingCount)
- **价格** (price)
- **App Store链接** (trackViewUrl)

### 详细信息（新增显示）
- **开发者** (sellerName)
- **发布日期** (releaseDate)
- **当前版本** (version)
- **版本更新日期** (currentVersionReleaseDate)
- **版本评分** (averageUserRatingForCurrentVersion)
- **版本评论数** (userRatingCountForCurrentVersion)
- **文件大小** (fileSizeBytes)
- **最低系统版本** (minimumOsVersion)
- **内容评级** (contentAdvisoryRating)
- **应用描述** (description)
- **应用截图** (screenshotUrls)
- **应用图标** (artworkUrl512/artworkUrl100)

## 数据存储

### 数据库表结构

1. **opportunities表** - 存储分析后的机会数据
   - 包含：基本信息 + 机会分数

2. **raw_apps表** - 存储完整的原始数据
   - 包含：App Store API返回的完整JSON数据
   - 用于详情页面显示更多信息

## 数据验证

### 如何验证数据真实性？

1. **对比App Store**
   - 点击"打开App Store"按钮
   - 对比显示的数据与App Store官方数据

2. **查看原始数据**
   - 所有原始数据保存在`data/raw/app_store/`目录
   - JSON格式，可直接查看

3. **检查数据时间戳**
   - 详情页面显示数据采集时间
   - 可以确认数据的新鲜度

## 数据更新

### 数据采集时机

- 手动触发：在"数据采集"页面启动采集任务
- 数据实时：每次采集都是最新的App Store数据

### 数据缓存

- 数据库存储：避免重复采集相同App
- 原始数据保留：完整保存，可随时查看

## 注意事项

1. **数据延迟**
   - App Store数据可能有1-2天延迟
   - 评分和评论数会定期更新

2. **数据完整性**
   - 部分App可能缺少某些字段（如描述、截图）
   - 这是App Store API的限制

3. **数据准确性**
   - 所有数据来自官方API，准确可靠
   - 机会分数是基于真实数据计算的

---

**数据来源：App Store官方API | 数据真实可靠** ✅
