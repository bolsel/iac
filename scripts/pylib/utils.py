import re
import yaml
import json
import subprocess

def normalize_dns_key(key: str, replace_str: str = '_', dot_replace: bool = False) -> str:
    """
    Normalize key to be used as a variable name
    
    Args:
        key (str): The key to normalize
        replace_str (str): The string to replace invalid chars with
        dot_replace (bool): Whether to replace dots with replace_str
    
    Returns:
        str: The normalized key
    """
    key = key.strip().lower()
    if dot_replace:
        key = key.replace('.', replace_str)
    key = key.replace('*', 'star')
    key = re.sub(r'[^a-z0-9\.-]+', replace_str, key) # replace invalid chars to replace_str
    key = key.strip(replace_str) # trim replace_str both side
    if not key: # if empty -> root
        key = 'root'
    if key[0].isdigit(): # if starts with digit -> prefix r
        key = f"r{replace_str}{key}"
    return key

def short_dns_name(full_name, zone_name):
    if full_name == zone_name:
        return "@"
    suffix = f".{zone_name}"
    if full_name.endswith(suffix):
        return full_name[:-len(suffix)]
    return full_name

def generate_dns_key(key: str, _type: str, results: dict, use_type=False, replace_str='_', dot_replace=False) -> str:
    """
    Generate a unique key for a DNS record
    
    Args:
        key (str): The key to generate a unique key for
        _type (str): The type of the DNS record
        results (dict): The results dictionary
        use_type (bool): Whether to use the type in the key
        replace_str (str): The string to replace invalid chars with
        dot_replace (bool): Whether to replace dots with replace_str
    
    Returns:
        str: The unique key for the DNS record
    """
    key = normalize_dns_key(key, replace_str=replace_str, dot_replace=dot_replace)
    base_key = f"{key}_{_type}" if use_type else key
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
