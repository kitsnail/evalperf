#!/usr/bin/env python3
"""
图表数据准备模块
Author: AI Assistant
Date: 2024
"""

from typing import List, Dict
import json


class ChartDataExtractor:
    """图表数据提取器"""
    
    def __init__(self, data: List[Dict]):
        # 按并发数排序数据，确保图表横轴有序
        self.data = sorted(data, key=lambda x: x['parallel'])
        
        # 按提示词类型分组数据
        self.grouped_data = self._group_data_by_prompt_type()
    
    def _group_data_by_prompt_type(self) -> Dict[str, List[Dict]]:
        """按提示词类型分组数据"""
        groups = {
            'short': [],
            'medium': [], 
            'long': []
        }
        
        for row in self.data:
            test_name = row['test_name']
            if 'short' in test_name:
                groups['short'].append(row)
            elif 'medium' in test_name:
                groups['medium'].append(row)
            elif 'long' in test_name:
                groups['long'].append(row)
        
        return groups
    
    def extract_basic_chart_data(self) -> Dict[str, List]:
        """
        提取基础图表数据
        Returns:
            Dict: 包含并发数、QPS、吞吐量、延迟等数据的字典
        """
        return {
            'parallels': [row['parallel'] for row in self.data],
            'qps_data': [row['qps'] for row in self.data],
            'throughput_data': [row['output_token_throughput'] for row in self.data],
            'latency_data': [row['avg_latency_ms'] for row in self.data],
            'ttft_data': [row['avg_ttft_ms'] for row in self.data],
            'success_rate': [row['success_rate'] for row in self.data],
            'error_rate': [row['error_rate'] for row in self.data]
        }
    
    def extract_percentile_latency_data(self) -> Dict[str, List]:
        """
        提取百分位数延迟数据
        Returns:
            Dict: 包含P50、P95、P99延迟数据的字典
        """
        return {
            'p50_latency': [row['p50_latency_ms'] for row in self.data],
            'p95_latency': [row['p95_latency_ms'] for row in self.data],
            'p99_latency': [row['p99_latency_ms'] for row in self.data]
        }
    
    def get_chart_js_data(self) -> str:
        """
        获取用于Chart.js的JSON格式数据
        Returns:
            str: JSON格式的图表数据字符串
        """
        basic_data = self.extract_basic_chart_data()
        percentile_data = self.extract_percentile_latency_data()
        
        chart_data = {
            'parallels': basic_data['parallels'],
            'qps_data': basic_data['qps_data'],
            'throughput_data': basic_data['throughput_data'],
            'latency_data': basic_data['latency_data'],
            'ttft_data': basic_data['ttft_data'],
            'p50_latency': percentile_data['p50_latency'],
            'p95_latency': percentile_data['p95_latency'],
            'p99_latency': percentile_data['p99_latency'],
            'success_rate': basic_data['success_rate'],
            'error_rate': basic_data['error_rate']
        }
        
        return json.dumps(chart_data)
    
    def get_qps_chart_config(self) -> Dict:
        """
        获取QPS图表配置
        Returns:
            Dict: QPS图表的配置对象
        """
        # 获取并发数标签（从short组获取，确保顺序一致）
        parallels = [row['parallel'] for row in self.grouped_data['short']]
        
        # 为每种提示词类型创建数据集
        datasets = []
        colors = {
            'short': '#667eea',
            'medium': '#28a745', 
            'long': '#ff6b6b'
        }
        
        for prompt_type, color in colors.items():
            qps_data = [row['qps'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'QPS ({prompt_type})',
                'data': qps_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)'),
                'borderColor': color,
                'borderWidth': 2,
                'borderRadius': 6
            })
        
        return {
            'type': 'bar',
            'data': {
                'labels': parallels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'top'
                    },
                    'tooltip': {
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'padding': 12,
                        'titleFont': {'size': 14},
                        'bodyFont': {'size': 13}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': '并发数',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'QPS (请求/秒)',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def get_throughput_chart_config(self) -> Dict:
        """
        获取吞吐量图表配置
        Returns:
            Dict: 吞吐量图表的配置对象
        """
        # 获取并发数标签（从short组获取，确保顺序一致）
        parallels = [row['parallel'] for row in self.grouped_data['short']]
        
        # 为每种提示词类型创建数据集
        datasets = []
        colors = {
            'short': '#667eea',
            'medium': '#28a745', 
            'long': '#ff6b6b'
        }
        
        for prompt_type, color in colors.items():
            throughput_data = [row['output_token_throughput'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'Token 吞吐量 ({prompt_type})',
                'data': throughput_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)'),
                'borderColor': color,
                'borderWidth': 2,
                'borderRadius': 6
            })
        
        return {
            'type': 'bar',
            'data': {
                'labels': parallels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'padding': 12,
                        'titleFont': {'size': 14},
                        'bodyFont': {'size': 13}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': '并发数',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'Tokens/秒',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def get_latency_chart_config(self) -> Dict:
        """
        获取延迟图表配置
        Returns:
            Dict: 延迟图表的配置对象
        """
        # 获取并发数标签（从short组获取，确保顺序一致）
        parallels = [row['parallel'] for row in self.grouped_data['short']]
        
        # 为每种提示词类型创建P95延迟数据集
        datasets = []
        colors = {
            'short': '#667eea',
            'medium': '#28a745', 
            'long': '#ff6b6b'
        }
        
        for prompt_type, color in colors.items():
            p95_data = [row['p95_latency_ms'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'P95 延迟 ({prompt_type})',
                'data': p95_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)'),
                'borderColor': color,
                'borderWidth': 2,
                'borderRadius': 6
            })
        
        return {
            'type': 'bar',
            'data': {
                'labels': parallels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'padding': 12,
                        'titleFont': {'size': 14},
                        'bodyFont': {'size': 13}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': '并发数',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'P95 延迟 (毫秒)',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def get_ttft_chart_config(self) -> Dict:
        """
        获取TTFT图表配置
        Returns:
            Dict: TTFT图表的配置对象
        """
        # 获取并发数标签（从short组获取，确保顺序一致）
        parallels = [row['parallel'] for row in self.grouped_data['short']]
        
        # 为每种提示词类型创建数据集
        datasets = []
        colors = {
            'short': '#667eea',
            'medium': '#28a745', 
            'long': '#ff6b6b'
        }
        
        for prompt_type, color in colors.items():
            ttft_data = [row['avg_ttft_ms'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'TTFT ({prompt_type})',
                'data': ttft_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)'),
                'borderColor': color,
                'borderWidth': 2,
                'borderRadius': 6
            })
        
        return {
            'type': 'bar',
            'data': {
                'labels': parallels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'padding': 12,
                        'titleFont': {'size': 14},
                        'bodyFont': {'size': 13}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': '并发数',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'TTFT (毫秒)',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def get_success_chart_config(self) -> Dict:
        """
        获取成功率图表配置
        Returns:
            Dict: 成功率图表的配置对象
        """
        # 获取并发数标签（从short组获取，确保顺序一致）
        parallels = [row['parallel'] for row in self.grouped_data['short']]
        
        # 为每种提示词类型创建成功率和错误率数据集
        datasets = []
        colors = {
            'short': '#667eea',
            'medium': '#28a745', 
            'long': '#ff6b6b'
        }
        
        for prompt_type, color in colors.items():
            # 成功率数据集
            success_data = [row['success_rate'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'成功率 ({prompt_type})',
                'data': success_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)'),
                'borderColor': color,
                'borderWidth': 2,
                'borderRadius': 6
            })
            
            # 错误率数据集
            error_data = [row['error_rate'] for row in self.grouped_data[prompt_type]]
            datasets.append({
                'label': f'错误率 ({prompt_type})',
                'data': error_data,
                'backgroundColor': color.replace('#', 'rgba(').replace(')', ', 0.8)').replace('667eea', 'ff6b6b').replace('28a745', 'ffc107').replace('ff6b6b', 'dc3545'),
                'borderColor': color.replace('#', '#').replace('667eea', 'ff6b6b').replace('28a745', 'ffc107').replace('ff6b6b', 'dc3545'),
                'borderWidth': 2,
                'borderRadius': 6
            })
        
        return {
            'type': 'bar',
            'data': {
                'labels': parallels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'padding': 12,
                        'titleFont': {'size': 14},
                        'bodyFont': {'size': 13}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': '并发数',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': '百分比 (%)',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': True,
                        'max': 100
                    }
                }
            }
        }
