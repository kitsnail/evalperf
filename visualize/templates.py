#!/usr/bin/env python3
"""
HTML模板和样式模块
Author: AI Assistant
Date: 2024
"""

from typing import Dict, List
from datetime import datetime


class HTMLTemplates:
    """HTML模板生成器"""
    
    @staticmethod
    def get_css_styles() -> str:
        """获取CSS样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }
        
        .stat-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2.2em;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9em;
        }
        
        .charts-section {
            padding: 40px;
        }
        
        .chart-container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .chart-container h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }
        
        .chart-wrapper {
            position: relative;
            height: 400px;
        }
        
        .table-container {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .table-container h2 {
            color: #333;
            margin-bottom: 30px;
            font-size: 1.5em;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }
        
        .table-section {
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .table-section h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.2em;
            font-weight: 600;
            border-left: 4px solid #667eea;
            padding-left: 12px;
        }
        
        table {
            width: 100%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .success {
            color: #28a745;
            font-weight: 600;
        }
        
        .warning {
            color: #ffc107;
            font-weight: 600;
        }
        
        .danger {
            color: #dc3545;
            font-weight: 600;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            table {
                font-size: 0.85em;
            }
        }
        """
    
    @staticmethod
    def get_header() -> str:
        """获取HTML头部"""
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>性能测试分析报告</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
            <style>
                {HTMLTemplates.get_css_styles()}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- 头部 -->
                <div class="header">
                    <h1>🚀 性能测试分析报告</h1>
                    <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
        """
    
    @staticmethod
    def get_stats_cards(stats: Dict) -> str:
        """获取统计卡片HTML"""
        return f"""
                <!-- 关键指标卡片 -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>最高 QPS</h3>
                        <div class="value">{stats.get('max_qps', 0):.2f}</div>
                        <div class="label">并发数: {stats.get('max_qps_parallel', 0)}</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>最高吞吐量</h3>
                        <div class="value">{stats.get('max_throughput', 0):.0f}</div>
                        <div class="label">tokens/s</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>最低延迟</h3>
                        <div class="value">{stats.get('min_latency', 0):.0f}</div>
                        <div class="label">毫秒</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>平均成功率</h3>
                        <div class="value">{stats.get('avg_success_rate', 0):.1f}%</div>
                        <div class="label">总测试: {stats.get('total_tests', 0)} 组</div>
                    </div>
                </div>
        """
    
    @staticmethod
    def get_charts_section() -> str:
        """获取图表区域HTML"""
        return """
                <!-- 图表区域 -->
                <div class="charts-section">
                    <!-- QPS 趋势 -->
                    <div class="chart-container">
                        <h2>📊 QPS 随并发数变化趋势</h2>
                        <div class="chart-wrapper">
                            <canvas id="qpsChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 吞吐量趋势 -->
                    <div class="chart-container">
                        <h2>📈 Token 吞吐量趋势</h2>
                        <div class="chart-wrapper">
                            <canvas id="throughputChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 延迟分析 -->
                    <div class="chart-container">
                        <h2>⏱️ 延迟分析 (P50/P95/P99)</h2>
                        <div class="chart-wrapper">
                            <canvas id="latencyChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- TTFT 分析 -->
                    <div class="chart-container">
                        <h2>🎯 首Token延迟 (TTFT)</h2>
                        <div class="chart-wrapper">
                            <canvas id="ttftChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 成功率 -->
                    <div class="chart-container">
                        <h2>✅ 成功率与错误率</h2>
                        <div class="chart-wrapper">
                            <canvas id="successChart"></canvas>
                        </div>
                    </div>
                </div>
        """
    
    @staticmethod
    def get_table_section(data: List[Dict]) -> str:
        """获取数据表格HTML - 按提示词类型分组"""
        
        # 按提示词类型分组数据
        short_data = [row for row in data if 'short' in row['test_name']]
        medium_data = [row for row in data if 'medium' in row['test_name']]
        long_data = [row for row in data if 'long' in row['test_name']]
        
        def generate_table_rows(data_list: List[Dict]) -> str:
            rows = ""
            for row in data_list:
                success_class = 'success' if row['success_rate'] >= 95 else ('warning' if row['success_rate'] >= 90 else 'danger')
                error_class = 'success' if row['error_rate'] == 0 else ('warning' if row['error_rate'] < 5 else 'danger')
                
                rows += f"""
                        <tr>
                            <td>{row['parallel']}</td>
                            <td>{row['num_requests']}</td>
                            <td>{row['qps']:.2f}</td>
                            <td>{row['output_token_throughput']:.0f}</td>
                            <td>{row['avg_latency_ms']:.0f}</td>
                            <td>{row['p95_latency_ms']:.0f}</td>
                            <td>{row['p99_latency_ms']:.0f}</td>
                            <td>{row['avg_ttft_ms']:.0f}</td>
                            <td class="{success_class}">{row['success_rate']:.1f}%</td>
                            <td class="{error_class}">{row['error_rate']:.1f}%</td>
                        </tr>
                """
            return rows
        
        return f"""
                <!-- 详细数据表 - 分组显示 -->
                <div class="table-container">
                    <h2>📋 详细测试数据</h2>
                    
                    <!-- Short Prompt Type -->
                    <div class="table-section">
                        <h3>🔵 Short 提示词测试数据</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>并发</th>
                                    <th>请求数</th>
                                    <th>QPS</th>
                                    <th>吞吐量<br>(tok/s)</th>
                                    <th>平均延迟<br>(ms)</th>
                                    <th>P95延迟<br>(ms)</th>
                                    <th>P99延迟<br>(ms)</th>
                                    <th>TTFT<br>(ms)</th>
                                    <th>成功率</th>
                                    <th>错误率</th>
                                </tr>
                            </thead>
                            <tbody>
                                {generate_table_rows(short_data)}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Medium Prompt Type -->
                    <div class="table-section">
                        <h3>🟢 Medium 提示词测试数据</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>并发</th>
                                    <th>请求数</th>
                                    <th>QPS</th>
                                    <th>吞吐量<br>(tok/s)</th>
                                    <th>平均延迟<br>(ms)</th>
                                    <th>P95延迟<br>(ms)</th>
                                    <th>P99延迟<br>(ms)</th>
                                    <th>TTFT<br>(ms)</th>
                                    <th>成功率</th>
                                    <th>错误率</th>
                                </tr>
                            </thead>
                            <tbody>
                                {generate_table_rows(medium_data)}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Long Prompt Type -->
                    <div class="table-section">
                        <h3>🔴 Long 提示词测试数据</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>并发</th>
                                    <th>请求数</th>
                                    <th>QPS</th>
                                    <th>吞吐量<br>(tok/s)</th>
                                    <th>平均延迟<br>(ms)</th>
                                    <th>P95延迟<br>(ms)</th>
                                    <th>P99延迟<br>(ms)</th>
                                    <th>TTFT<br>(ms)</th>
                                    <th>成功率</th>
                                    <th>错误率</th>
                                </tr>
                            </thead>
                            <tbody>
                                {generate_table_rows(long_data)}
                            </tbody>
                        </table>
                    </div>
                </div>
        """
    
    @staticmethod
    def get_footer(file_name: str) -> str:
        """获取HTML底部"""
        return f"""
                <!-- 页脚 -->
                <div class="footer">
                    <p>性能测试分析报告 | 数据来源: {file_name}</p>
                </div>
            </div>
        """
    
    @staticmethod
    def get_chart_js_scripts(chart_configs: Dict) -> str:
        """获取Chart.js脚本"""
        scripts = """
            <script>
                // Chart.js 配置
                Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
                Chart.defaults.color = '#666';
                
                const parallels = """ + chart_configs.get('parallels', '[]') + """;
        """
        
        # QPS图表
        if 'qps' in chart_configs:
            scripts += f"""
                // QPS 图表
                new Chart(document.getElementById('qpsChart'), {chart_configs['qps']});
            """
        
        # 吞吐量图表
        if 'throughput' in chart_configs:
            scripts += f"""
                // 吞吐量图表
                new Chart(document.getElementById('throughputChart'), {chart_configs['throughput']});
            """
        
        # 延迟图表
        if 'latency' in chart_configs:
            scripts += f"""
                // 延迟图表
                new Chart(document.getElementById('latencyChart'), {chart_configs['latency']});
            """
        
        # TTFT图表
        if 'ttft' in chart_configs:
            scripts += f"""
                // TTFT 图表
                new Chart(document.getElementById('ttftChart'), {chart_configs['ttft']});
            """
        
        # 成功率图表
        if 'success' in chart_configs:
            scripts += f"""
                // 成功率图表
                new Chart(document.getElementById('successChart'), {chart_configs['success']});
            """
        
        scripts += """
            </script>
        </body>
        </html>
        """
        
        return scripts
