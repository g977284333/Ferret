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
            # 使用更宽松的日期解析，支持多种格式
            df['date'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
            # 移除无效日期
            df = df.dropna(subset=['date'])
            df = df.sort_values('date')
        
        # 确保value列存在
        if 'value' not in df.columns:
            # 如果没有value列，尝试使用关键词作为列名
            if keyword in df.columns:
                df['value'] = df[keyword]
            else:
                # 如果都没有，返回空结果
                return {
                    'keyword': keyword,
                    'platform': platform,
                    'growth_rate': 0,
                    'trend': 'stable',
                    'avg_value': 0,
                    'max_value': 0,
                    'min_value': 0,
                    'volatility': 0,
                    'data_points': 0
                }
        
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
        avg_value = float(values.mean()) if len(values) > 0 else 0.0
        max_value = float(values.max()) if len(values) > 0 else 0.0
        min_value = float(values.min()) if len(values) > 0 else 0.0
        volatility = float(values.std() / avg_value * 100) if avg_value > 0 and len(values) > 0 else 0.0
        
        return {
            'keyword': keyword,
            'platform': platform,
            'growth_rate': float(growth_rate),
            'trend': trend,
            'avg_value': float(avg_value),
            'max_value': float(max_value),
            'min_value': float(min_value),
            'volatility': float(volatility),
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
        
        # 获取日期范围
        start_date = None
        end_date = None
        if 'date' in df.columns and not df.empty:
            try:
                date_min = df['date'].min()
                date_max = df['date'].max()
                start_date = date_min.isoformat() if hasattr(date_min, 'isoformat') else str(date_min)
                end_date = date_max.isoformat() if hasattr(date_max, 'isoformat') else str(date_max)
            except Exception as e:
                print(f"Error getting date range: {e}")
        
        summary = {
            'keyword': keyword,
            'platform': platform,
            'trend': analysis.get('trend', 'stable'),
            'growth_rate': analysis.get('growth_rate', 0),
            'trend_score': round(trend_score, 3),
            'avg_value': analysis.get('avg_value', 0),
            'data_points': analysis.get('data_points', len(df)),
            'period': {
                'start': start_date,
                'end': end_date
            }
        }
        
        return summary
    
    def recommend_opportunities(self, trends_data: List[Dict], 
                               min_trend_score: float = 0.6,
                               min_growth_rate: float = 15.0,
                               min_avg_value: float = 30.0) -> List[Dict]:
        """
        推荐高机会关键词
        
        推荐策略：
        1. 趋势分数 >= min_trend_score (默认0.6)
        2. 增长率 >= min_growth_rate (默认15%)
        3. 平均热度 >= min_avg_value (默认30)
        4. 数据点数量 >= 30 (至少1个月的数据)
        5. 波动率 < 40% (趋势相对稳定)
        
        Args:
            trends_data: 趋势分析结果列表
            min_trend_score: 最小趋势分数阈值
            min_growth_rate: 最小增长率阈值（%）
            min_avg_value: 最小平均热度阈值
            
        Returns:
            推荐的关键词列表，按机会分数排序
        """
        recommendations = []
        
        for trend in trends_data:
            trend_score = trend.get('trend_score', 0)
            growth_rate = trend.get('growth_rate', 0)
            avg_value = trend.get('avg_value', 0)
            volatility = trend.get('volatility', 0)
            data_points = trend.get('data_points', 0)
            
            # 应用推荐策略
            if (trend_score >= min_trend_score and
                growth_rate >= min_growth_rate and
                avg_value >= min_avg_value and
                data_points >= 30 and
                volatility < 40):
                
                # 计算综合机会分数（0-100）
                opportunity_score = (
                    trend_score * 40 +  # 趋势分数权重40%
                    min(growth_rate / 100, 1.0) * 30 +  # 增长率权重30%
                    min(avg_value / 100, 1.0) * 20 +  # 热度权重20%
                    min((100 - volatility) / 100, 1.0) * 10  # 稳定性权重10%
                ) * 100
                
                recommendation = {
                    'keyword': trend.get('keyword'),
                    'platform': trend.get('platform'),
                    'opportunity_score': round(opportunity_score, 2),
                    'trend_score': round(trend_score, 3),
                    'growth_rate': round(growth_rate, 2),
                    'avg_value': round(avg_value, 2),
                    'volatility': round(volatility, 2),
                    'data_points': data_points,
                    'trend': trend.get('trend', 'stable'),
                    'reason': self._generate_recommendation_reason(trend, opportunity_score)
                }
                recommendations.append(recommendation)
        
        # 按机会分数排序
        recommendations.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return recommendations
    
    def _generate_recommendation_reason(self, trend: Dict, opportunity_score: float) -> str:
        """生成推荐理由"""
        reasons = []
        
        growth_rate = trend.get('growth_rate', 0)
        avg_value = trend.get('avg_value', 0)
        volatility = trend.get('volatility', 0)
        trend_type = trend.get('trend', 'stable')
        
        if growth_rate > 30:
            reasons.append(f"快速增长（增长率{growth_rate:.1f}%）")
        elif growth_rate > 15:
            reasons.append(f"稳定增长（增长率{growth_rate:.1f}%）")
        
        if avg_value > 70:
            reasons.append("搜索热度高")
        elif avg_value > 40:
            reasons.append("搜索热度中等")
        
        if volatility < 20:
            reasons.append("趋势稳定")
        elif volatility < 35:
            reasons.append("趋势相对稳定")
        
        if trend_type == 'rising':
            reasons.append("上升趋势明显")
        elif trend_type == 'slightly_rising':
            reasons.append("呈现上升趋势")
        
        if not reasons:
            reasons.append("综合评分较高")
        
        return "；".join(reasons)


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
