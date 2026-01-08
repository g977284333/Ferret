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
        
        for idx, keyword in enumerate(keywords):
            print(f"[任务 {task_id}] 开始采集关键词: {keyword} ({idx+1}/{len(keywords)})")
            tasks[task_id]['progress']['current_keyword'] = keyword
            tasks[task_id]['progress']['current_progress'] = f"0/{limit_per_keyword}"
            print(f"[任务 {task_id}] 更新进度: {tasks[task_id]['progress']}")
            
            apps = scraper.search_apps(keyword, limit=limit_per_keyword)
            print(f"[任务 {task_id}] 关键词 {keyword} 采集到 {len(apps)} 个App")
            
            # 去重
            new_apps = []
            for app in apps:
                app_id = app.get('trackId')
                if app_id and app_id not in seen_app_ids:
                    seen_app_ids.add(app_id)
                    all_apps.append(app)
                    new_apps.append(app)
            
            tasks[task_id]['progress']['completed'] += len(new_apps)
            tasks[task_id]['progress']['current_progress'] = f"{len(new_apps)}/{limit_per_keyword}"
            print(f"[任务 {task_id}] 当前进度: 已完成 {tasks[task_id]['progress']['completed']}/{tasks[task_id]['progress']['total']}, 当前关键词: {len(new_apps)}/{limit_per_keyword}")
        
        # 保存原始数据到数据库
        if all_apps:
            print(f"任务 {task_id} 保存 {len(all_apps)} 个App到数据库")
            data_manager.save_raw_data(all_apps, 'app_store')
        
        # 保存JSON文件
        scraper.save_apps(all_apps)
        
        # 分析机会
        print(f"任务 {task_id} 开始分析机会")
        df = analyzer.analyze_opportunities(all_apps)
        
        # 保存机会到数据库
        opportunities_count = 0
        for _, row in df.iterrows():
            data_manager.save_opportunity(row.to_dict())
            opportunities_count += 1
        
        # 更新最终进度
        tasks[task_id]['progress']['completed'] = len(all_apps)
        tasks[task_id]['progress']['current_keyword'] = '完成'
        tasks[task_id]['progress']['current_progress'] = f"{len(all_apps)}/{len(all_apps)}"
        
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['results'] = {
            'apps_collected': len(all_apps),
            'opportunities_found': opportunities_count
        }
        print(f"任务 {task_id} 完成: 采集 {len(all_apps)} 个App, 发现 {opportunities_count} 个机会")
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        print(f"任务 {task_id} 出错: {error_msg}")
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = error_msg


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
    
    # 返回统一格式：status='success'表示API调用成功，data中包含任务状态
    response = {
        'status': 'success',
        'data': {
            'status': task['status'],  # 任务状态：pending, running, completed, error, stopped
            'progress': task.get('progress', {}),
            'results': task.get('results', {})
        }
    }
    
    if 'error' in task:
        response['data']['error'] = task['error']
    
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
