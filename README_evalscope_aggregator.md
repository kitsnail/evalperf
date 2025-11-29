# Evalscope 测试结果数据汇总工具

## 项目概述

这是一个专门用于汇总和统计evalscope测试结果原始数据的Python3脚本。该工具专注于数据聚合处理，不做任何性能解读，为后续分析提供标准化数据基础。

## 核心功能

- **自动数据发现**：递归扫描results目录，自动识别所有测试结果
- **多源数据提取**：从benchmark_summary.json、benchmark_args.json、benchmark_percentile.json和benchmark_data.db提取完整数据
- **数据标准化**：将不同数据源合并为统一记录格式
- **统计分析**：对相同配置的多次运行计算统计指标
- **多格式导出**：支持CSV和JSON格式输出
- **百分位数支持**：完整提取P10、P25、P50、P66、P75、P80、P90、P95、P98、P99百分位数数据
- **GPU内存统计**：从数据库中提取GPU内存使用统计信息

## 使用方法

### 基本用法

```bash
# 使用默认设置汇总数据
python3 evalscope_aggregator.py

# 指定results目录
python3 evalscope_aggregator.py --results-dir ./results

# 导出JSON格式
python3 evalscope_aggregator.py --format json

# 只导出统计数据
python3 evalscope_aggregator.py --data-type stats

# 自定义输出文件名
python3 evalscope_aggregator.py --output my_summary
```

### 高级用法

```bash
# 导出原始数据到JSON，统计数据到CSV
python3 evalscope_aggregator.py --format json --data-type raw --output raw_data
python3 evalscope_aggregator.py --format csv --data-type stats --output stats_data

# 完整示例
python3 evalscope_aggregator.py \
  --results-dir ./results \
  --format csv \
  --data-type both \
  --output evalperf_summary
```

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--results-dir` | 字符串 | `./results` | results目录路径 |
| `--format` | 选择 | `csv` | 输出格式：csv或json |
| `--output` | 字符串 | `summary` | 输出文件名前缀 |
| `--data-type` | 选择 | `both` | 数据类型：raw=原始数据, stats=统计数据, both=两者 |

## 输出文件

### 原始数据文件 (`*_raw.csv` 或 `*_raw.json`)
包含所有测试运行的完整数据记录：

```
timestamp,config,model,parallel,prompt_length,max_tokens,requests,time_taken,
output_throughput,total_throughput,request_throughput,latency,ttft,
token_latency,inter_token_latency,input_tokens,output_tokens,
avg_gpu_memory,max_gpu_memory,min_gpu_memory,
10p_ttft_,10p_itl_,10p_tpot_,10p_latency_,10p_output_(tok/s),10p_total_(tok/s),
25p_ttft_,25p_itl_,25p_tpot_,25p_latency_,25p_output_(tok/s),25p_total_(tok/s),
...所有百分位数字段
```

### 统计数据文件 (`*_stats.csv` 或 `*_stats.json`)
按配置分组的统计汇总数据：

```
config,count,model,parallel,prompt_length,max_tokens,
output_throughput_avg,output_throughput_std,output_throughput_min,output_throughput_max,
total_throughput_avg,total_throughput_std,total_throughput_min,total_throughput_max,
request_throughput_avg,request_throughput_std,request_throughput_min,request_throughput_max,
latency_avg,latency_std,latency_min,latency_max,
...所有字段的统计指标和百分位数统计
```

## 数据字段说明

### 基础信息
- `timestamp`: 测试时间戳
- `config`: 配置标识（如p32_n100_dp_long）
- `model`: 模型名称
- `parallel`: 并发数
- `prompt_length`: 提示词长度（long/short）
- `max_tokens`: 最大输出token数
- `requests`: 总请求数

### 平均值性能指标
- `time_taken`: 测试总耗时（秒）
- `output_throughput`: 输出token吞吐量（tok/s）
- `total_throughput`: 总token吞吐量（tok/s）
- `request_throughput`: 请求吞吐量（req/s）

### 平均值延迟指标
- `latency`: 平均延迟（秒）
- `ttft`: 平均首次token响应时间（秒）
- `token_latency`: 平均每个输出token时间（秒）
- `inter_token_latency`: 平均token间延迟（秒）

### 平均值Token指标
- `input_tokens`: 平均输入token数
- `output_tokens`: 平均输出token数

### GPU内存指标
- `avg_gpu_memory`: 平均GPU内存消耗
- `max_gpu_memory`: 最大GPU内存消耗
- `min_gpu_memory`: 最小GPU内存消耗

### 百分位数指标
- `10p_ttft_`: P10首次token响应时间（秒）
- `10p_latency_`: P10延迟（秒）
- `10p_output_(tok/s)`: P10输出吞吐量（tok/s）
- `10p_total_(tok/s)`: P10总吞吐量（tok/s）
- `25p_*`: P25对应指标
- `50p_*`: P50对应指标
- `66p_*`: P66对应指标
- `75p_*`: P75对应指标
- `80p_*`: P80对应指标
- `90p_*`: P90对应指标
- `95p_*`: P95对应指标
- `98p_*`: P98对应指标
- `99p_*`: P99对应指标

## 数据源说明

### benchmark_summary.json
包含平均性能指标：
- 延迟、吞吐量、token统计等平均值数据

### benchmark_args.json
包含测试配置参数：
- 模型信息、并发数、提示词、max_tokens等

### benchmark_percentile.json
包含详细百分位数数据：
- P10到P99各百分位数的性能表现
- 对于分析系统稳定性和极端性能表现非常重要

### benchmark_data.db
包含请求级别的详细数据：
- 每个请求的GPU内存消耗
- 详细的延迟和吞吐量数据
- 用于计算GPU内存统计信息

## 目录结构要求

脚本期望以下目录结构：

```
results/
├── config_name/
│   └── YYYYMMDD_HHMMSS/
│       └── model_name/
│           ├── benchmark_summary.json
│           ├── benchmark_args.json
│           ├── benchmark_percentile.json
│           ├── benchmark_data.db
│           └── benchmark.log
```

## 依赖要求

- Python 3.6+
- 标准库：os, json, csv, argparse, statistics, pathlib, typing
- sqlite3（用于读取benchmark_data.db）

## 错误处理

- 自动跳过不完整的测试结果目录
- 提供详细的错误信息和进度提示
- 容错处理JSON解析错误和文件访问错误
- 数据库读取失败时提供警告信息

## 使用示例

### 示例输出
```
发现 3 个测试结果目录
已处理: p32_n100_dp_long/20251129_135846
已处理: p32_n100_dp_short/20251129_135117
已处理: p64_n100_dp_short/20251129_135123
成功收集 3 条原始数据记录
已导出 raw 数据到: summary_raw.csv
已导出 stats 数据到: summary_stats.csv
数据汇总完成！
```

### 数据完整性验证
脚本现在能够提取以下完整数据：
- ✅ 基础配置信息
- ✅ 平均值性能指标
- ✅ 详细百分位数数据（P10-P99）
- ✅ GPU内存统计信息
- ✅ 按配置分组的统计分析

## 设计原则

1. **零性能解读**：只做数据汇总，不做性能分析
2. **数据完整性**：保持所有原始数据的完整性和准确性
3. **标准化输出**：提供标准化的数据格式，便于后续处理
4. **最小依赖**：主要使用Python标准库，减少外部依赖
5. **灵活性**：支持多种输出格式和配置选项

## 后续扩展

该工具作为"数据层"，为后续的分析工具提供数据基础：

- 性能对比分析工具
- 百分位数趋势分析工具
- GPU内存使用分析工具
- 可视化展示工具
- 异常检测工具

## 许可证

本工具遵循与evalscope项目相同的许可证。
