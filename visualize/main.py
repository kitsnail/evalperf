#!/usr/bin/env python3
"""
性能测试结果可视化分析工具 - 主入口文件
Author: AI Assistant
Date: 2024
"""

import argparse
import sys
from pathlib import Path
from visualize.visualizer import PerformanceVisualizer


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='性能测试结果可视化分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s report.csv                           # 使用默认输出文件名
  %(prog)s report.csv -o custom_report.html     # 自定义输出文件名
  %(prog)s report_summary.csv                   # 使用精简版 CSV
        """
    )
    
    parser.add_argument(
        'csv_file', 
        help='CSV 数据文件路径'
    )
    
    parser.add_argument(
        '-o', '--output', 
        help='输出 HTML 文件路径'
    )
    
    parser.add_argument(
        '--info', 
        action='store_true',
        help='只显示数据信息，不生成报告'
    )
    
    parser.add_argument(
        '--summary', 
        action='store_true',
        help='只显示性能摘要，不生成报告'
    )
    
    return parser.parse_args()


def validate_csv_file(csv_file: str) -> bool:
    """
    验证CSV文件
    Args:
        csv_file: CSV文件路径
    Returns:
        bool: 文件是否有效
    """
    file_path = Path(csv_file)
    
    if not file_path.exists():
        print(f"[ERROR] 文件不存在: {csv_file}")
        return False
    
    if not file_path.is_file():
        print(f"[ERROR] 路径不是文件: {csv_file}")
        return False
    
    if file_path.suffix.lower() != '.csv':
        print(f"[WARNING] 文件扩展名不是.csv: {csv_file}")
    
    return True


def display_data_info(visualizer: PerformanceVisualizer):
    """
    显示数据信息
    Args:
        visualizer: PerformanceVisualizer实例
    """
    info = visualizer.get_data_info()
    
    if not info:
        print("[ERROR] 无法获取数据信息")
        return
    
    print("=== 数据信息 ===")
    file_info = info.get('file_info', {})
    print(f"文件路径: {file_info.get('path', 'N/A')}")
    print(f"文件名: {file_info.get('name', 'N/A')}")
    print(f"文件大小: {file_info.get('size', 0)} 字节")
    print(f"记录数: {info.get('record_count', 0)} 条")
    
    columns = info.get('columns', [])
    if columns:
        print(f"数据列: {', '.join(columns)}")


def display_performance_summary(visualizer: PerformanceVisualizer):
    """
    显示性能摘要
    Args:
        visualizer: PerformanceVisualizer实例
    """
    summary = visualizer.get_performance_summary()
    
    if not summary:
        print("[ERROR] 无法获取性能摘要")
        return
    
    print("=== 性能摘要 ===")
    print(f"最高 QPS: {summary.get('max_qps', 0):.2f} (并发: {summary.get('max_qps_parallel', 0)})")
    print(f"最高吞吐量: {summary.get('max_throughput', 0):.0f} tokens/s")
    print(f"最低延迟: {summary.get('min_latency', 0):.0f} ms")
    print(f"平均成功率: {summary.get('avg_success_rate', 0):.1f}%")
    print(f"测试组数: {summary.get('total_tests', 0)}")
    
    # 延迟统计
    if 'min_ttft' in summary:
        print(f"TTFT范围: {summary.get('min_ttft', 0):.0f} - {summary.get('max_ttft', 0):.0f} ms")
    
    # 错误率统计
    if 'max_error_rate' in summary:
        print(f"最高错误率: {summary.get('max_error_rate', 0):.1f}%")


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 验证输入文件
    if not validate_csv_file(args.csv_file):
        sys.exit(1)
    
    # 创建可视化器实例
    visualizer = PerformanceVisualizer(
        csv_file=args.csv_file,
        output_file=args.output
    )
    
    # 加载数据
    if not visualizer.load_data():
        print("[ERROR] 无法加载数据")
        sys.exit(1)
    
    # 根据参数执行不同操作
    if args.info:
        display_data_info(visualizer)
    elif args.summary:
        display_performance_summary(visualizer)
    else:
        # 生成完整报告
        success = visualizer.run()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
