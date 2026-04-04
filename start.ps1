Write-Host "Starting Ngrok Tunnel..." -ForegroundColor Cyan
Start-Process "ngrok" -ArgumentList "http --domain=unsqueezable-prideful-laurice.ngrok-free.dev 5678"

Write-Host "Booting up n8n engine..." -ForegroundColor Green
$env:WEBHOOK_URL="https://unsqueezable-prideful-laurice.ngrok-free.dev"
npx n8n
