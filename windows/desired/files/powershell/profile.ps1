# win-env managed PowerShell profile.
# Keep this file silent: profiles are loaded by SSH, Git, scp, and other protocols.

if (
    $Host.Name -eq 'ConsoleHost' -and
    [Environment]::UserInteractive -and
    -not [Console]::IsInputRedirected -and
    -not [Console]::IsOutputRedirected
) {
    & {
        Import-Module PSReadLine -ErrorAction SilentlyContinue

        $setOption = Get-Command Set-PSReadLineOption -ErrorAction SilentlyContinue
        if (-not $setOption) { return }

        $options = @{
            HistoryNoDuplicates            = $true
            HistorySearchCursorMovesToEnd = $true
        }

        if ($setOption.Parameters.ContainsKey('PredictionSource')) {
            $options.PredictionSource = 'History'
        }

        Set-PSReadLineOption @options
    }
}
