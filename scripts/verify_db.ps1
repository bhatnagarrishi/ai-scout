$containerName = "cortex-neo4j"
$auth = "neo4j:password"
$encodedAuth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($auth))
$headers = @{ Authorization = "Basic $encodedAuth" }

# 1. Verify HTTP Connectivity
Write-Host "Verifying HTTP connectivity..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:7474/db/neo4j/tx/commit" -Method Post -Headers $headers -Body '{"statements": [{"statement": "RETURN 1"}]}' -ContentType "application/json"
    if ($response.results[0].data[0].row[0] -eq 1) {
        Write-Host "HTTP Connectivity Verified." -ForegroundColor Green
    }
    else {
        Write-Error "HTTP Connectivity Failed: Unexpected response."
    }
}
catch {
    Write-Error "HTTP Connectivity Failed: $_"
}

# 2. Verify Constraints (Duplicate Node Test)
Write-Host "`nVerifying Constraints..."
$createNode = "CREATE (n:BaseNode {id: 'test-id', slug: 'test-slug'})"
$createDuplicate = "CREATE (n:BaseNode {id: 'test-id', slug: 'other-slug'})"

# Clean up first
docker exec $containerName cypher-shell -u neo4j -p password "MATCH (n:BaseNode {id: 'test-id'}) DETACH DELETE n" | Out-Null

# Create first node
docker exec $containerName cypher-shell -u neo4j -p password $createNode | Out-Null

# Try to create duplicate
try {
    docker exec $containerName cypher-shell -u neo4j -p password $createDuplicate 2>&1 | Out-Null
    Write-Error "Constraint Verification Failed: Duplicate node created."
}
catch {
    # We expect an error here, but cypher-shell returns non-zero exit code which PowerShell catches? 
    # Actually, docker exec will return non-zero.
}

# Let's check the exit code of the duplicate creation explicitly
$process = Start-Process -FilePath "docker" -ArgumentList "exec $containerName cypher-shell -u neo4j -p password `"$createDuplicate`"" -NoNewWindow -PassThru -Wait
if ($process.ExitCode -ne 0) {
    Write-Host "Constraint Verification Verified (Duplicate rejected)." -ForegroundColor Green
}
else {
    Write-Error "Constraint Verification Failed: Duplicate node created (Exit Code 0)."
}

# Cleanup
docker exec $containerName cypher-shell -u neo4j -p password "MATCH (n:BaseNode {id: 'test-id'}) DETACH DELETE n" | Out-Null
