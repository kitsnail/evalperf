#!/bin/bash

# ============================================================================
# evalperf.sh - LLM性能快速测试工具
# ============================================================================

# ============================================================================
# 配置变量
# ============================================================================
MODEL=${EVALPERF_MODEL:-"Qwen3-VL-235B-A22B-Instruct"}
URL=${EVALPERF_URL:-"http://100.125.1.153/v1/chat/completions"}
DATASET=${EVALPERF_DATASET:-"./prompts/p_short.jsonl"}
MAX_TOKENS=${EVALPERF_MAX_TOKENS:-200}
OUTPUT_DIR=${EVALPERF_OUTPUT_DIR:-"./perf_results"}
PARALLEL=${EVALPERF_PARALLEL:-64}
REQUESTS=${EVALPERF_REQUESTS:-200}
CONNECT_TIMEOUT=${EVALPERF_CONNECT_TIMEOUT:-300}
READ_TIMEOUT=${EVALPERF_READ_TIMEOUT:-300}
RATE_LIMIT=${EVALPERF_RATE_LIMIT:-""}
SLEEP_INTERVAL=${EVALPERF_SLEEP_INTERVAL:-5}
DISABLE_TIMEOUT=${EVALPERF_NO_TIMEOUT:-false}

# ============================================================================
# 颜色和日志函数
# ============================================================================
init_colors() {
    # 检测终端是否支持颜色
    if [[ -t "$TERM" ]] || [[ "$TERM" = "dumb" ]] || [[ -n "$NO_COLOR" ]]; then
        RED='' GREEN='' NC='' BOLD=''
        return 1
    fi

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

    [[ -n "$GREEN" ]]
}

# 初始化颜色
RED='' GREEN='' NC='' BOLD=''
init_colors

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

# ============================================================================
# 环境检查
# ============================================================================
check_env() {
    command -v evalscope &>/dev/null || {
        error "未找到 evalscope 命令，安装: pip install evalscope"
        exit 2
    }
    mkdir -p "$OUTPUT_DIR" 2>/dev/null || {
        error "无法创建输出目录: $OUTPUT_DIR"
        exit 2
    }
}

# ============================================================================
# 参数验证
# ============================================================================
validate_range() {
    local value=$1 min=$2 max=$3 name=$4
    if (( value < min || value > max )); then
        error "$name 必须在 $min-$max 之间，当前: $value"
        exit 1
    fi
}

validate_basic_params() {
    local parallel=${1:-$PARALLEL}
    local requests=${2:-$REQUESTS}

    validate_range "$parallel" 1 2048 "并发数"
    validate_range "$requests" 1 999999 "请求数"
    validate_range "$MAX_TOKENS" 1 81920 "最大令牌数"

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

validate_timeout_params() {
    if [[ "$DISABLE_TIMEOUT" != "true" ]]; then
        validate_range "$CONNECT_TIMEOUT" 1 300 "连接超时"
        validate_range "$READ_TIMEOUT" 1 600 "读取超时"
    fi
}

validate_rate_limit() {
    if [[ -n "$RATE_LIMIT" ]]; then
        validate_range "$RATE_LIMIT" 1 1000 "速率限制"
    fi
}

validate_params() {
    validate_basic_params "$@"
    validate_timeout_params
    validate_rate_limit
}

# ============================================================================
# 命令构建
# ============================================================================
build_evalscope_command() {
    local parallel=$1
    local requests=$2
    local output_dir=$3
    local prompt=$4

    local cmd="evalscope perf"
    cmd="$cmd --model \"$MODEL\""
    cmd="$cmd --api \"openai\""
    cmd="$cmd --url \"$URL\""
    cmd="$cmd --prompt \"$prompt\""
    cmd="$cmd --parallel \"$parallel\""
    cmd="$cmd --number \"$requests\""
    cmd="$cmd --max-tokens \"$MAX_TOKENS\""
    cmd="$cmd --outputs-dir \"$output_dir\""
    cmd="$cmd --no-test-connection"
    cmd="$cmd --no-stream"

    if [[ "$DISABLE_TIMEOUT" != "true" ]]; then
        cmd="$cmd --connect-timeout $CONNECT_TIMEOUT"
        cmd="$cmd --read-timeout $READ_TIMEOUT"
    fi

    if [[ -n "$RATE_LIMIT" ]]; then
        cmd="$cmd --rate $RATE_LIMIT"
    fi

    cmd="$cmd --sleep-interval $SLEEP_INTERVAL"

    echo "$cmd"
}

# ============================================================================
# 测试执行
# ============================================================================
get_first_prompt() {
    head -1 "$DATASET" | jq -r '.messages[0].content' 2>/dev/null || echo "Hello, how are you?"
}

run_single_test() {
    local parallel=$1
    local requests=$2
    local dataset_basename=$3

    validate_params "$parallel" "$requests"

    local name="p${parallel}_n${requests}_d${dataset_basename}"
    local output_dir="$OUTPUT_DIR/$name"
    mkdir -p "$output_dir"

    local first_prompt=$(get_first_prompt)
    local evalscope_cmd=$(build_evalscope_command "$parallel" "$requests" "$output_dir" "$first_prompt")

    log "🚀 性能测试开始"
    log "📋 配置: 并发=$parallel 请求=$requests 提示=$first_prompt"
    log "⏱️  预计耗时: $((requests * 2 / parallel))分钟"
    log "----------------------------------------"
    log "🔧 执行命令: $evalscope_cmd"

    eval "$evalscope_cmd" 2>&1
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "✅ 测试完成"
        log "💾 结果保存: $output_dir"
    else
        error "❌ 测试执行失败 (退出码: $exit_code): 1.服务未运行 2.并发数过高 3.网络问题 4.参数错误"
        exit 3
    fi
    log "----------------------------------------"
}

quick_test() {
    log "⚡ 快速验证模式 (2分钟)"
    local dataset_basename=$(basename "$DATASET" .jsonl)
    run_single_test 32 50 "$dataset_basename"
    printf "\n💡 提示: 使用 -p 64 -n 200 进行完整测试\n"
}

# 1. 快速验证测试 (Quick Verification Test)
quick_verification_test() {
    log "⚡ 快速验证测试 (2分钟) - 基础配置，适合快速验证服务可用性"
    local dataset_basename=$(basename "$DATASET" .jsonl)
    
    # 设置参数：--timeout 30 --read-timeout 60 --sleep-interval 5 --rate 5
    local original_connect_timeout=$CONNECT_TIMEOUT
    local original_read_timeout=$READ_TIMEOUT
    local original_sleep_interval=$SLEEP_INTERVAL
    local original_rate_limit=$RATE_LIMIT
    
    CONNECT_TIMEOUT=30
    READ_TIMEOUT=60
    SLEEP_INTERVAL=5
    RATE_LIMIT=5
    
    run_single_test 32 50 "$dataset_basename"
    
    # 恢复原始参数
    CONNECT_TIMEOUT=$original_connect_timeout
    READ_TIMEOUT=$original_read_timeout
    SLEEP_INTERVAL=$original_sleep_interval
    RATE_LIMIT=$original_rate_limit
    
    printf "\n💡 提示: 使用标准性能测试进行更全面的评估\n"
}

# 2. 标准性能测试 (Standard Performance Test)
standard_performance_test() {
    log "📊 标准性能测试 (5分钟) - 生产环境基准测试，准确测量真实性能"
    local dataset_basename=$(basename "$DATASET" .jsonl)
    
    # 设置参数：--timeout 120 --read-timeout 300 --sleep-interval 10 --rate 20
    local original_connect_timeout=$CONNECT_TIMEOUT
    local original_read_timeout=$READ_TIMEOUT
    local original_sleep_interval=$SLEEP_INTERVAL
    local original_rate_limit=$RATE_LIMIT
    
    CONNECT_TIMEOUT=120
    READ_TIMEOUT=300
    SLEEP_INTERVAL=10
    RATE_LIMIT=20
    
    run_single_test 64 200 "$dataset_basename"
    
    # 恢复原始参数
    CONNECT_TIMEOUT=$original_connect_timeout
    READ_TIMEOUT=$original_read_timeout
    SLEEP_INTERVAL=$original_sleep_interval
    RATE_LIMIT=$original_rate_limit
    
    printf "\n💡 提示: 如需更高压力测试，请使用生产环境压力测试\n"
}

# 3. 生产环境压力测试 (Production Environment Stress Test)
production_stress_test() {
    log "🚀 生产环境压力测试 (8分钟) - 高负载测试，验证生产环境稳定性"
    local dataset_basename=$(basename "$DATASET" .jsonl)
    
    # 设置参数：--timeout 300 --read-timeout 600 --sleep-interval 15 --rate 50
    local original_connect_timeout=$CONNECT_TIMEOUT
    local original_read_timeout=$READ_TIMEOUT
    local original_sleep_interval=$SLEEP_INTERVAL
    local original_rate_limit=$RATE_LIMIT
    
    CONNECT_TIMEOUT=300
    READ_TIMEOUT=600
    SLEEP_INTERVAL=15
    RATE_LIMIT=50
    
    run_single_test 128 300 "$dataset_basename"
    
    # 恢复原始参数
    CONNECT_TIMEOUT=$original_connect_timeout
    READ_TIMEOUT=$original_read_timeout
    SLEEP_INTERVAL=$original_sleep_interval
    RATE_LIMIT=$original_rate_limit
    
    printf "\n💡 提示: 极限压力测试可找到服务最大承载能力\n"
}

# 4. 极限压力测试 (Extreme Stress Test)
extreme_stress_test() {
    log "🔥 极限压力测试 (15分钟) - 寻找服务性能极限，无速率限制"
    local dataset_basename=$(basename "$DATASET" .jsonl)
    
    # 设置参数：--timeout 300 --read-timeout 600 --sleep-interval 30 (无速率限制)
    local original_connect_timeout=$CONNECT_TIMEOUT
    local original_read_timeout=$READ_TIMEOUT
    local original_sleep_interval=$SLEEP_INTERVAL
    local original_rate_limit=$RATE_LIMIT
    
    CONNECT_TIMEOUT=300
    READ_TIMEOUT=600
    SLEEP_INTERVAL=30
    RATE_LIMIT=""
    
    run_single_test 256 500 "$dataset_basename"
    
    # 恢复原始参数
    CONNECT_TIMEOUT=$original_connect_timeout
    READ_TIMEOUT=$original_read_timeout
    SLEEP_INTERVAL=$original_sleep_interval
    RATE_LIMIT=$original_rate_limit
    
    printf "\n💡 提示: 请确保服务器资源充足，避免系统过载\n"
}

# ============================================================================
# 参数解析
# ============================================================================
parse_multi_values() {
    local param="$1"
    shift
    local values=()

    while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
        values+=("$1")
        shift
    done

    if [[ ${#values[@]} -eq 0 ]]; then
        error "参数 $param 需要至少一个数值"
        usage
        exit 1
    fi

    echo "${values[@]}"
}

parse_single_arg() {
    local arg="$1" var_name="$2" shift_count=1
    [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; }
    declare -g "$var_name"="$2"
    echo $((shift_count + 1))
}

handle_parallel_arg() {
    local -a parallel_values
    parallel_values=($(parse_multi_values "-p" "$@"))
    local processed=${#parallel_values[@]}
    for ((i=0; i<processed; i++)); do
        shift
    done
    echo "$processed"
}

handle_request_arg() {
    local -a request_values
    request_values=($(parse_multi_values "-n" "$@"))
    local processed=${#request_values[@]}
    for ((i=0; i<processed; i++)); do
        shift
    done
    echo "$processed"
}

# ============================================================================
# 帮助信息
# ============================================================================
usage() {
    cat << EOF
${GREEN}evalperf.sh${NC} - LLM性能快速测试工具

${GREEN}用法${NC}:
  evalperf.sh [选项]

${GREEN}常用命令${NC}:
  evalperf.sh                    快速验证（默认）
  evalperf.sh -p 64 -n 200      单次完整测试
  
${GREEN}预设测试场景${NC}:
  evalperf.sh --quick-verification 快速验证测试 (2分钟, 32并发50请求)
  evalperf.sh --standard          标准性能测试 (5分钟, 64并发200请求)  
  evalperf.sh --production        生产环境压力测试 (8分钟, 128并发300请求)
  evalperf.sh --extreme           极限压力测试 (15分钟, 256并发500请求)

${GREEN}参数说明${NC}:
  ${GREEN}-p <num> [num...]${NC}    并发数 (默认: 64, 环境变量: EVALPERF_PARALLEL)
  ${GREEN}-n <num> [num...]${NC}    请求数 (默认: 200, 环境变量: EVALPERF_REQUESTS)
  ${GREEN}-d <path>${NC}   数据集路径 (默认: ./prompts/p_short.jsonl, 环境变量: EVALPERF_DATASET)
  ${GREEN}-o <dir>${NC}    输出目录 (默认: ./results, 环境变量: EVALPERF_OUTPUT_DIR)
  ${GREEN}-m <name>${NC}   模型名称 (默认: Qwen3-VL-235B-A22B-Instruct, 环境变量: EVALPERF_MODEL)
  ${GREEN}-u <url>${NC}    服务URL (默认: http://100.125.1.153/v1/chat/completions, 环境变量: EVALPERF_URL)
  ${GREEN}-t <num>${NC}    最大令牌数 (默认: 200, 环境变量: EVALPERF_MAX_TOKENS)
  ${GREEN}--quick${NC}      快速验证模式 (32并发, 50请求)
  ${GREEN}--timeout <num>${NC} 连接超时秒数 (默认: 30)
  ${GREEN}--read-timeout <num>${NC} 读取超时秒数 (默认: 60)
  ${GREEN}--rate <num>${NC}  每秒请求数限制 (默认: 无限制)
  ${GREEN}--no-timeout${NC} 禁用所有超时限制
  ${GREEN}-h, --help${NC}   显示帮助信息

${GREEN}示例${NC}:
  evalperf.sh                              # 使用默认设置快速验证
  evalperf.sh --quick                       # 快速验证模式
  evalperf.sh -p 128 -n 100                # 128并发，100请求
  evalperf.sh -p 32 64 -n 50 100          # 多组测试：32/64并发 × 50/100请求
  evalperf.sh -p 64 -n 200 -d custom.jsonl # 自定义数据集
  evalperf.sh -m "gpt-4" -u "http://localhost:8000/v1/chat/completions" -t 512 # 自定义模型和URL
  evalperf.sh --timeout 60 --read-timeout 120 # 设置更长的超时时间
  evalperf.sh --rate 10 # 限制为每秒10个请求
  evalperf.sh --no-timeout # 禁用所有超时限制（用于长时间测试）
  EVALPERF_PARALLEL=32 EVALPERF_REQUESTS=100 evalperf.sh       # 通过环境变量设置默认值
EOF
}

# ============================================================================
# 主函数
# ============================================================================
run_test_combinations() {
    local dataset_basename=$(basename "$DATASET" .jsonl)
    for p_val in "${parallel_values[@]}"; do
        for n_val in "${request_values[@]}"; do
            if [[ ${#parallel_values[@]} -gt 1 || ${#request_values[@]} -gt 1 ]]; then
                log "🔄 运行测试组合: 并发=$p_val 请求=$n_val"
            fi
            run_single_test "$p_val" "$n_val" "$dataset_basename"
        done
    done
}

main() {
    local mode="single"
    local -a parallel_values=()
    local -a request_values=()

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p) shift; parallel_values=($(parse_multi_values "-p" "$@"));
                   for ((i=0; i<${#parallel_values[@]}; i++)); do shift; done ;;
            -n) shift; request_values=($(parse_multi_values "-n" "$@"));
                   for ((i=0; i<${#request_values[@]}; i++)); do shift; done ;;
            -d) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                   DATASET="$2"; shift 2 ;;
            -o) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                   OUTPUT_DIR="$2"; shift 2 ;;
            -m) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                   MODEL="$2"; shift 2 ;;
            -u) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                   URL="$2"; shift 2 ;;
            -t) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                   MAX_TOKENS="$2"; shift 2 ;;
            --timeout) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                       CONNECT_TIMEOUT="$2"; shift 2 ;;
            --read-timeout) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                         READ_TIMEOUT="$2"; shift 2 ;;
            --rate) [[ $# -lt 2 ]] && { error "参数 $1 需要值"; usage; exit 1; };
                    RATE_LIMIT="$2"; shift 2 ;;
            --no-timeout) DISABLE_TIMEOUT="true"; shift ;;
            --quick) mode="quick"; shift ;;
            --quick-verification) mode="quick_verification"; shift ;;
            --standard) mode="standard_performance"; shift ;;
            --production) mode="production_stress"; shift ;;
            --extreme) mode="extreme_stress"; shift ;;
            -h|--help) usage; exit 0 ;;
            *) error "未知参数: $1"; usage; exit 1 ;;
        esac
    done

    # 设置默认值
    [[ ${#parallel_values[@]} -eq 0 ]] && parallel_values=("$PARALLEL")
    [[ ${#request_values[@]} -eq 0 ]] && request_values=("$REQUESTS")

    check_env

    case $mode in
        quick) quick_test ;;
        quick_verification) quick_verification_test ;;
        standard_performance) standard_performance_test ;;
        production_stress) production_stress_test ;;
        extreme_stress) extreme_stress_test ;;
        single) run_test_combinations ;;
    esac
}

# 只有当脚本直接执行时才运行main，而不是被source时
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
