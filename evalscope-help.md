(evalscope) ➜  ~ evalscope perf -h
usage: evalscope <command> [<args>] perf [-h] --model MODEL [--attn-implementation ATTN_IMPLEMENTATION] [--api API] [--tokenizer-path TOKENIZER_PATH] [--url URL]
                                         [--port PORT] [--headers HEADERS [HEADERS ...]] [--api-key API_KEY] [--connect-timeout CONNECT_TIMEOUT]
                                         [--read-timeout READ_TIMEOUT] [--no-test-connection] [-n NUMBER [NUMBER ...]] [--parallel PARALLEL [PARALLEL ...]] [--rate RATE]
                                         [--sleep-interval SLEEP_INTERVAL] [--db-commit-interval DB_COMMIT_INTERVAL] [--queue-size-multiplier QUEUE_SIZE_MULTIPLIER]
                                         [--in-flight-task-multiplier IN_FLIGHT_TASK_MULTIPLIER] [--log-every-n-query LOG_EVERY_N_QUERY] [--debug]
                                         [--visualizer VISUALIZER] [--wandb-api-key WANDB_API_KEY] [--swanlab-api-key SWANLAB_API_KEY] [--name NAME]
                                         [--max-prompt-length MAX_PROMPT_LENGTH] [--min-prompt-length MIN_PROMPT_LENGTH] [--prefix-length PREFIX_LENGTH]
                                         [--prompt PROMPT] [--query-template QUERY_TEMPLATE] [--apply-chat-template APPLY_CHAT_TEMPLATE] [--image-width IMAGE_WIDTH]
                                         [--image-height IMAGE_HEIGHT] [--image-format IMAGE_FORMAT] [--image-num IMAGE_NUM] [--image-patch-size IMAGE_PATCH_SIZE]
                                         [--outputs-dir OUTPUTS_DIR] [--dataset DATASET] [--dataset-path DATASET_PATH] [--frequency-penalty FREQUENCY_PENALTY]
                                         [--repetition-penalty REPETITION_PENALTY] [--logprobs] [--max-tokens MAX_TOKENS] [--min-tokens MIN_TOKENS]
                                         [--n-choices N_CHOICES] [--seed SEED] [--stop [STOP ...]] [--stop-token-ids [STOP_TOKEN_IDS ...]] [--stream | --no-stream]
                                         [--temperature TEMPERATURE] [--top-p TOP_P] [--top-k TOP_K] [--extra-args EXTRA_ARGS]

options:
  -h, --help            show this help message and exit
  --model MODEL         The test model name.
  --attn-implementation ATTN_IMPLEMENTATION
                        Attention implementaion
  --api API             Specify the service API
  --tokenizer-path TOKENIZER_PATH
                        Specify the tokenizer weight path
  --url URL
  --port PORT           The port for local inference
  --headers HEADERS [HEADERS ...]
                        Extra HTTP headers
  --api-key API_KEY     The API key for authentication
  --connect-timeout CONNECT_TIMEOUT
                        The network connection timeout
  --read-timeout READ_TIMEOUT
                        The network read timeout
  --no-test-connection  Do not test the connection before starting the benchmark
  -n NUMBER [NUMBER ...], --number NUMBER [NUMBER ...]
                        How many requests to be made
  --parallel PARALLEL [PARALLEL ...]
                        Set number of concurrency requests, default 1
  --rate RATE           Number of requests per second. default None
  --sleep-interval SLEEP_INTERVAL
                        Sleep interval between performance runs, in seconds. Default 5
  --db-commit-interval DB_COMMIT_INTERVAL
                        Rows buffered before SQLite commit
  --queue-size-multiplier QUEUE_SIZE_MULTIPLIER
                        Queue maxsize = parallel * multiplier
  --in-flight-task-multiplier IN_FLIGHT_TASK_MULTIPLIER
                        Max scheduled tasks = parallel * multiplier
  --log-every-n-query LOG_EVERY_N_QUERY
                        Logging every n query
  --debug               Debug request send
  --visualizer VISUALIZER
                        The visualizer to use, default None
  --wandb-api-key WANDB_API_KEY
                        The wandb API key
  --swanlab-api-key SWANLAB_API_KEY
                        The swanlab API key
  --name NAME           The wandb/swanlab db result name and result db name
  --max-prompt-length MAX_PROMPT_LENGTH
                        Maximum input prompt length
  --min-prompt-length MIN_PROMPT_LENGTH
                        Minimum input prompt length
  --prefix-length PREFIX_LENGTH
                        The prefix length
  --prompt PROMPT       Specified the request prompt
  --query-template QUERY_TEMPLATE
                        Specify the query template
  --apply-chat-template APPLY_CHAT_TEMPLATE
                        Apply chat template to the prompt
  --image-width IMAGE_WIDTH
                        Width of the image for random VL dataset
  --image-height IMAGE_HEIGHT
                        Height of the image for random VL dataset
  --image-format IMAGE_FORMAT
                        Image format for random VL dataset
  --image-num IMAGE_NUM
                        Number of images for random VL dataset
  --image-patch-size IMAGE_PATCH_SIZE
                        Patch size for image tokenizer, only for local image token calculation
  --outputs-dir OUTPUTS_DIR
                        Outputs dir.
  --dataset DATASET     Specify the dataset
  --dataset-path DATASET_PATH
                        Path to the dataset file
  --frequency-penalty FREQUENCY_PENALTY
                        The frequency_penalty value
  --repetition-penalty REPETITION_PENALTY
                        The repetition_penalty value
  --logprobs            The logprobs
  --max-tokens MAX_TOKENS
                        The maximum number of tokens that can be generated
  --min-tokens MIN_TOKENS
                        The minimum number of tokens that can be generated
  --n-choices N_CHOICES
                        How many completion choices to generate
  --seed SEED           The random seed
  --stop [STOP ...]     The stop tokens
  --stop-token-ids [STOP_TOKEN_IDS ...]
                        Set the stop token IDs
  --stream, --no-stream
                        Stream output with SSE (default: True)
  --temperature TEMPERATURE
                        The sample temperature
  --top-p TOP_P         Sampling top p
  --top-k TOP_K         Sampling top k
  --extra-args EXTRA_ARGS
                        Extra arguments, should in JSON format
(evalscope) ➜  ~