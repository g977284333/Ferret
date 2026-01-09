"""
搜索趋势API
"""

import sys
import threading
from pathlib import Path
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pandas as pd

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from scrapers.trend_scraper import TrendScraper
from analyzers.trend_analyzer import TrendAnalyzer
from utils.data_manager import DataManager

trends_bp = Blueprint('trends', __name__)

# 存储任务状态（实际应该用Redis或数据库）
trend_tasks = {}

def run_trend_task(task_id, keywords, platforms, timeframe):
    """在后台线程运行趋势采集任务"""
    try:
        trend_tasks[task_id]['status'] = 'running'
        trend_tasks[task_id]['progress'] = {
            'total': len(keywords) * len(platforms),
            'completed': 0,
            'current_keyword': keywords[0] if keywords else '',
            'current_platform': platforms[0] if platforms else ''
        }
        
        scraper = TrendScraper()
        data_manager = DataManager()
        analyzer = TrendAnalyzer()
        
        all_trends = []
        completed = 0
        
        print(f"[Trend Task {task_id}] 开始采集任务，关键词: {keywords}, 平台: {platforms}, 时间范围: {timeframe}")
        
        for keyword in keywords:
            trend_tasks[task_id]['progress']['current_keyword'] = keyword
            
            for platform in platforms:
                trend_tasks[task_id]['progress']['current_platform'] = platform
                
                if platform == 'google_trends':
                    result = scraper.get_google_trends([keyword], timeframe=timeframe)
                    
                    print(f"[Trend Task {task_id}] 采集关键词 '{keyword}' 结果: success={result.get('success')}, error={result.get('error', 'None')}")
                    
                    if result['success'] and 'data' in result:
                        data = result['data']
                        interest_data = data.get('interest_over_time', [])
                        
                        print(f"[Trend Task {task_id}] interest_over_time 数据量: {len(interest_data) if isinstance(interest_data, list) else 0}")
                        
                        # 保存趋势数据
                        trends_to_save = []
                        if interest_data and isinstance(interest_data, list):
                            # interest_over_time现在是记录列表格式
                            for record in interest_data:
                                date_str = record.get('date', '')
                                # 获取该关键词的值
                                if keyword in record:
                                    value = record[keyword]
                                    if isinstance(value, (int, float)) and value > 0:
                                        trends_to_save.append({
                                            'keyword': keyword,
                                            'platform': 'google_trends',
                                            'date': str(date_str),
                                            'value': float(value),
                                            'metadata': {}
                                        })
                        
                        print(f"[Trend Task {task_id}] 准备保存 {len(trends_to_save)} 条趋势数据")
                        
                        if trends_to_save:
                            try:
                                data_manager.save_trend_batch(trends_to_save)
                                all_trends.extend(trends_to_save)
                                print(f"[Trend Task {task_id}] 成功保存 {len(trends_to_save)} 条趋势数据到数据库")
                            except Exception as e:
                                print(f"[Trend Task {task_id}] 保存趋势数据失败: {e}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"[Trend Task {task_id}] 警告: 没有可保存的趋势数据")
                    else:
                        print(f"[Trend Task {task_id}] 采集失败: {result.get('error', '未知错误')}")
                
                completed += 1
                trend_tasks[task_id]['progress']['completed'] = completed
        
        # 更新任务状态
        trend_tasks[task_id]['status'] = 'completed'
        trend_tasks[task_id]['results'] = {
            'keywords_collected': len(keywords),
            'trends_saved': len(all_trends),
            'platforms': platforms
        }
        
        # 保存任务到数据库
        data_manager.save_trend_task(
            task_id=task_id,
            keywords=keywords,
            platforms=platforms,
            timeframe=timeframe,
            status='completed',
            progress=trend_tasks[task_id]['progress'],
            results=trend_tasks[task_id]['results']
        )
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        trend_tasks[task_id]['status'] = 'error'
        trend_tasks[task_id]['error'] = error_msg
        
        data_manager = DataManager()
        data_manager.save_trend_task(
            task_id=task_id,
            keywords=keywords,
            platforms=platforms,
            timeframe=timeframe,
            status='error',
            error=error_msg
        )


@trends_bp.route('/start', methods=['POST'])
def start_trend_collection():
    """启动趋势数据采集"""
    data = request.json
    keywords = data.get('keywords', [])
    platforms = data.get('platforms', ['google_trends'])
    timeframe = data.get('timeframe', 'today 12-m')
    
    if not keywords:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_PARAMETER',
            'message': '关键词列表不能为空'
        }), 400
    
    # 生成任务ID
    task_id = f"trend_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 初始化任务状态
    trend_tasks[task_id] = {
        'status': 'pending',
        'keywords': keywords,
        'platforms': platforms,
        'timeframe': timeframe
    }
    
    # 保存任务到数据库
    data_manager = DataManager()
    data_manager.save_trend_task(
        task_id=task_id,
        keywords=keywords,
        platforms=platforms,
        timeframe=timeframe,
        status='pending'
    )
    
    # 在后台线程启动任务
    thread = threading.Thread(
        target=run_trend_task,
        args=(task_id, keywords, platforms, timeframe)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'success',
        'task_id': task_id,
        'message': '趋势采集任务已启动'
    })


@trends_bp.route('/status/<task_id>', methods=['GET'])
def get_trend_status(task_id):
    """获取趋势采集状态"""
    # 先从内存中获取
    if task_id in trend_tasks:
        task = trend_tasks[task_id]
    else:
        # 从数据库获取
        data_manager = DataManager()
        task = data_manager.get_trend_task(task_id)
        if task:
            trend_tasks[task_id] = task
    
    if not task:
        return jsonify({
            'status': 'error',
            'error_code': 'TASK_NOT_FOUND',
            'message': '任务不存在'
        }), 404
    
    response = {
        'status': 'success',
        'data': {
            'status': task['status'],
            'progress': task.get('progress', {}),
            'results': task.get('results', {})
        }
    }
    
    if 'error' in task:
        response['data']['error'] = task['error']
    
    return jsonify(response)


@trends_bp.route('/stop/<task_id>', methods=['POST'])
def stop_trend_collection(task_id):
    """停止趋势采集任务"""
    if task_id not in trend_tasks:
        # 尝试从数据库获取
        data_manager = DataManager()
        task = data_manager.get_trend_task(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'error_code': 'TASK_NOT_FOUND',
                'message': '任务不存在'
            }), 404
        trend_tasks[task_id] = task
    
    task = trend_tasks[task_id]
    
    # 只有运行中的任务才能停止
    if task['status'] not in ['pending', 'running']:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_STATUS',
            'message': f'任务状态为 {task["status"]}，无法停止'
        }), 400
    
    # 设置停止标志
    task['status'] = 'stopped'
    
    # 更新数据库
    data_manager = DataManager()
    data_manager.save_trend_task(
        task_id=task_id,
        keywords=task.get('keywords', []),
        platforms=task.get('platforms', []),
        timeframe=task.get('timeframe', 'today 12-m'),
        status='stopped',
        progress=task.get('progress', {})
    )
    
    return jsonify({
        'status': 'success',
        'message': '趋势采集任务已停止'
    })


@trends_bp.route('', methods=['GET'])
def get_trends():
    """获取趋势数据列表"""
    keyword = request.args.get('keyword')
    platform = request.args.get('platform')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data_manager = DataManager()
    df = data_manager.get_trend_data(
        keyword=keyword,
        platform=platform,
        start_date=start_date,
        end_date=end_date
    )
    
    if df.empty:
        return jsonify({
            'status': 'success',
            'data': {
                'trends': [],
                'total': 0
            }
        })
    
    # 转换为字典列表
    trends = df.to_dict('records')
    
    # 解析metadata
    for trend in trends:
        if trend.get('metadata'):
            try:
                import json
                trend['metadata'] = json.loads(trend['metadata'])
            except:
                pass
    
    return jsonify({
        'status': 'success',
        'data': {
            'trends': trends,
            'total': len(trends)
        }
    })


@trends_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """获取所有已采集的关键词列表"""
    data_manager = DataManager()
    keywords = data_manager.get_trend_keywords()
    
    return jsonify({
        'status': 'success',
        'data': {
            'keywords': keywords
        }
    })


@trends_bp.route('/analyze/<keyword>', methods=['GET'])
def analyze_trend(keyword):
    """分析关键词趋势"""
    try:
        platform = request.args.get('platform', 'google_trends')
        
        data_manager = DataManager()
        analyzer = TrendAnalyzer()
        
        # 获取趋势数据
        df = data_manager.get_trend_data(keyword=keyword, platform=platform)
        
        if df.empty:
            return jsonify({
                'status': 'error',
                'error_code': 'NO_DATA',
                'message': f'未找到关键词 "{keyword}" 在平台 "{platform}" 的数据'
            }), 404
        
        # 分析趋势
        try:
            analysis = analyzer.analyze_trend_growth(df, keyword, platform)
        except Exception as e:
            import traceback
            print(f"分析趋势增长失败: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error_code': 'ANALYSIS_ERROR',
                'message': f'分析趋势增长失败: {str(e)}'
            }), 500
        
        try:
            summary = analyzer.get_trend_summary(df, keyword, platform)
        except Exception as e:
            import traceback
            print(f"获取趋势摘要失败: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error_code': 'SUMMARY_ERROR',
                'message': f'获取趋势摘要失败: {str(e)}'
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': {
                'analysis': analysis,
                'summary': summary,
                'data_points': len(df)
            }
        })
    except Exception as e:
        import traceback
        print(f"分析关键词趋势失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error_code': 'INTERNAL_ERROR',
            'message': f'内部错误: {str(e)}'
        }), 500


@trends_bp.route('/compare', methods=['POST'])
def compare_keywords():
    """对比多个关键词的趋势"""
    data = request.json
    keywords = data.get('keywords', [])
    platform = data.get('platform', 'google_trends')
    
    if not keywords or len(keywords) < 2:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_PARAMETER',
            'message': '至少需要2个关键词进行对比'
        }), 400
    
    data_manager = DataManager()
    analyzer = TrendAnalyzer()
    
    # 获取所有关键词的数据
    trends_data = {}
    for keyword in keywords:
        df = data_manager.get_trend_data(keyword=keyword, platform=platform)
        if not df.empty:
            trends_data[keyword] = df
    
    if not trends_data:
        return jsonify({
            'status': 'error',
            'error_code': 'NO_DATA',
            'message': '未找到任何关键词的数据'
        }), 404
    
    # 对比分析
    comparison = analyzer.compare_keywords(trends_data, platform)
    
    return jsonify({
        'status': 'success',
        'data': {
            'comparison': comparison.to_dict('records'),
            'keywords': keywords,
            'platform': platform
        }
    })


@trends_bp.route('/hot', methods=['GET'])
def get_hot_keywords():
    """获取热门关键词（增长趋势明显的）"""
    platform = request.args.get('platform', 'google_trends')
    min_growth_rate = float(request.args.get('min_growth_rate', 10.0))  # 降低阈值，默认10%
    
    data_manager = DataManager()
    analyzer = TrendAnalyzer()
    
    # 获取所有关键词
    keywords = data_manager.get_trend_keywords()
    
    if not keywords:
        return jsonify({
            'status': 'success',
            'data': {
                'hot_keywords': [],
                'total': 0
            }
        })
    
    # 分析每个关键词
    trends_data = []
    for keyword in keywords:
        try:
            df = data_manager.get_trend_data(keyword=keyword, platform=platform)
            if not df.empty and len(df) >= 2:  # 至少需要2个数据点才能分析
                try:
                    analysis = analyzer.analyze_trend_growth(df, keyword, platform)
                    # 确保analysis包含所有必要字段
                    if analysis and 'growth_rate' in analysis:
                        trends_data.append(analysis)
                except Exception as e:
                    print(f"分析关键词 {keyword} 失败: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        except Exception as e:
            print(f"获取关键词 {keyword} 数据失败: {e}")
            continue
    
    # 识别热门关键词（增长率 >= 阈值）
    hot_keywords = analyzer.identify_hot_keywords(trends_data, min_growth_rate=min_growth_rate)
    
    # 如果热门关键词为空或太少，返回所有关键词（按增长率排序）
    # 这样可以确保用户能看到所有采集的关键词，即使增长率不高
    if len(hot_keywords) == 0 and trends_data:
        # 按增长率排序，返回前10个（包括负增长率的）
        trends_data.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        hot_keywords = trends_data[:10]
        print(f"[Hot Keywords] 没有符合阈值的关键词，返回所有关键词（按增长率排序）")
    elif len(hot_keywords) > 0 and len(hot_keywords) < len(trends_data):
        # 如果有热门关键词，但还有其他关键词，可以考虑显示更多
        # 这里保持只显示热门关键词，用户可以在"已采集关键词"中查看所有关键词
        pass
    
    return jsonify({
        'status': 'success',
        'data': {
            'hot_keywords': hot_keywords,
            'total': len(hot_keywords)
        }
    })


@trends_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """获取关键词建议（Google Trends）"""
    keyword = request.args.get('keyword')
    
    if not keyword:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_PARAMETER',
            'message': '关键词不能为空'
        }), 400
    
    scraper = TrendScraper()
    suggestions = scraper.get_google_trends_suggestions(keyword)
    
    return jsonify({
        'status': 'success',
        'data': {
            'suggestions': suggestions
        }
    })
