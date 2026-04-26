resource "cloudflare_dns_record" "this" {
  for_each = var.records

  zone_id  = var.zone_id
  name     = each.value.name
  type     = each.value.type
  content  = each.value.content
  ttl      = each.value.ttl
  proxied  = each.value.proxied
  priority = try(each.value.priority, null)
  comment  = each.value.comment
  settings = each.value.settings
  data     = each.value.data
  tags     = each.value.tags
}

output "record_ids" {
  value = { for k, r in cloudflare_dns_record.this : k => r.id }
}

output "record_names" {
  value = { for k, r in cloudflare_dns_record.this : k => r.name }
}

output "records" {
  value     = { for k, r in cloudflare_dns_record.this : k => r }
  sensitive = true
}
