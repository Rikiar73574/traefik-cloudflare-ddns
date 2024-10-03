# traefik-cloudflare-ddns

This repository provides a dynamic DNS (DDNS) solution to update Cloudflare DNS records with the public IP address of your Traefik router.

## Prerequisites

- Python 3.6 or higher
- Docker (optional for containerized deployment)
- Cloudflare account with API access

## Environment Variables

You need to set the following environment variables:

- `CF_ZONE_ID`: Your Cloudflare Zone ID
- `CF_API_KEY`: Your Cloudflare API Key
- `TRAEFIK_HOST`: Hostname of your Traefik instance (default: `traefik`)
- `TRAEFIK_PORT`: Port of your Traefik instance (default: `8080`)
- `EXTRA_DOMAINS`: Additional domains to update, separated by commas (optional)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Rikiar73574/traefik-cloudflare-ddns.git
    cd traefik-cloudflare-ddns
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the script, execute:

```sh
python main.py
```

Alternatively, you can use Docker:

1. Build the Docker image:

    ```sh
    docker build -t traefik-cloudflare-ddns .
    ```

2. Run the Docker container:

    ```sh
    docker run -e CF_ZONE_ID="your_zone_id" -e CF_API_KEY="your_api_key" -e TRAEFIK_HOST="traefik" -e TRAEFIK_PORT="8080" traefik-cloudflare-ddns
    ```

## Docker Compose

You can also use Docker Compose to manage the service. Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'

services:
  traefik-cloudflare-ddns:
    image: rikiar1/cf-traefik-ddns
    container_name: traefik-cloudflare-ddns
    environment:
      - CF_ZONE_ID=your_zone_id
      - CF_API_KEY=your_api_key
      - TRAEFIK_HOST=traefik
      - TRAEFIK_PORT=8080
      - EXTRA_DOMAINS=example.com,anotherdomain.com
    restart: always
```

Then run:

```sh
docker-compose up -d
```

## How It Works

1. The script fetches subdomains from the Traefik API.
2. It retrieves the public IP address.
3. It updates the A records on Cloudflare with the new public IP if there are any changes.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.
