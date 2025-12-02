# 自定义数据集

## quick test
```bash
./evalperf.sh -p 64 -n 1000 -d ./prompts/p_short.jsonl -o ./results/qwen3/1pod4gvllm_v1
```

## full test
```bash
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_short.jsonl -o ./results/qwen3/1pod4gvllm_v1
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_medium.jsonl -o ./results/qwen3/1pod4gvllm_v1
./evalperf.sh -p 1 2 4 8 16 32 64 96 128 256  -n 1000 -d ./prompts/p_long.jsonl -o ./results/qwen3/1pod4gvllm_v1
```

```bash
./evalscope_aggregator.py --results-dir ./perf_results
```