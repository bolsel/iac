locals {
  root_a = { name = "bolselkab-iac.dev", type = "A", content = "127.0.0.1", ttl = 1, proxied = false }
  dns_a  = { name = "dns.bolselkab-iac.dev", type = "A", content = "1.1.1.1", ttl = 1, proxied = false }
}
