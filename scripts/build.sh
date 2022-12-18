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
echo "DONE!"
