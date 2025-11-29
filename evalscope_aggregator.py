#!/usr/bin/env python3
"""
Evalscope 测试结果数据汇总脚本

功能：
1. 递归扫描results目录，自动发现所有测试结果
2. 提取benchmark_summary.json和benchmark_args.json的原始数据
3. 标准化数据格式，合并为统一记录
4. 对相同配置的多次运行计算统计指标
5. 支持CSV和JSON格式导出

使用方式：
python evalscope_aggregator.py --results-dir ./results --format csv --output summary.csv
"""

import os
import json
import csv
import argparse
import statistics
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple


class EvalscopeDataAggregator:
    """Evalscope测试结果数据汇总器"""
    
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.raw_data = []
        self.aggregated_data = {}
    
    def scan_results_directory(self) -> List[Path]:
        """扫描results目录，返回所有有效的测试结果目录路径"""
        result_dirs = []
        
        if not self.results_dir.exists():
            print(f"错误：results目录不存在: {self.results_dir}")
            return result_dirs
        
        # 遍历配置目录 (如p32_n100_dp_long等)
        for config_dir in self.results_dir.iterdir():
            if not config_dir.is_dir():
                continue
                
            # 遍历时间戳目录
            for timestamp_dir in config_dir.iterdir():
                if not timestamp_dir.is_dir():
                    continue
                    
                # 遍历模型目录
                for model_dir in timestamp_dir.iterdir():
                    if not model_dir.is_dir():
                        continue
                    
                    # 检查是否包含必需的文件
                    summary_file = model_dir / "benchmark_summary.json"
                    args_file = model_dir / "benchmark_args.json"
                    
                    if summary_file.exists() and args_file.exists():
                        result_dirs.append(model_dir)
        
        return sorted(result_dirs)
    
    def extract_single_run(self, result_dir: Path) -> Dict[str, Any]:
        """提取单次运行的原始数据"""
        config = result_dir.parent.parent.name
        timestamp = result_dir.parent.name
        model = result_dir.name
        
        # 读取summary数据
        summary_file = result_dir / "benchmark_summary.json"
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        # 读取args数据
        args_file = result_dir / "benchmark_args.json"
        with open(args_file, 'r', encoding='utf-8') as f:
            args_data = json.load(f)
        
        # 读取百分位数数据
        percentile_data = {}
        percentile_file = result_dir / "benchmark_percentile.json"
        if percentile_file.exists():
            with open(percentile_file, 'r', encoding='utf-8') as f:
                percentile_list = json.load(f)
            for item in percentile_list:
                percentile = item.get('Percentiles', '').replace('%', 'p')
                for key, value in item.items():
                    if key != 'Percentiles':
                        percentile_data[f'{percentile}_{key.lower().replace(" ", "_").replace("(s)", "")}'] = value
        
        # 读取数据库中的详细数据
        db_data = {}
        db_file = result_dir / "benchmark_data.db"
        if db_file.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("SELECT AVG(max_gpu_memory_cost), MAX(max_gpu_memory_cost), MIN(max_gpu_memory_cost) FROM result")
                db_avg, db_max, db_min = cursor.fetchone()
                db_data = {
                    'avg_gpu_memory': db_avg or 0,
                    'max_gpu_memory': db_max or 0,
                    'min_gpu_memory': db_min or 0
                }
                conn.close()
            except Exception as e:
                print(f"警告：无法读取数据库 {db_file}: {e}")
        
        # 提取prompt长度（基于内容估算）
        prompt = args_data.get('prompt', '')
        prompt_length = 'long' if len(prompt) > 50 else 'short'
        
        # 合并数据为统一格式
        record = {
            # 基础信息
            'timestamp': timestamp,
            'config': config,
            'model': args_data.get('model', model),
            'parallel': args_data.get('parallel', 0),
            'prompt_length': prompt_length,
            'max_tokens': args_data.get('max_tokens', 0),
            'requests': summary_data.get('Total requests', 0),
            
            # 性能指标
            'time_taken': summary_data.get('Time taken for tests (s)', 0),
            'output_throughput': summary_data.get('Output token throughput (tok/s)', 0),
            'total_throughput': summary_data.get('Total token throughput (tok/s)', 0),
            'request_throughput': summary_data.get('Request throughput (req/s)', 0),
            
            # 延迟指标
            'latency': summary_data.get('Average latency (s)', 0),
            'ttft': summary_data.get('Average time to first token (s)', 0),
            'token_latency': summary_data.get('Average time per output token (s)', 0),
            'inter_token_latency': summary_data.get('Average inter-token latency (s)', 0),
            
            # Token指标
            'input_tokens': summary_data.get('Average input tokens per request', 0),
            'output_tokens': summary_data.get('Average output tokens per request', 0),
            
            # GPU内存指标
            'avg_gpu_memory': db_data.get('avg_gpu_memory', 0),
            'max_gpu_memory': db_data.get('max_gpu_memory', 0),
            'min_gpu_memory': db_data.get('min_gpu_memory', 0),
        }
        
        # 添加百分位数数据
        record.update(percentile_data)
        
        return record
    
    def collect_raw_data(self) -> None:
        """收集所有原始数据"""
        result_dirs = self.scan_results_directory()
        
        if not result_dirs:
            print("未找到任何有效的测试结果目录")
            return
        
        print(f"发现 {len(result_dirs)} 个测试结果目录")
        
        for result_dir in result_dirs:
            try:
                record = self.extract_single_run(result_dir)
                self.raw_data.append(record)
                print(f"已处理: {result_dir.parent.parent.name}/{result_dir.parent.name}")
            except Exception as e:
                print(f"处理目录 {result_dir} 时出错: {e}")
        
        print(f"成功收集 {len(self.raw_data)} 条原始数据记录")
    
    def aggregate_by_config(self) -> Dict[str, List[Dict[str, Any]]]:
        """按配置分组汇总数据"""
        aggregated = {}
        
        for record in self.raw_data:
            config = record['config']
            if config not in aggregated:
                aggregated[config] = []
            aggregated[config].append(record)
        
        return aggregated
    
    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """计算统计指标"""
        if not values:
            return {'count': 0, 'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        if len(values) == 1:
            return {
                'count': 1,
                'mean': values[0],
                'std': 0,
                'min': values[0],
                'max': values[0]
            }
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'std': statistics.stdev(values),
            'min': min(values),
            'max': max(values)
        }
    
    def calculate_aggregated_statistics(self) -> List[Dict[str, Any]]:
        """计算汇总统计信息"""
        self.aggregated_data = self.aggregate_by_config()
        stats_list = []
        
        for config, records in self.aggregated_data.items():
            if not records:
                continue
            
            # 提取数值字段进行统计
            numeric_fields = [
                'output_throughput', 'total_throughput', 'request_throughput',
                'latency', 'ttft', 'token_latency', 'inter_token_latency',
                'input_tokens', 'output_tokens', 'time_taken',
                'avg_gpu_memory', 'max_gpu_memory', 'min_gpu_memory'
            ]
            
            # 添加百分位数字段
            percentile_fields = []
            for record in records:
                for key in record.keys():
                    if key.startswith(('p10_', 'p25_', 'p50_', 'p66_', 'p75_', 'p80_', 'p90_', 'p95_', 'p98_', 'p99_')):
                        if key not in percentile_fields:
                            percentile_fields.append(key)
            
            numeric_fields.extend(percentile_fields)
            
            stats_record = {
                'config': config,
                'count': len(records),
                'model': records[0]['model'],
                'parallel': records[0]['parallel'],
                'prompt_length': records[0]['prompt_length'],
                'max_tokens': records[0]['max_tokens']
            }
            
            # 为每个数值字段计算统计指标
            for field in numeric_fields:
                values = [record[field] for record in records if record[field] is not None]
                field_stats = self.calculate_statistics(values)
                
                # 添加到统计记录中
                stats_record[f'{field}_avg'] = field_stats['mean']
                stats_record[f'{field}_std'] = field_stats['std']
                stats_record[f'{field}_min'] = field_stats['min']
                stats_record[f'{field}_max'] = field_stats['max']
            
            stats_list.append(stats_record)
        
        return stats_list
    
    def export_csv(self, filename: str, data_type: str = 'raw') -> None:
        """导出为CSV格式"""
        if data_type == 'raw' and not self.raw_data:
            print("没有原始数据可导出")
            return
        
        if data_type == 'stats':
            stats_data = self.calculate_aggregated_statistics()
            if not stats_data:
                print("没有统计数据可导出")
                return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if data_type == 'raw':
                fieldnames = list(self.raw_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.raw_data)
            else:
                fieldnames = list(stats_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(stats_data)
        
        print(f"已导出 {data_type} 数据到: {filename}")
    
    def export_json(self, filename: str, data_type: str = 'raw') -> None:
        """导出为JSON格式"""
        if data_type == 'raw' and not self.raw_data:
            print("没有原始数据可导出")
            return
        
        if data_type == 'stats':
            stats_data = self.calculate_aggregated_statistics()
            if not stats_data:
                print("没有统计数据可导出")
                return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            if data_type == 'raw':
                json.dump(self.raw_data, jsonfile, indent=2, ensure_ascii=False)
            else:
                json.dump(stats_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"已导出 {data_type} 数据到: {filename}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Evalscope测试结果数据汇总脚本')
    parser.add_argument('--results-dir', default='./results', 
                       help='results目录路径 (默认: ./results)')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='输出格式 (默认: csv)')
    parser.add_argument('--output', default='summary',
                       help='输出文件名前缀 (默认: summary)')
    parser.add_argument('--data-type', choices=['raw', 'stats', 'both'], default='both',
                       help='数据类型：raw=原始数据, stats=统计数据, both=两者 (默认: both)')
    
    args = parser.parse_args()
    
    # 创建汇总器
    aggregator = EvalscopeDataAggregator(args.results_dir)
    
    # 收集数据
    aggregator.collect_raw_data()
    
    if not aggregator.raw_data:
        print("没有找到任何数据，脚本退出")
        return
    
    # 导出数据
    if args.data_type in ['raw', 'both']:
        if args.format == 'csv':
            aggregator.export_csv(f"{args.output}_raw.csv", 'raw')
        else:
            aggregator.export_json(f"{args.output}_raw.json", 'raw')
    
    if args.data_type in ['stats', 'both']:
        if args.format == 'csv':
            aggregator.export_csv(f"{args.output}_stats.csv", 'stats')
        else:
            aggregator.export_json(f"{args.output}_stats.json", 'stats')
    
    print("数据汇总完成！")


if __name__ == "__main__":
    main()
