<#
.SYNOPSIS
Installs the pinned Windows contributor toolchain.

.DESCRIPTION
Reads windows/toolchain.json and installs any missing contributor tools. The
current toolchain is Lua 5.4.6 from WinGet and Pester 5.7.1 from PowerShell
Gallery at CurrentUser scope. An already-resolvable WinGet tool command is left
alone without a version comparison; PowerShell modules must match the declared
version. This toolchain validates repository content and is not Windows host
desired state.

.EXAMPLE
PS> Get-Content .\windows\toolchain.json

Read-only. Review the exact tools and versions before installing them.

.EXAMPLE
PS> .\windows\tools\setup-dev.ps1

Changes the host. Installs missing pinned contributor tools from WinGet and
PowerShell Gallery, then refreshes PATH for the current process.

.NOTES
Requires network access to the configured package sources and WinGet when its
tool is missing. Pester is installed with Install-Module at
CurrentUser scope. The script exits 0 when the toolchain is ready and 1 when an
installation or provider fails. It does not Apply Windows desired state.

.LINK
https://github.com/shk95/configs/blob/dev/CONTRIBUTING.md#windows-changes
#>
[CmdletBinding()]
param()

# Install the tooling a Windows contributor needs to check their own work.
#
# The Unix-like domain declares its contributor tooling in
# modules/flake/dev-shell.nix and `nix develop` installs it. Windows had no
# equivalent, which is why a Windows clone could not run its own checks:
# nothing in this repository installed Lua or Pester, and only the CI workflow
# knew which versions were expected.
#
# Deliberately not part of windows/desired/manifest.json, and deliberately not
# under windows/desired/ at all. That manifest is host desired state, setup.ps1
# reports every missing entry in it as drift, and Get-WinEnvDesiredStateHash
# hashes the whole tree — a contributor tool declared there would make every
# user's machine report drift for a compiler it has no reason to own, and would
# change the desired-state hash for a change that deploys nothing.
#
# Zellij is not listed here. It is a real application this configuration
# installs through the manifest, so `bootstrap.ps1` already provides it.

$ErrorActionPreference = 'Stop'
$windowsRoot = Split-Path -Parent $PSScriptRoot
$toolchainPath = Join-Path $windowsRoot 'toolchain.json'
$toolchain = (Get-Content -LiteralPath $toolchainPath -Raw | ConvertFrom-Json).toolchain

foreach ($tool in $toolchain) {
    if ($tool.Provider -eq 'WinGet') {
        if (Get-Command $tool.Command -ErrorAction SilentlyContinue) {
            Write-Host "· $($tool.Name) is already available"
        }
        else {
            if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
                throw 'WinGet is required. Install or repair Microsoft App Installer first.'
            }

            Write-Host "→ installing $($tool.Name) $($tool.Version) — $($tool.Validates)"
            & winget.exe install --id $tool.Id --version $tool.Version --exact --source winget `
                --accept-source-agreements --accept-package-agreements --disable-interactivity
            if ($LASTEXITCODE -ne 0) {
                throw "$($tool.Name) installation failed with exit code $LASTEXITCODE."
            }
        }
    }
    elseif ($tool.Provider -eq 'PSGallery') {
        $present = Get-Module $tool.Id -ListAvailable |
            Where-Object Version -eq ([version]$tool.Version)

        if ($present) {
            Write-Host "· $($tool.Name) $($tool.Version) is already available"
        }
        else {
            Write-Host "→ installing $($tool.Name) $($tool.Version) — $($tool.Validates)"
            Install-Module $tool.Id -RequiredVersion $tool.Version -Scope CurrentUser -Force
        }
    }
    else {
        throw "Unknown provider '$($tool.Provider)' for $($tool.Id)."
    }
}

# A freshly installed WinGet package is not on this process's PATH yet.
$machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$env:Path = "$machinePath;$userPath;$env:Path"

Write-Host 'Contributor toolchain is ready.'
exit 0
