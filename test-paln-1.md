# 自定义数据集
```bash
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_short.jsonl
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_medium.jsonl
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_long.jsonl
```

```bash
./evalscope_aggregator.py --results-dir ./perf_results
```