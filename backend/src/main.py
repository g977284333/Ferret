"""
主程序 - 完整的工作流程
1. 数据采集 → 2. 数据分析 → 3. 机会评分 → 4. 输出结果
"""

from pathlib import Path
import sys

# 添加backend/src到路径
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
from utils.data_manager import DataManager


def main():
    """主流程"""
    print("=" * 50)
    print("Ferret - 机会发现工具")
    print("=" * 50)
    
    # 1. 数据采集
    print("\n[1/3] 数据采集...")
    scraper = AppStoreScraperWrapper()
    
    # 搜索关键词（可以根据需要修改）
    keywords = ["productivity", "task management", "note taking"]
    
    all_apps = []
    seen_app_ids = set()  # 用于去重
    
    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")
        apps = scraper.search_apps(keyword, limit=20)
        
        # 去重：基于trackId
        for app in apps:
            app_id = app.get('trackId')
            if app_id and app_id not in seen_app_ids:
                seen_app_ids.add(app_id)
                all_apps.append(app)
        
        print(f"找到 {len(apps)} 个App，新增 {len([a for a in apps if a.get('trackId') not in seen_app_ids])} 个")
    
    if not all_apps:
        print("未找到任何App，请检查网络连接或工具安装")
        return
    
    # 保存原始数据
    data_file = scraper.save_apps(all_apps)
    print(f"\n共采集 {len(all_apps)} 个App（已去重）")
    
    # 2. 数据分析
    print("\n[2/3] 数据分析...")
    analyzer = OpportunityAnalyzer()
    df = analyzer.analyze_opportunities(all_apps)
    
    # 3. 保存结果
    print("\n[3/3] 保存结果...")
    opportunity_file = analyzer.save_opportunities(df)
    
    # 保存到数据库
    data_manager = DataManager()
    for _, row in df.iterrows():
        data_manager.save_opportunity(row.to_dict())
    
    # 4. 输出Top机会
    print("\n" + "=" * 50)
    print("Top 10 机会:")
    print("=" * 50)
    
    # 格式化输出
    top_10 = df.head(10)
    for idx, row in top_10.iterrows():
        print(f"\n{idx+1}. {row['name']}")
        print(f"   评分: {row['rating']:.2f} | 评论数: {row['review_count']:,} | 机会分数: {row['opportunity_score']:.3f}")
        print(f"   分类: {row['category']} | 价格: ${row['price']:.2f}")
        print(f"   链接: {row['url']}")
    
    print(f"\n完整结果已保存到: {opportunity_file}")
    print(f"共发现 {len(df)} 个潜在机会")
    print("\n下一步: 选择Top机会，快速开发MVP验证！")


if __name__ == "__main__":
    main()
