# evalperf.sh - LLM性能快速测试

## 快速开始

```bash
# 快速验证（2分钟）
./evalperf.sh

# 完整测试（5分钟）
./evalperf.sh -p 64 -n 200

# 自定义配置
./evalperf.sh -p 32 -n 100 -d ./prompts/long.jsonl
```

## 核心功能

1. **单次测试** - 执行一次完整性能测试
2. **快速验证** - 2分钟快速确认服务状态
3. **结果输出** - 直接显示测试结果，evalscope保存输出文件
4. **智能命名** - 输出目录按格式 p并发_n请求数_d数据集命名

## 输出指标

- 吞吐量 (tokens/s)
- P50延迟 (ms)
- P99延迟 (ms)

## 输出目录结构

测试结果保存在 `results/` 目录下，目录命名格式为：
- `p64_n200_dp_short` - 64并发，200请求，使用p_short.jsonl数据集
- `p32_n50_dcustom` - 32并发，50请求，使用custom.jsonl数据集

每个测试目录包含 evalscope 生成的标准输出文件，如 benchmark_summary.json、benchmark_percentile.json 等。

## 参数说明

- `-p <num> [num...]` 并发数 (默认: 64, 环境变量: EVALPERF_PARALLEL)
- `-n <num> [num...]` 请求数 (默认: 200, 环境变量: EVALPERF_REQUESTS)
- `-d <path>` 数据集路径 (默认: ./prompts/p_short.jsonl)
- `-o <dir>` 输出目录 (默认: ./results)
- `-m <name>` 模型名称 (默认: Qwen3-VL-235B-A22B-Instruct)
- `-u <url>` 服务URL (默认: http://100.125.1.153/v1/chat/completions)
- `-t <num>` 最大令牌数 (默认: 200)
- `--quick` 快速验证模式 (32并发, 50请求)
- `-h, --help` 显示帮助信息

### 与 evalscope 的一致性

`-p` 和 `-n` 参数与 `evalscope perf` 命令保持一致的用法：
- `-p` 对应 evalscope 的 `--parallel` 参数
- `-n` 对应 evalscope 的 `-n/--number` 参数
- 支持多个数值参数，会自动运行所有组合的测试
- 用法与 evalscope 的标准用法完全一致

## 环境变量配置

所有配置都可以通过带 `EVALPERF_` 前缀的环境变量来设置默认值：

```bash
# 设置默认配置
export EVALPERF_MODEL="gpt-4"
export EVALPERF_URL="http://localhost:8000/v1/chat/completions"
export EVALPERF_DATASET="./prompts/custom.jsonl"
export EVALPERF_MAX_TOKENS=512
export EVALPERF_OUTPUT_DIR="./my_results"
export EVALPERF_PARALLEL=32
export EVALPERF_REQUESTS=100

# 运行测试（将使用环境变量中的默认值）
./evalperf.sh
```

### 环境变量列表

- `EVALPERF_MODEL` - 模型名称 (默认: Qwen3-VL-235B-A22B-Instruct)
- `EVALPERF_URL` - 服务URL (默认: http://100.125.1.153/v1/chat/completions)
- `EVALPERF_DATASET` - 数据集路径 (默认: ./prompts/p_short.jsonl)
- `EVALPERF_MAX_TOKENS` - 最大令牌数 (默认: 200)
- `EVALPERF_OUTPUT_DIR` - 输出目录 (默认: ./results)
- `EVALPERF_PARALLEL` - 并发数 (默认: 64)
- `EVALPERF_REQUESTS` - 请求数 (默认: 200)

## 示例

```bash
# 默认快速验证
./evalperf.sh

# 标准性能测试
./evalperf.sh -p 64 -n 200

# 多组测试：32和64并发 × 50和100请求（共4组测试）
./evalperf.sh -p 32 64 -n 50 100

# 单参数多值：测试32、64、128三种并发数
./evalperf.sh -p 32 64 128 -n 100

# 自定义数据集
./evalperf.sh -p 32 -n 100 -d ./prompts/long.jsonl

# 指定输出目录
./evalperf.sh -p 64 -n 200 -o ./my_results

# 通过环境变量设置默认值并运行
EVALPERF_PARALLEL=32 EVALPERF_REQUESTS=100 evalperf.sh

# 快速验证模式
./evalperf.sh --quick
```

## 依赖

- `evalscope` 命令（需要先安装：`pip install evalscope`）
- `jq` 命令（用于处理JSON格式的数据集）

## 文件结构

```
.
├── evalperf.sh          # 主脚本
├── prompts/
│   └── p_short.jsonl    # 示例数据集
├── results/             # 测试结果输出目录
└── README.md
