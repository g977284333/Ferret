"""
机会管理API
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify
import pandas as pd

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from utils.data_manager import DataManager

opportunities_bp = Blueprint('opportunities', __name__)
data_manager = DataManager()


@opportunities_bp.route('', methods=['GET'])
def get_opportunities():
    """获取机会列表"""
    # 获取查询参数
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sort_by = request.args.get('sort_by', 'opportunity_score')
    order = request.args.get('order', 'desc')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)
    category = request.args.get('category')
    search = request.args.get('search')
    
    # 从数据库获取数据
    opportunities = data_manager.get_opportunities()
    
    if not opportunities:
        return jsonify({
            'status': 'success',
            'data': {
                'opportunities': [],
                'pagination': {
                    'page': 1,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0
                }
            }
        })
    
    # 转换为DataFrame便于处理
    df = pd.DataFrame(opportunities)
    
    # 筛选
    if min_score is not None:
        df = df[df['opportunity_score'] >= min_score]
    if max_score is not None:
        df = df[df['opportunity_score'] <= max_score]
    if category:
        df = df[df['category'] == category]
    if search:
        df = df[df['name'].str.contains(search, case=False, na=False)]
    
    # 排序
    ascending = (order == 'asc')
    df = df.sort_values(sort_by, ascending=ascending)
    
    # 分页
    total = len(df)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    df_page = df.iloc[start:end]
    
    # 转换为字典列表
    opportunities_list = df_page.to_dict('records')
    
    return jsonify({
        'status': 'success',
        'data': {
            'opportunities': opportunities_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages
            }
        }
    })


@opportunities_bp.route('/<app_id>', methods=['GET'])
def get_opportunity_detail(app_id):
    """获取机会详情"""
    opportunity = data_manager.get_opportunity_by_id(str(app_id))
    
    if not opportunity:
        return jsonify({
            'status': 'error',
            'error_code': 'NOT_FOUND',
            'message': '机会不存在'
        }), 404
    
    # 从原始数据表获取完整信息
    import sqlite3
    import json
    from pathlib import Path
    
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    db_path = PROJECT_ROOT / "data" / "opportunities.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 获取最新的原始数据（可能有多个版本）
    cursor.execute('SELECT data FROM raw_apps WHERE app_id = ? ORDER BY created_at DESC LIMIT 1', (str(app_id),))
    row = cursor.fetchone()
    conn.close()
    
    # 合并原始数据
    if row:
        try:
            raw_data = json.loads(row[0])
            # 添加更多字段
            opportunity['description'] = raw_data.get('description', '')
            opportunity['release_date'] = raw_data.get('releaseDate', '')
            opportunity['current_version'] = raw_data.get('version', '')
            opportunity['current_version_date'] = raw_data.get('currentVersionReleaseDate', '')
            opportunity['seller_name'] = raw_data.get('sellerName', '')
            opportunity['file_size'] = raw_data.get('fileSizeBytes', 0)
            opportunity['content_advisory_rating'] = raw_data.get('contentAdvisoryRating', '')
            opportunity['language_codes'] = raw_data.get('languageCodesISO2A', [])
            # 处理截图URLs - 可能是字符串（逗号分隔）或列表
            screenshot_urls = raw_data.get('screenshotUrls', [])
            if isinstance(screenshot_urls, str):
                # 如果是字符串，可能是逗号分隔的URL列表
                if ',' in screenshot_urls:
                    screenshot_urls = [url.strip() for url in screenshot_urls.split(',') if url.strip()]
                else:
                    # 单个URL
                    screenshot_urls = [screenshot_urls] if screenshot_urls else []
            elif not isinstance(screenshot_urls, list):
                screenshot_urls = []
            opportunity['screenshot_urls'] = screenshot_urls[:5]  # 最多5张
            
            opportunity['artwork_url'] = raw_data.get('artworkUrl512', '') or raw_data.get('artworkUrl100', '')
            opportunity['current_version_rating'] = raw_data.get('averageUserRatingForCurrentVersion', 0)
            opportunity['current_version_reviews'] = raw_data.get('userRatingCountForCurrentVersion', 0)
            opportunity['minimum_os_version'] = raw_data.get('minimumOsVersion', '')
            opportunity['supported_devices'] = raw_data.get('supportedDevices', [])
            opportunity['is_game_center_enabled'] = raw_data.get('isGameCenterEnabled', False)
            opportunity['bundle_id'] = raw_data.get('bundleId', '')
        except Exception as e:
            print(f"解析原始数据失败: {e}")
    
    # 计算评分详情（需要从analyzer获取）
    # 这里简化处理，实际应该调用analyzer
    scoring_details = {
        'market_size': 1.0,
        'competition': 1.0,
        'user_satisfaction': 1.0,
        'growth_trend': 1.0,
        'monetization': 0.5
    }
    
    opportunity['scoring_details'] = scoring_details
    
    return jsonify({
        'status': 'success',
        'data': opportunity
    })


@opportunities_bp.route('/export', methods=['GET'])
def export_opportunities():
    """导出机会数据"""
    from flask import Response
    
    # 获取查询参数
    format_type = request.args.get('format', 'csv')
    app_id = request.args.get('app_id')
    
    # 获取数据
    if app_id:
        # 导出单个机会
        opportunity = data_manager.get_opportunity_by_id(str(app_id))
        if not opportunity:
            return jsonify({
                'status': 'error',
                'error_code': 'NOT_FOUND',
                'message': '机会不存在'
            }), 404
        opportunities = [opportunity]
    else:
        # 导出所有机会（应用筛选条件）
        opportunities = data_manager.get_opportunities()
        
        # 应用筛选（简化版）
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        category = request.args.get('category')
        search = request.args.get('search')
        
        df = pd.DataFrame(opportunities)
        
        if min_score is not None:
            df = df[df['opportunity_score'] >= min_score]
        if max_score is not None:
            df = df[df['opportunity_score'] <= max_score]
        if category:
            df = df[df['category'] == category]
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        
        opportunities = df.to_dict('records')
    
    if format_type == 'csv':
        # 导出CSV
        if not opportunities:
            return jsonify({
                'status': 'error',
                'message': '没有数据可导出'
            }), 400
        
        df = pd.DataFrame(opportunities)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        
        return Response(
            csv,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=opportunities.csv'
            }
        )
    else:
        # 导出JSON
        return jsonify({
            'status': 'success',
            'data': opportunities
        })
