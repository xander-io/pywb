#!/bin/bash

# NOTE: Please verify python3, pip3, docker, and gzip are installed on the system prior to building."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${DIR}/../
rm -r ./dist/* &> /dev/null

echo "Building python module..."
pip3 install wheel --quiet
python3 setup.py clean --all
python3 setup.py bdist_wheel

echo "Building Docker image..."
PYWB_WHEEL="$( ls -AU ./dist | head -1 )"
docker build -t pywb --build-arg wheel_name=$PYWB_WHEEL .
echo "Saving Docker image..."
docker save pywb:latest -o ./dist/pywb_docker.tar
echo "Compressing as a tgz..."
gzip -9c ./dist/pywb_docker.tar > ./dist/pywb_docker.tgz
rm ./dist/pywb_docker.tar

echo "Setting up release folder structure and moving files..."
mkdir ./dist/docker-windows
mkdir ./dist/docker-mac-linux
mkdir  ./dist/python
cp ./dist/pywb_docker.tgz ./dist/docker-windows/
mv ./dist/pywb_docker.tgz ./dist/docker-mac-linux/
mv ./dist/$PYWB_WHEEL_NAME ./dist/python/
cp ./scripts/docker/windows/* ./dist/docker-windows/
cp ./scripts/docker/mac-linux/* ./dist/docker-mac-linux/
cp ./README.md ./dist/
echo "DONE!"
