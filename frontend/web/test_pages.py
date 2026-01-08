"""
页面功能测试脚本
测试所有页面的可访问性和基本功能
"""

import sys
import io
import requests
import time

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000"

def test_page(url, name):
    """测试页面可访问性"""
    print(f"\n测试: {name}")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] 页面可访问 (状态码: {response.status_code})")
            print(f"     响应大小: {len(response.text)} 字节")
            return True
        else:
            print(f"[ERROR] 页面返回错误状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 无法连接到服务器")
        print(f"       请确保Flask应用正在运行: python app.py")
        return False
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return False

def test_api_endpoint(url, name, method='GET', data=None):
    """测试API端点"""
    print(f"\n测试: {name}")
    print(f"URL: {url}")
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] API正常 (状态码: {response.status_code})")
            if 'data' in result:
                print(f"     返回数据: {len(str(result['data']))} 字符")
            return True
        else:
            print(f"[ERROR] API返回错误状态码: {response.status_code}")
            try:
                error = response.json()
                print(f"     错误信息: {error.get('message', '未知错误')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 70)
    print("Ferret Web 页面功能测试")
    print("=" * 70)
    print("\n请确保Flask应用正在运行: python app.py")
    print("等待3秒后开始测试...\n")
    
    time.sleep(3)
    
    results = []
    
    # 测试页面
    print("\n" + "=" * 70)
    print("页面可访问性测试")
    print("=" * 70)
    
    pages = [
        ('/', '首页'),
        ('/scrape', '数据采集页面'),
        ('/opportunities', '机会列表页面'),
        ('/config', '配置页面'),
    ]
    
    for url, name in pages:
        result = test_page(BASE_URL + url, name)
        results.append(('页面', name, result))
    
    # 测试API
    print("\n" + "=" * 70)
    print("API端点测试")
    print("=" * 70)
    
    apis = [
        ('/api/v1/stats', '统计信息API'),
        ('/api/v1/opportunities?per_page=5', '机会列表API'),
        ('/api/v1/config', '配置API'),
    ]
    
    for url, name in apis:
        result = test_api_endpoint(BASE_URL + url, name)
        results.append(('API', name, result))
    
    # 测试详情页面（需要有效的app_id）
    print("\n" + "=" * 70)
    print("详情页面测试")
    print("=" * 70)
    
    # 先获取一个机会的ID
    try:
        response = requests.get(BASE_URL + '/api/v1/opportunities?per_page=1', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data', {}).get('opportunities'):
                app_id = data['data']['opportunities'][0].get('app_id')
                if app_id:
                    result = test_page(BASE_URL + f'/opportunities/{app_id}', f'机会详情页面 (ID: {app_id})')
                    results.append(('页面', '机会详情页面', result))
                else:
                    print("[SKIP] 没有可用的机会ID进行测试")
            else:
                print("[SKIP] 没有机会数据")
        else:
            print("[SKIP] 无法获取机会数据")
    except Exception as e:
        print(f"[SKIP] 无法测试详情页面: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for _, _, result in results if result)
    failed = total - passed
    
    print(f"\n总计: {total} 项")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    
    if failed > 0:
        print("\n失败的测试:")
        for category, name, result in results:
            if not result:
                print(f"  - {category}: {name}")
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("[SUCCESS] 所有测试通过！")
    else:
        print("[WARNING] 部分测试失败，请检查上述错误信息")
    print("=" * 70)

if __name__ == "__main__":
    main()
