#!/usr/bin/env python3
"""
测试服务器是否正常运行
"""

import requests
import sys

def test_server():
    """测试服务器"""
    base_url = "http://localhost:5000"
    
    print("=" * 50)
    print("测试Ferret服务器")
    print("=" * 50)
    print()
    
    # 测试1: 测试路由
    print("1. 测试 /test 路由...")
    try:
        response = requests.get(f"{base_url}/test", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        if response.status_code == 200:
            print("   ✓ 测试路由正常")
        else:
            print(f"   ✗ 测试路由返回错误: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return False
    
    print()
    
    # 测试2: 首页
    print("2. 测试首页 / ...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ 首页正常")
        else:
            print(f"   ✗ 首页返回错误: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    print()
    
    # 测试3: API路由
    print("3. 测试API路由 /api/v1/stats ...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats", timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ API路由正常")
        else:
            print(f"   ✗ API路由返回错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    print()
    print("=" * 50)
    print("测试完成")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_server()
