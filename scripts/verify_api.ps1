$baseUrl = "http://localhost:3000/api/v1"

# 1. Create a Node
Write-Host "Creating a Node..."
$nodeData = @{
    kind     = "CONTAINER"
    metadata = @{
        id     = "550e8400-e29b-41d4-a716-446655440000" # Valid UUID
        slug   = "api-test-node"
        name   = "API Test Node"
        labels = @{ env = "test" }
    }
    spec     = @{ technology = "Node.js" }
    status   = @{ uptime = "100%" }
}
$json = $nodeData | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/nodes" -Method Put -Body $json -ContentType "application/json"
    if ($response.id -eq "550e8400-e29b-41d4-a716-446655440000") {
        Write-Host "Node Created Successfully." -ForegroundColor Green
    }
    else {
        Write-Error "Node Creation Failed: Unexpected response."
    }
}
catch {
    Write-Error "Node Creation Failed: $_"
}

# 2. Get Graph
Write-Host "`nGetting Graph..."
try {
    $graph = Invoke-RestMethod -Uri "$baseUrl/graph" -Method Get
    $nodeExists = $graph.nodes | Where-Object { $_.properties.id -eq "550e8400-e29b-41d4-a716-446655440000" }
    
    if ($nodeExists) {
        Write-Host "Graph Retrieval Verified (Node found)." -ForegroundColor Green
    }
    else {
        Write-Error "Graph Retrieval Failed: Node not found."
    }
}
catch {
    Write-Error "Graph Retrieval Failed: $_"
}

# Cleanup (optional, but good for repeatability)
# We can't easily delete via API yet, so we'll leave it or use cypher-shell if needed.
