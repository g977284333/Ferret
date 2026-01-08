"""
App Store数据采集脚本
优先使用现成的开源工具：itunes-app-scraper
如果现成工具不满足需求，再考虑自己实现
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from itunes_app_scraper.scraper import AppStoreScraper
    HAS_SCRAPER = True
except ImportError:
    HAS_SCRAPER = False
    print("警告: itunes-app-scraper未安装，请运行: pip install itunes-app-scraper")

import requests
from tqdm import tqdm

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class AppStoreScraperWrapper:
    """App Store爬虫包装类"""
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: 请求间隔（秒），避免被封
        """
        self.delay = delay
        self.scraper = AppStoreScraper() if HAS_SCRAPER else None
        # 获取项目根目录
        # __file__ = backend/src/scrapers/app_store_scraper.py
        # parent.parent.parent.parent = 项目根目录
        PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
        self.data_dir = PROJECT_ROOT / "data" / "raw" / "app_store"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def search_apps(self, keyword: str, country: str = "us", limit: int = 50) -> List[Dict]:
        """
        搜索App
        
        Args:
            keyword: 搜索关键词
            country: 国家代码
            limit: 返回数量限制
            
        Returns:
            App列表
        """
        if not self.scraper:
            print("错误: itunes-app-scraper未安装")
            return []
        
        try:
            # 使用现成的工具搜索
            app_ids = self.scraper.get_app_ids_for_query(keyword, country=country)
            app_ids = app_ids[:limit]
            
            apps = []
            for app_id in tqdm(app_ids, desc=f"获取App详情: {keyword}"):
                try:
                    # 获取App详情
                    app_details = self.scraper.get_app_details(app_id, country=country)
                    if app_details:
                        apps.append(app_details)
                    time.sleep(self.delay)
                except Exception as e:
                    print(f"获取App {app_id} 详情失败: {e}")
                    continue
            
            return apps
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_category_top_apps(self, category: str, country: str = "us", limit: int = 100) -> List[Dict]:
        """
        获取分类Top Apps
        
        注意：itunes-app-scraper可能不支持直接获取分类，需要自己实现
        """
        # TODO: 如果现成工具不支持，需要自己实现
        # 可以使用App Store的RSS feed或网页爬虫
        print(f"获取分类 {category} 的Top Apps（待实现）")
        return []
    
    def save_apps(self, apps: List[Dict], filename: Optional[str] = None):
        """保存App数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"app_store_{timestamp}.json"
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(apps)} 个App数据到: {filepath}")
        return filepath


def main():
    """测试脚本"""
    scraper = AppStoreScraperWrapper()
    
    # 测试搜索
    print("测试搜索功能...")
    apps = scraper.search_apps("productivity", limit=10)
    print(f"找到 {len(apps)} 个App")
    
    if apps:
        scraper.save_apps(apps)
        print(f"\n示例App (前3个字段):")
        # 只显示关键字段，避免编码问题
        sample = apps[0]
        key_fields = ['trackId', 'trackName', 'averageUserRating', 'userRatingCount', 
                     'price', 'primaryGenreName', 'trackViewUrl']
        sample_summary = {k: sample.get(k, 'N/A') for k in key_fields if k in sample}
        print(json.dumps(sample_summary, indent=2, ensure_ascii=False))
        print(f"\n完整数据已保存到文件，共 {len(apps)} 个App")


if __name__ == "__main__":
    main()
