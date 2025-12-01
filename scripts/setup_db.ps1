$maxRetries = 30
$retryCount = 0
$containerName = "cortex-neo4j"

Write-Host "Waiting for Neo4j to be ready..."

while ($retryCount -lt $maxRetries) {
    $status = docker inspect --format='{{.State.Health.Status}}' $containerName 2>$null
    
    if ($status -eq "healthy") {
        Write-Host "Neo4j is ready!"
        break
    }
    
    Write-Host "Waiting for Neo4j... ($retryCount/$maxRetries)"
    Start-Sleep -Seconds 2
    $retryCount++
}

if ($retryCount -eq $maxRetries) {
    Write-Error "Timeout waiting for Neo4j to start."
    exit 1
}

Write-Host "Running initialization script..."
docker exec $containerName cypher-shell -u neo4j -p password -f /scripts/init-db.cypher

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database initialized successfully."
} else {
    Write-Error "Failed to initialize database."
}
