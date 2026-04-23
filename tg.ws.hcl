locals {
  author         = "bolselkab"
  dir_private    = ".private"
  dir_terraform  = "terraform"
  dir_terragrunt = "terragrunt"
  environment    = get_env("ENVIRONMENT", "dev")
}
