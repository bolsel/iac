resource "cloudflare_zone" "this" {
  name                = var.zone_name
  paused              = false
  type                = "full"
  vanity_name_servers = []
  account = {
    id = var.account_id
  }
}

output "id" {
  value = cloudflare_zone.this.id
}

output "name" {
  value = cloudflare_zone.this.name
}
