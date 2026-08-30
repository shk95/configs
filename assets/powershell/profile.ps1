# Unix-like managed PowerShell profile.
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
            # Declares modal editing here rather than leaving PSReadLine on
            # its emacs-style default, for the same reason zsh and readline
            # gain one in modules/shell.nix on the Unix-like side: an
            # undeclared default is silently correct until something changes
            # around it. Existed since PSReadLine 2.0, so it needs no
            # ContainsKey guard of its own.
            EditMode                       = 'Vi'
        }

        if ($setOption.Parameters.ContainsKey('PredictionSource')) {
            $options.PredictionSource = 'History'
        }

        # ViModeIndicator does not exist in older PSReadLine, hence its own
        # guard. 'Cursor' changes only the cursor shape between insert and
        # command mode, so it stays silent (no prompt or script text) and
        # keeps this profile safe to load from SSH, Git, and scp.
        if ($setOption.Parameters.ContainsKey('ViModeIndicator')) {
            $options.ViModeIndicator = 'Cursor'
        }

        Set-PSReadLineOption @options
    }
}
