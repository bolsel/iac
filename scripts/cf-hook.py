#!/usr/bin/env python
import os
import argparse
import yaml
import json
import pylib
import subprocess
import shutil
from cloudflare import Cloudflare

TG_CTX_COMMAND=os.environ.get('TG_CTX_COMMAND')
TG_CTX_HOOK_NAME=os.environ.get('TG_CTX_HOOK_NAME')
TG_CTX_TF_PATH=os.environ.get('TG_CTX_TF_PATH')

parser = argparse.ArgumentParser()
parser.add_argument("--resource", required=True)
parser.add_argument("locals_json")

args = parser.parse_args()
resource = args.resource
envs = json.loads(args.locals_json)
path_generated_env = envs['path_private_env'] + '/env.generated.yaml'

def generate_env_vars(data):
    if TG_CTX_COMMAND != "apply":
        return
    try:
        env_vars = yaml.safe_load(open(path_generated_env)) or {}
    except:
        env_vars = {}
    env_vars.update(data)
    with open(path_generated_env, "w") as f:
        yaml.safe_dump(env_vars, f, sort_keys=True)

resources_check_exists = {
    "account": 'cloudflare_account_id' in envs['env_vars'],
    "zone": 'cloudflare_zone_id' in envs['env_vars'],
    "dns": 'cloudflare_zone_id' in envs['env_vars']
}

match TG_CTX_HOOK_NAME:
    case 'check_resource':
        client = Cloudflare(
            api_email=envs['env_vars']['cloudflare_account_email'],
            api_key=envs['env_vars']['cloudflare_api_key']
        )

        if pylib.utils.tf_resource_has_state():
            print(f"Resource '{resource}' already has state. skipping")
            exit(0)
        if not resources_check_exists[resource]:
            print(f"Resource '{resource}' is newly created. skipping import")
            exit(0)

        import_contents = ""
        tf_vars = ""
        match resource:
            case "account":
                account = client.accounts.get(
                    account_id=envs['env_vars']['cloudflare_account_id'],
                )
                import_contents = pylib.utils.tf_import_block("account", account.id)
                tf_vars += pylib.utils.tf_make_var('account_name', account.name)
            case "zone":
                zone = client.zones.get(
                    zone_id=envs['env_vars']['cloudflare_zone_id']
                )
                import_contents = pylib.utils.tf_import_block("zone", zone.id)
                tf_vars += pylib.utils.tf_make_vars({
                    'account_id': zone.account.id,
                    'zone_name': zone.name
                })
            case "dns":
                page = client.dns.records.list(
                    zone_id=envs['env_vars']['cloudflare_zone_id'], per_page=5000000
                )
                results = {}
                for record in page.result:
                    key = record.name.replace(f".{envs['env_vars']['cloudflare_zone_name']}", '')
                    if key == envs['env_vars']['cloudflare_zone_name']:
                        key = "root"
                    name = pylib.utils.short_dns_name(record.name, envs['env_vars']['cloudflare_zone_name'])
                    key_type = pylib.utils.generate_dns_key(key, record.type.lower(), results)
                    item = {
                        "name": name,
                        "type": record.type,
                        "content": record.content
                    }
                    if int(record.ttl) != 1:
                        item["ttl"] = int(record.ttl)
                    if record.proxied:
                        item["proxied"] = True
                    if getattr(record, 'priority', None) is not None:
                        item["priority"] = record.priority
                    if record.comment:
                        item["comment"] = record.comment
                    results[key_type] = item

                    import_contents += pylib.utils.tf_import_block("dns_record", f"{envs['env_vars']['cloudflare_zone_id']}/{record.id}", f'this["{key_type}"]')
                
                with open(f"{envs['path_tmp']}/{envs['environment']}_cloudflare_dns_records.yaml", "w") as f:
                    yaml.dump(results, f, indent=2, sort_keys=False)
                
                with open('.auto.tfvars.json', 'w') as f:
                    json.dump({'records':results}, f, indent=2)
            case _:
                print(f"Unknown resource type: {resource}")
                exit(1)

        if import_contents:
            with open("import.tf", "w") as f:
                f.write(import_contents)
        if tf_vars:
            with open("terraform.tfvars", "w") as f:
                f.write(tf_vars)

    case 'generate_resource':
        outputs = pylib.utils.tf_get_outputs()
        match resource:
            case "account":
                generate_env_vars({
                    'cloudflare_account_id': outputs['id']['value'],
                    'cloudflare_account_name': outputs['name']['value']
                })
            case "zone":
                generate_env_vars({
                    'cloudflare_zone_id': outputs['id']['value'],
                    'cloudflare_zone_name': outputs['name']['value']
                })
            case "dns":
                if os.path.exists(f"{envs['path_tmp']}/{envs['environment']}_cloudflare_dns_records.yaml"):
                    shutil.move(f"{envs['path_tmp']}/{envs['environment']}_cloudflare_dns_records.yaml", f"{envs['path_private_env']}/cloudflare_dns_records.yaml")
            case _:
                print(f"Unknown resource type: {resource}")
                exit(1)
    case _:
        print(f"Unknown hook name: {TG_CTX_HOOK_NAME}")
        exit(1)