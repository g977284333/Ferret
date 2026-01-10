#!/usr/bin/env python3
"""
检查依赖是否安装
"""

import sys
import os

# 避免某些导入导致崩溃
os.environ['PYTHONUNBUFFERED'] = '1'

def check_dependency(module_name, package_name=None):
    """检查依赖是否安装"""
    if package_name is None:
        package_name = module_name
    
    try:
        # 使用更安全的导入方式
        import importlib
        importlib.import_module(module_name)
        print(f"✓ {package_name} 已安装")
        return True
    except (ImportError, Exception) as e:
        print(f"✗ {package_name} 未安装")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("检查依赖安装状态")
    print("=" * 50)
    print()
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('pytrends', 'pytrends'),
        ('deep_translator', 'deep-translator'),
    ]
    
    all_ok = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_ok = False
    
    print()
    print("=" * 50)
    if all_ok:
        print("✓ 所有依赖已安装，可以启动服务器")
        print()
        print("启动命令:")
        print("  cd /Users/chen/WorkSpace/gechen/Ferret/frontend/web")
        print("  python3 app.py")
    else:
        print("✗ 有依赖未安装，请先安装依赖")
        print()
        print("安装命令:")
        print("  cd /Users/chen/WorkSpace/gechen/Ferret")
        print("  pip3 install -r requirements.txt")
        print("  cd frontend/web")
        print("  pip3 install -r requirements.txt")
    print("=" * 50)

if __name__ == '__main__':
    main()
