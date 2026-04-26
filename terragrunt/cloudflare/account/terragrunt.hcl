include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common       = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
  account_name = try(include.root.locals.env_vars.cloudflare_account_name, "")
}

generate = local.common.generate

remote_state = local.common.remote_state

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/account"
  before_hook "check_resource" {
    commands = ["plan", "apply"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "account",
      jsonencode(include.root.locals)
    ]
  }
  after_hook "generate_resource" {
    commands = ["apply", "import"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "account",
      jsonencode(include.root.locals)
    ]
  }
}

inputs = {
  account_name = local.account_name
}

