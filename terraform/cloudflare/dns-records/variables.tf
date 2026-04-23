variable "zone_id" {
  type        = string
  description = "Cloudflare Zone ID"
}

variable "records" {
  type = map(object({
    name     = string
    type     = string
    content  = string
    ttl      = optional(number, 1)
    proxied  = optional(bool, false)
    priority = optional(number)
  }))
  description = "Map of DNS records to create, keyed by a unique identifier"
}
