param(
    [Parameter(Mandatory = $true, Position = 0)][string]$Path
)

$tokens = $null
$parseErrors = $null
$resolvedPath = (Resolve-Path -LiteralPath $Path).Path

[System.Management.Automation.Language.Parser]::ParseFile(
    $resolvedPath,
    [ref]$tokens,
    [ref]$parseErrors
) > $null

if ($parseErrors.Count -gt 0) {
    foreach ($parseError in $parseErrors) {
        Write-Error ("{0}:{1}:{2}: {3}" -f $resolvedPath, $parseError.Extent.StartLineNumber, $parseError.Extent.StartColumnNumber, $parseError.Message)
    }
    exit 1
}

Write-Output "PowerShell syntax OK: $resolvedPath"
