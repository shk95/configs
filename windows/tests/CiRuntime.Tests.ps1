BeforeAll {
    $windowsRoot = Split-Path -Parent $PSScriptRoot
    $reader = Join-Path $windowsRoot 'tool/read-ci-runtime.ps1'
    $declaration = Join-Path $windowsRoot 'tool/ci-runtime.json'
    $pwshPath = (Get-Process -Id $PID).Path
    function Invoke-CiRuntimeReader {
        param([string] $Path = $declaration)
        $info = [System.Diagnostics.ProcessStartInfo]::new()
        $info.FileName = $pwshPath
        $info.UseShellExecute = $false
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        foreach ($argument in @('-NoLogo', '-NoProfile', '-File', $reader, '-Path', $Path)) {
            $info.ArgumentList.Add($argument)
        }
        $process = [System.Diagnostics.Process]::Start($info)
        try {
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
            return [pscustomobject]@{ Exit = $process.ExitCode; Out = $stdout; Error = $stderr }
        }
        finally { $process.Dispose() }
    }
}

Describe 'Windows CI runtime declaration' {
    # INV windows/ci-runtime-declared
    It 'reads the exact management artifact and separate inbox bootstrap without changing the declaration' {
        $before = (Get-FileHash -LiteralPath $declaration).Hash
        $result = Invoke-CiRuntimeReader
        $result.Exit | Should -Be 0
        $result.Error | Should -BeNullOrEmpty
        $value = $result.Out | ConvertFrom-Json
        $value.management.version | Should -BeExactly '7.6.6'
        $value.management.asset.uri | Should -BeExactly 'https://github.com/PowerShell/PowerShell/releases/download/v7.6.6/PowerShell-7.6.6-win-x64.zip'
        $value.management.asset.sha256 | Should -BeExactly '02fe458be20493fbdf43f61ea20610b811ee6c738ab1676c61b9cfcd1a33c860'
        $value.bootstrap.version | Should -BeExactly '5.1'
        $value.bootstrap.source | Should -BeExactly 'inbox'
        (Get-FileHash -LiteralPath $declaration).Hash | Should -BeExactly $before
        # The returned version is desired verification data, not a claim about
        # the version of the process running this test.
        $value.PSObject.Properties.Name | Should -Not -Contain 'observedVersion'
    }

    It 'refuses <Name> instead of returning an ambiguous automation input' -ForEach @(
        @{ Name = 'unknown format'; Change = { param($v) $v.formatVersion = 2 }; Reason = 'Unsupported CI runtime formatVersion' },
        @{ Name = 'missing management version'; Change = { param($v) $v.management.PSObject.Properties.Remove('version') }; Reason = "missing 'version'" },
        @{ Name = 'unversioned management'; Change = { param($v) $v.management.version = 'latest' }; Reason = 'exact stable' },
        @{ Name = 'different architecture'; Change = { param($v) $v.management.architecture = 'arm64' }; Reason = 'architecture' },
        @{ Name = 'untrusted artifact'; Change = { param($v) $v.management.asset.uri = 'https://example.invalid/runtime.zip' }; Reason = 'official versioned' },
        @{ Name = 'mismatched artifact version'; Change = { param($v) $v.management.version = '7.6.5' }; Reason = 'official versioned' },
        @{ Name = 'missing hash'; Change = { param($v) $v.management.asset.sha256 = '' }; Reason = 'SHA256' },
        @{ Name = 'wrong bootstrap'; Change = { param($v) $v.bootstrap.version = '7.6.6' }; Reason = 'separate inbox' },
        @{ Name = 'extra entry point'; Change = { param($v) $v.bootstrap.entryPoints += 'extra.ps1' }; Reason = 'entryPoints' },
        @{ Name = 'unknown field'; Change = { param($v) $v | Add-Member -NotePropertyName minimumHostVersion -NotePropertyValue '7.6.6' }; Reason = 'unknown field' }
    ) {
        $value = Get-Content -LiteralPath $declaration -Raw | ConvertFrom-Json
        & $Change $value
        $path = Join-Path $TestDrive 'invalid.json'
        $value | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $path -Encoding utf8
        $result = Invoke-CiRuntimeReader -Path $path
        $result.Exit | Should -Be 1
        $result.Out | Should -BeNullOrEmpty
        $result.Error | Should -Match $Reason
    }
}
