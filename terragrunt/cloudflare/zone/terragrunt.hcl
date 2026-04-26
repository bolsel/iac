include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common          = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
  account_id      = local.common.locals.account_id
  is_deps_account = local.account_id == null
  zone_name       = try(include.root.locals.env_vars.cloudflare_zone_name, "")
}

generate = local.common.generate

remote_state = local.common.remote_state

dependency "account" {
  config_path = "../account"
  enabled     = local.is_deps_account
  mock_outputs = {
    id = local.account_id
  }

}

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/zone"
  before_hook "check_resource" {
    commands = ["plan", "apply"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "zone",
      jsonencode(include.root.locals)
    ]
  }
  after_hook "generate_resource" {
    commands = ["apply", "import"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "zone",
      jsonencode(include.root.locals)
    ]
  }
}

inputs = {
  account_id = try(dependency.account.outputs.id, local.account_id)
  zone_name  = local.zone_name
}

