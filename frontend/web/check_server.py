"""
检查服务器状态
"""

import requests
import sys

def check_server():
    """检查服务器是否运行"""
    url = "http://localhost:5000"
    
    print("=" * 60)
    print("检查服务器状态")
    print("=" * 60)
    print(f"\n尝试访问: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\n[OK] 服务器正在运行！")
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字节")
        print(f"\n可以在浏览器中访问: {url}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] 无法连接到服务器")
        print("可能的原因:")
        print("1. 服务器未启动 - 请运行: python app.py")
        print("2. 端口被占用 - 检查是否有其他程序使用5000端口")
        print("3. 防火墙阻止 - 检查防火墙设置")
        return False
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        return False

def check_api():
    """检查API是否正常"""
    url = "http://localhost:5000/api/v1/stats"
    
    print(f"\n尝试访问API: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] API正常")
            data = response.json()
            print(f"总机会数: {data.get('data', {}).get('total_opportunities', 0)}")
            return True
        else:
            print(f"[ERROR] API返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] API错误: {e}")
        return False

if __name__ == "__main__":
    if check_server():
        check_api()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
