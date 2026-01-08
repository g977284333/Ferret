"""
搜索趋势分析器
分析关键词的搜索趋势，识别增长机会
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class TrendAnalyzer:
    """搜索趋势分析器"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def analyze_trend_growth(self, df: pd.DataFrame, keyword: str, platform: str) -> Dict:
        """
        分析趋势增长情况
        
        Args:
            df: 趋势数据DataFrame，包含date和value列
            keyword: 关键词
            platform: 平台
            
        Returns:
            包含分析结果的字典
        """
        if df.empty:
            return {
                'keyword': keyword,
                'platform': platform,
                'growth_rate': 0,
                'trend': 'stable',
                'avg_value': 0,
                'max_value': 0,
                'min_value': 0,
                'volatility': 0
            }
        
        # 确保日期列是datetime类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        values = df['value'].values
        
        # 计算增长率（最近30天 vs 前30天）
        if len(values) >= 60:
            recent_30 = values[-30:].mean()
            previous_30 = values[-60:-30].mean()
            if previous_30 > 0:
                growth_rate = (recent_30 - previous_30) / previous_30 * 100
            else:
                growth_rate = 0
        elif len(values) >= 2:
            # 如果数据不足60天，使用最近和最早的数据
            growth_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] > 0 else 0
        else:
            growth_rate = 0
        
        # 判断趋势
        if growth_rate > 20:
            trend = 'rising'
        elif growth_rate > 5:
            trend = 'slightly_rising'
        elif growth_rate < -20:
            trend = 'declining'
        elif growth_rate < -5:
            trend = 'slightly_declining'
        else:
            trend = 'stable'
        
        # 计算统计指标
        avg_value = values.mean()
        max_value = values.max()
        min_value = values.min()
        volatility = values.std() / avg_value * 100 if avg_value > 0 else 0
        
        return {
            'keyword': keyword,
            'platform': platform,
            'growth_rate': round(growth_rate, 2),
            'trend': trend,
            'avg_value': round(avg_value, 2),
            'max_value': round(max_value, 2),
            'min_value': round(min_value, 2),
            'volatility': round(volatility, 2),
            'data_points': len(values)
        }
    
    def compare_keywords(self, trends_data: Dict[str, pd.DataFrame], platform: str) -> pd.DataFrame:
        """
        对比多个关键词的趋势
        
        Args:
            trends_data: 字典，key为关键词，value为趋势DataFrame
            platform: 平台
            
        Returns:
            包含对比结果的DataFrame
        """
        comparisons = []
        
        for keyword, df in trends_data.items():
            analysis = self.analyze_trend_growth(df, keyword, platform)
            comparisons.append(analysis)
        
        return pd.DataFrame(comparisons)
    
    def identify_hot_keywords(self, trends_data: List[Dict], min_growth_rate: float = 20.0) -> List[Dict]:
        """
        识别热门关键词（增长趋势明显的）
        
        Args:
            trends_data: 趋势数据列表
            min_growth_rate: 最小增长率阈值（%）
            
        Returns:
            热门关键词列表
        """
        hot_keywords = []
        
        for trend in trends_data:
            if trend.get('growth_rate', 0) >= min_growth_rate:
                hot_keywords.append(trend)
        
        # 按增长率排序
        hot_keywords.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        
        return hot_keywords
    
    def calculate_trend_score(self, analysis: Dict) -> float:
        """
        计算趋势分数（0-1），用于机会评分
        
        Args:
            analysis: 趋势分析结果
            
        Returns:
            趋势分数
        """
        growth_rate = analysis.get('growth_rate', 0)
        avg_value = analysis.get('avg_value', 0)
        volatility = analysis.get('volatility', 0)
        
        # 增长率分数（0-0.5）
        if growth_rate > 50:
            growth_score = 0.5
        elif growth_rate > 20:
            growth_score = 0.4
        elif growth_rate > 10:
            growth_score = 0.3
        elif growth_rate > 5:
            growth_score = 0.2
        else:
            growth_score = 0.1
        
        # 平均热度分数（0-0.3）
        # 假设Google Trends的值范围是0-100
        if avg_value > 80:
            avg_score = 0.3
        elif avg_value > 50:
            avg_score = 0.2
        elif avg_value > 20:
            avg_score = 0.15
        else:
            avg_score = 0.1
        
        # 稳定性分数（0-0.2，波动越小越好）
        if volatility < 10:
            stability_score = 0.2
        elif volatility < 20:
            stability_score = 0.15
        elif volatility < 30:
            stability_score = 0.1
        else:
            stability_score = 0.05
        
        total_score = growth_score + avg_score + stability_score
        
        return min(total_score, 1.0)
    
    def get_trend_summary(self, df: pd.DataFrame, keyword: str, platform: str) -> Dict:
        """
        获取趋势摘要
        
        Args:
            df: 趋势数据DataFrame
            keyword: 关键词
            platform: 平台
            
        Returns:
            趋势摘要字典
        """
        analysis = self.analyze_trend_growth(df, keyword, platform)
        trend_score = self.calculate_trend_score(analysis)
        
        summary = {
            'keyword': keyword,
            'platform': platform,
            'trend': analysis['trend'],
            'growth_rate': analysis['growth_rate'],
            'trend_score': round(trend_score, 3),
            'avg_value': analysis['avg_value'],
            'data_points': analysis['data_points'],
            'period': {
                'start': df['date'].min().isoformat() if 'date' in df.columns and not df.empty else None,
                'end': df['date'].max().isoformat() if 'date' in df.columns and not df.empty else None
            }
        }
        
        return summary


def main():
    """测试脚本"""
    analyzer = TrendAnalyzer()
    
    # 创建示例数据
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    values = np.random.randint(20, 80, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 20
    
    df = pd.DataFrame({
        'date': dates,
        'value': values
    })
    
    # 分析趋势
    result = analyzer.analyze_trend_growth(df, 'productivity', 'google_trends')
    print("趋势分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 计算趋势分数
    score = analyzer.calculate_trend_score(result)
    print(f"\n趋势分数: {score:.3f}")


if __name__ == "__main__":
    main()
