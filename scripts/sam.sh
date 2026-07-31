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
        --s3-bucket local-bucket
}

deploy_remote() {
    AWS_TARGET="remote"
    build_package

    sam_cmd deploy \
        --template-file .aws-sam/build/template.yaml \
        --stack-name "$STACK_NAME" \
        --capabilities CAPABILITY_IAM \
        --guided
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
    *)
        echo "Usage: $0 {local|deploy-local|deploy-remote}" >&2
        exit 2
        ;;
esac
