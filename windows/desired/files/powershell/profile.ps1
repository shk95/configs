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
            EditMode                      = 'Vi'
            HistoryNoDuplicates            = $true
            HistorySearchCursorMovesToEnd = $true
        }

        if ($setOption.Parameters.ContainsKey('PredictionSource')) {
            $options.PredictionSource = 'History'
        }

        if ($setOption.Parameters.ContainsKey('ViModeIndicator')) {
            $options.ViModeIndicator = 'Cursor'
        }

        Set-PSReadLineOption @options

        # PSReadLine versions before 2.2.1 do not bind reverse history search
        # in Vi mode; bind it explicitly so it stays reachable on every
        # version.
        $setKeyHandler = Get-Command Set-PSReadLineKeyHandler -ErrorAction SilentlyContinue
        if ($setKeyHandler) {
            Set-PSReadLineKeyHandler -Chord Ctrl+r -Function ReverseSearchHistory
        }
    }
}
