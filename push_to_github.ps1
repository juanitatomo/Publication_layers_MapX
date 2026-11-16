# Run after: (1) gh auth login  (2) empty repo created OR this script creates it
$ErrorActionPreference = "Stop"
$gh = "$env:USERPROFILE\tools\gh\bin\gh.exe"
$git = "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
if (-not (Test-Path $gh)) { $gh = "gh" }
if (-not (Test-Path $git)) { $git = "git" }

Set-Location $PSScriptRoot

& $gh auth status
$exists = $true
try { & $gh repo view juanitatomo/Publication_layers_MapX | Out-Null } catch { $exists = $false }

if (-not $exists) {
  & $gh repo create Publication_layers_MapX --public --description "Sustainable Caucasus GeoNode to MapX — publication catalogue, metadata, styles, and automated methodology" --source . --remote origin --push
} else {
  $remotes = & $git remote
  if ($remotes -notcontains "origin") {
    & $git remote add origin "https://github.com/juanitatomo/Publication_layers_MapX.git"
  }
  & $git push -u origin main
}

Write-Host "Done: https://github.com/juanitatomo/Publication_layers_MapX"
