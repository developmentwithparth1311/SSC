# Deploy SSC backend to Google Cloud Run (project super-chat-b0992)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$Backend = Join-Path $RepoRoot "backend"
$EnvFile = Join-Path $Backend "cloud_run.env"
$Project = "super-chat-b0992"
$Region = "europe-west1"
$Service = "ssc-api"
$Python = Join-Path $Backend "venv\Scripts\python.exe"

function Get-Gcloud {
    $cmd = Get-Command gcloud -ErrorAction SilentlyContinue
    $paths = @()
    if ($cmd) { $paths += $cmd.Source }
    $paths += "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    foreach ($p in $paths) {
        if ($p -and (Test-Path $p)) { return $p }
    }
    throw "gcloud not found"
}

$gcloud = Get-Gcloud
Write-Host "gcloud: $gcloud"

$auth = & $gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $auth) { throw "Run: gcloud auth login" }

if (-not (Test-Path $EnvFile)) {
    throw "Missing $EnvFile"
}

& $Python (Join-Path $Backend "scripts\prepare_cloud_run_deploy.py")
if ($LASTEXITCODE -ne 0) { throw "prepare_cloud_run_deploy failed" }

$envYaml = Join-Path $Backend ".cloudrun\deploy_env.yaml"

& $gcloud config set project $Project | Out-Null
& $gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --quiet

Write-Host "Deploying $Service ($Region) - first deploy may take 5-10 minutes..."
Push-Location $Backend
try {
    & $gcloud run deploy $Service `
        --source . `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 512Mi `
        --timeout 300 `
        --min-instances 0 `
        --max-instances 3 `
        --vpc-connector ssc-vpc-connector `
        --vpc-egress all-traffic `
        --env-vars-file $envYaml
} finally {
    Pop-Location
}
if ($LASTEXITCODE -ne 0) { throw "deploy failed" }

$url = (& $gcloud run services describe $Service --region $Region --format="value(status.url)").Trim()

# Patch OAuth redirect to Cloud Run URL for next deploy (optional)
Write-Host ""
Write-Host "DEPLOYED: $url"
Write-Host "Health:   $url/api/health"
Write-Host ""
Write-Host "Next: REACT_APP_BACKEND_URL=$url in frontend/.env.production.local, rebuild APK"