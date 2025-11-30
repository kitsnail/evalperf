# 性能测试可视化分析工具 - 模块化版本

## 重构概述

原始的 `visualize_perf_report.py` 已经被重构为一个模块化的架构，具有更好的可维护性和扩展性。

## 文件结构

```
visualize/
├── __init__.py              # 模块初始化，导出主要类
├── cli.py                  # 命令行入口文件
├── main.py                 # 主逻辑文件，包含参数解析和主要功能
├── data_loader.py          # CSV数据加载和处理模块
├── statistics.py           # 统计计算模块
├── chart_data.py           # 图表数据提取和配置模块
├── templates.py            # HTML模板和样式模块
├── html_generator.py       # HTML报告生成模块
├── visualizer.py           # 主要的可视化器类
└── README.md              # 本文档
```

## 模块说明

### 1. DataLoader (data_loader.py)
- 负责CSV文件的加载和基本处理
- 自动类型转换（字符串转数字）
- 文件验证和错误处理

### 2. StatisticsCalculator (statistics.py)
- 计算各种性能统计指标
- 支持基本统计、延迟分析、吞吐量统计、成功率分析等
- 提供完整的性能摘要

### 3. ChartDataExtractor (chart_data.py)
- 提取和准备图表数据
- 生成Chart.js配置对象
- 支持多种图表类型（线图、柱状图）

### 4. HTMLTemplates (templates.py)
- 提供HTML模板和CSS样式
- 模块化的HTML组件生成
- 响应式设计支持

### 5. HTMLGenerator (html_generator.py)
- 整合所有组件生成完整的HTML报告
- 协调统计信息和图表配置
- 处理文件输出

### 6. PerformanceVisualizer (visualizer.py)
- 主要的可视化器类
- 协调各个模块的工作
- 提供高级API接口

## 使用方法

### 基本用法

```bash
# 从 visualize 目录运行
cd visualize
python cli.py data.csv

# 从项目根目录运行
python -m visualize data.csv
```

### 命令行选项

```bash
python cli.py data.csv                    # 使用默认输出文件名
python cli.py data.csv -o report.html   # 自定义输出文件名
python cli.py data.csv --info           # 只显示数据信息
python cli.py data.csv --summary        # 只显示性能摘要
python cli.py data.csv --help           # 显示帮助信息
```

### 编程接口

```python
from visualize import PerformanceVisualizer

# 创建可视化器实例
visualizer = PerformanceVisualizer('data.csv', 'output.html')

# 加载数据
if visualizer.load_data():
    # 生成报告
    html_file = visualizer.generate_html()
    print(f"报告已生成: {html_file}")
    
    # 获取数据信息
    info = visualizer.get_data_info()
    print(f"记录数: {info['record_count']}")
    
    # 获取性能摘要
    summary = visualizer.get_performance_summary()
    print(f"最高QPS: {summary['max_qps']}")
```

## 数据格式要求

### 当前支持格式
工具当前期望CSV文件包含以下列名：

- `test_name` - 测试名称
- `parallel` - 并发数
- `qps` - 每秒请求数
- `output_token_throughput` - Token吞吐量
- `avg_latency_ms` - 平均延迟（毫秒）
- `avg_ttft_ms` - 首Token延迟（毫秒）
- `p50_latency_ms` - P50延迟
- `p95_latency_ms` - P95延迟
- `p99_latency_ms` - P99延迟
- `success_rate` - 成功率（百分比）
- `error_rate` - 错误率（百分比）
- `num_requests` - 请求数量

### 数据适配
如果您的CSV文件使用不同的列名，您可以通过以下方式适配：

1. **预处理CSV文件**：在加载数据前重命名列
2. **创建适配器**：继承DataLoader类并重写数据处理逻辑
3. **转换数据**：使用pandas等工具转换数据格式

## 扩展性

模块化设计使得以下扩展变得容易：

1. **新增图表类型**：在ChartDataExtractor中添加新的图表配置方法
2. **自定义统计指标**：在StatisticsCalculator中添加新的计算方法
3. **修改样式**：在HTMLTemplates中修改CSS样式
4. **添加输出格式**：创建新的生成器类（如PDF生成器）

## 测试

```bash
# 测试帮助信息
python cli.py --help

# 测试数据信息显示
python cli.py ../perf_results/summary_raw.csv --info

# 测试摘要显示
python cli.py ../perf_results/summary_raw.csv --summary
```

## 错误处理

- 文件不存在或无法读取时显示错误信息
- 数据格式错误时提供详细错误提示
- 内存不足时给出优化建议
- 权限问题时提示解决方案

## 性能优化

- 流式处理大型CSV文件
- 按需生成图表数据
- 内存使用优化
- 缓存机制（可选）

## 与原版本对比

| 特性 | 原版本 | 重构版本 |
|------|---------|----------|
| 代码结构 | 单文件 | 多模块 |
| 可维护性 | 中等 | 高 |
| 可扩展性 | 低 | 高 |
| 测试能力 | 困难 | 容易 |
| 错误处理 | 基础 | 完善 |
| 代码复用 | 有限 | 良好 |

## 贡献指南

1. 遵循现有的模块结构
2. 添加适当的文档和注释
3. 实现错误处理
4. 考虑性能影响
5. 编写测试用例

## 许可证

与原项目保持一致的许可证。
