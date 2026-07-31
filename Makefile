AWS_TARGET ?= local
AWS_LOCAL_ENDPOINT ?= http://localhost:4566
TEMPLATE_FILE ?= template.yaml

.PHONY: format lint typecheck test check sam-validate sam-local deploy-local deploy-remote delete-local delete-remote ministack-health show-config

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
	sam validate --template-file $(TEMPLATE_FILE)

sam-local:
	./scripts/sam.sh local

deploy-local:
	./scripts/sam.sh deploy-local

deploy-remote:
	./scripts/sam.sh deploy-remote

delete-local:
	./scripts/sam.sh delete-local

delete-remote:
	./scripts/sam.sh delete-remote

ministack-health:
	curl $(AWS_LOCAL_ENDPOINT)/_ministack/health

show-config:
	@echo "AWS_TARGET=$(AWS_TARGET)"
	@echo "AWS_LOCAL_ENDPOINT=$(AWS_LOCAL_ENDPOINT)"
	@echo "TEMPLATE_FILE=$(TEMPLATE_FILE)"
