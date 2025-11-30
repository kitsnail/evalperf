#!/usr/bin/env python3
"""
性能测试可视化分析器主类
Author: AI Assistant
Date: 2024
"""

import sys
from pathlib import Path
from typing import List, Dict
from visualize.data_loader import DataLoader
from visualize.html_generator import HTMLGenerator


class PerformanceVisualizer:
    """性能测试可视化分析器"""
    
    def __init__(self, csv_file: str, output_file: str = None):
        self.csv_file = csv_file
        self.output_file = output_file or self._get_default_output_file()
        self.data: List[Dict] = []
        
        # 初始化组件
        self.data_loader = DataLoader(csv_file)
        self.html_generator = None
    
    def _get_default_output_file(self) -> str:
        """获取默认输出文件名"""
        csv_path = Path(self.csv_file)
        return str(csv_path.parent / f"{csv_path.stem}_report.html")
    
    def load_data(self) -> bool:
        """
        加载CSV数据
        Returns:
            bool: 加载是否成功
        """
        success = self.data_loader.load_data()
        if success:
            self.data = self.data_loader.get_data()
        return success
    
    def generate_html(self) -> Path:
        """
        生成HTML报告
        Returns:
            Path: 生成的HTML文件路径
        """
        if not self.data:
            raise ValueError("数据未加载，请先调用 load_data()")
        
        # 获取文件名
        file_name = Path(self.csv_file).name
        
        # 初始化HTML生成器
        self.html_generator = HTMLGenerator(self.data, self.output_file, file_name)
        
        # 生成报告
        return self.html_generator.generate_html_report()
    
    def run(self) -> bool:
        """
        运行完整的可视化流程
        Returns:
            bool: 运行是否成功
        """
        print("="*60)
        print("性能测试可视化分析")
        print("="*60)
        
        # 加载数据
        if not self.load_data():
            print("[ERROR] 无法加载数据")
            return False
        
        try:
            # 生成HTML报告
            html_file = self.generate_html()
            
            # 显示成功信息
            print("="*60)
            print(f"✓ 报告生成成功!")
            print(f"  文件: {html_file}")
            
            # 获取摘要信息
            if self.html_generator:
                summary = self.html_generator.get_report_summary()
                print(f"  数据源: {summary['data_source']}")
                print(f"  记录数: {summary['record_count']} 条")
                print(f"  图表数: {summary['charts_count']} 个")
                print(f"  文件大小: {summary['file_size_kb']:.1f} KB")
            
            print(f"\n打开方式:")
            print(f"  浏览器: file://{html_file.absolute()}")
            print(f"  命令行: xdg-open {html_file}  # Linux")
            print(f"          open {html_file}      # macOS")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 生成报告失败: {e}")
            return False
    
    def get_data_info(self) -> Dict:
        """
        获取数据信息
        Returns:
            Dict: 数据信息字典
        """
        if not self.data:
            return {}
        
        file_info = self.data_loader.get_file_info()
        
        return {
            'file_info': file_info,
            'record_count': len(self.data),
            'columns': list(self.data[0].keys()) if self.data else []
        }
    
    def get_performance_summary(self) -> Dict:
        """
        获取性能测试摘要
        Returns:
            Dict: 性能测试摘要
        """
        if not self.data:
            return {}
        
        from visualize.statistics import StatisticsCalculator
        stats_calc = StatisticsCalculator(self.data)
        return stats_calc.get_performance_summary()
