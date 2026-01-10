#!/bin/bash
# Ferret 一键安装和启动脚本

set -e  # 遇到错误立即退出

echo "========================================"
echo "Ferret 系统安装和启动"
echo "========================================"
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

echo "✓ Python版本:"
python3 --version
echo ""

# 步骤1: 检查依赖
echo "========================================"
echo "步骤1: 检查依赖"
echo "========================================"
echo ""

cd frontend/web
python3 check_dependencies.py
DEPENDENCIES_OK=$?
cd "$SCRIPT_DIR"

echo ""

if [ $DEPENDENCIES_OK -ne 0 ]; then
    echo "========================================"
    echo "步骤2: 安装依赖"
    echo "========================================"
    echo ""
    
    # 安装项目根目录依赖
    echo "📦 安装项目依赖..."
    python3 -m pip install --user -r requirements.txt || {
        echo "⚠️  某些依赖安装失败，尝试安装核心依赖..."
        python3 -m pip install --user Flask Flask-CORS pandas numpy pytrends deep-translator openpyxl tqdm beautifulsoup4 requests
    }
    
    echo ""
    echo "📦 安装前端依赖..."
    cd frontend/web
    python3 -m pip install --user -r requirements.txt || {
        echo "⚠️  前端依赖安装失败，尝试单独安装..."
        python3 -m pip install --user Flask Flask-CORS deep-translator
    }
    cd "$SCRIPT_DIR"
    
    echo ""
    echo "📦 安装 itunes-app-scraper (从GitHub)..."
    python3 -m pip install --user git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git || {
        echo "⚠️  itunes-app-scraper 安装失败，某些功能可能不可用"
    }
    
    echo ""
    echo "========================================"
    echo "再次检查依赖"
    echo "========================================"
    echo ""
    cd frontend/web
    python3 check_dependencies.py
    cd "$SCRIPT_DIR"
    echo ""
fi

# 步骤3: 启动服务器
echo "========================================"
echo "步骤3: 启动服务器"
echo "========================================"
echo ""
echo "🚀 正在启动Ferret服务器..."
echo ""
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""
echo "========================================"
echo ""

cd frontend/web
python3 app.py
