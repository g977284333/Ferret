"""
搜索趋势数据采集器
支持多个平台的搜索趋势数据采集：
- Google Trends
- 百度指数
- 微信指数
- YouTube趋势
"""

import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Google Trends
try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False
    print("警告: pytrends未安装，Google Trends功能不可用。安装: pip install pytrends")

# 百度指数（可选，需要cookie）
try:
    # 可以使用 gopup 或其他库
    HAS_BAIDU = False  # 暂时标记为False，需要时再实现
except ImportError:
    HAS_BAIDU = False

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class TrendScraper:
    """搜索趋势数据采集器"""
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: 请求间隔（秒），避免被封
        """
        self.delay = delay
        self.pytrends = None
        if HAS_PYTRENDS:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
            except Exception as e:
                print(f"初始化Google Trends失败: {e}")
        
        self.data_dir = PROJECT_ROOT / "data" / "raw" / "trends"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_google_trends(self, keywords: List[str], timeframe: str = 'today 12-m', 
                          geo: str = '', cat: int = 0) -> Dict:
        """
        获取Google Trends数据
        
        Args:
            keywords: 关键词列表（最多5个）
            timeframe: 时间范围，如 'today 12-m', 'today 3-m', 'all'
            geo: 地理位置代码，如 'US', 'CN', ''表示全球
            cat: 分类代码，0表示所有分类
            
        Returns:
            包含趋势数据的字典
        """
        if not HAS_PYTRENDS or not self.pytrends:
            return {
                'success': False,
                'error': 'pytrends未安装或初始化失败',
                'data': {}
            }
        
        if not keywords:
            return {
                'success': False,
                'error': '关键词列表不能为空',
                'data': {}
            }
        
        # Google Trends最多支持5个关键词
        keywords = keywords[:5]
        
        try:
            # 构建请求
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=cat,
                timeframe=timeframe,
                geo=geo,
                gprop=''  # 默认网页搜索，也可以是 'images', 'news', 'youtube', 'froogle'
            )
            
            # 获取时间序列数据
            interest_over_time = self.pytrends.interest_over_time()
            
            # 获取相关查询
            related_queries = self.pytrends.related_queries()
            
            # 获取相关主题
            related_topics = self.pytrends.related_topics()
            
            # 处理时间序列数据，转换为易处理的格式
            interest_data = []
            if not interest_over_time.empty:
                # 重置索引，确保date在列中
                df = interest_over_time.reset_index()
                # 转换为记录列表
                for _, row in df.iterrows():
                    record = {}
                    # 获取日期
                    if 'date' in df.columns:
                        record['date'] = str(row['date'])
                    elif df.index.name == 'date':
                        record['date'] = str(df.index[_])
                    else:
                        # 尝试从索引获取
                        record['date'] = str(row.name) if hasattr(row, 'name') else str(_)
                    
                    # 获取每个关键词的值
                    for kw in keywords:
                        if kw in row:
                            record[kw] = float(row[kw]) if pd.notna(row[kw]) else 0.0
                    
                    interest_data.append(record)
            
            # 转换为字典格式
            result = {
                'success': True,
                'platform': 'google_trends',
                'keywords': keywords,
                'timeframe': timeframe,
                'geo': geo,
                'data': {
                    'interest_over_time': interest_data,  # 返回记录列表，更易处理
                    'related_queries': {
                        kw: {
                            'top': related_queries[kw]['top'].to_dict('records') if related_queries[kw]['top'] is not None else [],
                            'rising': related_queries[kw]['rising'].to_dict('records') if related_queries[kw]['rising'] is not None else []
                        } for kw in keywords if kw in related_queries
                    },
                    'related_topics': {
                        kw: {
                            'top': related_topics[kw]['top'].to_dict('records') if related_topics[kw]['top'] is not None else [],
                            'rising': related_topics[kw]['rising'].to_dict('records') if related_topics[kw]['rising'] is not None else []
                        } for kw in keywords if kw in related_topics
                    }
                }
            }
            
            time.sleep(self.delay)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def get_google_trends_suggestions(self, keyword: str) -> List[Dict]:
        """
        获取Google Trends关键词建议
        
        Args:
            keyword: 关键词
            
        Returns:
            建议列表
        """
        if not HAS_PYTRENDS or not self.pytrends:
            return []
        
        try:
            suggestions = self.pytrends.suggestions(keyword=keyword)
            return suggestions if suggestions else []
        except Exception as e:
            print(f"获取Google Trends建议失败: {e}")
            return []
    
    def get_baidu_index(self, keywords: List[str], start_date: str, end_date: str) -> Dict:
        """
        获取百度指数数据
        
        Args:
            keywords: 关键词列表（最多3个）
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            
        Returns:
            包含百度指数数据的字典
        
        注意：需要cookie或BDUSS，这里提供接口框架
        """
        # TODO: 实现百度指数采集
        # 可以使用 baidu_index 库或 gopup 库
        # 需要用户提供cookie或BDUSS
        
        return {
            'success': False,
            'error': '百度指数功能待实现，需要cookie或BDUSS',
            'data': {}
        }
    
    def get_wechat_index(self, keyword: str) -> Dict:
        """
        获取微信指数数据
        
        Args:
            keyword: 关键词
            
        Returns:
            包含微信指数数据的字典
        
        注意：微信指数可能需要登录或API密钥
        """
        # TODO: 实现微信指数采集
        # 微信指数可能需要登录或特殊API
        
        return {
            'success': False,
            'error': '微信指数功能待实现',
            'data': {}
        }
    
    def get_youtube_trends(self, keywords: List[str], region: str = 'US') -> Dict:
        """
        获取YouTube搜索趋势数据
        
        Args:
            keywords: 关键词列表
            region: 地区代码，如 'US', 'CN'
            
        Returns:
            包含YouTube趋势数据的字典
        
        注意：可以使用YouTube Data API v3，需要API密钥
        """
        # TODO: 实现YouTube趋势采集
        # 可以使用YouTube Data API v3
        
        return {
            'success': False,
            'error': 'YouTube趋势功能待实现，需要API密钥',
            'data': {}
        }
    
    def get_trends_multi_platform(self, keywords: List[str], platforms: List[str] = None,
                                  timeframe: str = 'today 12-m') -> Dict:
        """
        从多个平台获取趋势数据
        
        Args:
            keywords: 关键词列表
            platforms: 平台列表，如 ['google_trends', 'baidu_index', 'wechat_index', 'youtube']
            timeframe: 时间范围
            
        Returns:
            包含所有平台数据的字典
        """
        if platforms is None:
            platforms = ['google_trends']  # 默认只使用Google Trends
        
        results = {
            'keywords': keywords,
            'timeframe': timeframe,
            'platforms': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for platform in platforms:
            if platform == 'google_trends':
                data = self.get_google_trends(keywords, timeframe=timeframe)
                results['platforms']['google_trends'] = data
            elif platform == 'baidu_index':
                # 计算日期范围
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                data = self.get_baidu_index(
                    keywords,
                    start_date.strftime('%Y%m%d'),
                    end_date.strftime('%Y%m%d')
                )
                results['platforms']['baidu_index'] = data
            elif platform == 'wechat_index':
                # 微信指数一次只能查询一个关键词
                wechat_data = {}
                for keyword in keywords:
                    data = self.get_wechat_index(keyword)
                    wechat_data[keyword] = data
                results['platforms']['wechat_index'] = wechat_data
            elif platform == 'youtube':
                data = self.get_youtube_trends(keywords)
                results['platforms']['youtube'] = data
        
        return results
    
    def save_trends(self, trends_data: Dict, filename: Optional[str] = None) -> Path:
        """保存趋势数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trends_{timestamp}.json"
        
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trends_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"已保存趋势数据到: {filepath}")
        return filepath


def main():
    """测试脚本"""
    scraper = TrendScraper()
    
    # 测试Google Trends
    print("测试Google Trends...")
    keywords = ["productivity", "task management"]
    result = scraper.get_google_trends(keywords, timeframe='today 3-m')
    
    if result['success']:
        print(f"成功获取 {len(keywords)} 个关键词的趋势数据")
        print(f"数据时间范围: {result['timeframe']}")
        
        # 保存数据
        scraper.save_trends(result)
    else:
        print(f"获取失败: {result.get('error', '未知错误')}")
    
    # 测试关键词建议
    print("\n测试关键词建议...")
    suggestions = scraper.get_google_trends_suggestions("productivity")
    print(f"找到 {len(suggestions)} 个建议")
    if suggestions:
        print("前5个建议:")
        for s in suggestions[:5]:
            print(f"  - {s.get('title', 'N/A')}")


if __name__ == "__main__":
    main()
