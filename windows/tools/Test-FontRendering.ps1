[CmdletBinding()]
param()

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
