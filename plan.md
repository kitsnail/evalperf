# evalperf 方案 - 极简三核心版

## 一、脚本定位

```
脚本名称：evalperf.sh
核心理念：做好三件事，不多不少
目标时间：10分钟学会，5分钟出结果
代码规模：300行以内
```

---

## 二、三大核心功能详细设计

### 功能1：单次测试（基础功能）

#### 设计目标
```
让用户用最少的参数完成一次完整测试
```

#### 最小可用参数
```bash
# 只需要2个参数就能运行
./evalperf.sh -p 64 -n 200

# 其他都用合理默认值
MODEL: Qwen3-VL-235B-A22B-Instruct
URL: http://100.125.1.153/v1/chat/completions
DATASET: ./prompts/p_short.jsonl
MAX_TOKENS: 200
```

#### 输入验证（3项检查）
```bash
1. 并发数合理性
   - 范围：1-256
   - 默认：64
   - 不合理时：给出建议值

2. 请求数合理性
   - 最小：10（太少没意义）
   - 建议：50-500
   - 不合理时：给出警告但继续

3. 数据集存在性
   - 检查文件存在
   - 检查文件非空
   - 失败时：明确报错退出
```

#### 执行流程（5步）
```
1. 参数验证（3秒）
   ├─ 检查必需参数
   ├─ 验证数值范围
   └─ 检查数据集文件

2. 环境检查（2秒）
   ├─ evalscope命令存在
   └─ 输出目录可写

3. 执行测试（主要时间）
   ├─ 显示测试配置
   ├─ 调用evalscope
   └─ 实时输出日志

4. 提取指标（5秒）
   ├─ 解析日志文件
   ├─ 提取4个核心指标
   └─ 格式化输出

5. 保存结果（1秒）
   ├─ 完整日志
   └─ 指标摘要
```

#### 输出设计
```bash
# 开始
🚀 性能测试开始
📋 配置: 并发=64 请求=200 数据集=p_short.jsonl
⏱️  预计耗时: 3-5分钟
----------------------------------------

# 进行中（evalscope原生输出）
[evalscope的实时日志...]

# 完成
----------------------------------------
✅ 测试完成 (耗时: 4m23s)

📊 核心指标:
   吞吐量: 1250.5 tokens/s
   P50延迟: 845 ms
   P99延迟: 2103 ms
   成功率: 100.0%

💾 结果保存: ./results/test_20240115_143022
```

#### 错误处理
```bash
# 只处理3类错误

1. 参数错误
   → 显示正确用法
   → 退出码: 1

2. 环境错误
   → 明确提示缺少什么
   → 退出码: 2

3. 测试失败
   → 显示失败原因
   → 保留日志文件
   → 退出码: 3
```

---

### 功能2：快速验证（效率功能）

#### 设计目标
```
2分钟内确认服务是否正常
```

#### 固定配置（不可修改）
```bash
并发数: 32      # 保守值，不易崩溃
请求数: 50      # 最小有效样本
超时: 60s       # 快速失败
数据集: 使用默认  # 不增加复杂度
```

#### 使用场景
```
✅ 每天第一次测试前
✅ 代码改动后验证
✅ 部署后快速确认
✅ 调试时频繁检查
```

#### 实现逻辑
```bash
quick_test() {
    # 固定参数，不接受修改
    local parallel=32
    local requests=50
    local name="quick_$(date +%H%M%S)"
  
    log "⚡ 快速验证模式 (2分钟)"
  
    # 复用单次测试函数
    run_single_test $parallel $requests $name
}
```

#### 输出设计
```bash
⚡ 快速验证模式
📋 固定配置: 并发=32 请求=50
⏱️  预计耗时: 2分钟
----------------------------------------
[测试输出...]
----------------------------------------
✅ 服务正常 (耗时: 1m47s)

📊 快速指标:
   吞吐量: 890.2 tokens/s
   平均延迟: 720 ms
   成功率: 100.0%

💡 提示: 使用 -p 64 -n 200 进行完整测试
```

#### 简化点
```
❌ 不保存详细日志（减少IO）
❌ 不生成报告文件（减少处理）
✅ 只输出到终端
✅ 只显示核心指标
✅ 只判断成功/失败
```

---

### 功能3：结果提取（可用性功能）

#### 设计目标
```
自动提取4个核心指标，无需手动grep
```

#### 核心指标（只提取4个）
```
1. 吞吐量 (tokens/s)
   - 最重要的指标
   - 正则: throughput.*?(\d+\.?\d*)\s*tokens/s

2. P50延迟 (ms)
   - 典型响应时间
   - 正则: P50.*?(\d+\.?\d*)\s*ms

3. P99延迟 (ms)
   - 最差情况
   - 正则: P99.*?(\d+\.?\d*)\s*ms

4. 成功率 (%)
   - 可靠性指标
   - 计算: (成功请求/总请求) * 100
```

#### 提取策略
```bash
# 策略1：从evalscope的标准输出提取
extract_from_stdout() {
    # evalscope会在最后输出汇总
    # 直接解析最后几行
}

# 策略2：从日志文件提取（备用）
extract_from_logfile() {
    # 如果stdout没有，从日志文件找
    # 更可靠但稍慢
}

# 优先级：stdout > logfile
```

#### 容错处理
```bash
# 如果某个指标提取失败
提取失败 → 显示 "N/A"
不要因为一个指标失败就整体失败

示例输出：
📊 核心指标:
   吞吐量: 1250.5 tokens/s
   P50延迟: N/A
   P99延迟: 2103 ms
   成功率: 100.0%
```

#### 输出格式（2种）

**格式1：终端输出（人类可读）**
```bash
📊 核心指标:
   吞吐量: 1250.5 tokens/s
   P50延迟: 845 ms
   P99延迟: 2103 ms
   成功率: 100.0%
```

**格式2：文件保存（机器可读）**
```bash
# summary.txt
throughput_tokens_per_sec=1250.5
latency_p50_ms=845
latency_p99_ms=2103
success_rate_percent=100.0
test_duration_sec=263
timestamp=2024-01-15T14:30:22
```

#### 实现要点
```bash
extract_metrics() {
    local logfile=$1
  
    # 1. 提取原始值（容错）
    local throughput=$(grep -oP 'throughput.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
    local p50=$(grep -oP 'P50.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
    local p99=$(grep -oP 'P99.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
  
    # 2. 格式化输出
    printf "📊 核心指标:\n"
    printf "   吞吐量: %s tokens/s\n" "$throughput"
    printf "   P50延迟: %s ms\n" "$p50"
    printf "   P99延迟: %s ms\n" "$p99"
  
    # 3. 保存到文件（可选）
    if [ -n "$output_dir" ]; then
        cat > "$output_dir/summary.txt" << EOF
throughput_tokens_per_sec=$throughput
latency_p50_ms=$p50
latency_p99_ms=$p99
EOF
    fi
}
```

---

## 三、脚本整体结构

### 代码组织（150行）

```bash
#!/bin/bash
set -euo pipefail

# ============================================
# Part 1: 配置和常量 (15行)
# ============================================
# - 默认参数（10行）
# - 颜色定义（5行）

# ============================================
# Part 2: 工具函数 (20行)
# ============================================
log()          # 普通日志 (3行)
error()        # 错误日志 (3行)
check_env()    # 环境检查 (10行)
usage()        # 帮助信息 (15行)

# ============================================
# Part 3: 核心功能 (80行)
# ============================================
run_single_test()   # 单次测试 (35行)
quick_test()        # 快速验证 (10行)
extract_metrics()   # 结果提取 (25行)

# ============================================
# Part 4: 主程序 (35行)
# ============================================
parse_args()   # 参数解析 (20行)
main()         # 主流程 (15行)
```

### 函数依赖关系

```
main()
├── parse_args()
├── check_env()
└── 模式分发
    ├── quick_test()
    │   └── run_single_test()
    │       └── extract_metrics()
    └── run_single_test()
        └── extract_metrics()
```

---

## 四、参数设计

### 必需参数（0个）
```bash
# 无参数时运行快速验证
./evalperf.sh
# 等同于
./evalperf.sh --quick
```

### 常用参数（2个）
```bash
-p <num>    并发数 (parallel)
-n <num>    请求数 (number)
```

### 可选参数（3个）
```bash
-d <path>   数据集路径 (dataset)
-o <dir>    输出目录 (output)
-m <name>   模型名称 (model)
```

### 模式参数（1个）
```bash
--quick     快速验证模式
```

### 帮助参数（1个）
```bash
-h, --help  显示帮助
```

### 参数优先级
```
命令行参数 > 环境变量 > 默认值
```

---

## 五、默认值设计

### 核心原则
```
默认值必须是最常用的、最安全的配置
```

### 具体默认值
```bash
# 性能参数
PARALLEL=64          # 中等并发，适合大多数场景
REQUESTS=200         # 足够的样本量
MAX_TOKENS=200       # 常见输出长度

# 服务配置
MODEL="Qwen3-VL-235B-A22B-Instruct"
URL="http://100.125.1.153/v1/chat/completions"

# 数据集
DATASET="./prompts/p_short.jsonl"

# 输出
OUTPUT_DIR="./results"

# 超时
CONNECT_TIMEOUT=300
READ_TIMEOUT=300
```

### 默认值选择理由
```
并发=64
  ✓ 不会太低（能体现并发性能）
  ✓ 不会太高（不易崩溃）
  ✓ 是2的幂次（便于调整）

请求=200
  ✓ 统计上足够（>100）
  ✓ 不会太久（<10分钟）
  ✓ 是整数（便于计算）

数据集=short
  ✓ 快速完成（输入输出都短）
  ✓ 适合日常测试
  ✓ 不依赖特殊数据
```

---

## 六、错误处理策略

### 三层防御

#### 第1层：参数验证（预防）
```bash
# 在执行前检查
validate_params() {
    # 并发数
    if [ $PARALLEL -lt 1 ] || [ $PARALLEL -gt 256 ]; then
        error "并发数必须在 1-256 之间"
        exit 1
    fi
  
    # 请求数
    if [ $REQUESTS -lt 10 ]; then
        error "请求数至少为 10"
        exit 1
    fi
  
    # 数据集
    if [ ! -f "$DATASET" ]; then
        error "数据集不存在: $DATASET"
        exit 1
    fi
}
```

#### 第2层：环境检查（预防）
```bash
check_env() {
    # evalscope命令
    if ! command -v evalscope &>/dev/null; then
        error "未找到 evalscope 命令"
        error "安装: pip install evalscope"
        exit 2
    fi
  
    # 输出目录
    if ! mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
        error "无法创建输出目录: $OUTPUT_DIR"
        exit 2
    fi
}
```

#### 第3层：执行监控（响应）
```bash
run_single_test() {
    # 使用 set -e 自动失败
    # 使用 || 捕获特定错误
  
    if ! evalscope perf ...; then
        error "❌ 测试执行失败"
        error "💡 可能原因:"
        error "   1. 服务未运行"
        error "   2. 并发数过高"
        error "   3. 网络问题"
        exit 3
    fi
}
```

### 错误信息设计

```bash
# 好的错误信息（3要素）
error "❌ 数据集不存在: ./prompts/missing.jsonl"
error "💡 请检查:"
error "   1. 文件路径是否正确"
error "   2. 文件是否已创建"
error "   3. 当前目录: $(pwd)"

# 不好的错误信息
error "File not found"  # ❌ 不知道哪个文件
error "Error"           # ❌ 不知道什么错误
```

---

## 七、日志设计

### 日志级别（2个）

```bash
# INFO - 正常信息
log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $*"
}

# ERROR - 错误信息
error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}
```

### 日志内容（最小化）

```bash
# 只记录关键节点
log "🚀 开始测试"           # 开始
log "⏳ 运行中..."          # 进行中（可选）
log "✅ 测试完成"           # 完成
error "❌ 测试失败"         # 失败

# 不记录
❌ 详细的参数信息（太多）
❌ 中间状态（evalscope会输出）
❌ 调试信息（不需要）
```

---

## 八、输出目录结构

### 简单结构（2个文件）

```
./results/
└── test_20240115_143022/
    ├── test.log        # 完整日志（evalscope输出）
    └── summary.txt     # 指标摘要（脚本生成）
```

### 命名规则

```bash
# 目录名：test_日期_时间
test_20240115_143022

# 快速模式：quick_时间
quick_143022

# 自定义名称（如果提供）
baseline_test
```

---

## 九、健壮性设计

### 1. 幂等性
```bash
# 多次运行不会相互影响
./evalperf.sh -p 64 -n 200  # 第1次
./evalperf.sh -p 64 -n 200  # 第2次
# 结果保存在不同目录（时间戳）
```

### 2. 原子性
```bash
# 测试失败不会留下垃圾文件
run_single_test() {
    local output_dir="$OUTPUT_DIR/test_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$output_dir"
  
    # 如果失败，目录会保留（便于调试）
    # 但不会影响下次测试
}
```

### 3. 可恢复性
```bash
# 测试中断后可以继续
# 不需要特殊的恢复机制
# 直接重新运行即可
```

### 4. 防御性编程
```bash
# 使用 set -euo pipefail
set -e   # 命令失败立即退出
set -u   # 使用未定义变量报错
set -o pipefail  # 管道中任何命令失败都报错

# 引用所有变量
"$PARALLEL"  # ✅
$PARALLEL    # ❌

# 检查文件存在
[ -f "$file" ]  # ✅
cat "$file"     # ❌ 直接使用
```

---

## 十、易维护性设计

### 1. 函数单一职责

```bash
# 好的设计
run_single_test()   # 只负责执行测试
extract_metrics()   # 只负责提取指标

# 不好的设计
run_test_and_analyze()  # ❌ 做太多事
```

### 2. 魔法数字消除

```bash
# 不好
if [ $parallel -gt 256 ]; then

# 好
MAX_PARALLEL=256
if [ $parallel -gt $MAX_PARALLEL ]; then
```

### 3. 注释策略

```bash
# 只注释"为什么"，不注释"是什么"

# 好的注释
# 使用32并发是因为更保守，不易崩溃
QUICK_PARALLEL=32

# 不好的注释
# 设置并发为32
QUICK_PARALLEL=32  # ❌ 废话
```

### 4. 代码格式

```bash
# 函数间空2行
function1() {
    ...
}


function2() {
    ...
}

# 逻辑块间空1行
validate_params

check_env

run_test
```

---

## 十一、测试计划

### 单元测试（手动）

```bash
# 测试1：正常流程
./evalperf.sh -p 64 -n 100
# 预期：成功完成，输出指标

# 测试2：快速模式
./evalperf.sh --quick
# 预期：2分钟内完成

# 测试3：参数错误
./evalperf.sh -p 0
# 预期：报错退出

# 测试4：文件不存在
./evalperf.sh -d /not/exist.jsonl
# 预期：报错退出

# 测试5：无参数
./evalperf.sh
# 预期：运行快速模式
```

### 边界测试

```bash
# 最小值
./evalperf.sh -p 1 -n 10

# 最大值
./evalperf.sh -p 256 -n 1000

# 异常值
./evalperf.sh -p -1    # 负数
./evalperf.sh -p 999   # 超大
./evalperf.sh -p abc   # 非数字
```

---

## 十二、性能要求

### 脚本启动时间
```
< 100ms  # 参数解析 + 环境检查
```

### 快速模式完成时间
```
< 3分钟  # 包括测试执行 + 结果提取
```

### 单次测试完成时间
```
取决于参数，但应该有预估
p64_n200 → 约5分钟
p32_n100 → 约3分钟
```

---

## 十三、文档要求

### README.md（简短）

```markdown
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
```

### 帮助信息（内置）

```bash
./evalperf.sh -h

输出：
evalperf.sh - LLM性能快速测试工具

用法:
  evalperf.sh [选项]

常用命令:
  evalperf.sh              快速验证（默认）
  evalperf.sh -p 64 -n 200 单次测试

参数:
  -p <num>    并发数 (默认: 64)
  -n <num>    请求数 (默认: 200)
  -d <path>   数据集路径
  -o <dir>    输出目录
  --quick     快速验证模式
  -h          显示帮助

示例:
  evalperf.sh --quick
  evalperf.sh -p 32 -n 100
  evalperf.sh -p 64 -n 200 -d ./prompts/long.jsonl
```

---

## 十四、代码规范

### 变量命名

```bash
# 全局常量：大写
MODEL="..."
URL="..."

# 局部变量：小写
local parallel=64
local output_dir="..."

# 函数名：小写+下划线
run_single_test()
extract_metrics()
```

### 引号使用

```bash
# 变量：双引号
"$PARALLEL"
"$OUTPUT_DIR"

# 字符串：双引号
"Hello World"

# 命令替换：双引号
"$(date +%s)"
```

### 条件判断

```bash
# 数值比较：使用 (( ))
if (( parallel > 256 )); then

# 字符串比较：使用 [[ ]]
if [[ "$mode" == "quick" ]]; then

# 文件检查：使用 [ ]
if [ -f "$file" ]; then
```

---

## 十五、实现检查清单

开发完成后，检查：

```
□ 代码总行数 < 150行
□ 核心函数 < 40行
□ 无参数运行正常（快速模式）
□ 帮助信息清晰完整
□ 错误信息友好明确
□ 所有变量都加引号
□ 使用 set -euo pipefail
□ 函数有简短注释
□ 通过5个基本测试
□ 快速模式 < 3分钟
□ 指标提取准确
□ 无外部依赖（除evalscope）
```

---

## 十六、版本规划

### v1.0（本周）
```
✅ 三大核心功能
✅ 基础错误处理
✅ 简单文档
```

### v1.1（按需）
```
⚠️ 只在确实需要时添加：
- 边界测试模式
- 对比测试模式
- 历史结果查看
```

---

## 总结

**脚本名称**：`evalperf.sh`

**核心功能**：3个
1. 单次测试 - 基础
2. 快速验证 - 效率
3. 结果提取 - 可用性

**设计原则**：
- 简单：150行代码
- 健壮：三层错误防御
- 易维护：单一职责，清晰结构

**成功标准**：
- 10分钟学会
- 2分钟快速验证
- 5分钟完整测试
- 零外部依赖