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

    # A bare `zellij` starts config.kdl's `session_name` with
    # `attach_to_session`, which zellij 0.45.1 resolves against live sessions
    # only: an exited `win-env` is not resurrected but replaced by a new
    # session of the same name. `attach --create` resurrects before it
    # creates, as the Windows Terminal profile already does. Defined at this
    # scope rather than inside the block above so the dot-sourced profile
    # leaves it in the session.
    function zellij {
        if ($args.Count -eq 0) {
            & zellij.exe attach --create win-env
        } else {
            & zellij.exe @args
        }
    }
}
