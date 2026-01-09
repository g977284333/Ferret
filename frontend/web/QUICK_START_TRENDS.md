# 快速启动趋势功能测试

## 问题排查

如果无法访问 `/trends` 页面，请按以下步骤检查：

### 1. 确认Flask服务正在运行

```bash
cd frontend/web
python app.py
```

应该看到类似输出：
```
 * Running on http://0.0.0.0:5000
```

### 2. 检查端口是否被占用

如果5000端口被占用，可以：
- 关闭占用端口的程序
- 或者修改 `app.py` 最后一行改为其他端口，如 `port=5001`

### 3. 访问正确的URL

- 正确：`http://localhost:5000/trends`
- 或：`http://127.0.0.1:5000/trends`

### 4. 检查浏览器控制台

按F12打开开发者工具，查看：
- Console标签：是否有JavaScript错误
- Network标签：请求是否成功（状态码200）

### 5. 检查文件是否存在

确认以下文件存在：
- `frontend/web/templates/trends.html`
- `frontend/web/static/js/trends.js`
- `frontend/web/api/trends.py`

## 快速测试

### 方法1：使用批处理文件（Windows）

双击运行：`frontend/web/start_trends_test.bat`

### 方法2：手动启动

```bash
cd frontend/web
python app.py
```

然后在浏览器访问：`http://localhost:5000/trends`

## 常见问题

### 问题1：404 Not Found

**原因**：路由未注册或服务未启动

**解决**：
1. 确认 `app.py` 中有 `@app.route('/trends')`
2. 确认 `trends_bp` 已注册
3. 重启Flask服务

### 问题2：500 Internal Server Error

**原因**：模板文件错误或导入失败

**解决**：
1. 查看Flask终端输出的错误信息
2. 检查 `templates/trends.html` 是否存在
3. 检查 `api/trends.py` 是否有语法错误

### 问题3：页面空白

**原因**：JavaScript加载失败

**解决**：
1. 检查浏览器控制台错误
2. 确认 `static/js/trends.js` 存在
3. 检查网络请求是否成功

## 验证步骤

1. ✅ Flask服务启动成功
2. ✅ 访问 `http://localhost:5000` 能看到首页
3. ✅ 导航栏有"搜索趋势"链接
4. ✅ 点击链接能跳转到 `/trends` 页面
5. ✅ 页面能正常显示（即使没有数据）

如果以上都正常，说明功能已配置成功！
