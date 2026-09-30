# INV repository/windows-ci-runtime-bound
param([string] $Version, [string] $Architecture, [string] $Executable)
$ErrorActionPreference = 'Stop'
try {
    $actualVersion = $PSVersionTable.PSVersion.ToString()
    $actualArchitecture = [Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture.ToString().ToLowerInvariant()
    $actualExecutable = (Get-Process -Id $PID).Path
    $resolvedExecutable = (Get-Command pwsh.exe -CommandType Application -ErrorAction Stop).Source
    if ($actualVersion -cne $Version -or $actualArchitecture -cne $Architecture -or
        -not [string]::Equals($actualExecutable, $Executable, [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals($resolvedExecutable, $Executable, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Runtime mismatch: actual=$actualVersion/$actualArchitecture/$actualExecutable; nested=$resolvedExecutable"
    }
    [pscustomobject]@{
        version = $actualVersion; architecture = $actualArchitecture
        executable = $actualExecutable; nestedExecutable = $resolvedExecutable
    } | ConvertTo-Json -Compress
    exit 0
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
