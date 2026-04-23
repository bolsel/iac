include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
}

generate = local.common.generate

remote_state = local.common.remote_state

dependency "account" {
  config_path = "../account"
}

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/zone"
}

inputs = {
  account_id = dependency.account.outputs.id
  zone_name  = include.root.locals.env_vars.cloudflare_zone_name
}

