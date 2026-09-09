<#
.SYNOPSIS
Prints a visual glyph sample for the configured terminal font.

.DESCRIPTION
Writes ASCII, Hangul, box-drawing, Nerd Font icon, and ligature samples for an
operator to inspect in the current terminal. It does not install fonts, change
terminal settings, or decide pass or fail from the rendered pixels.

.EXAMPLE
PS> .\windows\tools\Test-FontRendering.ps1

Read-only. Compare alignment and glyph availability in Windows Terminal using
the expected D2KodingLigature Nerd Font Mono face.

.NOTES
Run in the terminal profile being evaluated. Exit 0 only means the samples were
printed successfully; visual acceptance remains an operator decision.

.LINK
https://github.com/shk95/configs/blob/dev/README.md#windows
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$hangul = -join (0xAC00, 0xB098, 0xB2E4, 0xB77C, 0xB9C8 | ForEach-Object { [char]$_ })
$horizontal = -join (1..8 | ForEach-Object { [char]0x2500 })
$boxTop = [char]0x250C + $horizontal + [char]0x2510
$boxMiddle = [char]0x251C + $horizontal + [char]0x2524
$boxBottom = [char]0x2514 + $horizontal + [char]0x2518
$icons = -join (0xE0B0, 0x20, 0xF120, 0x20, 0xF17C, 0x20, 0xF489 | ForEach-Object { [char]$_ })

Write-Host 'win-env font rendering check'
Write-Host 'ASCII : |1234567890|'
Write-Host ("Hangul: |{0}|  (should align with ten ASCII cells)" -f $hangul)
Write-Host ("Boxes : {0} {1} {2}" -f $boxTop, $boxMiddle, $boxBottom)
Write-Host ("Icons : {0}" -f $icons)
Write-Host 'Ligatures: => != <= ->'
Write-Host 'Expected Terminal face: D2KodingLigature Nerd Font Mono'
exit 0
