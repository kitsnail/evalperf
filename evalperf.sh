#!/bin/bash

# 默认配置
MODEL=${EVALPERF_MODEL:-"Qwen3-VL-235B-A22B-Instruct"}
URL=${EVALPERF_URL:-"http://100.125.1.153/v1/chat/completions"}
DATASET=${EVALPERF_DATASET:-"./prompts/p_short.jsonl"}
MAX_TOKENS=${EVALPERF_MAX_TOKENS:-200}
OUTPUT_DIR=${EVALPERF_OUTPUT_DIR:-"./results"}
PARALLEL=${EVALPERF_PARALLEL:-64}
REQUESTS=${EVALPERF_REQUESTS:-200}

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
  ${GREEN}-p <num> [num...]${NC}    并发数 (默认: 64, 环境变量: EVALPERF_PARALLEL)
  ${GREEN}-n <num> [num...]${NC}    请求数 (默认: 200, 环境变量: EVALPERF_REQUESTS)
  ${GREEN}-d <path>${NC}   数据集路径 (默认: ./prompts/p_short.jsonl, 环境变量: EVALPERF_DATASET)
  ${GREEN}-o <dir>${NC}    输出目录 (默认: ./results, 环境变量: EVALPERF_OUTPUT_DIR)
  ${GREEN}-m <name>${NC}   模型名称 (默认: Qwen3-VL-235B-A22B-Instruct, 环境变量: EVALPERF_MODEL)
  ${GREEN}-u <url>${NC}    服务URL (默认: http://100.125.1.153/v1/chat/completions, 环境变量: EVALPERF_URL)
  ${GREEN}-t <num>${NC}    最大令牌数 (默认: 200, 环境变量: EVALPERF_MAX_TOKENS)
  ${GREEN}--quick${NC}      快速验证模式 (32并发, 50请求)
  ${GREEN}-h, --help${NC}   显示帮助信息

${GREEN}示例${NC}:
  evalperf.sh                              # 使用默认设置快速验证
  evalperf.sh --quick                       # 快速验证模式
  evalperf.sh -p 128 -n 100                # 128并发，100请求
  evalperf.sh -p 32 64 -n 50 100          # 多组测试：32/64并发 × 50/100请求
  evalperf.sh -p 64 -n 200 -d custom.jsonl # 自定义数据集
  evalperf.sh -m "gpt-4" -u "http://localhost:8000/v1/chat/completions" -t 512 # 自定义模型和URL
  EVALPERF_PARALLEL=32 EVALPERF_REQUESTS=100 evalperf.sh       # 通过环境变量设置默认值
EOF
}

validate_params() {
    local parallel=${1:-$PARALLEL}
    local requests=${2:-$REQUESTS}
    
    if (( parallel < 1 || parallel > 256 )); then
        error "并发数必须在 1-256 之间，当前: $parallel"
        exit 1
    fi
    if (( requests < 1 )); then
        error "请求数至少为 1，当前: $requests"
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

run_single_test() {
    local parallel=$1 requests=$2 dataset_basename=$3
    validate_params "$parallel" "$requests"
    local name="p${parallel}_n${requests}_d${dataset_basename}"
    local output_dir="$OUTPUT_DIR/$name"
    mkdir -p "$output_dir"
    
    # 从数据集中获取第一个提示用于测试
    local first_prompt=$(head -1 "$DATASET" | jq -r '.messages[0].content' 2>/dev/null || echo "Hello, how are you?")
    
    log "🚀 性能测试开始"
    log "📋 配置: 并发=$parallel 请求=$requests 提示=$first_prompt"
    log "⏱️  预计耗时: $((requests * 2 / parallel))分钟"
    log "----------------------------------------"
    # 执行 evalscope 命令并直接输出结果
    # 设置更短的超时时间以避免无限重试
    timeout 300 evalscope perf --model "$MODEL" --api "openai" --url "$URL" --prompt "$first_prompt" \
        --parallel "$parallel" --number "$requests" --max-tokens "$MAX_TOKENS" \
        --outputs-dir "$output_dir" --no-test-connection 2>&1
    local exit_code=$?
    
    # 检查是否被timeout终止
    if [ $exit_code -eq 124 ]; then
        error "❌ 测试超时 (5分钟): 服务响应过慢或网络连接问题"
        exit 3
    fi
    
    # 检查测试是否成功完成
    if [ $exit_code -eq 0 ]; then
        log "✅ 测试完成"
        log "💾 结果保存: $output_dir"
    else
        error "❌ 测试执行失败: 1.服务未运行 2.并发数过高 3.网络问题"
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

# 解析多个数值的函数
parse_multi_values() {
    local param="$1"
    shift
    local values=()
    
    # 收集所有数值直到遇到下一个参数或结束
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

# 修复参数解析逻辑
main() {
    local mode="single"
    local parallel_values=()
    local request_values=()
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p) 
                shift
                parallel_values=($(parse_multi_values "-p" "$@"))
                # 计算已处理的参数数量
                local processed=${#parallel_values[@]}
                for ((i=0; i<processed; i++)); do
                    shift
                done ;;
            -n) 
                shift
                request_values=($(parse_multi_values "-n" "$@"))
                # 计算已处理的参数数量
                local processed=${#request_values[@]}
                for ((i=0; i<processed; i++)); do
                    shift
                done ;;
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
    
    # 如果没有指定 -p 或 -n，使用默认值
    [[ ${#parallel_values[@]} -eq 0 ]] && parallel_values=("$PARALLEL")
    [[ ${#request_values[@]} -eq 0 ]] && request_values=("$REQUESTS")
    
    check_env
    case $mode in
        quick) 
            # 快速模式忽略指定的参数，使用固定值
            quick_test ;;
        single) 
            # 运行多组测试
            local dataset_basename=$(basename "$DATASET" .jsonl)
            for p_val in "${parallel_values[@]}"; do
                for n_val in "${request_values[@]}"; do
                    if [[ ${#parallel_values[@]} -gt 1 || ${#request_values[@]} -gt 1 ]]; then
                        log "🔄 运行测试组合: 并发=$p_val 请求=$n_val"
                    fi
                    run_single_test "$p_val" "$n_val" "$dataset_basename"
                done
            done ;;
    esac
}

# 只有当脚本直接执行时才运行main，而不是被source时
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
