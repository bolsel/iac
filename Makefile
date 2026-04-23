ENVIRONMENT ?= dev
# TF_PATH ?= /usr/bin/tofu
TF_PATH ?= /usr/bin/terraform

override PATH_WS := $(shell pwd)
override DIR_TERRAGRUNT := $(PATH_WS)/terragrunt
override DIR_TERRAFORM := $(PATH_WS)/terraform
override BASE_CACHE_DIR := $(PATH_WS)/.caches

export ENVIRONMENT
export TF_PLUGIN_CACHE_DIR=$(BASE_CACHE_DIR)/plugins

define _TG_COMMON_ARGS
--tf-path=$(TF_PATH) --source-update
endef

TG_RUN ?= apply

tg-run:
	terragrunt run --working-dir=$(DIR_TERRAGRUNT)/$(TG_PATH) $(TG_RUN) $(call _TG_COMMON_ARGS) -- $(ARGS)

tg-cf: ## Terragrunt run cloudflare units
	terragrunt run $(call _TG_COMMON_ARGS) --working-dir=$(DIR_TERRAGRUNT)/cloudflare --all -- $(TG_RUN) $(ARGS)

tg-cf-stack: ## Terragrunt run cloudflare stack
	terragrunt stack run $(call _TG_COMMON_ARGS) --working-dir=$(DIR_TERRAGRUNT)/stacks/cloudflare -- $(TG_RUN) $(ARGS)

tg-cf-dns: ## Terragrunt run cloudflare DNS
	$(MAKE) tg-run TG_PATH=cloudflare/dns

tg-cf-account: ## Terragrunt run cloudflare account
	$(MAKE) tg-run TG_PATH=cloudflare/account

tg-cf-zone: ## Terragrunt run cloudflare zone
	$(MAKE) tg-run TG_PATH=cloudflare/zone

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'
