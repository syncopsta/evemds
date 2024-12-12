from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from jinja2 import Environment, BaseLoader
from yaml import safe_load, dump
from typing import Dict, List
from pathlib import Path

app = FastAPI(
    title="evemds - eve metadata server",
    description="Provides cloud-init configuration for hosts",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Constants
CONFIG_FILE = "hosts_config.yaml"
METADATA_TEMPLATE = """## template: jinja
#cloud-config
ssh_authorized_keys:
{% for key in keys %}
  - {{ key }}
{% endfor %}
growpart:
  devices: [/]
  ignore_growroot_disabled: false
  mode: auto
resize_rootfs: noblock
package_reboot_if_required: true
package_update: true
package_upgrade: true
manage_etc_hosts: localhost"""

def load_config() -> Dict:
    """
    Load configuration from YAML file.

    Returns:
        Dict: Configuration dictionary

    Raises:
        FileNotFoundError: If config file is not found
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        config_path = Path(CONFIG_FILE)
        with config_path.open("r") as file:
            return safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {CONFIG_FILE} not found")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")

def get_ssh_keys(hostname: str, config: Dict) -> List[str]:
    """
    Get SSH keys for a specific hostname.

    Args:
        hostname: Host to get keys for
        config: Configuration dictionary

    Returns:
        List[str]: List of SSH keys
    """
    hosts = config.get("hosts", {})
    return (
        hosts.get(hostname, {}).get("ssh_keys", []) or
        hosts.get("fallback.evectl", {}).get("ssh_keys", [])
    )

@app.get("/{hostname}/user-data", response_class=PlainTextResponse)
async def get_user_data(hostname: str) -> str:
    """
    Generate user-data configuration for cloud-init.

    Args:
        hostname: Target hostname

    Returns:
        str: Rendered user-data configuration
    """
    config = load_config()
    ssh_keys = get_ssh_keys(hostname, config)
    template = Environment(loader=BaseLoader).from_string(METADATA_TEMPLATE)
    return template.render(keys=ssh_keys)

@app.get("/{hostname}/meta-data", response_class=PlainTextResponse)
async def get_meta_data(hostname: str) -> str:
    """
    Generate meta-data configuration for cloud-init.

    Args:
        hostname: Target hostname

    Returns:
        str: YAML formatted meta-data
    """
    data = {
        "instance-id": hostname,
        "local-hostname": hostname,
        "cloud-name": "evectl",
        "region": "local"
    }
    return dump(data)

@app.get("/{hostname}/vendor-data", response_class=PlainTextResponse)
async def get_vendor_data(hostname: str) -> str:
    """
    Return empty vendor-data.

    Args:
        hostname: Target hostname

    Returns:
        str: Empty string
    """
    return ""