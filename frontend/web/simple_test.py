#!/usr/bin/env python3
"""
最简单的Flask测试应用
用于诊断403错误
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World!</h1><p>如果你看到这个，说明Flask正常工作</p>'

@app.route('/test')
def test():
    return {'status': 'ok', 'message': '测试成功'}

if __name__ == '__main__':
    print("=" * 50)
    print("简单测试服务器")
    print("=" * 50)
    print("访问: http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)
