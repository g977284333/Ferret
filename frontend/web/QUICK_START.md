# 快速开始指南

## 启动应用

### 1. 安装依赖

```bash
# 安装Flask相关依赖
cd frontend/web
pip install -r requirements.txt

# 确保项目根目录的依赖也已安装
cd ../..
pip install -r requirements.txt
```

### 2. 启动Flask应用

```bash
cd frontend/web
python app.py
```

应用将在 http://localhost:5000 启动

### 3. 访问应用

打开浏览器访问：
- 首页: http://localhost:5000
- API测试: http://localhost:5000/api/v1/stats

## 测试API

运行测试脚本：

```bash
cd frontend/web
python test_api.py
```

## 当前功能

### ✅ 已实现
- Flask应用框架
- API路由（统计、机会、配置、采集）
- 首页模板和基础功能
- Tailwind CSS + Flowbite集成

### ⏳ 待实现
- 数据采集页面
- 机会列表页面
- 机会详情页面
- 配置页面

## 开发建议

1. **先测试基础功能**
   - 访问首页查看UI
   - 测试API端点
   - 验证数据流

2. **逐步实现页面**
   - 先实现简单的页面
   - 再实现复杂交互
   - 最后优化体验

3. **使用浏览器开发者工具**
   - 查看网络请求
   - 调试JavaScript
   - 检查样式

## 常见问题

### 1. 端口被占用
```bash
# 修改app.py中的端口
app.run(debug=True, host='0.0.0.0', port=5001)
```

### 2. 模块导入错误
确保项目结构正确，backend/src目录存在

### 3. 数据库连接错误
确保data目录存在，数据库文件可创建

---

**开始开发吧！** 🚀
