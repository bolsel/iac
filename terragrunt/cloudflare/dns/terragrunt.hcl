include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

locals {
  common      = read_terragrunt_config(find_in_parent_folders("cloudflare.common.hcl"))
  dns_records = read_terragrunt_config("${include.root.locals.path_private_env}/cloudflare_dns_records.hcl").locals
}

generate = local.common.generate

remote_state = local.common.remote_state

dependency "zone" {
  config_path = "../zone"
}

terraform {
  source = "${include.root.locals.path_terraform}/cloudflare/dns-records"
}

inputs = {
  zone_id = dependency.zone.outputs.id
  records = local.dns_records
}

