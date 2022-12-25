#!/bin/bash

sudo=''
if (( $EUID != 0 )); then
    sudo="sudo"
fi

if ! [ -x "$(command -v docker)" ]; then
    echo "Downloading Docker Installer..."
    sudo apt-get update
    sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

echo "Importing Docker image..."
docker load -i pywb_docker.tgz
echo "Copying executable file to PATH..."
$sudo cp run_pywb.sh /usr/local/bin/pywb
echo "DONE!"