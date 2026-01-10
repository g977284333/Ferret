@echo off
chcp 65001 >nul
echo ========================================
echo Ferret 系统安装和启动
echo ========================================
echo.

cd /d %~dp0
echo 项目目录: %CD%
echo.

echo 检查Python...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.7 或更高版本
    pause
    exit /b 1
)
echo.

echo ========================================
echo 步骤1: 检查依赖
echo ========================================
echo.

cd frontend\web
python check_dependencies.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo 步骤2: 安装依赖
    echo ========================================
    echo.
    
    echo 安装项目依赖...
    cd ..\..
    python -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo 某些依赖安装失败，尝试安装核心依赖...
        python -m pip install --user Flask Flask-CORS pandas numpy pytrends deep-translator openpyxl tqdm beautifulsoup4 requests
    )
    
    echo.
    echo 安装前端依赖...
    cd frontend\web
    python -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo 前端依赖安装失败，尝试单独安装...
        python -m pip install --user Flask Flask-CORS deep-translator
    )
    
    echo.
    echo 安装 itunes-app-scraper...
    python -m pip install --user git+https://github.com/digitalmethodsinitiative/itunes-app-scraper.git
    if errorlevel 1 (
        echo itunes-app-scraper 安装失败，某些功能可能不可用
    )
    
    echo.
    echo ========================================
    echo 再次检查依赖
    echo ========================================
    echo.
    python check_dependencies.py
)

echo.
echo ========================================
echo 步骤3: 启动服务器
echo ========================================
echo.
echo 正在启动Ferret服务器...
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.
echo ========================================
echo.

python app.py
pause
