"""
数据管理工具
统一管理数据的存储和读取
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd


# 获取项目根目录
# __file__ = backend/src/utils/data_manager.py
# parent.parent.parent.parent = 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class DataManager:
    """数据管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            self.db_path = PROJECT_ROOT / "data" / "opportunities.db"
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建机会表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT,
                name TEXT,
                category TEXT,
                rating REAL,
                review_count INTEGER,
                price REAL,
                opportunity_score REAL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(app_id)
            )
        ''')
        
        # 创建原始数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT,
                data TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_opportunity(self, opportunity: Dict):
        """保存机会到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO opportunities 
            (app_id, name, category, rating, review_count, price, opportunity_score, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            opportunity.get('app_id'),
            opportunity.get('name'),
            opportunity.get('category'),
            opportunity.get('rating'),
            opportunity.get('review_count'),
            opportunity.get('price'),
            opportunity.get('opportunity_score'),
            opportunity.get('url'),
        ))
        
        conn.commit()
        conn.close()
    
    def get_top_opportunities(self, limit: int = 20) -> pd.DataFrame:
        """获取Top机会"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            f'SELECT * FROM opportunities ORDER BY opportunity_score DESC LIMIT {limit}',
            conn
        )
        conn.close()
        return df
    
    def save_raw_data(self, data: List[Dict], source: str):
        """保存原始数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in data:
            app_id = item.get('trackId') or item.get('id', '')
            data_json = json.dumps(item, ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO raw_apps (app_id, data, source)
                VALUES (?, ?, ?)
            ''', (app_id, data_json, source))
        
        conn.commit()
        conn.close()
