#!/bin/bash
set -e

# Update and install dependencies
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release

# Install Docker (official convenience script)
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

# Pull and run the trading bot container
docker pull ${docker_image}

docker rm -f trading-bot 2>/dev/null || true

docker run \
  --restart unless-stopped \
  -d \
  --name trading-bot \
  ${docker_image}
