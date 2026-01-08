"""
检查原始数据中的截图字段
"""

import sqlite3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
db_path = PROJECT_ROOT / "data" / "opportunities.db"

app_id = '281796108'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT data FROM raw_apps WHERE app_id = ? ORDER BY created_at DESC LIMIT 1', (app_id,))
row = cursor.fetchone()

if row:
    data = json.loads(row[0])
    print('检查截图相关字段:')
    print(f'  screenshotUrls: {bool(data.get("screenshotUrls"))}')
    print(f'  screenshotUrls type: {type(data.get("screenshotUrls"))}')
    print(f'  screenshotUrls length: {len(data.get("screenshotUrls", []))}')
    print(f'  screenshotUrls sample: {data.get("screenshotUrls", [])[:2]}')
    print(f'\n  ipadScreenshotUrls: {bool(data.get("ipadScreenshotUrls"))}')
    print(f'  ipadScreenshotUrls length: {len(data.get("ipadScreenshotUrls", []))}')
    
    # 检查所有包含screenshot的字段
    print('\n所有包含screenshot的字段:')
    for key in data.keys():
        if 'screenshot' in key.lower() or 'screen' in key.lower():
            print(f'  {key}: {type(data[key])}, length: {len(data[key]) if isinstance(data[key], list) else "N/A"}')
            if isinstance(data[key], list) and len(data[key]) > 0:
                print(f'    Sample: {data[key][0][:100] if isinstance(data[key][0], str) else data[key][0]}')
else:
    print('未找到原始数据')

conn.close()
