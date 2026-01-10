#!/bin/bash
# 启动服务器 - 修复版

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 进入前端目录
cd "$SCRIPT_DIR/frontend/web"

# 确认文件存在
if [ ! -f "app.py" ]; then
    echo "错误: 找不到 app.py 文件"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo "========================================"
echo "启动Ferret服务器"
echo "========================================"
echo "当前目录: $(pwd)"
echo "文件: $(pwd)/app.py"
echo ""

# 直接使用绝对路径启动
python3 "$(pwd)/app.py"
