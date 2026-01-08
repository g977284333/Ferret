"""
下载前端资源到本地
避免CDN延迟，提升加载速度
"""

import requests
import os
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static" / "vendor"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

RESOURCES = {
    'jquery': {
        'url': 'https://unpkg.com/jquery@3.7.1/dist/jquery.min.js',
        'path': 'jquery.min.js'
    },
    'flowbite_css': {
        'url': 'https://fastly.jsdelivr.net/npm/flowbite@2.2.1/dist/flowbite.min.css',
        'path': 'flowbite.min.css'
    },
    'flowbite_js': {
        'url': 'https://fastly.jsdelivr.net/npm/flowbite@2.2.1/dist/flowbite.min.js',
        'path': 'flowbite.min.js'
    }
}

def download_resource(name, url, filepath):
    """下载资源"""
    print(f"下载 {name}...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            full_path = STATIC_DIR / filepath
            full_path.write_bytes(response.content)
            size = len(response.content)
            print(f"  [OK] 已保存到 {filepath} ({size:,} 字节)")
            return True
        else:
            print(f"  [ERROR] 下载失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] 下载失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("下载前端资源到本地")
    print("=" * 60)
    print(f"\n保存目录: {STATIC_DIR}")
    print("\n开始下载...\n")
    
    results = []
    for name, info in RESOURCES.items():
        success = download_resource(name, info['url'], info['path'])
        results.append((name, success))
    
    print("\n" + "=" * 60)
    print("下载完成")
    print("=" * 60)
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n所有资源已下载！")
        print("下一步：更新base.html使用本地资源")
    else:
        print("\n部分资源下载失败，请检查网络连接")

if __name__ == "__main__":
    main()
