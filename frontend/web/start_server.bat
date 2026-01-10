@echo off
chcp 65001 >nul
echo ========================================
echo Ferret Flask Server 启动脚本
echo ========================================
echo.
cd /d %~dp0
echo 当前目录: %CD%
echo.

echo 检查Python...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3
    pause
    exit /b 1
)
echo.

echo 检查依赖...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask未安装，正在安装依赖...
    echo.
    
    echo 1. 安装项目根目录依赖...
    cd ..\..
    if exist requirements.txt (
        python -m pip install -r requirements.txt
    )
    
    echo.
    echo 2. 安装前端依赖...
    cd frontend\web
    if exist requirements.txt (
        python -m pip install -r requirements.txt
    )
    
    echo.
    echo 3. 检查 itunes-app-scraper...
    python -c "import itunes_app_scraper" 2>nul
    if errorlevel 1 (
        echo 安装 itunes-app-scraper...
        python -m pip install git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git
    )
) else (
    echo ✓ Flask已安装
)

echo.
echo ========================================
echo 启动服务器...
echo ========================================
echo 服务器地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.
python app.py
pause
