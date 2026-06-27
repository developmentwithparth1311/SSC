# Run AFTER: gh auth login
# Applies branch protection on main for raullavita/SSC

$ErrorActionPreference = "Stop"

gh auth status | Out-Null

$body = @{
    required_status_checks = @{
        strict = $true
        contexts = @(
            "Frontend tests"
            "Backend tests"
        )
    }
    enforce_admins = $false
    required_pull_request_reviews = $null
    restrictions = $null
    allow_force_pushes = $false
    allow_deletions = $false
    required_linear_history = $false
    block_creations = $false
    required_conversation_resolution = $false
    lock_branch = $false
    allow_fork_syncing = $true
} | ConvertTo-Json -Depth 5

$body | gh api repos/raullavita/SSC/branches/main/protection -X PUT --input -

Write-Host "Branch protection applied on main."
Write-Host "Required checks: Frontend tests, Backend tests"
Write-Host "Force push + deletion: blocked"
Write-Host "You can still push directly to main when CI is green (no PR required)."