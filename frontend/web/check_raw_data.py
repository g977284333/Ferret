"""
检查原始数据
"""

import sqlite3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
db_path = PROJECT_ROOT / "data" / "opportunities.db"

app_id = '281796108'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查raw_apps表
cursor.execute('SELECT COUNT(*) FROM raw_apps WHERE app_id = ?', (app_id,))
count = cursor.fetchone()[0]
print(f'Raw data count for {app_id}: {count}')

if count > 0:
    cursor.execute('SELECT data FROM raw_apps WHERE app_id = ? LIMIT 1', (app_id,))
    row = cursor.fetchone()
    if row:
        data = json.loads(row[0])
        print(f'\nHas description: {"description" in data and bool(data.get("description"))}')
        print(f'Has sellerName: {"sellerName" in data and bool(data.get("sellerName"))}')
        print(f'Has releaseDate: {"releaseDate" in data and bool(data.get("releaseDate"))}')
        print(f'\nSample keys: {list(data.keys())[:15]}')
        
        # 检查关键字段
        print(f'\nKey fields:')
        print(f'  sellerName: {data.get("sellerName", "N/A")}')
        print(f'  releaseDate: {data.get("releaseDate", "N/A")}')
        print(f'  version: {data.get("version", "N/A")}')
        print(f'  description length: {len(data.get("description", ""))}')
else:
    print(f'\nNo raw data found for app_id: {app_id}')
    print('This means raw data was not saved during collection.')
    print('\nChecking all raw_apps:')
    cursor.execute('SELECT COUNT(*) FROM raw_apps')
    total = cursor.fetchone()[0]
    print(f'Total raw_apps records: {total}')

conn.close()
