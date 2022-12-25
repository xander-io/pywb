$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) -eq $false)
{
    Write-Output "ERROR: Must run as Administrator to install!"
    exit 1
}

try 
{
    docker -v > $null 2>&1
    $docker_installed = $?
    if ($docker_installed -eq $false) 
    {
        $installer_path = "$HOME/Downloads/docker_installer.exe" 
        Write-Output "Downloading Docker Installer..."
        Invoke-WebRequest https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe -OutFile $installer_path
        Start-Process $installer_path -Wait install
        Remove-Item $installer_path
    }
    Write-Output "Importing Docker image..."
    docker load -i pywb_docker.tgz
    Write-Output "Copying executable file to PATH..."
    Copy-Item run_pywb.ps1 C:\Windows\System32\pywb.ps1
}
catch 
{
    Write-Output "Installation ERROR:" $_
}


