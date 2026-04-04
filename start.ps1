# AI Scout & Mentor - Launch Script
# -------------------------------
# This script loads environment variables and starts n8n + ngrok.

# --- Helper: Load .env file ---
if (Test-Path ".env") {
    foreach ($line in Get-Content ".env") {
        if ($line -match "^([^#\s][^=]*)=(.+)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# --- Check for Required Variable ---
if (-not $env:NGROK_DOMAIN) {
    Write-Host "Error: NGROK_DOMAIN is not set." -ForegroundColor Red
    Write-Host "Please add it to your .env file or set it in your shell: `$env:NGROK_DOMAIN='your-domain.ngrok-free.dev'" -ForegroundColor Yellow
    exit 1
}

$domain = $env:NGROK_DOMAIN

Write-Host "Starting Ngrok Tunnel for $domain..." -ForegroundColor Cyan
Start-Process "ngrok" -ArgumentList "http --domain=$domain 5678"

Write-Host "Booting up n8n engine..." -ForegroundColor Green
$env:WEBHOOK_URL = "https://$domain"
npx n8n
