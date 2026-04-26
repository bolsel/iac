include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common        = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
  zone_id       = local.common.locals.zone_id
  zone_name     = include.root.locals.env_vars.cloudflare_zone_name
  need_zone_dep = local.zone_id == null
  dns_config    = try(yamldecode(file("${include.root.locals.path_private_env}/cloudflare_dns_records.yaml")), {})
  dns_records = {
    for k, v in local.dns_config :
    k => merge(v, {
      name = v.name == "@" ? local.zone_name : "${v.name}.${local.zone_name}"
    })
  }
}

generate = local.common.generate

remote_state = local.common.remote_state

dependency "zone" {
  config_path = "../zone"
  enabled     = local.need_zone_dep
  mock_outputs = {
    id = local.zone_id
  }
}

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/dns-records"
  before_hook "check_resource" {
    commands = ["import", "plan", "apply"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "dns",
      jsonencode(include.root.locals)
    ]
  }
  after_hook "generate_resource" {
    commands = ["apply", "import"]
    execute = [
      "${include.root.locals.path_scripts}/cf-hook.py",
      "--resource", "dns",
      jsonencode(include.root.locals)
    ]
  }
}

inputs = {
  zone_id = try(dependency.zone.outputs.id, local.zone_id)
  records = local.dns_records
}

