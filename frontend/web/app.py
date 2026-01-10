"""
Flask Web应用主文件
Ferret - 机会发现工具前端
"""

import sys
import os
import traceback
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 添加backend/src到路径，以便导入现有模块
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

# 导入后端模块（如果失败，应用仍可启动）
try:
    from scrapers.app_store_scraper import AppStoreScraperWrapper
    from analyzers.opportunity_analyzer import OpportunityAnalyzer
    from utils.data_manager import DataManager
    BACKEND_MODULES_LOADED = True
except Exception as e:
    print(f"警告: 后端模块导入失败: {e}")
    print("某些功能可能不可用")
    BACKEND_MODULES_LOADED = False

# 创建Flask应用
# 显式指定静态文件和模板文件夹路径
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
app.config['SECRET_KEY'] = 'ferret-secret-key-change-in-production'
# CORS配置 - 允许所有来源
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许跨域请求

# 注册蓝图（如果导入失败，应用仍可启动）
try:
    from api.scrape import scrape_bp
    from api.opportunities import opportunities_bp
    from api.config import config_bp
    from api.stats import stats_bp
    from api.translate import translate_bp
    from api.trends import trends_bp
    
    app.register_blueprint(scrape_bp, url_prefix='/api/v1/scrape')
    app.register_blueprint(opportunities_bp, url_prefix='/api/v1/opportunities')
    app.register_blueprint(config_bp, url_prefix='/api/v1/config')
    app.register_blueprint(stats_bp, url_prefix='/api/v1/stats')
    app.register_blueprint(translate_bp, url_prefix='/api/v1/translate')
    app.register_blueprint(trends_bp, url_prefix='/api/v1/trends')
    print("✓ 所有API蓝图已注册")
except Exception as e:
    print(f"⚠️  警告: 蓝图注册失败: {e}")
    print("应用将继续运行，但某些API功能可能不可用")
    traceback.print_exc()


# 添加请求日志
@app.before_request
def log_request():
    """记录所有请求"""
    print(f"[请求] {request.method} {request.path} - {request.remote_addr}")
    # 不返回任何内容，让请求继续处理
    # 确保不返回任何值，否则会导致请求被中断
    return None


@app.route('/')
def index():
    """首页"""
    try:
        # 先尝试简单返回，确认路由工作
        print(f"[路由] 访问首页: {request.path}")
        return render_template('index.html')
    except Exception as e:
        print(f"错误: 渲染index.html失败: {e}")
        traceback.print_exc()
        # 如果模板失败，返回简单HTML
        return f'''<html><body>
            <h1>Ferret 服务器运行中</h1>
            <p>模板加载失败: {str(e)}</p>
            <p>但服务器正常工作！</p>
            <p><a href="/hello">测试路由</a></p>
        </body></html>''', 200


@app.route('/scrape')
def scrape_page():
    """数据采集页面"""
    return render_template('scrape.html')


@app.route('/opportunities')
def opportunities_page():
    """机会列表页面"""
    return render_template('opportunities.html')


@app.route('/opportunities/<app_id>')
def opportunity_detail(app_id):
    """机会详情页面"""
    return render_template('detail.html', app_id=app_id)


@app.route('/config')
def config_page():
    """配置页面"""
    return render_template('config.html')


@app.route('/trends')
def trends_page():
    """搜索趋势页面"""
    return render_template('trends.html')


@app.route('/test')
def test():
    """测试路由"""
    return jsonify({
        'status': 'success',
        'message': '服务器运行正常',
        'static_folder': app.static_folder,
        'template_folder': app.template_folder
    })


@app.route('/hello')
def hello():
    """最简单的测试路由"""
    return '<h1>Hello! 服务器运行正常</h1><p>如果你看到这个，说明Flask服务器正常工作</p>'


@app.errorhandler(403)
def forbidden(error):
    """处理403错误"""
    print(f"[403错误] {request.path} - {request.method}")
    print(f"错误详情: {error}")
    traceback.print_exc()
    return jsonify({
        'error': 'Forbidden',
        'message': '访问被拒绝，请检查权限设置',
        'path': request.path,
        'method': request.method
    }), 403


@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        'error': 'Not Found',
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 确保在正确的目录下运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 50)
    print("Ferret Flask 服务器启动")
    print("=" * 50)
    print(f"工作目录: {os.getcwd()}")
    print(f"静态文件目录: {app.static_folder}")
    print(f"模板目录: {app.template_folder}")
    
    # 检查关键文件是否存在
    static_path = Path(app.static_folder)
    template_path = Path(app.template_folder)
    print(f"静态文件目录存在: {static_path.exists()}")
    print(f"模板目录存在: {template_path.exists()}")
    
    if template_path.exists():
        templates = list(template_path.glob('*.html'))
        print(f"找到 {len(templates)} 个模板文件")
    
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("测试路由: http://localhost:5000/test")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    print()
    
    try:
        # 自动查找可用端口
        import socket
        
        def find_free_port(start_port=5000, max_attempts=10):
            """查找可用端口"""
            for i in range(max_attempts):
                port = start_port + i
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result != 0:  # 端口未被占用
                    return port
            return None
        
        port = find_free_port(5000, 20)
        
        if port is None:
            print("❌ 错误: 无法找到可用端口（5000-5019都被占用）")
            print("请手动停止占用端口的进程，或修改代码使用其他端口")
            sys.exit(1)
        
        if port != 5000:
            print(f"⚠️  端口 5000 被占用，使用端口 {port}")
        else:
            print(f"✓ 端口 {port} 可用")
        
        print(f"🌐 访问地址: http://localhost:{port}")
        print()
        
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        traceback.print_exc()
