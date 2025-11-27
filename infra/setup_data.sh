#!/bin/bash
set -e

# install docker
apt-get update
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Allow docker without sudo for 'ubuntu' user
usermod -aG docker ubuntu || true

# optionally pull image, run container
# Replace DOCKER_IMAGE with the full image name via Terraform replace/substitution if desired,
# or you can do 'docker pull gcr.io/<PROJECT>/<IMAGE>' here manually.
DOCKER_IMAGE="${docker_image:-__TO_REPLACE_WITH_IMAGE__}"

if [ "${DOCKER_IMAGE}" != "__TO_REPLACE_WITH_IMAGE__" ]; then
  docker pull "${DOCKER_IMAGE}"
  # create a data dir
  mkdir -p /opt/trading/data
  # example run: mount a GCS fuse or use service account creds - we use the VM SA so app can access GCS via google-cloud libs
  docker run -d --name trading-bot \
    --restart unless-stopped \
    -v /opt/trading/data:/data \
    "${DOCKER_IMAGE}" \
    python main.py --csv /data/trades.csv --timeframe 1min --gcs-bucket "${bucket_name:-}"
fi
