$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8

try {
    $requestText = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($requestText)) {
        throw 'The Appx query request was empty.'
    }

    $request = $requestText | ConvertFrom-Json -ErrorAction Stop
    $requestProperties = @($request.PSObject.Properties.Name | Sort-Object)
    if (($requestProperties -join ',') -ne 'Name,SchemaVersion') {
        throw 'The Appx query request has an unexpected shape.'
    }
    if (($request.SchemaVersion -isnot [int]) -and ($request.SchemaVersion -isnot [long])) {
        throw 'The Appx query request SchemaVersion must be an integer.'
    }
    if ($request.SchemaVersion -ne 1) {
        throw "Unsupported Appx query request schema: $($request.SchemaVersion)"
    }
    if ($request.Name -isnot [string] -or [string]::IsNullOrWhiteSpace($request.Name)) {
        throw 'The Appx query request Name must be a non-empty string.'
    }

    $packages = @(Get-AppxPackage -Name $request.Name -ErrorAction Stop)
    $first = $packages | Select-Object -First 1
    $response = [ordered]@{
        SchemaVersion = 1
        Name          = if ($first) { [string]$first.Name } else { [string]$request.Name }
        Present       = [bool]$first
        Version       = if ($first) { [string]$first.Version } else { $null }
    }
    [Console]::Out.Write(($response | ConvertTo-Json -Compress))
    exit 0
}
catch {
    [Console]::Error.Write($_.Exception.Message)
    exit 1
}
