#!/usr/bin/env python
import os
import argparse
import yaml
import json
import subprocess
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

def tf_import_block(type, id, resource_name = "this"):
    return f"""
import {{
  to = cloudflare_{type}.{resource_name}
  id = "{id}"
}}
"""

def tf_make_var(key, value):
    if value is None:
        val = "null"
    elif isinstance(value, bool):
        val = "true" if value else "false"
    elif isinstance(value, (str, list, dict)):
        val = json.dumps(value)
    else:
        val = str(value)
    return f"{key} = {val}\n"

def tf_make_vars(data):
    _vars = ""
    for k, v in data.items():
        _vars += tf_make_var(k, v)
    return _vars

def tf_resource_has_state():
    try:
        out = subprocess.check_output(
            ["terraform", "state", "list"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        return out
    except:
        return False

def tf_get_outputs():
    result = subprocess.check_output(
        ["terraform", "output", "-json"],
        text=True
    )
    return json.loads(result)

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
    "zone": 'cloudflare_zone_id' in envs['env_vars']
}

match TG_CTX_HOOK_NAME:
    case 'check_resource':
        client = Cloudflare(
            api_email=envs['env_vars']['cloudflare_account_email'],
            api_key=envs['env_vars']['cloudflare_api_key']
        )

        if tf_resource_has_state():
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
                import_contents = tf_import_block("account", account.id)
                tf_vars += tf_make_var('account_name', account.name)
            case "zone":
                zone = client.zones.get(
                    zone_id=envs['env_vars']['cloudflare_zone_id']
                )
                import_contents = tf_import_block("zone", zone.id)
                tf_vars += tf_make_vars({
                    'account_id': zone.account.id,
                    'zone_name': zone.name
                })
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
        outputs = tf_get_outputs()
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
            case _:
                raise ValueError(f"Unknown resource type: {resource}")
    case _:
        print(f"Unknown hook name: {TG_CTX_HOOK_NAME}")
        exit(1)