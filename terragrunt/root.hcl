locals {
  path_ws          = dirname(find_in_parent_folders("tg.ws.hcl"))
  ws_config        = read_terragrunt_config("${local.path_ws}/tg.ws.hcl").locals
  environment      = local.ws_config.environment
  path_root        = "${local.path_ws}/${local.ws_config.dir_terragrunt}"
  path_private     = "${local.path_ws}/${local.ws_config.dir_private}"
  path_private_env = "${local.path_private}/envs/${local.environment}"
  path_terraform   = "${local.path_ws}/${local.ws_config.dir_terraform}"


  env_vars_default     = read_terragrunt_config("${local.path_private}/default.env.hcl").locals
  env_vars_environment = fileexists("${local.path_private}/${local.environment}.env.hcl") ? read_terragrunt_config("${local.path_private}/${local.environment}.env.hcl").locals : {}
  env_vars             = merge(local.env_vars_default, local.env_vars_environment)

}
