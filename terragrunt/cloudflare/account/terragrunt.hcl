include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
}

generate = local.common.generate

remote_state = local.common.remote_state

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/account"
}

inputs = {
  account_name = include.root.locals.env_vars.cloudflare_account_name
}

