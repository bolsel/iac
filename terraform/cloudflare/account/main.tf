resource "cloudflare_account" "this" {
  name = var.account_name
  settings = {
    abuse_contact_email = null
    enforce_twofactor   = false
  }
}

output "id" {
  value = cloudflare_account.this.id
}

output "name" {
  value = cloudflare_account.this.name
}
