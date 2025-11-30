#!/usr/bin/env python3
"""
Evalscope 测试结果可视化脚本

功能：
1. 读取汇总后的测试数据（CSV或JSON格式）
2. 生成HTML可视化报告，包含多种图表
3. 支持原始数据和统计数据的可视化
4. 提供交互式图表和数据筛选功能

使用方式：
python evalscope_visualizer.py --input summary_stats.csv --output visualization.html
python evalscope_visualizer.py --input summary_raw.json --output visualization.html
"""

import os
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Any, Union
import html


class EvalscopeVisualizer:
    """Evalscope测试结果可视化器"""
    
    def __init__(self, input_file: str):
        self.input_file = Path(input_file)
        self.data = []
        self.data_type = None
        
    def load_data(self) -> None:
        """加载数据文件"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.input_file}")
        
        file_ext = self.input_file.suffix.lower()
        
        if file_ext == '.json':
            self._load_json()
        elif file_ext == '.csv':
            self._load_csv()
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        print(f"成功加载 {len(self.data)} 条数据记录")
        
    def _load_json(self) -> None:
        """加载JSON格式数据"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            self.data = data
        else:
            self.data = [data]
        
        # 判断数据类型
        if self.data and 'config' in self.data[0] and 'count' in self.data[0]:
            self.data_type = 'stats'
        else:
            self.data_type = 'raw'
    
    def _load_csv(self) -> None:
        """加载CSV格式数据"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        
        # 判断数据类型
        if self.data and 'config' in self.data[0] and 'count' in self.data[0]:
            self.data_type = 'stats'
        else:
            self.data_type = 'raw'
        
        # 转换数值字段
        self._convert_numeric_fields()
    
    def _convert_numeric_fields(self) -> None:
        """转换数值字段为数字类型"""
        numeric_fields = [
            'output_throughput', 'total_throughput', 'request_throughput',
            'latency', 'ttft', 'token_latency', 'inter_token_latency',
            'input_tokens', 'output_tokens', 'time_taken', 'parallel',
            'max_tokens', 'requests', 'avg_gpu_memory', 'max_gpu_memory', 
            'min_gpu_memory', 'count'
        ]
        
        # 添加可能的统计字段
        if self.data_type == 'stats':
            for field in numeric_fields:
                numeric_fields.extend([f'{field}_avg', f'{field}_std', 
                                      f'{field}_min', f'{field}_max'])
        
        # 添加百分位数字段
        percentile_prefixes = ['p10_', 'p25_', 'p50_', 'p66_', 'p75_', 
                              'p80_', 'p90_', 'p95_', 'p98_', 'p99_']
        for record in self.data:
            for key in record.keys():
                if any(key.startswith(prefix) for prefix in percentile_prefixes):
                    if key not in numeric_fields:
                        numeric_fields.append(key)
        
        for record in self.data:
            for field in numeric_fields:
                if field in record and record[field] != '':
                    try:
                        record[field] = float(record[field])
                    except (ValueError, TypeError):
                        record[field] = 0.0
    
    def generate_html(self, output_file: str) -> None:
        """生成HTML可视化报告"""
        html_content = self._build_html()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML可视化报告已生成: {output_file}")
    
    def _build_html(self) -> str:
        """构建HTML内容"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evalscope 性能测试可视化报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .info-bar {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .info-item {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .info-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .info-value {{
            font-size: 1.2em;
            font-weight: 600;
        }}
        
        .controls {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        select, button {{
            padding: 10px 15px;
            border: 2px solid #e1e1e3;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        select:hover, button:hover {{
            border-color: #667eea;
            transform: translateY(-1px);
        }}
        
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }}
        
        button:hover {{
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .chart-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #1d1d1f;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .chart-icon {{
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        
        canvas {{
            max-height: 400px;
        }}
        
        .data-table {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e1e3;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .numeric {{
            text-align: right;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        
        .highlight {{
            background: #fff3cd;
            font-weight: 600;
        }}
        
        .metric-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .metric-change {{
            font-size: 0.8em;
            margin-top: 5px;
            padding: 2px 8px;
            border-radius: 4px;
            background: #e8f5e8;
            color: #28a745;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .info-bar {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Evalscope 性能测试可视化报告</h1>
            <div class="subtitle">基于 {self.input_file.name} 的性能分析</div>
            <div class="info-bar">
                <div class="info-item">
                    <div class="info-label">数据类型</div>
                    <div class="info-value">{'统计数据' if self.data_type == 'stats' else '原始数据'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">记录数量</div>
                    <div class="info-value">{len(self.data)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">配置数量</div>
                    <div class="info-value">{len(set(record.get('config', 'unknown') for record in self.data))}</div>
                </div>
            </div>
        </header>

        <div class="controls">
            <select id="configFilter">
                <option value="">所有配置</option>
                {self._get_config_options()}
            </select>
            <select id="chartType">
                <option value="bar">柱状图</option>
                <option value="line">折线图</option>
                <option value="radar">雷达图</option>
                <option value="scatter">散点图</option>
            </select>
            <button onclick="updateCharts()">🔄 更新图表</button>
            <button onclick="exportData()">📊 导出数据</button>
        </div>

        <div class="metric-summary" id="metricSummary">
            {self._generate_metric_summary()}
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">📈</div>
                    吞吐量性能对比
                </div>
                <canvas id="throughputChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">⏱️</div>
                    延迟性能分析
                </div>
                <canvas id="latencyChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">🔤</div>
                    Token 处理效率
                </div>
                <canvas id="tokenChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">💾</div>
                    GPU 内存使用情况
                </div>
                <canvas id="memoryChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">📊</div>
                    百分位数延迟分布
                </div>
                <canvas id="percentileChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">
                    <div class="chart-icon">⚡</div>
                    综合性能雷达图
                </div>
                <canvas id="radarChart"></canvas>
            </div>
        </div>

        <div class="data-table">
            <div class="chart-title">
                <div class="chart-icon">📋</div>
                详细数据表
            </div>
            <table id="dataTable">
                {self._generate_data_table()}
            </table>
        </div>

        <footer class="footer">
            <p>📅 报告生成时间: {self._get_current_time()} | 🔧 Powered by Evalscope & Chart.js</p>
        </footer>
    </div>

    <script>
        // 数据存储
        const rawData = {json.dumps(self.data, ensure_ascii=False)};
        let filteredData = [...rawData];
        
        // Chart.js 全局配置
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.color = '#1d1d1f';
        
        // 图表实例存储
        let charts = {{}};
        
        // 初始化所有图表
        function initCharts() {{
            initThroughputChart();
            initLatencyChart();
            initTokenChart();
            initMemoryChart();
            initPercentileChart();
            initRadarChart();
        }}
        
        // 吞吐量图表
        function initThroughputChart() {{
            const ctx = document.getElementById('throughputChart').getContext('2d');
            const config = filteredData.length > 0 ? Object.keys(filteredData[0]).filter(k => k.includes('throughput')) : [];
            
            charts.throughput = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: filteredData.map(d => d.config || d.model || 'Unknown'),
                    datasets: config.map((field, index) => ({{
                        label: field.replace(/_/g, ' ').replace(/avg/g, '平均').replace(/min/g, '最小').replace(/max/g, '最大'),
                        data: filteredData.map(d => d[field] || 0),
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)'
                        ][index % 4],
                        borderColor: [
                            'rgba(102, 126, 234
