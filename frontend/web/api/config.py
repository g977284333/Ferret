"""
配置管理API
"""

import yaml
from pathlib import Path
from flask import Blueprint, request, jsonify

config_bp = Blueprint('config', __name__)

# 配置文件路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "backend" / "config" / "config.yaml"


@config_bp.route('', methods=['GET'])
def get_config():
    """获取配置"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return jsonify({
            'status': 'success',
            'data': config
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_code': 'INTERNAL_ERROR',
            'message': str(e)
        }), 500


@config_bp.route('', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.json
        
        # 读取现有配置
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新配置
        if 'scoring' in data:
            config['scoring'] = data['scoring']
        if 'data_sources' in data:
            config['data_sources'] = data['data_sources']
        
        # 保存配置
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        return jsonify({
            'status': 'success',
            'message': '配置已更新'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_code': 'INTERNAL_ERROR',
            'message': str(e)
        }), 500
