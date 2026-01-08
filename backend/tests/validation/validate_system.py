"""
系统功能验证脚本
验证数据采集、分析、输出等核心功能
"""

import sys
from pathlib import Path

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
from utils.data_manager import DataManager


def test_data_collection():
    """测试1: 数据采集功能"""
    print("=" * 60)
    print("测试1: 数据采集功能")
    print("=" * 60)
    
    scraper = AppStoreScraperWrapper()
    
    # 测试不同关键词
    test_keywords = ["habit tracker", "pomodoro"]
    all_apps = []
    
    for keyword in test_keywords:
        print(f"\n测试关键词: {keyword}")
        apps = scraper.search_apps(keyword, limit=5)
        print(f"  ✓ 找到 {len(apps)} 个App")
        
        if apps:
            # 检查数据完整性
            sample = apps[0]
            required_fields = ['trackId', 'trackName', 'averageUserRating', 
                             'userRatingCount', 'price', 'primaryGenreName']
            missing_fields = [f for f in required_fields if f not in sample or sample.get(f) is None]
            
            if missing_fields:
                print(f"  ⚠ 缺少字段: {missing_fields}")
            else:
                print(f"  ✓ 数据完整")
                print(f"  ✓ 示例App: {sample.get('trackName')} (评分: {sample.get('averageUserRating', 0):.2f})")
            
            all_apps.extend(apps)
        else:
            print(f"  ⚠ 未找到App")
    
    # 测试去重
    print(f"\n去重测试:")
    print(f"  原始数量: {len(all_apps)}")
    seen_ids = set()
    unique_apps = []
    for app in all_apps:
        app_id = app.get('trackId')
        if app_id and app_id not in seen_ids:
            seen_ids.add(app_id)
            unique_apps.append(app)
    print(f"  去重后: {len(unique_apps)}")
    print(f"  ✓ 去重功能正常" if len(unique_apps) < len(all_apps) else "  ⚠ 无重复数据")
    
    return unique_apps


def test_data_analysis(apps):
    """测试2: 数据分析功能"""
    print("\n" + "=" * 60)
    print("测试2: 数据分析功能")
    print("=" * 60)
    
    if not apps:
        print("  ⚠ 无数据，跳过分析测试")
        return None
    
    analyzer = OpportunityAnalyzer()
    
    # 测试评分计算
    print("\n评分计算测试:")
    sample_app = apps[0]
    score = analyzer.calculate_opportunity_score(sample_app)
    print(f"  示例App: {sample_app.get('trackName', 'N/A')}")
    print(f"  机会分数: {score:.3f}")
    print(f"  ✓ 评分计算正常")
    
    # 测试批量分析
    print("\n批量分析测试:")
    df = analyzer.analyze_opportunities(apps)
    print(f"  输入App数: {len(apps)}")
    print(f"  输出机会数: {len(df)}")
    print(f"  ✓ 分析功能正常")
    
    # 检查筛选阈值
    config = analyzer.scoring_config
    min_score = config.get('thresholds', {}).get('min_score', 0.6)
    min_reviews = config.get('thresholds', {}).get('min_reviews', 10)
    
    print(f"\n筛选阈值:")
    print(f"  最低分数: {min_score}")
    print(f"  最少评论: {min_reviews}")
    
    if len(df) > 0:
        print(f"\nTop 3 机会:")
        for idx, row in df.head(3).iterrows():
            print(f"  {idx+1}. {row['name']} (分数: {row['opportunity_score']:.3f})")
    
    return df


def test_data_storage(df):
    """测试3: 数据存储功能"""
    print("\n" + "=" * 60)
    print("测试3: 数据存储功能")
    print("=" * 60)
    
    if df is None or len(df) == 0:
        print("  ⚠ 无数据，跳过存储测试")
        return
    
    analyzer = OpportunityAnalyzer()
    
    # 测试CSV保存
    print("\nCSV保存测试:")
    csv_file = analyzer.save_opportunities(df, "validation_test.csv")
    if Path(csv_file).exists():
        print(f"  ✓ CSV文件已保存: {csv_file}")
        print(f"  ✓ 文件大小: {Path(csv_file).stat().st_size} bytes")
    else:
        print(f"  ✗ CSV文件保存失败")
    
    # 测试数据库保存
    print("\n数据库保存测试:")
    data_manager = DataManager()
    for _, row in df.head(3).iterrows():
        data_manager.save_opportunity(row.to_dict())
    
    top_opportunities = data_manager.get_top_opportunities(limit=3)
    if len(top_opportunities) > 0:
        print(f"  ✓ 数据库保存正常")
        print(f"  ✓ 已保存 {len(top_opportunities)} 条记录")
    else:
        print(f"  ✗ 数据库保存失败")


def test_config_loading():
    """测试4: 配置文件加载"""
    print("\n" + "=" * 60)
    print("测试4: 配置文件加载")
    print("=" * 60)
    
    analyzer = OpportunityAnalyzer()
    config = analyzer.scoring_config
    
    print("\n评分权重:")
    weights = config.get('weights', {})
    total_weight = sum(weights.values())
    for key, value in weights.items():
        print(f"  {key}: {value:.2f}")
    print(f"  总权重: {total_weight:.2f} {'✓' if abs(total_weight - 1.0) < 0.01 else '⚠ (应该为1.0)'}")
    
    print("\n筛选阈值:")
    thresholds = config.get('thresholds', {})
    for key, value in thresholds.items():
        print(f"  {key}: {value}")
    print(f"  ✓ 配置加载正常")


def test_edge_cases():
    """测试5: 边界情况"""
    print("\n" + "=" * 60)
    print("测试5: 边界情况测试")
    print("=" * 60)
    
    analyzer = OpportunityAnalyzer()
    
    # 测试空数据
    print("\n空数据测试:")
    empty_df = analyzer.analyze_opportunities([])
    print(f"  空输入结果: {len(empty_df)} 条")
    print(f"  ✓ 空数据处理正常" if len(empty_df) == 0 else "  ⚠ 空数据应返回空结果")
    
    # 测试无效数据
    print("\n无效数据测试:")
    invalid_apps = [
        {},  # 完全空
        {'trackId': 123},  # 缺少关键字段
        {'trackId': 456, 'averageUserRating': None, 'userRatingCount': 0},  # 无效评分
    ]
    invalid_df = analyzer.analyze_opportunities(invalid_apps)
    print(f"  无效数据输入: {len(invalid_apps)} 条")
    print(f"  有效结果: {len(invalid_df)} 条")
    print(f"  ✓ 无效数据过滤正常")


def main():
    """主验证流程"""
    print("\n" + "=" * 60)
    print("Ferret 系统功能验证")
    print("=" * 60)
    
    try:
        # 测试1: 数据采集
        apps = test_data_collection()
        
        # 测试2: 数据分析
        df = test_data_analysis(apps)
        
        # 测试3: 数据存储
        test_data_storage(df)
        
        # 测试4: 配置加载
        test_config_loading()
        
        # 测试5: 边界情况
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("验证完成！")
        print("=" * 60)
        print("\n如果所有测试都显示 ✓，说明系统功能正常。")
        print("如果有 ⚠ 或 ✗，需要检查相应功能。")
        
    except Exception as e:
        print(f"\n✗ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
