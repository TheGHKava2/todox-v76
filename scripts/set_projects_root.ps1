\
# Defina a raiz de projetos ToDoX no Windows (ex.: E:\)
param([string]$Path="E:\")
[Environment]::SetEnvironmentVariable("TODOX_PROJECTS_ROOT", $Path, "User")
Write-Host "TODOX_PROJECTS_ROOT definido como $Path (nível User). Reinicie o terminal para aplicar."
