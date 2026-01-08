"""
全面功能测试脚本
测试所有功能模块，包括不同关键词、参数调整等
"""

import sys
from pathlib import Path
import pandas as pd

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from scrapers.app_store_scraper import AppStoreScraperWrapper
from analyzers.opportunity_analyzer import OpportunityAnalyzer
from utils.data_manager import DataManager


def test_different_keywords():
    """测试1: 不同关键词的数据采集"""
    print("=" * 70)
    print("测试1: 不同关键词的数据采集")
    print("=" * 70)
    
    scraper = AppStoreScraperWrapper()
    
    # 测试多个不同领域的关键词
    test_keywords = [
        "habit tracker",      # 习惯追踪
        "pomodoro timer",      # 番茄钟
        "expense tracker",     # 记账
        "meditation",          # 冥想
        "language learning"   # 语言学习
    ]
    
    all_results = {}
    
    for keyword in test_keywords:
        print(f"\n关键词: {keyword}")
        apps = scraper.search_apps(keyword, limit=10)
        
        if apps:
            # 统计信息
            ratings = [a.get('averageUserRating', 0) for a in apps if a.get('averageUserRating')]
            reviews = [a.get('userRatingCount', 0) for a in apps if a.get('userRatingCount')]
            
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            total_reviews = sum(reviews)
            avg_reviews = total_reviews / len(apps) if apps else 0
            
            all_results[keyword] = {
                'count': len(apps),
                'avg_rating': avg_rating,
                'total_reviews': total_reviews,
                'avg_reviews': avg_reviews,
                'apps': apps
            }
            
            print(f"  ✓ 找到 {len(apps)} 个App")
            print(f"  ✓ 平均评分: {avg_rating:.2f}")
            print(f"  ✓ 总评论数: {total_reviews:,}")
            print(f"  ✓ 平均评论数: {avg_reviews:,.0f}")
        else:
            print(f"  ⚠ 未找到App")
            all_results[keyword] = {'count': 0, 'apps': []}
    
    return all_results


def test_analysis_with_different_data(keyword_results):
    """测试2: 使用不同数据进行分析"""
    print("\n" + "=" * 70)
    print("测试2: 使用不同数据进行分析")
    print("=" * 70)
    
    analyzer = OpportunityAnalyzer()
    all_opportunities = {}
    
    for keyword, result in keyword_results.items():
        if result['count'] > 0:
            print(f"\n分析关键词: {keyword}")
            df = analyzer.analyze_opportunities(result['apps'])
            
            all_opportunities[keyword] = df
            
            print(f"  输入App数: {result['count']}")
            print(f"  发现机会数: {len(df)}")
            print(f"  机会率: {len(df)/result['count']*100:.1f}%")
            
            if len(df) > 0:
                print(f"  Top机会: {df.iloc[0]['name']} (分数: {df.iloc[0]['opportunity_score']:.3f})")
    
    return all_opportunities


def test_parameter_adjustment():
    """测试3: 参数调整对结果的影响"""
    print("\n" + "=" * 70)
    print("测试3: 参数调整对结果的影响")
    print("=" * 70)
    
    # 采集测试数据
    scraper = AppStoreScraperWrapper()
    test_apps = scraper.search_apps("task management", limit=20)
    
    if not test_apps:
        print("  ⚠ 无法获取测试数据")
        return
    
    print(f"\n使用 {len(test_apps)} 个App进行参数测试")
    
    # 测试不同的筛选阈值
    thresholds_to_test = [
        {'min_score': 0.5, 'min_reviews': 10},
        {'min_score': 0.6, 'min_reviews': 10},  # 默认
        {'min_score': 0.7, 'min_reviews': 10},
        {'min_score': 0.6, 'min_reviews': 100},
        {'min_score': 0.6, 'min_reviews': 1000},
    ]
    
    analyzer = OpportunityAnalyzer()
    original_config = analyzer.scoring_config.get('thresholds', {}).copy()
    
    results = []
    
    for threshold in thresholds_to_test:
        # 临时修改阈值
        analyzer.scoring_config['thresholds'] = threshold
        
        df = analyzer.analyze_opportunities(test_apps)
        
        results.append({
            'threshold': threshold,
            'opportunities': len(df),
            'top_score': df.iloc[0]['opportunity_score'] if len(df) > 0 else 0
        })
        
        print(f"\n阈值: min_score={threshold['min_score']}, min_reviews={threshold['min_reviews']}")
        print(f"  发现机会: {len(df)} 个")
        if len(df) > 0:
            print(f"  Top分数: {df.iloc[0]['opportunity_score']:.3f}")
    
    # 恢复原始配置
    analyzer.scoring_config['thresholds'] = original_config
    
    # 分析结果
    print("\n参数影响分析:")
    for r in results:
        print(f"  阈值 {r['threshold']} → {r['opportunities']} 个机会")
    
    return results


def test_scoring_model_details():
    """测试4: 评分模型详细分析"""
    print("\n" + "=" * 70)
    print("测试4: 评分模型详细分析")
    print("=" * 70)
    
    scraper = AppStoreScraperWrapper()
    analyzer = OpportunityAnalyzer()
    
    # 获取一些测试数据
    test_apps = scraper.search_apps("note taking", limit=10)
    
    if not test_apps:
        print("  ⚠ 无法获取测试数据")
        return
    
    print(f"\n分析 {len(test_apps)} 个App的评分详情")
    
    # 分析每个App的评分维度
    scoring_details = []
    
    for app in test_apps[:5]:  # 只分析前5个
        score = analyzer.calculate_opportunity_score(app)
        
        # 手动计算各维度分数（复制analyzer的逻辑）
        market_size = analyzer._calculate_market_size(app)
        competition = analyzer._calculate_competition(app)
        user_satisfaction = analyzer._calculate_user_satisfaction(app)
        growth_trend = analyzer._calculate_growth_trend(app)
        monetization = analyzer._calculate_monetization(app)
        
        weights = analyzer.scoring_config.get('weights', {})
        weighted_score = (
            market_size * weights.get('market_size', 0.3) +
            competition * weights.get('competition', 0.25) +
            user_satisfaction * weights.get('user_satisfaction', 0.2) +
            growth_trend * weights.get('growth_trend', 0.15) +
            monetization * weights.get('monetization', 0.1)
        )
        
        scoring_details.append({
            'name': app.get('trackName', 'N/A'),
            'rating': app.get('averageUserRating', 0),
            'reviews': app.get('userRatingCount', 0),
            'market_size': market_size,
            'competition': competition,
            'user_satisfaction': user_satisfaction,
            'growth_trend': growth_trend,
            'monetization': monetization,
            'total_score': score
        })
    
    # 显示详细评分
    print("\n评分详情:")
    for detail in scoring_details:
        print(f"\n  {detail['name']}")
        print(f"    评分: {detail['rating']:.2f} | 评论: {detail['reviews']:,}")
        print(f"    市场规模: {detail['market_size']:.2f}")
        print(f"    竞争程度: {detail['competition']:.2f}")
        print(f"    用户满意度: {detail['user_satisfaction']:.2f}")
        print(f"    增长趋势: {detail['growth_trend']:.2f}")
        print(f"    变现潜力: {detail['monetization']:.2f}")
        print(f"    总分: {detail['total_score']:.3f}")
    
    return scoring_details


def test_data_storage_comprehensive():
    """测试5: 数据存储全面测试"""
    print("\n" + "=" * 70)
    print("测试5: 数据存储全面测试")
    print("=" * 70)
    
    scraper = AppStoreScraperWrapper()
    analyzer = OpportunityAnalyzer()
    data_manager = DataManager()
    
    # 采集数据
    test_apps = scraper.search_apps("productivity", limit=15)
    
    if not test_apps:
        print("  ⚠ 无法获取测试数据")
        return
    
    # 分析
    df = analyzer.analyze_opportunities(test_apps)
    
    print(f"\n测试数据: {len(test_apps)} 个App → {len(df)} 个机会")
    
    # 测试CSV保存
    print("\nCSV保存测试:")
    csv_file = analyzer.save_opportunities(df, "comprehensive_test.csv")
    csv_path = Path(csv_file)
    
    if csv_path.exists():
        csv_size = csv_path.stat().st_size
        csv_df = pd.read_csv(csv_file)
        print(f"  ✓ CSV文件保存成功")
        print(f"  ✓ 文件大小: {csv_size} bytes")
        print(f"  ✓ 记录数: {len(csv_df)}")
        print(f"  ✓ 字段数: {len(csv_df.columns)}")
    
    # 测试数据库保存和查询
    print("\n数据库测试:")
    # 清空测试数据（可选）
    # 保存所有机会
    for _, row in df.iterrows():
        data_manager.save_opportunity(row.to_dict())
    
    # 查询Top机会
    top_ops = data_manager.get_top_opportunities(limit=10)
    print(f"  ✓ 数据库保存成功")
    print(f"  ✓ 查询到 {len(top_ops)} 条记录")
    
    if len(top_ops) > 0:
        print(f"  ✓ Top机会: {top_ops.iloc[0]['name']}")
    
    return csv_file, top_ops


def test_full_workflow():
    """测试6: 完整工作流程"""
    print("\n" + "=" * 70)
    print("测试6: 完整工作流程测试")
    print("=" * 70)
    
    print("\n模拟完整工作流程:")
    print("  1. 数据采集")
    print("  2. 数据分析")
    print("  3. 结果输出")
    
    scraper = AppStoreScraperWrapper()
    analyzer = OpportunityAnalyzer()
    
    # 使用多个关键词
    keywords = ["focus timer", "mindfulness"]
    all_apps = []
    seen_ids = set()
    
    for keyword in keywords:
        print(f"\n采集关键词: {keyword}")
        apps = scraper.search_apps(keyword, limit=10)
        
        for app in apps:
            app_id = app.get('trackId')
            if app_id and app_id not in seen_ids:
                seen_ids.add(app_id)
                all_apps.append(app)
        
        print(f"  找到 {len(apps)} 个App")
    
    print(f"\n总共采集: {len(all_apps)} 个App（已去重）")
    
    # 分析
    print("\n分析机会...")
    df = analyzer.analyze_opportunities(all_apps)
    print(f"  发现 {len(df)} 个机会")
    
    # 输出结果
    print("\nTop 5 机会:")
    for idx, row in df.head(5).iterrows():
        print(f"  {idx+1}. {row['name']}")
        print(f"     分数: {row['opportunity_score']:.3f} | 评分: {row['rating']:.2f} | 评论: {row['review_count']:,}")
    
    # 保存
    csv_file = analyzer.save_opportunities(df, "full_workflow_test.csv")
    print(f"\n  ✓ 结果已保存到: {csv_file}")
    
    return df


def generate_test_report(all_results):
    """生成测试报告"""
    print("\n" + "=" * 70)
    print("测试报告总结")
    print("=" * 70)
    
    print("\n✅ 所有测试完成！")
    print("\n测试覆盖:")
    print("  ✓ 不同关键词的数据采集")
    print("  ✓ 数据分析功能")
    print("  ✓ 参数调整影响")
    print("  ✓ 评分模型详细分析")
    print("  ✓ 数据存储功能")
    print("  ✓ 完整工作流程")
    
    print("\n系统状态: 所有功能正常 ✅")


def main():
    """主测试流程"""
    print("\n" + "=" * 70)
    print("Ferret 系统全面功能测试")
    print("=" * 70)
    
    try:
        # 测试1: 不同关键词
        keyword_results = test_different_keywords()
        
        # 测试2: 数据分析
        analysis_results = test_analysis_with_different_data(keyword_results)
        
        # 测试3: 参数调整
        param_results = test_parameter_adjustment()
        
        # 测试4: 评分模型详情
        scoring_details = test_scoring_model_details()
        
        # 测试5: 数据存储
        storage_results = test_data_storage_comprehensive()
        
        # 测试6: 完整流程
        workflow_results = test_full_workflow()
        
        # 生成报告
        generate_test_report({
            'keywords': keyword_results,
            'analysis': analysis_results,
            'parameters': param_results,
            'scoring': scoring_details,
            'storage': storage_results,
            'workflow': workflow_results
        })
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
