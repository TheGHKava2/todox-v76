
# add_sqlmodel.ps1
# Acrescenta sqlmodel==0.0.22 ao backend\requirements.txt, se ausente.

param(
  [string]$ProjectRoot = "."
)
$req = Join-Path $ProjectRoot "backend\requirements.txt"
if (!(Test-Path $req)) {
  Write-Error "Arquivo não encontrado: $req"
}
$txt = Get-Content -Raw -Path $req -Encoding UTF8
if ($txt -notmatch "(?im)^\s*sqlmodel\s*==\s*0\.0\.22\s*$") {
  Add-Content -Path $req -Value "`nsqlmodel==0.0.22`n" -Encoding UTF8
  Write-Host "sqlmodel==0.0.22 adicionado a $req"
} else {
  Write-Host "sqlmodel já presente em $req"
}
