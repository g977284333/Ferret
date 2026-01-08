"""
翻译API
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

translate_bp = Blueprint('translate', __name__)


@translate_bp.route('/text', methods=['POST'])
def translate_text():
    """翻译文本"""
    if not HAS_TRANSLATOR:
        return jsonify({
            'status': 'error',
            'error_code': 'TRANSLATOR_NOT_AVAILABLE',
            'message': '翻译功能未安装，请运行: pip install deep-translator'
        }), 503
    
    data = request.json
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'zh-CN')  # 默认翻译成简体中文
    
    if not text:
        return jsonify({
            'status': 'error',
            'error_code': 'INVALID_PARAMETER',
            'message': '文本不能为空'
        }), 400
    
    try:
        # 使用Google翻译（免费，无需API key）
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated_text = translator.translate(text)
        
        return jsonify({
            'status': 'success',
            'data': {
                'original_text': text,
                'translated_text': translated_text,
                'source_lang': 'auto',
                'target_lang': target_lang
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_code': 'TRANSLATION_FAILED',
            'message': f'翻译失败: {str(e)}'
        }), 500
