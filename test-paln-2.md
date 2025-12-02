# 自定义数据集

## quick test
```bash
./evalperf.sh -m DeepSeek-V3.1 -p 48  -n 300 -d ./prompts/p_short.jsonl
```

## full test
```bash
./evalperf.sh -m DeepSeek-V3.1 -p 1 2 4 8 16 32 48 64 96 128 256   -n 1000 -d ./prompts/p_short.jsonl
./evalperf.sh -m DeepSeek-V3.1 -p 1 2 4 8 16 32 64 96 128 256   -n 1000 -d ./prompts/p_medium.jsonl
./evalperf.sh -m DeepSeek-V3.1 -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_long.jsonl
```

## aggregate
```bash
./evalscope_aggregator.py --results-dir ./perf_results
```

## report
```bash
./evalscope_reporter.py --results-dir ./perf_results --output-file ./perf_results/report.html
```
