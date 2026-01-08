"""
Flask Web应用主文件
Ferret - 机会发现工具前端
"""

import sys
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# 添加backend/src到路径，以便导入现有模块
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

# 导入后端模块
from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
from utils.data_manager import DataManager

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ferret-secret-key-change-in-production'
CORS(app)  # 允许跨域请求

# 注册蓝图
from api.scrape import scrape_bp
from api.opportunities import opportunities_bp
from api.config import config_bp
from api.stats import stats_bp
from api.translate import translate_bp

app.register_blueprint(scrape_bp, url_prefix='/api/v1/scrape')
app.register_blueprint(opportunities_bp, url_prefix='/api/v1/opportunities')
app.register_blueprint(config_bp, url_prefix='/api/v1/config')
app.register_blueprint(stats_bp, url_prefix='/api/v1/stats')
app.register_blueprint(translate_bp, url_prefix='/api/v1/translate')


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
