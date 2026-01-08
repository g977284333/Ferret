"""
从JSON文件恢复原始数据到数据库
用于修复已有数据缺少原始信息的问题
"""

import json
import sys
from pathlib import Path

# 添加backend/src到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

from utils.data_manager import DataManager

def restore_from_json_files():
    """从JSON文件恢复数据"""
    data_dir = PROJECT_ROOT / "data" / "raw" / "app_store"
    
    if not data_dir.exists():
        print(f"数据目录不存在: {data_dir}")
        return
    
    json_files = list(data_dir.glob("*.json"))
    print(f"找到 {len(json_files)} 个JSON文件")
    
    if not json_files:
        print("没有找到JSON文件")
        return
    
    data_manager = DataManager()
    total_restored = 0
    
    for json_file in json_files:
        print(f"\n处理文件: {json_file.name}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                apps = json.load(f)
            
            if not isinstance(apps, list):
                print(f"  跳过：不是列表格式")
                continue
            
            # 保存到数据库
            data_manager.save_raw_data(apps, 'app_store')
            total_restored += len(apps)
            print(f"  已恢复 {len(apps)} 个App的原始数据")
            
        except Exception as e:
            print(f"  处理失败: {e}")
    
    print(f"\n总共恢复 {total_restored} 个App的原始数据")

if __name__ == "__main__":
    restore_from_json_files()
