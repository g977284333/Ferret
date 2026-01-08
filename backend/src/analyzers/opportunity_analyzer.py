"""
机会分析器
分析采集的数据，识别潜在机会
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import yaml


# 获取项目根目录（backend/src的父目录的父目录）
# __file__ = backend/src/analyzers/opportunity_analyzer.py
# parent = backend/src/analyzers
# parent.parent = backend/src
# parent.parent.parent = backend
# parent.parent.parent.parent = 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class OpportunityAnalyzer:
    """机会分析器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """加载配置"""
        if config_path is None:
            config_path = PROJECT_ROOT / "backend" / "config" / "config.yaml"
        else:
            config_path = Path(config_path)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.scoring_config = self.config.get('scoring', {})
        self.data_dir = PROJECT_ROOT / "data" / "processed"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_apps(self, data_file: str) -> List[Dict]:
        """加载App数据"""
        filepath = PROJECT_ROOT / "data" / "raw" / "app_store" / data_file
        if not filepath.exists():
            print(f"文件不存在: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_opportunity_score(self, app: Dict) -> float:
        """
        计算机会分数
        
        评分维度：
        1. 市场规模 (market_size)
        2. 竞争程度 (competition) - 越低越好
        3. 用户满意度 (user_satisfaction) - 有改进空间
        4. 增长趋势 (growth_trend)
        5. 变现潜力 (monetization)
        
        Args:
            app: App数据字典
            
        Returns:
            机会分数 (0-1)
        """
        weights = self.scoring_config.get('weights', {})
        
        # 1. 市场规模 - 基于下载量/评论数
        market_size = self._calculate_market_size(app)
        
        # 2. 竞争程度 - 基于评分分布（评分中等 = 竞争不激烈）
        competition = self._calculate_competition(app)
        
        # 3. 用户满意度 - 评分在4.0-4.5之间 = 有改进空间
        user_satisfaction = self._calculate_user_satisfaction(app)
        
        # 4. 增长趋势 - 基于更新频率、新评论等
        growth_trend = self._calculate_growth_trend(app)
        
        # 5. 变现潜力 - 基于价格、内购等
        monetization = self._calculate_monetization(app)
        
        # 加权计算总分
        score = (
            market_size * weights.get('market_size', 0.3) +
            competition * weights.get('competition', 0.25) +
            user_satisfaction * weights.get('user_satisfaction', 0.2) +
            growth_trend * weights.get('growth_trend', 0.15) +
            monetization * weights.get('monetization', 0.1)
        )
        
        return round(score, 3)
    
    def _calculate_market_size(self, app: Dict) -> float:
        """计算市场规模分数"""
        # 基于评论数或下载量
        # 这里需要根据实际数据结构调整
        review_count = app.get('userRatingCount', 0) or 0
        
        # 评论数越多，市场规模越大（归一化到0-1）
        if review_count > 10000:
            return 1.0
        elif review_count > 1000:
            return 0.7
        elif review_count > 100:
            return 0.5
        elif review_count > 10:
            return 0.3
        else:
            return 0.1
    
    def _calculate_competition(self, app: Dict) -> float:
        """计算竞争程度分数（越低越好，所以分数越高 = 竞争越不激烈）"""
        # 如果评分中等（4.0-4.5），说明竞争不激烈，有机会
        rating = app.get('averageUserRating', 0) or 0
        
        if 4.0 <= rating <= 4.5:
            return 1.0  # 竞争不激烈，有机会
        elif 4.5 < rating <= 4.8:
            return 0.6  # 竞争中等
        else:
            return 0.3  # 竞争激烈或产品太差
    
    def _calculate_user_satisfaction(self, app: Dict) -> float:
        """计算用户满意度（有改进空间 = 机会）"""
        rating = app.get('averageUserRating', 0) or 0
        
        # 评分在4.0-4.5之间 = 有改进空间 = 机会
        if 4.0 <= rating <= 4.5:
            return 1.0
        elif 4.5 < rating <= 4.7:
            return 0.7
        else:
            return 0.3
    
    def _calculate_growth_trend(self, app: Dict) -> float:
        """计算增长趋势"""
        # 基于更新日期、新评论等
        try:
            # 检查最近更新日期
            current_version_date = app.get('currentVersionReleaseDate', '')
            if current_version_date:
                from datetime import datetime
                release_date = datetime.fromisoformat(current_version_date.replace('Z', '+00:00'))
                days_since_update = (datetime.now(release_date.tzinfo) - release_date).days
                
                # 最近30天内有更新 = 活跃
                if days_since_update <= 30:
                    return 1.0
                elif days_since_update <= 90:
                    return 0.7
                elif days_since_update <= 180:
                    return 0.5
                else:
                    return 0.3
            
            # 检查当前版本评论数（相对于总评论数）
            current_version_reviews = app.get('userRatingCountForCurrentVersion', 0) or 0
            total_reviews = app.get('userRatingCount', 0) or 0
            
            if total_reviews > 0:
                review_ratio = current_version_reviews / total_reviews
                # 当前版本评论占比高 = 活跃
                if review_ratio > 0.3:
                    return 0.8
                elif review_ratio > 0.1:
                    return 0.6
        except:
            pass
        
        return 0.5  # 默认值
    
    def _calculate_monetization(self, app: Dict) -> float:
        """计算变现潜力"""
        # 基于价格、内购等
        price = app.get('price', 0) or 0
        
        # 有价格 = 有变现潜力
        if price > 0:
            return 0.8
        else:
            return 0.5  # 免费App也可能有内购
    
    def analyze_opportunities(self, apps: List[Dict]) -> pd.DataFrame:
        """
        分析机会
        
        Args:
            apps: App列表
            
        Returns:
            包含机会分数的DataFrame
        """
        opportunities = []
        
        for app in apps:
            score = self.calculate_opportunity_score(app)
            
            opportunity = {
                'app_id': app.get('trackId', ''),
                'name': app.get('trackName', ''),
                'category': app.get('primaryGenreName', ''),
                'rating': app.get('averageUserRating', 0),
                'review_count': app.get('userRatingCount', 0),
                'price': app.get('price', 0),
                'opportunity_score': score,
                'url': app.get('trackViewUrl', ''),
            }
            
            opportunities.append(opportunity)
        
        # 如果没有数据，返回空DataFrame
        if not opportunities:
            return pd.DataFrame(columns=['app_id', 'name', 'category', 'rating', 
                                        'review_count', 'price', 'opportunity_score', 'url'])
        
        df = pd.DataFrame(opportunities)
        
        # 按分数排序
        df = df.sort_values('opportunity_score', ascending=False)
        
        # 应用阈值过滤
        thresholds = self.scoring_config.get('thresholds', {})
        min_score = thresholds.get('min_score', 0.6)
        min_reviews = thresholds.get('min_reviews', 10)
        
        df = df[
            (df['opportunity_score'] >= min_score) &
            (df['review_count'] >= min_reviews)
        ]
        
        # 去重（基于app_id）
        df = df.drop_duplicates(subset=['app_id'], keep='first')
        
        return df
    
    def save_opportunities(self, df: pd.DataFrame, filename: str = "opportunities.csv"):
        """保存机会分析结果"""
        filepath = self.data_dir / filename
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(df)} 个机会到: {filepath}")
        return filepath


def main():
    """测试脚本"""
    analyzer = OpportunityAnalyzer()
    
    # 测试：如果有数据文件，可以加载分析
    print("机会分析器已初始化")
    print("使用方法:")
    print("1. 先运行数据采集: python scrapers/app_store_scraper.py")
    print("2. 然后运行分析: analyzer.analyze_opportunities(apps)")


if __name__ == "__main__":
    main()
