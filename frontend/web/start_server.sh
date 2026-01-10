#!/bin/bash
# Ferret Flask服务器启动脚本

echo "========================================"
echo "Ferret Flask Server 启动脚本"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "当前目录: $SCRIPT_DIR"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    echo "请先安装 Python 3"
    exit 1
fi

echo "Python版本:"
python3 --version
echo ""

# 检查Flask是否安装
echo "检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask未安装，正在安装依赖..."
    echo ""
    
    # 安装项目根目录的依赖
    echo "1. 安装项目根目录依赖..."
    cd ../..
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
    fi
    
    # 安装前端依赖
    echo ""
    echo "2. 安装前端依赖..."
    cd frontend/web
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
    fi
    
    # 检查itunes-app-scraper
    if ! python3 -c "import itunes_app_scraper" 2>/dev/null; then
        echo ""
        echo "3. 安装 itunes-app-scraper..."
        python3 -m pip install git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git
    fi
else
    echo "✓ Flask已安装"
fi

echo ""
echo "========================================"
echo "启动服务器..."
echo "========================================"
echo "服务器地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python3 app.py
