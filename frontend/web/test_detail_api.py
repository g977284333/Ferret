"""
测试详情API
"""

import sys
from pathlib import Path

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from utils.data_manager import DataManager

dm = DataManager()

# 获取所有机会
opps = dm.get_opportunities()
print(f"总机会数: {len(opps)}")

if opps:
    # 测试第一个机会
    first_opp = opps[0]
    app_id = first_opp.get('app_id')
    print(f"\n第一个机会的app_id: {repr(app_id)}")
    print(f"app_id类型: {type(app_id)}")
    
    # 尝试查询
    print(f"\n尝试查询 app_id='{app_id}'...")
    result = dm.get_opportunity_by_id(str(app_id))
    print(f"查询结果: {result is not None}")
    
    if result:
        print(f"找到的数据键: {list(result.keys())}")
        print(f"app_id值: {repr(result.get('app_id'))}")
    else:
        print("未找到数据！")
        
        # 检查数据库中的实际值
        import sqlite3
        db_path = PROJECT_ROOT / "data" / "opportunities.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT app_id, name FROM opportunities LIMIT 5")
        rows = cursor.fetchall()
        print(f"\n数据库中的前5条记录:")
        for row in rows:
            print(f"  app_id: {repr(row[0])}, name: {row[1]}")
        conn.close()
