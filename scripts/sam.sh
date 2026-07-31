#!/usr/bin/env sh

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

load_env() {
    if [ -n "${ENV_FILE:-}" ] && [ -f "$ENV_FILE" ]; then
        set -a
        case "$ENV_FILE" in
            */*) . "$ENV_FILE" ;;
            *) . "./$ENV_FILE" ;;
        esac
        set +a
    elif [ -f ".env" ]; then
        set -a
        . "./.env"
        set +a
    fi
}

sam_cmd() {
    if [ "$AWS_TARGET" = "local" ]; then
        env -u AWS_PROFILE \
            AWS_SDK_LOAD_CONFIG=0 \
            AWS_ACCESS_KEY_ID=test \
            AWS_SECRET_ACCESS_KEY=test \
            AWS_DEFAULT_REGION="$AWS_REGION" \
            AWS_REGION="$AWS_REGION" \
            AWS_ENDPOINT_URL="$AWS_LOCAL_ENDPOINT" \
            sam "$@"
    elif [ "$AWS_TARGET" = "remote" ]; then
        sam "$@"
    else
        echo "AWS_TARGET must be 'local' or 'remote'." >&2
        exit 2
    fi
}

aws_cmd() {
    if [ "$AWS_TARGET" = "local" ]; then
        env -u AWS_PROFILE \
            AWS_SDK_LOAD_CONFIG=0 \
            AWS_ACCESS_KEY_ID=test \
            AWS_SECRET_ACCESS_KEY=test \
            AWS_DEFAULT_REGION="$AWS_REGION" \
            AWS_REGION="$AWS_REGION" \
            aws --endpoint-url="$AWS_LOCAL_ENDPOINT" "$@"
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

get_api_id() {
    aws_cmd cloudformation describe-stack-resource \
        --stack-name "$STACK_NAME" \
        --logical-resource-id TicketingApi \
        --query "StackResourceDetail.PhysicalResourceId" \
        --output text
}

get_api_stage() {
    aws_cmd apigateway get-stages \
        --rest-api-id "$1" \
        --query "item[?stageName=='prod'].stageName | [0]" \
        --output text
}

print_api_url() {
    API_ID="$(get_api_id)"
    API_STAGE="$(get_api_stage "$API_ID")"

    if [ "$API_STAGE" = "None" ] || [ -z "$API_STAGE" ]; then
        API_STAGE="prod"
    fi

    if [ "$AWS_TARGET" = "local" ]; then
        API_URL="$AWS_LOCAL_ENDPOINT/restapis/$API_ID/$API_STAGE/_user_request_"
    else
        API_URL="https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/$API_STAGE"
    fi

    printf "\nAPI Gateway URL:\n%s\n\n" "$API_URL"
    printf "Example:\ncurl -i %s/events\n\n" "$API_URL"
}

run_local_api() {
    AWS_TARGET="${AWS_TARGET:-local}"
    build_package

    sam_cmd local start-api \
        --template .aws-sam/build/template.yaml \
        --port "$SAM_LOCAL_PORT"
}

deploy_local() {
    AWS_TARGET="local"
    build_package

    sam_cmd deploy \
        --template-file .aws-sam/build/template.yaml \
        --stack-name "$STACK_NAME" \
        --capabilities CAPABILITY_IAM \
        --resolve-s3 false \
        --s3-bucket local-bucket \
        --guided

    print_api_url
}

deploy_remote() {
    AWS_TARGET="remote"
    build_package

    sam_cmd deploy \
        --template-file .aws-sam/build/template.yaml \
        --stack-name "$STACK_NAME" \
        --capabilities CAPABILITY_IAM \
        --guided

    print_api_url
}

delete_local() {
    AWS_TARGET="local"

    aws_cmd cloudformation delete-stack --stack-name "$STACK_NAME"
    aws_cmd cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"

    printf "\nDeleted local stack: %s\n\n" "$STACK_NAME"
}

delete_remote() {
    AWS_TARGET="remote"

    sam_cmd delete \
        --stack-name "$STACK_NAME"
}

load_env

ACTION="${1:-local}"
AWS_REGION="${AWS_REGION:-sa-east-1}"
AWS_LOCAL_ENDPOINT="${AWS_LOCAL_ENDPOINT:-http://localhost:4566}"
STACK_NAME="${STACK_NAME:-serverless-ticketing-notifications}"
TEMPLATE_FILE="${TEMPLATE_FILE:-template.yaml}"
SAM_LOCAL_PORT="${SAM_LOCAL_PORT:-3000}"
REQUIREMENTS_FILE="src/requirements.txt"

trap cleanup_requirements EXIT HUP INT TERM

case "$ACTION" in
    local) run_local_api ;;
    deploy-local) deploy_local ;;
    deploy-remote) deploy_remote ;;
    delete-local) delete_local ;;
    delete-remote) delete_remote ;;
    *)
        echo "Usage: $0 {local|deploy-local|deploy-remote|delete-local|delete-remote}" >&2
        exit 2
        ;;
esac
