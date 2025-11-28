#!/bin/bash
set -euo pipefail

MODEL=${MODEL:-"Qwen3-VL-235B-A22B-Instruct"}
URL=${URL:-"http://100.125.1.153/v1/chat/completions"}
DATASET=${DATASET:-"./prompts/p_short.jsonl"}
MAX_TOKENS=${MAX_TOKENS:-200}
OUTPUT_DIR=${OUTPUT_DIR:-"./results"}
PARALLEL=${PARALLEL:-64}
REQUESTS=${REQUESTS:-200}

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

check_env() {
    command -v evalscope &>/dev/null || { error "未找到 evalscope 命令，安装: pip install evalscope"; exit 2; }
    mkdir -p "$OUTPUT_DIR" 2>/dev/null || { error "无法创建输出目录: $OUTPUT_DIR"; exit 2; }
}

usage() {
    echo "evalperf.sh - LLM性能快速测试工具"
    echo "用法: evalperf.sh [选项]"
    echo "常用命令:"
    echo "  evalperf.sh              快速验证（默认）"
    echo "  evalperf.sh -p 64 -n 200 单次测试"
    echo "参数: -p <num> 并发数(64) -n <num> 请求数(200) -d <path> 数据集路径"
    echo "      -o <dir> 输出目录 -m <name> 模型名称 --quick 快速验证 -h 帮助"
}

validate_params() {
    (( PARALLEL < 1 || PARALLEL > 256 )) && { error "并发数必须在 1-256 之间，当前: $PARALLEL"; exit 1; }
    (( REQUESTS < 10 )) && { error "请求数至少为 10，当前: $REQUESTS"; exit 1; }
    [ ! -f "$DATASET" ] && { error "数据集不存在: $DATASET"; exit 1; }
    [ ! -s "$DATASET" ] && { error "数据集文件为空: $DATASET"; exit 1; }
}

extract_metrics() {
    local logfile=$1
    log "📊 提取核心指标..."
    local throughput=$(grep -oP 'throughput.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
    local p50=$(grep -oP 'P50.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
    local p99=$(grep -oP 'P99.*?\K\d+\.?\d*' "$logfile" 2>/dev/null || echo "N/A")
    printf "📊 核心指标:\n   吞吐量: %s tokens/s\n   P50延迟: %s ms\n   P99延迟: %s ms\n" "$throughput" "$p50" "$p99"
    [ -n "${output_dir:-}" ] && cat > "$output_dir/summary.txt" << EOF
throughput_tokens_per_sec=$throughput
latency_p50_ms=$p50
latency_p99_ms=$p99
timestamp=$(date -Iseconds)
EOF
}

run_single_test() {
    local parallel=$1 requests=$2 name=${3:-"test_$(date +%Y%m%d_%H%M%S)"}
    validate_params
    local output_dir="$OUTPUT_DIR/$name" logfile="$output_dir/test.log"
    mkdir -p "$output_dir"
    log "🚀 性能测试开始"
    log "📋 配置: 并发=$parallel 请求=$requests 数据集=$(basename "$DATASET")"
    log "⏱️  预计耗时: $((requests * 2 / parallel))分钟"
    log "----------------------------------------"
    if ! evalscope perf --model "$MODEL" --server-url "$URL" --dataset "$DATASET" \
        --parallel "$parallel" --requests "$requests" --max-tokens "$MAX_TOKENS" \
        --output-dir "$output_dir" 2>&1 | tee "$logfile"; then
        error "❌ 测试执行失败: 1.服务未运行 2.并发数过高 3.网络问题"; exit 3
    fi
    log "----------------------------------------"
    log "✅ 测试完成"
    log "💾 结果保存: $output_dir"
    extract_metrics "$logfile"
}

quick_test() {
    log "⚡ 快速验证模式 (2分钟)"
    run_single_test 32 50 "quick_$(date +%H%M%S)"
    printf "\n💡 提示: 使用 -p 64 -n 200 进行完整测试\n"
}

parse_args() {
    local mode="single"
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p) PARALLEL="$2"; shift 2 ;;
            -n) REQUESTS="$2"; shift 2 ;;
            -d) DATASET="$2"; shift 2 ;;
            -o) OUTPUT_DIR="$2"; shift 2 ;;
            -m) MODEL="$2"; shift 2 ;;
            --quick) mode="quick"; shift ;;
            -h|--help) usage; exit 0 ;;
            *) error "未知参数: $1"; usage; exit 1 ;;
        esac
    done
    echo "$mode"
}

main() {
    local mode=$(parse_args "$@")
    check_env
    case $mode in
        quick) quick_test ;;
        single) run_single_test "$PARALLEL" "$REQUESTS" ;;
    esac
}

main "$@"
