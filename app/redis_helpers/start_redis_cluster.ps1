# Указываем пути к Redis-серверу и конфигурационным файлам
$redisServerPath = "C:\Redis-7.4.1-Windows-x64\redis-server.exe"
$redisCliPath = "C:\Redis-7.4.1-Windows-x64\redis-cli.exe"
$configFiles = @("redis1.conf", "redis2.conf", "redis3.conf")

# Функция для запуска Redis-ноды
function Start-RedisNode {
    param (
        [string]$configFile
    )
    Write-Host "Starting Redis node with config file: $configFile"
    Start-Process -FilePath $redisServerPath -ArgumentList $configFile -NoNewWindow -PassThru
}

# Функция для создания Redis-кластера
function Create-RedisCluster {
    param (
        [string[]]$nodes
    )
    Write-Host "Creating Redis Cluster with nodes: $nodes"
    $command = "--cluster create $($nodes -join ' ') --cluster-replicas 0"
    & $redisCliPath $command
}

# Запускаем все три ноды
$nodes = @()
foreach ($config in $configFiles) {
    Start-RedisNode -configFile $config
    Start-Sleep -Seconds 2 # Даем время для запуска
    # Извлекаем порт из имени файла (например, "7000" из "redis1.conf")
    $port = ($config -replace 'redis(\d+).conf', '$1')
    $nodes += "127.0.0.1:$port"
}

# Создаем кластер
Start-Sleep -Seconds 5 # Ждем, пока все ноды инициализируются
Create-RedisCluster -nodes $nodes
