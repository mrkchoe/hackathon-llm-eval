# Run from the repo root:  .\scripts\push-to-github.ps1
# Target: https://github.com/mrkchoe/hackeval

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$GitHubUser = "mrkchoe"
$RepoName = "hackeval"
$RepoFull = "$GitHubUser/$RepoName"

$gh = "$env:ProgramFiles\GitHub CLI\gh.exe"
if (-not (Test-Path $gh)) { $gh = "$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe" }
if (-not (Test-Path $gh)) { $gh = "gh" }

Write-Host "==> Local repo: $(Get-Location)" -ForegroundColor Cyan
Write-Host "==> GitHub target: https://github.com/$RepoFull" -ForegroundColor Cyan

# 1) Git identity (local to this repo only)
$name = git config user.name 2>$null
$email = git config user.email 2>$null
if (-not $name) {
  $name = Read-Host "Git user.name [Mark Choe]"
  if (-not $name) { $name = "Mark Choe" }
  git config user.name $name
}
if (-not $email) {
  $defaultEmail = "$GitHubUser@users.noreply.github.com"
  $email = Read-Host "Git user.email [$defaultEmail]"
  if (-not $email) { $email = $defaultEmail }
  git config user.email $email
}
Write-Host "Using git identity: $name <$email>"

# 2) Commit if needed
git branch -M main 2>$null
$hasCommit = $true
try { git rev-parse HEAD | Out-Null } catch { $hasCommit = $false }
if (-not $hasCommit) {
  git add .env.example .gitignore COMPARISON_TABLE.md LICENSE README.md RESEARCH_REPORT.md fixtures outputs requirements.txt scripts sources tasks
  git commit -m "Initial HackEval research packet for hackathon LLM comparisons."
  Write-Host "Created initial commit on main."
} else {
  Write-Host "Commit already exists: $(git log -1 --oneline)"
}

# 3) GitHub auth (log in as mrkchoe)
& $gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Log in to GitHub as $GitHubUser in the browser..." -ForegroundColor Yellow
  & $gh auth login --hostname github.com --git-protocol https --web
}

$authed = (& $gh api user --jq .login 2>$null)
if ($authed -and ($authed -ne $GitHubUser)) {
  Write-Host "Warning: logged in as '$authed', expected '$GitHubUser'." -ForegroundColor Yellow
}

# 4) Attach to existing empty repo (or create if missing), then push
$remote = git remote get-url origin 2>$null
if (-not $remote) {
  git remote add origin "https://github.com/$RepoFull.git"
  $remote = "https://github.com/$RepoFull.git"
}
Write-Host "Remote origin: $remote"

$exists = $true
try { & $gh repo view $RepoFull 2>$null | Out-Null } catch { $exists = $false }
if ($LASTEXITCODE -ne 0) { $exists = $false }

if (-not $exists) {
  Write-Host "Repo not found; creating https://github.com/$RepoFull ..." -ForegroundColor Cyan
  & $gh repo create $RepoFull --public --description "Hackathon-derived LLM comparison research packet (tasks, sources, minimal runner)."
}

Write-Host "Pushing main -> origin ..." -ForegroundColor Cyan
git push -u origin main

Write-Host "`nDone: https://github.com/$RepoFull" -ForegroundColor Green
& $gh repo view $RepoFull --web
