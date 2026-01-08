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
        
        # 创建搜索趋势表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                platform TEXT,
                date TEXT,
                value REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(keyword, platform, date)
            )
        ''')
        
        # 创建趋势采集任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE,
                keywords TEXT,
                platforms TEXT,
                timeframe TEXT,
                status TEXT,
                progress TEXT,
                results TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def get_opportunities(self) -> List[Dict]:
        """获取所有机会"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM opportunities ORDER BY opportunity_score DESC')
        
        columns = [description[0] for description in cursor.description]
        opportunities = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return opportunities
    
    def get_opportunity_by_id(self, app_id: str) -> Optional[Dict]:
        """根据app_id获取机会"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM opportunities WHERE app_id = ?', (str(app_id),))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
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
    
    def save_trend_data(self, keyword: str, platform: str, date: str, value: float, metadata: Optional[Dict] = None):
        """保存趋势数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO search_trends 
            (keyword, platform, date, value, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (keyword, platform, date, value, metadata_json))
        
        conn.commit()
        conn.close()
    
    def save_trend_batch(self, trends: List[Dict]):
        """批量保存趋势数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for trend in trends:
            metadata_json = json.dumps(trend.get('metadata'), ensure_ascii=False) if trend.get('metadata') else None
            cursor.execute('''
                INSERT OR REPLACE INTO search_trends 
                (keyword, platform, date, value, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                trend.get('keyword'),
                trend.get('platform'),
                trend.get('date'),
                trend.get('value'),
                metadata_json
            ))
        
        conn.commit()
        conn.close()
    
    def get_trend_data(self, keyword: str = None, platform: str = None, 
                      start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取趋势数据"""
        conn = sqlite3.connect(self.db_path)
        
        query = 'SELECT * FROM search_trends WHERE 1=1'
        params = []
        
        if keyword:
            query += ' AND keyword = ?'
            params.append(keyword)
        if platform:
            query += ' AND platform = ?'
            params.append(platform)
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY date ASC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def get_trend_keywords(self) -> List[str]:
        """获取所有已采集的关键词列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT keyword FROM search_trends ORDER BY keyword')
        keywords = [row[0] for row in cursor.fetchall()]
        conn.close()
        return keywords
    
    def save_trend_task(self, task_id: str, keywords: List[str], platforms: List[str], 
                       timeframe: str, status: str = 'pending', progress: Dict = None,
                       results: Dict = None, error: str = None):
        """保存趋势采集任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        platforms_json = json.dumps(platforms, ensure_ascii=False)
        progress_json = json.dumps(progress, ensure_ascii=False) if progress else None
        results_json = json.dumps(results, ensure_ascii=False) if results else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO trend_tasks 
            (task_id, keywords, platforms, timeframe, status, progress, results, error, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (task_id, keywords_json, platforms_json, timeframe, status, progress_json, results_json, error))
        
        conn.commit()
        conn.close()
    
    def get_trend_task(self, task_id: str) -> Optional[Dict]:
        """获取趋势采集任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trend_tasks WHERE task_id = ?', (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            task = dict(zip(columns, row))
            # 解析JSON字段
            task['keywords'] = json.loads(task['keywords']) if task['keywords'] else []
            task['platforms'] = json.loads(task['platforms']) if task['platforms'] else []
            task['progress'] = json.loads(task['progress']) if task.get('progress') else {}
            task['results'] = json.loads(task['results']) if task.get('results') else {}
            return task
        return None