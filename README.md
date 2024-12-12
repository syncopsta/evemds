# evemds - eve Metadata Server

## Overview

evemds (eve Metadata Server) is a lightweight cloud-init metadata server designed to provide minimal cloud-init configuration for virtual machines. It's built specifically for the [evectl](https://github.com/syncopsta/evectl) project.

## Features

- Serves cloud-init metadata, user-data, and vendor-data
- Configurable SSH key distribution based on hostname
- Fallback configuration for unknown hosts

## Configuration

The server uses a YAML configuration file (`hosts_config.yaml`) to manage SSH keys and instance assignments.

### Sample Configuration

```yaml
hosts:
  dbserver.example.com:
    ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2E... admin@company.com"
      - "ssh-rsa AAAAB3N5aD1eaFE... admin2@company.com"

  fallback.evectl:
    ssh_keys:
      - "ssh-rsa AAAAB3NzaNyRRk...eRzRCyip3oM="
```

The `fallback.evectl` entry is used when the requesting hostname is not explicitly listed.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `hosts_config.yaml` with your SSH keys and hostnames
4. Run the server: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Systemd Service

A sample systemd service file (`evemds.service`) is provided, pre-configured for the evectl install script.

## API Endpoints

- `GET /{hostname}/user-data`: Returns cloud-init user-data configuration
- `GET /{hostname}/meta-data`: Returns cloud-init meta-data configuration
- `GET /{hostname}/vendor-data`: Returns empty vendor-data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Please see the file called `LICENSE`.