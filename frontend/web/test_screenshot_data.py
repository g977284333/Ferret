"""
测试截图数据解析
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
    screenshot_urls = data.get('screenshotUrls', [])
    
    print(f'screenshotUrls type: {type(screenshot_urls)}')
    print(f'screenshotUrls value (first 200 chars): {str(screenshot_urls)[:200]}')
    
    # 尝试解析
    if isinstance(screenshot_urls, str):
        print('\n尝试解析字符串...')
        try:
            parsed = json.loads(screenshot_urls)
            print(f'解析成功! 类型: {type(parsed)}')
            if isinstance(parsed, list):
                print(f'列表长度: {len(parsed)}')
                print(f'第一个URL: {parsed[0] if parsed else "None"}')
        except Exception as e:
            print(f'解析失败: {e}')
            # 检查是否是单个URL
            if screenshot_urls.startswith('http'):
                print('看起来是单个URL')
                print(f'URL: {screenshot_urls[:100]}')

conn.close()
