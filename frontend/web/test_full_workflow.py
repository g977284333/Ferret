"""
完整工作流程测试
测试从数据采集到查看机会的完整流程
"""

import sys
import io
import requests
import time
import json

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def test_step(step_num, description, test_func):
    """执行测试步骤"""
    print(f"\n[步骤 {step_num}] {description}")
    print("-" * 70)
    try:
        result = test_func()
        if isinstance(result, tuple):
            # 如果返回元组，解包
            success, *extra = result
            if success:
                print(f"[OK] 步骤 {step_num} 通过")
                return (True, *extra)
            else:
                print(f"[FAIL] 步骤 {step_num} 失败")
                return (False, *extra)
        else:
            # 如果返回单个值
            if result:
                print(f"[OK] 步骤 {step_num} 通过")
                return result
            else:
                print(f"[FAIL] 步骤 {step_num} 失败")
                return False
    except Exception as e:
        print(f"[ERROR] 步骤 {step_num} 出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_homepage():
    """测试1: 访问首页"""
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code == 200:
        print(f"  首页加载成功 (大小: {len(response.text)} 字节)")
        return True
    return False

def test_stats_api():
    """测试2: 获取统计信息"""
    response = requests.get(f"{API_BASE}/stats", timeout=5)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('data', {})
        print(f"  总机会数: {stats.get('total_opportunities', 0)}")
        print(f"  今日采集: {stats.get('today_collected', 0)}")
        print(f"  进行中任务: {stats.get('active_tasks', 0)}")
        return True
    return False

def test_opportunities_list():
    """测试3: 获取机会列表"""
    response = requests.get(f"{API_BASE}/opportunities?per_page=5", timeout=5)
    if response.status_code == 200:
        data = response.json()
        opportunities = data.get('data', {}).get('opportunities', [])
        print(f"  获取到 {len(opportunities)} 个机会")
        if opportunities:
            opp = opportunities[0]
            print(f"  示例: {opp.get('name')} (分数: {opp.get('opportunity_score', 0):.3f})")
        return True, opportunities
    return False, []

def test_opportunity_detail(opportunities):
    """测试4: 获取机会详情"""
    if not opportunities:
        print("  跳过：没有可用机会")
        return True
    
    app_id = opportunities[0].get('app_id')
    response = requests.get(f"{API_BASE}/opportunities/{app_id}", timeout=5)
    if response.status_code == 200:
        data = response.json()
        opp = data.get('data', {})
        print(f"  详情加载成功: {opp.get('name')}")
        print(f"  评分详情: {len(opp.get('scoring_details', {}))} 个维度")
        return True
    return False

def test_config_api():
    """测试5: 获取配置"""
    response = requests.get(f"{API_BASE}/config", timeout=5)
    if response.status_code == 200:
        data = response.json()
        config = data.get('data', {})
        weights = config.get('scoring', {}).get('weights', {})
        print(f"  配置加载成功")
        print(f"  评分权重: {len(weights)} 个维度")
        return True, config
    return False, None

def test_update_config(config):
    """测试6: 更新配置（测试后恢复）"""
    if not config:
        print("  跳过：无法获取配置")
        return True
    
    # 保存原始配置
    original_weights = config.get('scoring', {}).get('weights', {}).copy()
    
    # 创建测试配置（微调）
    test_config = {
        'scoring': {
            'weights': {
                'market_size': 0.31,
                'competition': 0.24,
                'user_satisfaction': 0.20,
                'growth_trend': 0.15,
                'monetization': 0.10
            },
            'thresholds': config.get('scoring', {}).get('thresholds', {})
        }
    }
    
    # 更新配置
    response = requests.post(
        f"{API_BASE}/config",
        json=test_config,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    if response.status_code == 200:
        print("  配置更新成功")
        
        # 恢复原始配置
        restore_config = {
            'scoring': {
                'weights': original_weights,
                'thresholds': config.get('scoring', {}).get('thresholds', {})
            }
        }
        requests.post(
            f"{API_BASE}/config",
            json=restore_config,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print("  配置已恢复")
        return True
    return False

def test_start_scrape():
    """测试7: 启动采集任务"""
    scrape_data = {
        'keywords': ['productivity'],
        'data_source': 'app_store',
        'limit_per_keyword': 3  # 少量测试
    }
    
    response = requests.post(
        f"{API_BASE}/scrape/start",
        json=scrape_data,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        task_id = result.get('task_id')
        print(f"  采集任务已启动 (任务ID: {task_id})")
        return True, task_id
    return False, None

def test_scrape_status(task_id):
    """测试8: 检查采集状态"""
    if not task_id:
        print("  跳过：没有任务ID")
        return True
    
    # 等待几秒让任务开始
    print("  等待任务启动...")
    time.sleep(3)
    
    response = requests.get(f"{API_BASE}/scrape/status/{task_id}", timeout=5)
    if response.status_code == 200:
        data = response.json()
        status = data.get('status')
        progress = data.get('progress', {})
        print(f"  任务状态: {status}")
        print(f"  进度: {progress.get('completed', 0)}/{progress.get('total', 0)}")
        return True
    return False

def test_export_functionality(opportunities):
    """测试9: 测试导出功能"""
    if not opportunities:
        print("  跳过：没有可用机会")
        return True
    
    # 测试CSV导出
    response = requests.get(
        f"{API_BASE}/opportunities/export?format=csv&per_page=5",
        timeout=10
    )
    
    if response.status_code == 200:
        csv_content = response.text
        print(f"  CSV导出成功 (大小: {len(csv_content)} 字节)")
        return True
    return False

def test_search_and_filter():
    """测试10: 测试搜索和筛选"""
    # 测试搜索
    response = requests.get(
        f"{API_BASE}/opportunities?search=evernote&per_page=5",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        opportunities = data.get('data', {}).get('opportunities', [])
        print(f"  搜索功能正常，找到 {len(opportunities)} 个结果")
        
        # 测试筛选
        response2 = requests.get(
            f"{API_BASE}/opportunities?min_score=0.8&per_page=5",
            timeout=5
        )
        if response2.status_code == 200:
            data2 = response2.json()
            opportunities2 = data2.get('data', {}).get('opportunities', [])
            print(f"  筛选功能正常，找到 {len(opportunities2)} 个高分机会")
            return True
    return False

def main():
    """主测试函数"""
    print_section("Ferret Web 完整工作流程测试")
    print("\n请确保Flask应用正在运行: python app.py")
    print("等待3秒后开始测试...\n")
    
    time.sleep(3)
    
    results = []
    opportunities = []
    task_id = None
    config = None
    
    # 执行测试步骤
    results.append(("访问首页", test_step(1, "访问首页", test_homepage)))
    
    results.append(("获取统计信息", test_step(2, "获取统计信息", test_stats_api)))
    
    success, opportunities = test_step(3, "获取机会列表", test_opportunities_list)
    results.append(("获取机会列表", success))
    
    results.append(("获取机会详情", test_step(4, "获取机会详情", 
                                               lambda: test_opportunity_detail(opportunities))))
    
    success, config = test_step(5, "获取配置", test_config_api)
    results.append(("获取配置", success))
    
    results.append(("更新配置", test_step(6, "更新配置（测试后恢复）",
                                          lambda: test_update_config(config))))
    
    success, task_id = test_step(7, "启动采集任务", test_start_scrape)
    results.append(("启动采集任务", success))
    
    results.append(("检查采集状态", test_step(8, "检查采集状态",
                                              lambda: test_scrape_status(task_id))))
    
    results.append(("导出功能", test_step(9, "测试导出功能",
                                         lambda: test_export_functionality(opportunities))))
    
    results.append(("搜索和筛选", test_step(10, "测试搜索和筛选", test_search_and_filter)))
    
    # 测试所有页面
    print_section("页面可访问性测试")
    
    pages = [
        ("/", "首页"),
        ("/scrape", "数据采集页面"),
        ("/opportunities", "机会列表页面"),
        ("/config", "配置页面"),
    ]
    
    for url, name in pages:
        try:
            response = requests.get(BASE_URL + url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name} - 可访问")
                results.append((name, True))
            else:
                print(f"[FAIL] {name} - 状态码: {response.status_code}")
                results.append((name, False))
        except Exception as e:
            print(f"[ERROR] {name} - {e}")
            results.append((name, False))
    
    # 测试详情页面
    if opportunities:
        app_id = opportunities[0].get('app_id')
        try:
            response = requests.get(f"{BASE_URL}/opportunities/{app_id}", timeout=5)
            if response.status_code == 200:
                print(f"[OK] 机会详情页面 - 可访问")
                results.append(("机会详情页面", True))
            else:
                results.append(("机会详情页面", False))
        except:
            results.append(("机会详情页面", False))
    
    # 总结
    print_section("测试总结")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print(f"\n总计: {total} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    print(f"通过率: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n失败的测试:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("[SUCCESS] 所有测试通过！系统功能正常！")
    else:
        print(f"[WARNING] {failed} 项测试失败，请检查上述错误信息")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
