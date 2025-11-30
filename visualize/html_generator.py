#!/usr/bin/env python3
"""
HTML报告生成模块
Author: AI Assistant
Date: 2024
"""

import json
from pathlib import Path
from typing import List, Dict
from visualize.templates import HTMLTemplates
from visualize.statistics import StatisticsCalculator
from visualize.chart_data import ChartDataExtractor


class HTMLGenerator:
    """HTML报告生成器"""
    
    def __init__(self, data: List[Dict], output_file: str, file_name: str):
        self.data = data
        self.output_file = Path(output_file)
        self.file_name = file_name
        
        # 初始化组件
        self.stats_calculator = StatisticsCalculator(data)
        self.chart_data_extractor = ChartDataExtractor(data)
    
    def generate_html_report(self) -> Path:
        """
        生成完整的HTML报告
        Returns:
n            Path: 生成的HTML文件路径
        """
        print(f"[INFO] 生成 HTML 报告: {self.output_file}")
        
        # 获取统计信息
        stats = self.stats_calculator.calculate_basic_stats()
        
        # 获取图表配置
        chart_configs = self._get_chart_configurations()
        
        # 构建HTML内容
        html_content = self._build_html_content(stats, chart_configs)
        
        # 写入文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 计算文件大小
        file_size = self.output_file.stat().st_size / 1024
        print(f"[INFO] ✓ HTML 报告已生成")
        print(f"[INFO] 文件大小: {file_size:.1f} KB")
        
        return self.output_file
    
    def _get_chart_configurations(self) -> Dict:
        """
        获取所有图表配置
        Returns:
            Dict: 包含所有图表配置的字典
        """
        # 提取基础数据
        basic_data = self.chart_data_extractor.extract_basic_chart_data()
        
        return {
            'parallels': json.dumps(basic_data['parallels']),
            'qps': json.dumps(self.chart_data_extractor.get_qps_chart_config()),
            'throughput': json.dumps(self.chart_data_extractor.get_throughput_chart_config()),
            'latency': json.dumps(self.chart_data_extractor.get_latency_chart_config()),
            'ttft': json.dumps(self.chart_data_extractor.get_ttft_chart_config()),
            'success': json.dumps(self.chart_data_extractor.get_success_chart_config())
        }
    
    def _build_html_content(self, stats: Dict, chart_configs: Dict) -> str:
        """
        构建完整的HTML内容
        Args:
            stats: 统计信息
            chart_configs: 图表配置
        Returns:
            str: 完整的HTML内容
        """
        # 组装HTML各个部分，使用已排序的数据
        html_parts = [
            HTMLTemplates.get_header(),
            HTMLTemplates.get_stats_cards(stats),
            HTMLTemplates.get_charts_section(),
            HTMLTemplates.get_table_section(self.chart_data_extractor.data),  # 使用已排序的数据
            HTMLTemplates.get_footer(self.file_name),
            HTMLTemplates.get_chart_js_scripts(chart_configs)
        ]
        
        return '\n'.join(html_parts)
    
    def get_report_summary(self) -> Dict:
        """
        获取报告摘要信息
        Returns:
            Dict: 报告摘要信息
        """
        stats = self.stats_calculator.get_performance_summary()
        
        return {
            'output_file': str(self.output_file),
            'data_source': self.file_name,
            'record_count': len(self.data),
            'stats': stats,
            'charts_count': 5,  # QPS, 吞吐量, 延迟, TTFT, 成功率
            'file_size_kb': self.output_file.stat().st_size / 1024 if self.output_file.exists() else 0
        }
