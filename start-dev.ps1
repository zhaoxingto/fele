param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$backendEnvExample = Join-Path $backendDir ".env.example"
$backendEnv = Join-Path $backendDir ".env"
$backendVenvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
$frontendNodeModules = Join-Path $frontendDir "node_modules"

function Write-Step([string]$message) {
    Write-Host "[fele] $message" -ForegroundColor Cyan
}

function Invoke-OrDescribe([string]$message, [scriptblock]$action) {
    Write-Step $message
    if (-not $DryRun) {
        & $action
    }
}

function Ensure-Command([string]$commandName, [string]$hint) {
    if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
        throw "Missing command '$commandName'. $hint"
    }
}

Ensure-Command "python" "Please install Python 3.11+ and add it to PATH."
Ensure-Command "corepack" "Please install Node.js 20+."

if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found: $backendDir"
}

if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

if (-not (Test-Path $backendEnv) -and (Test-Path $backendEnvExample)) {
    Invoke-OrDescribe "Creating backend .env from .env.example" {
        Copy-Item -LiteralPath $backendEnvExample -Destination $backendEnv
    }
}

if (-not (Test-Path $backendVenvPython)) {
    Invoke-OrDescribe "Creating backend virtual environment" {
        Push-Location $backendDir
        try {
            python -m venv .venv
        }
        finally {
            Pop-Location
        }
    }
}

Invoke-OrDescribe "Ensuring backend pip is available" {
    Push-Location $backendDir
    try {
        & $backendVenvPython -m ensurepip --upgrade
    }
    finally {
        Pop-Location
    }
}

Invoke-OrDescribe "Installing backend dependencies" {
    Push-Location $backendDir
    try {
        & $backendVenvPython -m pip install -e .
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path $frontendNodeModules)) {
    Invoke-OrDescribe "Installing frontend dependencies" {
        Push-Location $frontendDir
        try {
            corepack pnpm install
        }
        finally {
            Pop-Location
        }
    }
}

$backendCommand = "Set-Location '$backendDir'; & '$backendVenvPython' -m uvicorn app.main:app --reload"
$frontendCommand = "Set-Location '$frontendDir'; corepack pnpm dev"

Invoke-OrDescribe "Starting backend window on http://127.0.0.1:8000" {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $backendCommand
    ) | Out-Null
}

Invoke-OrDescribe "Starting frontend window on http://127.0.0.1:9527" {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $frontendCommand
    ) | Out-Null
}

Write-Host ""
Write-Host "Frontend: http://127.0.0.1:9527/login" -ForegroundColor Green
Write-Host "Backend : http://127.0.0.1:8000/docs" -ForegroundColor Green
