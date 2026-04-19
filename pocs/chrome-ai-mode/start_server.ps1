# start_server.ps1 — Chrome AI Mode backend launcher
# Run from the pocs/chrome-ai-mode directory

$Root = Resolve-Path "..\.."
$VenvActivate = Join-Path $Root ".venv\Scripts\Activate.ps1"
$ServerDir = Join-Path $PSScriptRoot "server"
$RequirementsFile = Join-Path $PSScriptRoot "requirements.txt"

Write-Host "🚀 Starting Chrome AI Mode backend..." -ForegroundColor Cyan

# Activate root venv
if (Test-Path $VenvActivate) {
    Write-Host "✅ Activating venv from: $VenvActivate" -ForegroundColor Green
    & $VenvActivate
} else {
    Write-Host "⚠️  No .venv found at root. Creating one..." -ForegroundColor Yellow
    python -m venv "$Root\.venv"
    & $VenvActivate
}

# Load .env from repo root
$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
    Write-Host "✅ Loaded environment from $EnvFile" -ForegroundColor Green
} else {
    Write-Host "⚠️  No .env file found at repo root. OPENAI_API_KEY must be set manually." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan
pip install -r $RequirementsFile --quiet

# Launch server
Write-Host ""
Write-Host "🌐 Server starting at http://localhost:8000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"

Set-Location $ServerDir
Write-Host ""
Write-Host "Web server starting at http://localhost:8000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

& $PythonExe -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
