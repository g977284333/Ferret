#!/usr/bin/env python3
"""
最小化测试应用 - 用于诊断403错误
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World!</h1><p>如果你看到这个，说明Flask正常工作</p>'

@app.route('/test')
def test():
    return {'status': 'ok', 'message': '测试成功'}

@app.route('/hello')
def hello():
    return '<h1>Hello!</h1>'

if __name__ == '__main__':
    print("=" * 50)
    print("最小化测试服务器")
    print("=" * 50)
    print("访问: http://localhost:5002")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5002)
