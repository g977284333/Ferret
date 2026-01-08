# 问题排查指南

## 问题：http://localhost:5000 打不开

### 检查步骤

#### 1. 确认应用正在运行

```bash
# 检查端口是否被占用
netstat -ano | findstr :5000

# 应该看到类似输出：
# TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING
```

#### 2. 测试API是否可访问

```bash
# 使用curl测试
curl http://localhost:5000/api/v1/stats

# 或使用PowerShell
Invoke-WebRequest -Uri http://localhost:5000/api/v1/stats
```

#### 3. 检查浏览器

**可能的原因**：
- 浏览器缓存问题
- 代理设置问题
- 防火墙阻止

**解决方案**：
1. **清除浏览器缓存**
   - Chrome: Ctrl+Shift+Delete
   - 或使用无痕模式

2. **尝试不同浏览器**
   - Chrome
   - Firefox
   - Edge

3. **检查防火墙**
   - Windows防火墙可能阻止了端口5000
   - 临时关闭防火墙测试

4. **尝试127.0.0.1**
   - http://127.0.0.1:5000
   - 而不是 localhost

#### 4. 重启应用

```bash
# 停止当前应用（如果有）
# 然后重新启动
cd frontend/web
python app.py
```

#### 5. 检查错误日志

查看终端输出，看是否有错误信息。

### 常见问题

#### 问题1：端口被占用

**错误信息**：
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

**解决方案**：
```python
# 修改app.py，使用其他端口
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 问题2：模板文件不存在

**错误信息**：
```
jinja2.exceptions.TemplateNotFound: index.html
```

**解决方案**：
确保 `templates/index.html` 文件存在

#### 问题3：模块导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'api.scrape'
```

**解决方案**：
确保 `api/` 目录和文件都存在

### 快速测试

运行测试脚本：

```bash
cd frontend/web
python test_api.py
```

如果API测试通过，说明应用正常运行，问题可能在浏览器端。

### 替代访问方式

如果localhost不行，尝试：

1. **使用127.0.0.1**
   ```
   http://127.0.0.1:5000
   ```

2. **使用本机IP**
   ```bash
   # 查看本机IP
   ipconfig
   
   # 使用IP访问，例如：
   http://192.168.1.100:5000
   ```

3. **修改hosts文件**（如果需要）
   ```
   C:\Windows\System32\drivers\etc\hosts
   添加：127.0.0.1 localhost
   ```

### 调试模式

启用详细日志：

```python
# 在app.py中
import logging
logging.basicConfig(level=logging.DEBUG)

app.run(debug=True, host='0.0.0.0', port=5000)
```

### 如果还是不行

1. **检查Python版本**
   ```bash
   python --version
   # 应该是3.7+
   ```

2. **重新安装依赖**
   ```bash
   pip install --upgrade Flask Flask-CORS
   ```

3. **检查文件权限**
   - 确保有读取templates目录的权限

4. **查看完整错误信息**
   - 运行 `python app.py` 查看完整输出

---

**如果问题仍然存在，请提供具体的错误信息！**
