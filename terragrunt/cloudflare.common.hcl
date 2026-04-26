include "root" {
  path   = "root.hcl"
  expose = true
}

locals {
  api_key       = include.root.locals.env_vars.cloudflare_api_key
  api_token     = include.root.locals.env_vars.cloudflare_api_token
  account_id    = try(include.root.locals.env_vars.cloudflare_account_id, null)
  account_email = include.root.locals.env_vars.cloudflare_account_email
  zone_id       = try(include.root.locals.env_vars.cloudflare_zone_id, null)
  resource_name = basename(get_original_terragrunt_dir())
}

generate "provider" {
  path      = "provider_cloudflare.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5"
    }
  }
}
provider "cloudflare" {
  api_token = "${local.api_token}"
}
EOF
}

remote_state {
  backend = "local"
  config = {
    path = "${include.root.locals.path_private_env}/tf-states/cloudflare_${local.resource_name}.tfstate"
  }
  generate = {
    path      = "backend.generated.tf"
    if_exists = "overwrite_terragrunt"
  }
}
