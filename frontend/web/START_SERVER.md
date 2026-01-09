# 启动Flask服务指南

## 问题：localhost 拒绝了我们的连接请求

这个错误说明**Flask服务没有启动**。

## 解决方法

### 方法1：使用批处理文件启动（推荐）

1. 双击运行：`frontend/web/start_server.bat`
2. 等待看到类似输出：
   ```
   * Running on http://0.0.0.0:5000
   ```
3. 保持这个窗口打开
4. 在浏览器访问：`http://localhost:5000`

### 方法2：手动启动

1. 打开终端（PowerShell或CMD）
2. 进入项目目录：
   ```bash
   cd D:\workspace\GC\Ferret\frontend\web
   ```
3. 启动服务：
   ```bash
   python app.py
   ```
4. 看到以下输出说明启动成功：
   ```
   * Running on http://0.0.0.0:5000
   * Debug mode: on
   ```
5. **保持这个终端窗口打开**（关闭窗口会停止服务）
6. 在浏览器访问：`http://localhost:5000`

## 常见问题

### 问题1：端口5000被占用

**错误信息**：
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
```

**解决方法**：
1. 找到占用端口的程序：
   ```bash
   netstat -ano | findstr :5000
   ```
2. 关闭占用端口的程序，或修改端口：
   编辑 `app.py` 最后一行，改为：
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```
   然后访问：`http://localhost:5001`

### 问题2：Python模块导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'flask'
```

**解决方法**：
```bash
pip install flask flask-cors
```

### 问题3：服务启动后立即退出

**可能原因**：
- 代码有语法错误
- 导入模块失败

**解决方法**：
1. 查看终端输出的完整错误信息
2. 根据错误信息修复问题

## 验证服务是否运行

### 方法1：检查端口
```bash
netstat -ano | findstr :5000
```
如果看到输出，说明服务正在运行。

### 方法2：访问首页
在浏览器打开：`http://localhost:5000`
- 如果看到首页，说明服务正常
- 如果显示"拒绝连接"，说明服务未启动

### 方法3：测试API
```bash
curl http://localhost:5000/api/v1/stats
```
如果返回JSON数据，说明服务正常。

## 重要提示

⚠️ **Flask服务必须在终端中保持运行**，关闭终端窗口会停止服务。

如果需要后台运行，可以使用：
```bash
# Windows (PowerShell)
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden

# 或者使用nohup（如果安装了）
nohup python app.py > server.log 2>&1 &
```

## 下一步

服务启动成功后：
1. 访问 `http://localhost:5000` 查看首页
2. 点击导航栏的"搜索趋势"进入趋势页面
3. 测试趋势功能
