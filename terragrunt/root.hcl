locals {
  path_ws          = dirname(find_in_parent_folders("tg.ws.hcl"))
  ws_config        = read_terragrunt_config("${local.path_ws}/tg.ws.hcl").locals
  environment      = local.ws_config.environment
  path_root        = "${local.path_ws}/${local.ws_config.dir_terragrunt}"
  path_private     = "${local.path_ws}/${local.ws_config.dir_private}"
  path_private_env = "${local.path_private}/envs/${local.environment}"
  path_terraform   = "${local.path_ws}/${local.ws_config.dir_terraform}"
  path_scripts     = "${local.path_ws}/${local.ws_config.dir_scripts}"


  env_vars_default     = try(yamldecode(file("${local.path_private}/env.default.yaml")), {})
  env_vars_environment = try(yamldecode(file("${local.path_private}/env.${local.environment}.yaml")), {})
  env_vars_generated   = try(yamldecode(file("${local.path_private_env}/env.generated.yaml")), {})
  env_vars             = merge(local.env_vars_generated, local.env_vars_default, local.env_vars_environment)


}
