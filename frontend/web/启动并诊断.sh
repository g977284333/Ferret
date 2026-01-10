#!/bin/bash
# 启动服务器并显示详细输出

cd "$(dirname "$0")"

echo "========================================"
echo "启动Ferret服务器（详细模式）"
echo "========================================"
echo ""

# 检查Flask
echo "检查Flask..."
python3 -c "import flask; print('Flask版本:', flask.__version__)" || {
    echo "错误: Flask未安装"
    exit 1
}
echo ""

# 启动服务器并捕获所有输出
echo "启动服务器..."
echo "如果看到错误，请查看下面的输出"
echo ""
echo "========================================"
echo ""

python3 app.py 2>&1 | tee server.log
