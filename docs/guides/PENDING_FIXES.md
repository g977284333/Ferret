# 待修复问题记录

## 问题1: 导出数据标题仍为英文

### 问题描述
- **位置**: 机会列表页面 (`/opportunities`)
- **操作**: 点击"导出数据"按钮，选择CSV或Excel格式
- **现象**: 导出的文件中，列标题仍然是英文（如 `app_id`, `name`, `category` 等），而不是中文（如 `应用名称`, `分类` 等）

### 已尝试的修复方法
1. **方法1**: 使用 `df.rename(columns=column_mapping)` 重命名列
   - 文件: `frontend/web/api/opportunities.py`
   - 结果: 未生效

2. **方法2**: 创建新的DataFrame，逐列复制并重命名
   ```python
   df_export = pd.DataFrame()
   for col in df.columns:
       new_col_name = column_mapping.get(col, col)
       df_export[new_col_name] = df[col]
   ```
   - 文件: `frontend/web/api/opportunities.py` (第255-260行)
   - 结果: 未生效

3. **调试信息**: 已添加打印语句，可在服务器终端查看映射过程
   - 位置: `frontend/web/api/opportunities.py` (第262-265行)
   - 输出: `[导出] 原始列名`, `[导出] 映射后列名`, `[导出] 数据行数`

### 可能的原因分析
1. **浏览器缓存**: 浏览器可能缓存了旧的导出文件
2. **数据源问题**: 从数据库获取的数据可能已经包含某些字段，但映射表不完整
3. **导出时机**: 映射可能在导出前没有正确应用
4. **CSV编码问题**: CSV文件的BOM标记可能影响列名显示

### 相关代码位置
- **导出函数**: `frontend/web/api/opportunities.py` - `export_opportunities()` (第173行)
- **前端调用**: `frontend/web/static/js/opportunities.js` - `exportData()` (第395行)
- **列名映射表**: `frontend/web/api/opportunities.py` (第225-253行)

### 后续修复建议
1. **检查实际数据**: 在导出函数中添加更多调试信息，查看实际从数据库获取的列名
2. **验证映射**: 在导出前打印 `df_export.columns`，确认映射是否生效
3. **测试不同格式**: 分别测试CSV和Excel导出，看是否格式相关
4. **清除缓存**: 建议用户清除浏览器缓存或使用无痕模式测试
5. **检查数据库结构**: 确认 `opportunities` 表的实际列名是否与映射表匹配

---

## 问题2: 趋势图表不是通栏宽度

### 问题描述
- **位置**: 搜索趋势页面 (`/trends`)
- **现象**: 趋势图表区域的宽度与"热门关键词"和"已采集关键词"卡片相同（两列布局），右侧有大量空白，没有占满整行宽度

### 已尝试的修复方法
1. **方法1**: 添加 `w-full` 类
   - 结果: 未生效，因为父容器 `container mx-auto` 限制了宽度

2. **方法2**: 使用负边距突破container限制
   ```css
   margin-left: -1rem; 
   margin-right: -1rem; 
   width: calc(100% + 2rem);
   ```
   - 结果: 未生效

3. **方法3**: 使用视口单位突破限制
   ```css
   margin-left: calc(-50vw + 50%);
   margin-right: calc(-50vw + 50%);
   width: 100vw;
   ```
   - 文件: `frontend/web/templates/trends.html` (第260行)
   - 结果: 未生效

### 可能的原因分析
1. **父容器限制**: `base.html` 中的 `<main class="container mx-auto px-4 py-6">` 限制了最大宽度
2. **CSS优先级**: Tailwind CSS的类可能覆盖了内联样式
3. **布局结构**: 趋势图表在grid布局之后，但仍在container内

### 相关代码位置
- **HTML模板**: `frontend/web/templates/trends.html` (第259-283行)
- **基础模板**: `frontend/web/templates/base.html` (第89行) - `container mx-auto px-4 py-6`
- **布局结构**: 趋势图表在 `<!-- 趋势数据展示 -->` grid布局之后

### 后续修复建议
1. **修改HTML结构**: 将趋势图表移出 `main` 容器的 `container` 类，或者使用独立的容器
2. **使用CSS Grid**: 修改整个页面的布局结构，让图表区域独立
3. **JavaScript动态调整**: 使用JavaScript在页面加载后动态调整图表容器的宽度
4. **检查Tailwind配置**: 确认 `container` 类的最大宽度设置
5. **使用CSS变量**: 定义CSS变量来控制图表宽度，更容易调试

### 当前HTML结构
```html
<main class="container mx-auto px-4 py-6">
    <!-- 其他内容 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- 热门关键词 -->
        <!-- 已采集关键词 -->
    </div>
    
    <!-- 趋势图表 - 应该通栏但未生效 -->
    <div class="bg-white ..." style="...">
        <!-- 图表内容 -->
    </div>
</main>
```

---

## 问题修复优先级
- **问题1 (导出标题)**: 中等优先级 - 影响用户体验，但不影响核心功能
- **问题2 (图表宽度)**: 低优先级 - 主要是视觉效果，不影响功能

## 修复时间建议
- 建议在下一个开发周期中集中修复
- 修复前先进行详细的问题复现和调试
- 考虑创建测试用例来验证修复效果

## 备注
- 两个问题都已尝试多次修复但未成功
- 需要更深入的调试和测试
- 可能需要重新审视整体架构和设计
