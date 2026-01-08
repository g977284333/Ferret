"""
API测试脚本
测试各个API端点是否正常工作
"""

import sys
import io
import requests
import json

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000/api/v1"

def test_stats():
    """测试统计信息API"""
    print("=" * 60)
    print("测试1: 统计信息API")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            print("[OK] 统计信息API正常")
        else:
            print("[ERROR] 统计信息API异常")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")

def test_opportunities():
    """测试机会列表API"""
    print("\n" + "=" * 60)
    print("测试2: 机会列表API")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/opportunities?per_page=5")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            print("[OK] 机会列表API正常")
        else:
            print("[ERROR] 机会列表API异常")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")

def test_config():
    """测试配置API"""
    print("\n" + "=" * 60)
    print("测试3: 配置API")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            print("[OK] 配置API正常")
        else:
            print("[ERROR] 配置API异常")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")

def test_scrape_start():
    """测试启动采集API"""
    print("\n" + "=" * 60)
    print("测试4: 启动采集API")
    print("=" * 60)
    try:
        data = {
            "keywords": ["productivity"],
            "data_source": "app_store",
            "limit_per_keyword": 5
        }
        response = requests.post(
            f"{BASE_URL}/scrape/start",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            print("[OK] 启动采集API正常")
            return result.get('task_id')
        else:
            print("[ERROR] 启动采集API异常")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
    return None

def test_scrape_status(task_id):
    """测试采集状态API"""
    if not task_id:
        return
    print("\n" + "=" * 60)
    print("测试5: 采集状态API")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/scrape/status/{task_id}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if response.status_code == 200:
            print("[OK] 采集状态API正常")
        else:
            print("[ERROR] 采集状态API异常")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Ferret Web API 测试")
    print("=" * 60)
    print("\n请确保Flask应用正在运行: python app.py")
    print("等待3秒后开始测试...\n")
    
    import time
    time.sleep(3)
    
    # 测试各个API
    test_stats()
    test_opportunities()
    test_config()
    task_id = test_scrape_start()
    test_scrape_status(task_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
