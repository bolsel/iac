resource "cloudflare_account" "this" {
  name = var.account_name
  settings = {
    abuse_contact_email    = null
    access_approval_expiry = null
    api_access_enabled     = null
    enforce_twofactor      = false
  }
}

output "id" {
  value = cloudflare_account.this.id
}
