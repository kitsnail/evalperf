#!/usr/bin/env python3
"""
数据加载和处理模块
Author: AI Assistant
Date: 2024
"""

import csv
from pathlib import Path
from typing import List, Dict


class DataLoader:
    """性能测试数据加载器"""
    
    def __init__(self, csv_file: str):
        self.csv_file = Path(csv_file)
        self.data: List[Dict] = []
        
    def load_data(self) -> bool:
        """
        加载 CSV 数据
        Returns:
            bool: 加载是否成功
        """
        print(f"[INFO] 加载数据: {self.csv_file}")
        
        if not self.csv_file.exists():
            print(f"[ERROR] 文件不存在: {self.csv_file}")
            return False
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        except Exception as e:
            print(f"[ERROR] 读取文件失败: {e}")
            return False
        
        # 转换数值类型
        for row in self.data:
            for key in row:
                if key in ['test_name', 'prompt_type', 'test_time', 'config', 'model', 'timestamp']:
                    continue
                try:
                    if '.' in str(row[key]):
                        row[key] = float(row[key])
                    else:
                        row[key] = int(row[key])
                except (ValueError, KeyError):
                    pass
        
        # 适配数据格式
        self._adapt_data_format()
        
        print(f"[INFO] 已加载 {len(self.data)} 条记录")
        return len(self.data) > 0
    
    def _adapt_data_format(self):
        """适配CSV数据格式到期望的格式"""
        if not self.data:
            return
        
        for row in self.data:
            # 检查是否需要适配
            if 'qps' in row:
                continue  # 已经是正确格式
            
            # 计算QPS (每秒请求数)
            if 'request_throughput' in row:
                row['qps'] = row['request_throughput']
            elif 'requests' in row and 'time_taken' in row:
                row['qps'] = row['requests'] / row['time_taken'] if row['time_taken'] > 0 else 0
            else:
                row['qps'] = 0
            
            # 映射列名
            if 'latency' in row:
                row['avg_latency_ms'] = row['latency']
            
            if 'ttft' in row:
                row['avg_ttft_ms'] = row['ttft']
            
            if 'output_throughput' in row:
                row['output_token_throughput'] = row['output_throughput']
            
            if 'requests' in row:
                row['num_requests'] = row['requests']
            
            if 'config' in row:
                row['test_name'] = row['config']
            else:
                row['test_name'] = f"test_{row.get('parallel', 0)}"
            
            # 处理百分位数延迟
            if '50p_latency_' in row:
                row['p50_latency_ms'] = row['50p_latency_']
            else:
                row['p50_latency_ms'] = row.get('latency', 0)
            
            if '95p_latency_' in row:
                row['p95_latency_ms'] = row['95p_latency_']
            else:
                row['p95_latency_ms'] = row.get('latency', 0)
            
            if '99p_latency_' in row:
                row['p99_latency_ms'] = row['99p_latency_']
            else:
                row['p99_latency_ms'] = row.get('latency', 0)
            
            # 设置成功率和错误率（默认值，因为数据中没有明显的错误信息）
            row['success_rate'] = 100.0  # 假设所有请求都成功
            row['error_rate'] = 0.0      # 假设没有错误
            
            # 确保数值类型
            numeric_fields = [
                'qps', 'avg_latency_ms', 'avg_ttft_ms', 'output_token_throughput',
                'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms',
                'success_rate', 'error_rate', 'num_requests', 'parallel'
            ]
            
            for field in numeric_fields:
                if field in row and isinstance(row[field], str):
                    try:
                        if '.' in row[field]:
                            row[field] = float(row[field])
                        else:
                            row[field] = int(row[field])
                    except (ValueError, TypeError):
                        row[field] = 0
                elif field not in row:
                    row[field] = 0
    
    def get_data(self) -> List[Dict]:
        """获取加载的数据"""
        return self.data
    
    def get_file_info(self) -> Dict:
        """获取文件信息"""
        return {
            'name': self.csv_file.name,
            'path': str(self.csv_file.absolute()),
            'size': self.csv_file.stat().st_size if self.csv_file.exists() else 0,
            'record_count': len(self.data)
        }
