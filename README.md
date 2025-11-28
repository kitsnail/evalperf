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
3. **结果提取** - 自动提取4个核心指标

## 输出指标

- 吞吐量 (tokens/s)
- P50延迟 (ms)
- P99延迟 (ms)
- 成功率 (%)

## 参数说明

- `-p <num>` 并发数 (默认: 64)
- `-n <num>` 请求数 (默认: 200)
- `-d <path>` 数据集路径
- `-o <dir>` 输出目录
- `-m <name>` 模型名称
- `--quick` 快速验证模式
- `-h` 显示帮助

## 示例

```bash
# 默认快速验证
./evalperf.sh

# 标准性能测试
./evalperf.sh -p 64 -n 200

# 自定义数据集
./evalperf.sh -p 32 -n 100 -d ./prompts/long.jsonl

# 指定输出目录
./evalperf.sh -p 64 -n 200 -o ./my_results
```

## 依赖

- `evalscope` 命令（需要先安装：`pip install evalscope`）

## 文件结构

```
.
├── evalperf.sh          # 主脚本
├── prompts/
│   └── p_short.jsonl    # 示例数据集
├── results/             # 测试结果输出目录
└── README.md
