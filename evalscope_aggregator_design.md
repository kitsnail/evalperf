# Evalscope 测试结果数据汇总脚本设计方案

## 脚本概述
**目标**: 创建一个Python3脚本，专门用于汇总和统计evalscope测试的原始数据，不做任何性能解读，只做纯粹的数据聚合处理。

## 核心功能
1. **数据扫描**: 递归扫描results目录，自动发现所有测试结果
2. **数据提取**: 从每个测试目录中提取benchmark_summary.json和benchmark_args.json的原始数据
3. **数据标准化**: 将不同文件的数据合并为统一的记录格式
4. **数据统计**: 对相同配置的多次运行计算统计指标（平均值、标准差、最值等）
5. **数据导出**: 支持CSV和JSON格式输出，便于后续分析工具使用

## 数据字段映射
**核心数据字段**:
- timestamp, config, model, parallel, prompt_length, max_tokens
- requests, time_taken, output_throughput, total_throughput, request_throughput
- latency, ttft, token_latency, inter_token_latency
- input_tokens, output_tokens

## 脚本结构
```
evalscope_aggregator.py
├── 单一职责函数设计
├── 命令行接口
├── 多格式输出支持
└── 错误处理机制
```

## 使用方式
```bash
python evalscope_aggregator.py --results-dir ./results --format csv --output summary.csv
```

## 设计原则
- 零性能解读，纯粹数据汇总
- 保持数据原始性和完整性
- 输出标准化格式，便于后续处理
- 最小依赖，主要使用Python标准库

这个脚本将成为evalscope测试结果的"数据层"，为所有后续分析工具提供干净、标准化的数据基础。
