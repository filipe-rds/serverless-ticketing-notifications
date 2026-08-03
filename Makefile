ifneq (,$(wildcard .env))
include .env
endif

ENV ?= local
STAGE ?= dev

.PHONY: format lint typecheck test check sam-validate sam-local deploy delete ministack-health show-config

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
	sam validate --template-file template.yaml

sam-local:
	./scripts/sam.sh local $(STAGE)

deploy:
	./scripts/sam.sh deploy $(ENV) $(STAGE)

delete:
	./scripts/sam.sh delete $(ENV) $(STAGE)

ministack-health:
	curl http://localhost:4566/_ministack/health

show-config:
	@echo "ENV=$(ENV)"
	@echo "STAGE=$(STAGE)"
