#!/bin/bash
# 快速启动脚本 - 简化版

echo "========================================"
echo "Ferret 快速启动"
echo "========================================"
echo ""

cd "$(dirname "$0")"
cd frontend/web

echo "当前目录: $(pwd)"
echo ""

# 直接尝试启动，如果失败会显示错误
echo "正在启动服务器..."
echo "如果看到依赖错误，请先运行: pip3 install Flask Flask-CORS"
echo ""
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""
echo "========================================"
echo ""

python3 app.py
