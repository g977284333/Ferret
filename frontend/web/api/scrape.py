"""
数据采集API
"""

import sys
import threading
from pathlib import Path
from flask import Blueprint, request, jsonify
from datetime import datetime

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
from utils.data_manager import DataManager

scrape_bp = Blueprint('scrape', __name__)

# 存储任务状态（实际应该用Redis或数据库）
tasks = {}

def run_scrape_task(task_id, keywords, data_source, limit_per_keyword):
    """在后台线程运行采集任务"""
    try:
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['progress'] = {
            'total': len(keywords) * limit_per_keyword,
            'completed': 0,
            'current_keyword': keywords[0] if keywords else '',
            'current_progress': '0/0'
        }
        
        scraper = AppStoreScraperWrapper()
        data_manager = DataManager()
        analyzer = OpportunityAnalyzer()
        
        all_apps = []
        seen_app_ids = set()  # 去重
        
        for keyword in keywords:
            tasks[task_id]['progress']['current_keyword'] = keyword
            apps = scraper.search_apps(keyword, limit=limit_per_keyword)
            
            # 去重
            for app in apps:
                app_id = app.get('trackId')
                if app_id and app_id not in seen_app_ids:
                    seen_app_ids.add(app_id)
                    all_apps.append(app)
            
            tasks[task_id]['progress']['completed'] += len(apps)
            tasks[task_id]['progress']['current_progress'] = f"{len(apps)}/{limit_per_keyword}"
        
        # 保存原始数据到数据库
        if all_apps:
            data_manager.save_raw_data(all_apps, 'app_store')
        
        # 保存JSON文件
        scraper.save_apps(all_apps)
        
        # 分析机会
        df = analyzer.analyze_opportunities(all_apps)
        
        # 保存机会到数据库
        opportunities_count = 0
        for _, row in df.iterrows():
            data_manager.save_opportunity(row.to_dict())
            opportunities_count += 1
        
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['results'] = {
            'apps_collected': len(all_apps),
            'opportunities_found': opportunities_count
        }
        
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)


@scrape_bp.route('/start', methods=['POST'])
def start_scrape():
    """启动数据采集"""
    data = request.json
    keywords = data.get('keywords', [])
    data_source = data.get('data_source', 'app_store')
    limit_per_keyword = data.get('limit_per_keyword', 20)
    
    if not keywords:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_PARAMETER',
            'message': '关键词列表不能为空'
        }), 400
    
    # 生成任务ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 初始化任务状态
    tasks[task_id] = {
        'status': 'pending',
        'keywords': keywords,
        'data_source': data_source,
        'limit_per_keyword': limit_per_keyword
    }
    
    # 在后台线程启动任务
    thread = threading.Thread(
        target=run_scrape_task,
        args=(task_id, keywords, data_source, limit_per_keyword)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'success',
        'task_id': task_id,
        'message': '采集任务已启动'
    })


@scrape_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """获取采集状态"""
    if task_id not in tasks:
        return jsonify({
            'status': 'error',
            'error_code': 'TASK_NOT_FOUND',
            'message': '任务不存在'
        }), 404
    
    task = tasks[task_id]
    response = {
        'status': task['status'],
        'progress': task.get('progress', {}),
        'results': task.get('results', {})
    }
    
    if 'error' in task:
        response['error'] = task['error']
    
    return jsonify(response)


@scrape_bp.route('/stop/<task_id>', methods=['POST'])
def stop_scrape(task_id):
    """停止采集"""
    if task_id not in tasks:
        return jsonify({
            'status': 'error',
            'error_code': 'TASK_NOT_FOUND',
            'message': '任务不存在'
        }), 404
    
    tasks[task_id]['status'] = 'stopped'
    
    return jsonify({
        'status': 'success',
        'message': '采集任务已停止'
    })
