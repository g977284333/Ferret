"""
统计信息API
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify
import pandas as pd

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from utils.data_manager import DataManager

stats_bp = Blueprint('stats', __name__)
data_manager = DataManager()


@stats_bp.route('', methods=['GET'])
def get_stats():
    """获取统计信息"""
    opportunities = data_manager.get_opportunities()
    
    total_opportunities = len(opportunities) if opportunities else 0
    
    # 计算分类统计
    top_categories = []
    if opportunities:
        df = pd.DataFrame(opportunities)
        category_counts = df['category'].value_counts().head(5)
        top_categories = [
            {'category': cat, 'count': int(count)}
            for cat, count in category_counts.items()
        ]
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_opportunities': total_opportunities,
            'today_collected': 0,  # 需要从数据库查询
            'active_tasks': 0,  # 需要从任务管理器获取
            'top_categories': top_categories
        }
    })
