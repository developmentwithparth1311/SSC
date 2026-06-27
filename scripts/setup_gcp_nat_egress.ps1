# SSC TASK O.6 — GCP static egress for Cloud Run → MongoDB Atlas IP allowlist
# Idempotent: safe to re-run. Requires gcloud auth + project super-chat-b0992.
$ErrorActionPreference = "Stop"
$Project = "super-chat-b0992"
$Region = "europe-west1"
$NatIpName = "ssc-nat-ip"
$RouterName = "ssc-nat-router"
$NatName = "ssc-cloud-nat"
$ConnectorName = "ssc-vpc-connector"
$Service = "ssc-api"

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
& $gcloud config set project $Project | Out-Null
& $gcloud services enable compute.googleapis.com vpcaccess.googleapis.com run.googleapis.com --quiet

$ipExists = & $gcloud compute addresses describe $NatIpName --region=$Region --format="value(address)" 2>$null
if (-not $ipExists) {
    Write-Host "Creating static IP $NatIpName..."
    & $gcloud compute addresses create $NatIpName --region=$Region --quiet
}
$natIp = (& $gcloud compute addresses describe $NatIpName --region=$Region --format="value(address)").Trim()
Write-Host "NAT egress IP: $natIp"

$routerExists = & $gcloud compute routers describe $RouterName --region=$Region --format="value(name)" 2>$null
if (-not $routerExists) {
    Write-Host "Creating router $RouterName..."
    & $gcloud compute routers create $RouterName --network=default --region=$Region --quiet
}

$natExists = & $gcloud compute routers nats describe $NatName --router=$RouterName --region=$Region --format="value(name)" 2>$null
if (-not $natExists) {
    Write-Host "Creating Cloud NAT $NatName..."
    & $gcloud compute routers nats create $NatName `
        --router=$RouterName `
        --region=$Region `
        --nat-external-ip-pool=$NatIpName `
        --nat-all-subnet-ip-ranges `
        --quiet
}

$connExists = & $gcloud compute networks vpc-access connectors describe $ConnectorName --region=$Region --format="value(name)" 2>$null
if (-not $connExists) {
    Write-Host "Creating VPC connector $ConnectorName (several minutes)..."
    & $gcloud compute networks vpc-access connectors create $ConnectorName `
        --region=$Region `
        --network=default `
        --range=10.8.0.0/28 `
        --min-instances=2 `
        --max-instances=3 `
        --quiet
}

Write-Host "Updating Cloud Run service $Service (all-traffic via VPC)..."
& $gcloud run services update $Service `
    --region=$Region `
    --vpc-connector=$ConnectorName `
    --vpc-egress=all-traffic `
    --quiet

Write-Host ""
Write-Host "DONE — add this IP in Atlas Network Access:"
Write-Host "  $natIp/32  (comment: SSC Cloud Run NAT egress)"
Write-Host ""
Write-Host "Verify: curl https://api.supersecurechat.com/api/health"