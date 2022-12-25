# NOTE: Please verify python3, pip3, docker, and gzip are installed on the system prior to building."

try 
{    
    Write-Output "Building python module..."
    Set-Location -Path $PSScriptRoot/../
    pip3 install wheel setuptools --quiet
    python3 setup.py clean --all
    Remove-Item -r ./dist/*
    python3 setup.py bdist_wheel

    $PYWB_WHEEL = Get-ChildItem -Path ./dist -Force -Recurse -File | Select-Object -First 1
    $PYWB_WHEEL_NAME = $PYWB_WHEEL.Name
    
    Write-Output "Building Docker image..."
    docker build -t pywb --build-arg wheel_name=$PYWB_WHEEL_NAME .
    Write-Output "Saving Docker image..."
    docker save pywb:latest -o ./dist/pywb_docker.tar
    Write-Output "Compressing as a tgz..."
    7z.exe a -tgzip ./dist/pywb_docker.tgz ./dist/pywb_docker.tar
    Remove-Item ./dist/pywb_docker.tar
    
    Write-Output "Setting up release folder structure and moving files..."
    mkdir ./dist/docker-windows
    mkdir ./dist/docker-mac-linux
    mkdir  ./dist/python
    Copy-Item ./dist/pywb_docker.tgz ./dist/docker-windows/
    Move-Item ./dist/pywb_docker.tgz ./dist/docker-mac-linux/
    Move-Item ./dist/$PYWB_WHEEL_NAME ./dist/python/
    Copy-Item ./scripts/docker/windows/* ./dist/docker-windows/
    Copy-Item ./scripts/docker/mac-linux/* ./dist/docker-mac-linux/
    Copy-Item ./README.md ./dist/
    Write-Output "DONE!"
} 
catch 
{
    Write-Output "Build ERROR:" $_
}

