#!/bin/bash

# 默认配置
MODEL=${MODEL:-"Qwen3-VL-235B-A22B-Instruct"}
URL=${URL:-"http://100.125.1.153/v1/chat/completions"}
DATASET=${DATASET:-"./prompts/p_short.jsonl"}
MAX_TOKENS=${MAX_TOKENS:-200}
OUTPUT_DIR=${OUTPUT_DIR:-"./results"}
PARALLEL=${PARALLEL:-64}
REQUESTS=${REQUESTS:-200}

# 检测终端颜色支持
detect_colors() {
    if [[ -t "$TERM" ]] || [[ "$TERM" = "dumb" ]] || [[ -n "$NO_COLOR" ]]; then
        # 终端不支持颜色或用户禁用颜色
        RED=''
        GREEN=''
        NC=''
        BOLD=''
        return 1
    fi
    
    # 测试终端是否支持颜色
    if command -v tput &>/dev/null; then
        RED=$(tput setaf 1 2>/dev/null || echo '')
        GREEN=$(tput setaf 2 2>/dev/null || echo '')
        NC=$(tput sgr0 2>/dev/null || echo '')
        BOLD=$(tput bold 2>/dev/null || echo '')
    else
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        NC='\033[0m'
        BOLD='\033[1m'
    fi
    
    # 如果颜色变量为空，说明不支持颜色
    [[ -z "$GREEN" ]] && return 1 || return 0
}

# 初始化颜色
RED=''
GREEN=''
NC=''
BOLD=''
detect_colors

log() { 
    if [[ -n "$GREEN" ]]; then
        echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $*"
    else
        echo "[$(date +%H:%M:%S)] $*"
    fi
}

error() { 
    if [[ -n "$RED" ]]; then
        echo -e "${RED}[ERROR]${NC} $*" >&2
    else
        echo "[ERROR] $*" >&2
    fi
}

check_env() {
    command -v evalscope &>/dev/null || { error "未找到 evalscope 命令，安装: pip install evalscope"; exit 2; }
    mkdir -p "$OUTPUT_DIR" 2>/dev/null || { error "无法创建输出目录: $OUTPUT_DIR"; exit 2; }
}

usage() {
    cat << EOF
${GREEN}evalperf.sh${NC} - LLM性能快速测试工具

${GREEN}用法${NC}:
  evalperf.sh [选项]

${GREEN}常用命令${NC}:
  evalperf.sh                    快速验证（默认）
  evalperf.sh -p 64 -n 200      单次完整测试

${GREEN}参数说明${NC}:
  ${GREEN}-p <num>${NC}    并发数 (默认: 64, 环境变量: PARALLEL)
  ${GREEN}-n <num>${NC}    请求数 (默认: 200, 环境变量: REQUESTS)
  ${GREEN}-d <path>${NC}   数据集路径 (默认: ./prompts/p_short.jsonl, 环境变量: DATASET)
  ${GREEN}-o <dir>${NC}    输出目录 (默认: ./results, 环境变量: OUTPUT_DIR)
  ${GREEN}-m <name>${NC}   模型名称 (默认: Qwen3-VL-235B-A22B-Instruct, 环境变量: MODEL)
  ${GREEN}-u <url>${NC}    服务URL (默认: http://100.125.1.153/v1/chat/completions, 环境变量: URL)
  ${GREEN}-t <num>${NC}    最大令牌数 (默认: 200, 环境变量: MAX_TOKENS)
  ${GREEN}--quick${NC}      快速验证模式 (32并发, 50请求)
  ${GREEN}-h, --help${NC}   显示帮助信息

${GREEN}示例${NC}:
  evalperf.sh                              # 使用默认设置快速验证
  evalperf.sh --quick                       # 快速验证模式
  evalperf.sh -p 128 -n 100                # 128并发，100请求
  evalperf.sh -p 64 -n 200 -d custom.jsonl # 自定义数据集
  evalperf.sh -m "gpt-4" -u "http://localhost:8000/v1/chat/completions" -t 512 # 自定义模型和URL
  PARALLEL=32 REQUESTS=100 evalperf.sh       # 通过环境变量设置默认值
EOF
}

validate_params() {
    if (( PARALLEL < 1 || PARALLEL > 256 )); then
        error "并发数必须在 1-256 之间，当前: $PARALLEL"
        exit 1
    fi
    if (( REQUESTS < 10 )); then
        error "请求数至少为 10，当前: $REQUESTS"
        exit 1
    fi
    if (( MAX_TOKENS < 1 || MAX_TOKENS > 8192 )); then
        error "最大令牌数必须在 1-8192 之间，当前: $MAX_TOKENS"
        exit 1
    fi
    if [[ ! -f "$DATASET" ]]; then
        error "数据集不存在: $DATASET"
        exit 1
    fi
    if [[ ! -s "$DATASET" ]]; then
        error "数据集文件为空: $DATASET"
        exit 1
    fi
    if [[ ! "$URL" =~ ^https?:// ]]; then
        error "URL格式不正确，必须以http://或https://开头: $URL"
        exit 1
    fi
}

extract_metrics() {
    local logfile=$1
    local output_dir=$2
    log "📊 提取核心指标..."
    # 基于实际 evalscope 输出格式提取指标
    local throughput=$(grep -o 'Output token throughput.*tok/s' "$logfile" 2>/dev/null | grep -o '[0-9.]*' | head -1 || echo "N/A")
    local p50_latency=$(grep -E '|\s*50%\s*|' "$logfile" 2>/dev/null | awk -F'|' '{gsub(/[^0-9.]/,"",$5); print $5}' | head -1 || echo "N/A")
    local p99_latency=$(grep -E '|\s*99%\s*|' "$logfile" 2>/dev/null | awk -F'|' '{gsub(/[^0-9.]/,"",$5); print $5}' | head -1 || echo "N/A")
    
    # 备用模式：查找其他可能的格式
    [ "$throughput" = "N/A" ] && throughput=$(grep -oE 'throughput[^:]*[:\\s]+[0-9.]+' "$logfile" 2>/dev/null | grep -oE '[0-9.]+' | head -1 || echo "N/A")
    [ "$p50_latency" = "N/A" ] && p50_latency=$(grep -oE 'P50[^:]*[:\\s]+[0-9.]+' "$logfile" 2>/dev/null | grep -oE '[0-9.]+' | head -1 || echo "N/A")
    [ "$p99_latency" = "N/A" ] && p99_latency=$(grep -oE 'P99[^:]*[:\\s]+[0-9.]+' "$logfile" 2>/dev/null | grep -oE '[0-9.]+' | head -1 || echo "N/A")
    
    # 转换延迟为毫秒（如果提取到的是秒）- 使用 awk 而不是 bc
    if [[ "$p50_latency" != "N/A" && "$p50_latency" =~ ^[0-9]*\.?[0-9]+$ ]]; then
        # 简单检查是否小于10，如果是秒则转换为毫秒
        if (( $(echo "$p50_latency < 10" | awk '{print ($1 < 10) ? 1 : 0}') )); then
            p50_latency=$(awk "BEGIN {printf \"%.0f\", $p50_latency * 1000}")
        fi
    fi
    if [[ "$p99_latency" != "N/A" && "$p99_latency" =~ ^[0-9]*\.?[0-9]+$ ]]; then
        if (( $(echo "$p99_latency < 10" | awk '{print ($1 < 10) ? 1 : 0}') )); then
            p99_latency=$(awk "BEGIN {printf \"%.0f\", $p99_latency * 1000}")
        fi
    fi
    
    printf "📊 核心指标:\n   吞吐量: %s tokens/s\n   P50延迟: %s ms\n   P99延迟: %s ms\n" "$throughput" "$p50_latency" "$p99_latency"
    [ -n "$output_dir" ] && cat > "$output_dir/summary.txt" << EOF
throughput_tokens_per_sec=$throughput
latency_p50_ms=$p50_latency
latency_p99_ms=$p99_latency
timestamp=$(date -Iseconds)
EOF
}

run_single_test() {
    local parallel=$1 requests=$2 name=${3:-"test_$(date +%Y%m%d_%H%M%S)"}
    validate_params
    local output_dir="$OUTPUT_DIR/$name"
    local logfile="$output_dir/test.log"
    mkdir -p "$output_dir"
    
    # 从数据集中获取第一个提示用于测试
    local first_prompt=$(head -1 "$DATASET" | jq -r '.messages[0].content' 2>/dev/null || echo "Hello, how are you?")
    
    log "🚀 性能测试开始"
    log "📋 配置: 并发=$parallel 请求=$requests 提示=$first_prompt"
    log "⏱️  预计耗时: $((requests * 2 / parallel))分钟"
    log "----------------------------------------"
    # 执行 evalscope 命令并捕获输出，使用 --prompt 参数
    evalscope perf --model "$MODEL" --api "openai" --url "$URL" --prompt "$first_prompt" \
        --parallel "$parallel" --number "$requests" --max-tokens "$MAX_TOKENS" \
        --outputs-dir "$output_dir" --no-test-connection 2>&1 | tee "$logfile"
    local exit_code=$?
    # 检查是否成功提取到指标，即使命令返回非零状态码
    if grep -qi "throughput" "$logfile" && (grep -qi "latency" "$logfile" || grep -qi "P50" "$logfile"); then
        log "✅ 测试完成"
        log "💾 结果保存: $output_dir"
        extract_metrics "$logfile" "$output_dir"
    elif [ $exit_code -ne 0 ]; then
        error "❌ 测试执行失败: 1.服务未运行 2.并发数过高 3.网络问题"
        exit 3
    else
        error "❌ 未能提取到性能指标"
        exit 3
    fi
    log "----------------------------------------"
}

quick_test() {
    log "⚡ 快速验证模式 (2分钟)"
    run_single_test 32 50 "quick_$(date +%H%M%S)"
    printf "\n💡 提示: 使用 -p 64 -n 200 进行完整测试\n"
}

# 修复参数解析逻辑
main() {
    local mode="single"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                PARALLEL="$2"; shift 2 ;;
            -n) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                REQUESTS="$2"; shift 2 ;;
            -d) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                DATASET="$2"; shift 2 ;;
            -o) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                OUTPUT_DIR="$2"; shift 2 ;;
            -m) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                MODEL="$2"; shift 2 ;;
            -u) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                URL="$2"; shift 2 ;;
            -t) 
                [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
                MAX_TOKENS="$2"; shift 2 ;;
            --quick) mode="quick"; shift ;;
            -h|--help) usage; exit 0 ;;
            *) error "未知参数: $1"; usage; exit 1 ;;
        esac
    done
    
    check_env
    case $mode in
        quick) quick_test ;;
        single) run_single_test "$PARALLEL" "$REQUESTS" ;;
    esac
}

# 只有当脚本直接执行时才运行main，而不是被source时
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
