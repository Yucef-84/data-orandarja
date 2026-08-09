$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$corePath = Join-Path $root 'data\oran_darija_verified.tsv'
$additionPath = Join-Path $root 'data\madoran_expansion_a2_388_final.tsv'
$core = Import-Csv $corePath -Delimiter "`t"
$addition = Import-Csv $additionPath -Delimiter "`t"

function Write-Utf8NoBomCsv($rows, $path) {
  $csv = $rows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation
  [System.IO.File]::WriteAllLines($path, $csv, (New-Object System.Text.UTF8Encoding($false)))
}

$combined = @()
if ($core.Count -eq 888) {
  $combined = @($core)
} elseif ($core.Count -eq 500) {
  throw 'Legacy 500-row inputs are not a reproducible release source after GPT corrections. Use the committed 888-row verified dataset as the release input.'
} else {
  throw "Expected the verified core to contain 500 rows, found $($core.Count)."
}
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

if ($core.Count -eq 500) {
  Write-Utf8NoBomCsv $combined $corePath
  Write-Output "Wrote the balanced 888-row dataset to $corePath"
}

# Rows that only document a metalinguistic claim, a fragment, or a construction
# must not be emitted as independent learner vocabulary entries.
$specialStatuses = @('disputed', 'metalinguistic_only', 'fragment_only', 'construction_specific', 'native_review_required')
$learnerReady = @($combined | Where-Object { $_.status -notin $specialStatuses })
$learnerReadyPath = Join-Path $root 'data\oran_darija_learner_ready.tsv'
Write-Utf8NoBomCsv $learnerReady $learnerReadyPath
Write-Output "Wrote $($learnerReady.Count)-row learner-ready export to $learnerReadyPath"
if ($learnerReady.Count -ne 888) {
  Write-Warning 'Learner-ready export excludes special-status rows and is not A1/A2 rebalanced. Replace excluded rows before publishing it as a balanced core.'
}
