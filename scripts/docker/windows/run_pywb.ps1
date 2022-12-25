docker container inspect pywb > $null 2>&1
$container_exists = $?
if ($container_exists -eq $false) 
{
    docker run -it --name pywb -v $HOME/Desktop/pywb/data:/app/data pywb
}
else
{
    docker start -ia pywb
}