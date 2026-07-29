AWS_TARGET ?= local
AWS_REGION ?= sa-east-1
AWS_LOCAL_ENDPOINT ?= http://localhost:4566
STACK_NAME ?= serverless-ticketing-notifications
TEMPLATE_FILE ?= template.yaml
SAM_LOCAL_PORT ?= 3000

ifeq ($(AWS_TARGET),local)
AWS := AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(AWS_REGION) AWS_REGION=$(AWS_REGION) aws --endpoint-url=$(AWS_LOCAL_ENDPOINT)
SAM := env -u AWS_PROFILE AWS_SDK_LOAD_CONFIG=0 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(AWS_REGION) AWS_REGION=$(AWS_REGION) AWS_ENDPOINT_URL=$(AWS_LOCAL_ENDPOINT) sam
else ifeq ($(AWS_TARGET),remote)
AWS := aws
SAM := sam
else
$(error AWS_TARGET must be "local" or "remote")
endif

.PHONY: format lint typecheck test check sam-validate sam-build sam-local aws-whoami ministack-health cfn-validate cfn-deploy cfn-delete cfn-describe show-aws-config

format:
	uv run ruff format

lint:
	uv run ruff check

typecheck:
	uv run ty check

test:
	uv run pytest tests

check: format lint typecheck test

sam-validate:
	$(SAM) validate --template-file $(TEMPLATE_FILE)

sam-build:
	$(SAM) build --template-file $(TEMPLATE_FILE)

sam-local: sam-build
	$(SAM) local start-api --template .aws-sam/build/template.yaml --port $(SAM_LOCAL_PORT)

aws-whoami:
	$(AWS) sts get-caller-identity

ministack-health:
	curl $(AWS_LOCAL_ENDPOINT)/_ministack/health

cfn-validate:
	$(AWS) cloudformation validate-template --template-body file://$(TEMPLATE_FILE)

cfn-deploy:
	$(AWS) cloudformation deploy --stack-name $(STACK_NAME) --template-file $(TEMPLATE_FILE) --capabilities CAPABILITY_IAM

cfn-delete:
	$(AWS) cloudformation delete-stack --stack-name $(STACK_NAME)

cfn-describe:
	$(AWS) cloudformation describe-stacks --stack-name $(STACK_NAME)

show-aws-config:
	@echo "AWS_TARGET=$(AWS_TARGET)"
	@echo "AWS_REGION=$(AWS_REGION)"
	@echo "AWS_LOCAL_ENDPOINT=$(AWS_LOCAL_ENDPOINT)"
	@echo "SAM_LOCAL_PORT=$(SAM_LOCAL_PORT)"
	@echo "AWS=$(AWS)"
	@echo "SAM=$(SAM)"
