# Add SSC App Distribution testers — project super-chat-b0992
# Prerequisite: firebase login
#
# Usage:
#   cd C:\Users\smash\SSC-main
#   .\scripts\add_firebase_testers.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$ListFile = Join-Path $PSScriptRoot "firebase_testers.txt"
$ExampleFile = Join-Path $PSScriptRoot "firebase_testers.txt.example"

if (-not (Test-Path $ListFile)) {
    Write-Error "Missing $ListFile — copy firebase_testers.txt.example and add your tester emails (file is gitignored)."
}

if (-not (Get-Command firebase -ErrorAction SilentlyContinue)) {
    Write-Error "firebase CLI not found. Run: npm install -g firebase-tools"
}

$emails = Get-Content $ListFile | Where-Object { $_ -match "\S" } | ForEach-Object { $_.Trim() }
if (-not $emails.Count) {
    Write-Error "No emails in $ListFile"
}

Write-Host "Adding $($emails.Count) testers to App Distribution (project super-chat-b0992)..."
Write-Host ($emails -join ", ")

Push-Location $RepoRoot
try {
    firebase appdistribution:testers:add --file $ListFile
} finally {
    Pop-Location
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK - testers added. They will receive invites when you upload an APK release."
} else {
    throw "firebase appdistribution:testers:add failed (exit $LASTEXITCODE). Run firebase login first."
}