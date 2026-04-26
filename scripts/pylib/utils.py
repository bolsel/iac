import re
import yaml
import json
import subprocess

def normalize_key(key: str) -> str:
    """
    Normalize key to be used as a variable name
    
    Args:
        key (str): The key to normalize
    
    Returns:
        str: The normalized key
    """
    key = key.strip().lower()
    key = re.sub(r'[^a-z0-9_]+', '_', key) # replace invalid chars to underscore
    key = re.sub(r'_+', '_', key) # remove duplicate underscores
    key = key.strip('_') # trim underscore both side
    if not key: # if empty -> root
        key = 'root'
    if key[0].isdigit(): # if starts with digit -> prefix r
        key = f"r_{key}"
    return key

def short_dns_name(full_name, zone_name):
    if full_name == zone_name:
        return "@"
    suffix = f".{zone_name}"
    if full_name.endswith(suffix):
        return full_name[:-len(suffix)]
    return full_name

def generate_dns_key(key: str, _type: str, results: dict) -> str:
    """
    Generate a unique key for a DNS record
    
    Args:
        key (str): The key to generate a unique key for
        _type (str): The type of the DNS record
        results (dict): The results dictionary
    
    Returns:
        str: The unique key for the DNS record
    """
    key = normalize_key(key)
    base_key = f"{key}_{_type}"
    if base_key not in results:
        return base_key
    _next = 2
    while True:
        curr_key = f"{base_key}_{_next:02d}"
        if curr_key not in results:
            return curr_key
        _next += 1


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
