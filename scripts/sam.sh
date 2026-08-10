#!/usr/bin/env sh

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

local_aws_env() {
    env -u AWS_PROFILE \
        AWS_SDK_LOAD_CONFIG=0 \
        AWS_ACCESS_KEY_ID=test \
        AWS_SECRET_ACCESS_KEY=test \
        AWS_DEFAULT_REGION="$LOCAL_AWS_REGION" \
        AWS_REGION="$LOCAL_AWS_REGION" \
        AWS_ENDPOINT_URL="$LOCAL_AWS_ENDPOINT" \
        "$@"
}

sam_cmd() {
    if [ "$AWS_TARGET" = "local" ]; then
        local_aws_env sam "$@"
    elif [ "$AWS_TARGET" = "remote" ]; then
        sam "$@"
    else
        echo "AWS_TARGET must be 'local' or 'remote'." >&2
        exit 2
    fi
}

aws_cmd() {
    if [ "$AWS_TARGET" = "local" ]; then
        local_aws_env aws --endpoint-url="$LOCAL_AWS_ENDPOINT" "$@"
    elif [ "$AWS_TARGET" = "remote" ]; then
        aws "$@"
    else
        echo "AWS_TARGET must be 'local' or 'remote'." >&2
        exit 2
    fi
}

cleanup_requirements() {
    rm -f "$REQUIREMENTS_FILE"
}

build_package() {
    uv export \
        --quiet \
        --no-cache \
        --format requirements.txt \
        --no-dev \
        --no-emit-project \
        --no-header \
        --no-hashes \
        --no-annotate \
        --output-file "$REQUIREMENTS_FILE"

    sam_cmd build --template-file "$TEMPLATE_FILE"
    cleanup_requirements
}

get_stack_output() {
    aws_cmd cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" \
        --output text
}

default_stack_name() {
    if [ "$AWS_TARGET" = "local" ]; then
        printf "%s" "$PROJECT_NAME-local-$API_STAGE"
    else
        printf "%s" "$PROJECT_NAME-$API_STAGE"
    fi
}

default_sam_config_env() {
    if [ "$AWS_TARGET" = "local" ]; then
        printf "%s" "local-$API_STAGE"
    else
        printf "%s" "$API_STAGE"
    fi
}

ensure_local_bucket() {
    if aws_cmd s3api head-bucket --bucket "$LOCAL_ARTIFACT_BUCKET" 2>/dev/null; then
        return 0
    fi

    aws_cmd s3 mb "s3://$LOCAL_ARTIFACT_BUCKET"
}

validate_stage() {
    case "$API_STAGE" in
        dev | prod) ;;
        *)
            echo "STAGE must be 'dev' or 'prod'." >&2
            exit 2
            ;;
    esac
}

validate_target() {
    case "$AWS_TARGET" in
        local | remote) ;;
        *)
            echo "ENV must be 'local' or 'remote'." >&2
            exit 2
            ;;
    esac
}

usage() {
    echo "Usage: $0 local {dev|prod} | $0 {deploy|delete} {local|remote} {dev|prod}" >&2
    exit 2
}

print_api_url() {
    if [ "$AWS_TARGET" = "local" ]; then
        API_ID="$(get_stack_output ApiId)"
        API_STAGE="$(get_stack_output ApiStage)"
        API_URL="$LOCAL_AWS_ENDPOINT/restapis/$API_ID/$API_STAGE/_user_request_"
    else
        API_URL="$(get_stack_output ApiUrl)"
    fi

    printf "\nAPI Gateway URL:\n%s\n\n" "$API_URL"
    printf "Example:\ncurl -i %s/events\n\n" "$API_URL"
}

run_local_api() {
    AWS_TARGET="local"
    build_package

    sam_cmd local start-api \
        --template "$BUILT_TEMPLATE_FILE" \
        --port "$SAM_LOCAL_PORT"
}

deploy() {
    STACK_NAME="$(default_stack_name)"
    SAM_CONFIG_ENV="$(default_sam_config_env)"
    build_package

    if [ "$AWS_TARGET" = "local" ]; then
        ensure_local_bucket
    fi

    if [ "$AWS_TARGET" = "local" ]; then
        sam_cmd deploy \
            --config-file "$SAM_CONFIG_FILE" \
            --config-env "$SAM_CONFIG_ENV" \
            --template-file "$BUILT_TEMPLATE_FILE" \
            --stack-name "$STACK_NAME" \
            --s3-bucket "$LOCAL_ARTIFACT_BUCKET"
    else
        sam_cmd deploy \
            --config-file "$SAM_CONFIG_FILE" \
            --config-env "$SAM_CONFIG_ENV" \
            --template-file "$BUILT_TEMPLATE_FILE" \
            --stack-name "$STACK_NAME"
    fi

    print_api_url
}

delete() {
    STACK_NAME="$(default_stack_name)"
    SAM_CONFIG_ENV="$(default_sam_config_env)"

    if [ "$AWS_TARGET" = "local" ]; then
        aws_cmd cloudformation delete-stack --stack-name "$STACK_NAME"
        aws_cmd cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"

        printf "\nDeleted local stack: %s\n\n" "$STACK_NAME"
    else
        sam_cmd delete \
            --config-file "$SAM_CONFIG_FILE" \
            --config-env "$SAM_CONFIG_ENV" \
            --stack-name "$STACK_NAME"
    fi
}

PROJECT_NAME="serverless-ticketing-notifications"
LOCAL_AWS_REGION="sa-east-1"
LOCAL_AWS_ENDPOINT="http://localhost:4566"
TEMPLATE_FILE="template.yaml"
BUILT_TEMPLATE_FILE="$PROJECT_ROOT/.aws-sam/build/template.yaml"
SAM_LOCAL_PORT="3000"
LOCAL_ARTIFACT_BUCKET="local-bucket"
SAM_CONFIG_FILE="$PROJECT_ROOT/samconfig.yaml"
REQUIREMENTS_FILE="src/requirements.txt"

ACTION="${1:-local}"
case "$ACTION" in
    local)
        AWS_TARGET="local"
        API_STAGE="${2:-dev}"
        ;;
    deploy | delete)
        AWS_TARGET="${2:-local}"
        API_STAGE="${3:-dev}"
        ;;
    *) usage ;;
esac

trap cleanup_requirements EXIT HUP INT TERM
validate_stage
validate_target

case "$ACTION" in
    local) run_local_api ;;
    deploy) deploy ;;
    delete) delete ;;
    *) usage ;;
esac
