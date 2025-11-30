#!/usr/bin/env python3
"""
统计计算模块
Author: AI Assistant
Date: 2024
"""

from typing import List, Dict, Tuple


class StatisticsCalculator:
    """性能测试统计计算器"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
    
    def calculate_basic_stats(self) -> Dict:
        """
        计算基本统计信息
        Returns:
            Dict: 包含最大QPS、吞吐量、最小延迟、平均成功率等的字典
        """
        if not self.data:
            return {}
        
        # 提取数据
        parallels = [row['parallel'] for row in self.data]
        qps_data = [row['qps'] for row in self.data]
        throughput_data = [row['output_token_throughput'] for row in self.data]
        latency_data = [row['avg_latency_ms'] for row in self.data]
        success_rate = [row['success_rate'] for row in self.data]
        
        # 计算统计信息
        max_qps = max(qps_data)
        max_qps_idx = qps_data.index(max_qps)
        max_throughput = max(throughput_data)
        min_latency = min(latency_data)
        avg_success = sum(success_rate) / len(success_rate)
        
        return {
            'max_qps': max_qps,
            'max_qps_parallel': parallels[max_qps_idx],
            'max_throughput': max_throughput,
            'min_latency': min_latency,
            'avg_success_rate': avg_success,
            'total_tests': len(self.data)
        }
    
    def calculate_percentiles(self) -> Dict[str, List[float]]:
        """
        计算各种百分位数的延迟
        Returns:
            Dict: 包含P50、P95、P99延迟的字典
        """
        return {
            'p50_latency': [row['p50_latency_ms'] for row in self.data],
            'p95_latency': [row['p95_latency_ms'] for row in self.data],
            'p99_latency': [row['p99_latency_ms'] for row in self.data]
        }
    
    def calculate_throughput_stats(self) -> Dict:
        """
        计算吞吐量相关统计
        Returns:
            Dict: 包含吞吐量统计信息的字典
        """
        throughput_data = [row['output_token_throughput'] for row in self.data]
        
        return {
            'max_throughput': max(throughput_data),
            'min_throughput': min(throughput_data),
            'avg_throughput': sum(throughput_data) / len(throughput_data),
            'total_tokens': sum(throughput_data)
        }
    
    def calculate_latency_stats(self) -> Dict:
        """
        计算延迟相关统计
        Returns:
            Dict: 包含延迟统计信息的字典
        """
        latency_data = [row['avg_latency_ms'] for row in self.data]
        ttft_data = [row['avg_ttft_ms'] for row in self.data]
        
        return {
            'min_avg_latency': min(latency_data),
            'max_avg_latency': max(latency_data),
            'avg_avg_latency': sum(latency_data) / len(latency_data),
            'min_ttft': min(ttft_data),
            'max_ttft': max(ttft_data),
            'avg_ttft': sum(ttft_data) / len(ttft_data)
        }
    
    def calculate_success_stats(self) -> Dict:
        """
        计算成功率相关统计
        Returns:
            Dict: 包含成功率统计信息的字典
        """
        success_rate = [row['success_rate'] for row in self.data]
        error_rate = [row['error_rate'] for row in self.data]
        
        return {
            'avg_success_rate': sum(success_rate) / len(success_rate),
            'min_success_rate': min(success_rate),
            'max_success_rate': max(success_rate),
            'avg_error_rate': sum(error_rate) / len(error_rate),
            'max_error_rate': max(error_rate)
        }
    
    def get_performance_summary(self) -> Dict:
        """
        获取性能测试汇总信息
        Returns:
            Dict: 包含所有性能指标的汇总信息
        """
        if not self.data:
            return {}
        
        basic_stats = self.calculate_basic_stats()
        throughput_stats = self.calculate_throughput_stats()
        latency_stats = self.calculate_latency_stats()
        success_stats = self.calculate_success_stats()
        
        return {
            **basic_stats,
            **throughput_stats,
            **latency_stats,
            **success_stats
        }
