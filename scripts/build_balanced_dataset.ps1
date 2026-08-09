$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$corePath = Join-Path $root 'data\oran_darija_verified.tsv'
$additionPath = Join-Path $root 'data\madoran_expansion_a2_388_final.tsv'
$core = Import-Csv $corePath -Delimiter "`t"
$addition = Import-Csv $additionPath -Delimiter "`t"

if ($core.Count -eq 888) {
  Write-Output 'Balanced dataset already built.'
  exit 0
}
if ($core.Count -ne 500) {
  throw "Expected the verified core to contain 500 rows, found $($core.Count)."
}
if ($addition.Count -ne 388) {
  throw "Expected 388 A2 additions, found $($addition.Count)."
}

$combined = @($core) + @($addition)
if (($combined.id | Sort-Object -Unique).Count -ne 888) {
  throw 'ID uniqueness check failed.'
}
if (($combined.arabic | Sort-Object -Unique).Count -ne 888) {
  throw 'Arabic headword uniqueness check failed.'
}
if (($combined | Where-Object cefr -eq 'A1').Count -ne 444 -or
    ($combined | Where-Object cefr -eq 'A2').Count -ne 444) {
  throw 'A1/A2 balance check failed.'
}

$combined | Export-Csv $corePath -Delimiter "`t" -NoTypeInformation -Encoding utf8
Write-Output "Wrote the balanced 888-row dataset to $corePath"
