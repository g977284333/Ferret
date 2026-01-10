# 🚀 启动服务器 - 最简单方法

## 方法1：直接命令（推荐）

在终端执行以下命令（**注意：不要有多余的斜杠**）：

```bash
cd /Users/chen/WorkSpace/gechen/Ferret/frontend/web
python3 app.py
```

**重要**：确保路径是 `app.py` 而不是 `app.py/`

## 方法2：使用脚本

```bash
cd /Users/chen/WorkSpace/gechen/Ferret
bash 启动服务器.sh
```

## 验证服务器启动

启动成功后，你应该看到：

```
==================================================
Ferret Flask 服务器启动
==================================================
 * Running on http://0.0.0.0:5000
```

## 访问系统

在浏览器打开：**http://localhost:5000**

## 如果遇到错误

### 错误1：`can't open file 'app.py/'`
- **原因**：路径末尾多了一个斜杠
- **解决**：确保命令是 `python3 app.py` 而不是 `python3 app.py/`

### 错误2：`ModuleNotFoundError`
- **解决**：运行 `pip3 install --user pyyaml Flask Flask-CORS`

### 错误3：端口被占用
- **解决**：停止占用5000端口的进程，或修改app.py中的端口号
