# 🚀 Ferret 快速启动指南

## 一键启动（推荐）

### macOS/Linux:
```bash
cd /Users/chen/WorkSpace/gechen/Ferret
./一键启动.sh
```

### Windows:
```bash
cd C:\Users\chen\WorkSpace\gechen\Ferret
一键启动.bat
```

脚本会自动：
1. ✅ 检查Python环境
2. ✅ 检查依赖是否安装
3. ✅ 自动安装缺失的依赖
4. ✅ 启动服务器

## 手动启动

如果一键启动不工作，可以手动执行：

### 步骤1: 安装依赖

```bash
# 进入项目目录
cd /Users/chen/WorkSpace/gechen/Ferret

# 安装项目依赖
pip3 install -r requirements.txt

# 安装前端依赖
cd frontend/web
pip3 install -r requirements.txt
```

### 步骤2: 启动服务器

```bash
cd frontend/web
python3 app.py
```

### 步骤3: 访问系统

浏览器打开：http://localhost:5000

## 验证安装

运行依赖检查脚本：

```bash
cd frontend/web
python3 check_dependencies.py
```

## 常见问题

### 1. 权限错误
使用 `--user` 参数：
```bash
pip3 install --user -r requirements.txt
```

### 2. 网络问题
使用国内镜像：
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 某些包安装失败
可以单独安装核心依赖：
```bash
pip3 install Flask Flask-CORS pandas numpy pytrends
```

## 启动成功的标志

看到以下输出说明启动成功：

```
==================================================
Ferret Flask 服务器启动
==================================================
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

然后就可以在浏览器访问 http://localhost:5000 了！
