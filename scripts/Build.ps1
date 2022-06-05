try 
{
    $p = &{python3 -V; pip3 -V}
    Write-Output $p "Building..."
    
    Set-Location -Path $PSScriptRoot/../
    pip3 install wheel --quiet
    python3 setup.py bdist_wheel
} 
catch 
{
    Write-Output "Build Error:" $_
}

