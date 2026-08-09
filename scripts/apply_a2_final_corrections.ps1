$ErrorActionPreference = 'Stop'

$source = Join-Path $PSScriptRoot '..\data\madoran_expansion_a2_388_verified_v4.tsv'
$target = Join-Path $PSScriptRoot '..\data\madoran_expansion_a2_388_final.tsv'
$rows = Import-Csv $source -Delimiter "`t"

$changes = @{
  'OD-0588' = @{ ko = '우리는 그것(여성형)을 한다'; en = 'we do it (f.)' }
  'OD-0597' = @{ note = '미완료형; 형태 태그상 주어=그; 목적어 접사=그들을' }
  'OD-0603' = @{ ko = '실례해 줘; 용서해 줘 (여성 단수에게 하는 명령)' }
  'OD-0604' = @{ ko = '나는 그녀에게 말한다/그것을 말한다' }
  'OD-0612' = @{ ko = '우리가 ~하게 해 줘; 우리를 내버려 둬' }
  'OD-0620' = @{ ko = '나는 오래 걸리지 않는다'; en = 'I do not take long' }
  'OD-0626' = @{ ko = '나는 그것(여성형)을 한다'; en = 'I do it (f.)' }
  'OD-0633' = @{ ko = '너(남성 단수)는 그에게 준다/그것을 준다' }
  'OD-0645' = @{ arabic = 'نديرلك'; latin = 'ndirlek'; note = 'MADOran 원문 표면형 ندريلك(철자 전도)을 학습용 표준형 نديرلك로 정규화; 미완료형; 주어=나; 간접목적어=너에게' }
  'OD-0648' = @{ ko = '우리는 할 수 없다'; en = 'we cannot'; note = '미완료형; 형태 태그상 주어=우리; -ch 부정 표면형' }
  'OD-0655' = @{ ko = '우리는 한다'; en = 'we do'; note = '미완료형; 형태 태그상 주어=우리' }
  'OD-0661' = @{ en = 'some of them' }
  'OD-0670' = @{ ko = '그는 그것(여성형)을 했다'; en = 'he did it (f.)'; note = '완료형; 형태 태그상 주어=그; 목적어 접사=그녀를/그것(여성형)을' }
  'OD-0673' = @{ ko = '너는 알고 있다'; en = 'you know' }
  'OD-0676' = @{ note = '명령형; 형태 태그상 주어=너(남성 단수); 간접목적어 접사=나에게' }
  'OD-0707' = @{ ko = '그들은 논다' }
  'OD-0709' = @{ ko = '우리는 요리한다' }
  'OD-0727' = @{ ko = '보통; 대개' }
  'OD-0793' = @{ ko = '나는 임대한다' }
  'OD-0814' = @{ ko = '그들은 지었다' }
  'OD-0847' = @{ ko = '나는 수영한다' }
  'OD-0850' = @{ ko = '나는 요리한다' }
  'OD-0862' = @{ ko = '나는 쉰다' }
  'OD-0871' = @{ ko = '나는 일어난다'; en = 'I get up' }
  'OD-0876' = @{ ko = '나는 만난다' }
  'OD-0880' = @{ ko = '나는 길을 연다/비켜 준다' }
  'OD-0881' = @{ ko = '나는 터진다' }
  'OD-0882' = @{ ko = '나는 묻는다/문의한다' }
  'OD-0886' = @{ ko = '나는 달린다' }
}

foreach ($row in $rows) {
  if ($changes.ContainsKey($row.id)) {
    foreach ($field in $changes[$row.id].Keys) {
      $row.$field = $changes[$row.id][$field]
    }
  }
}

$rows | Export-Csv $target -Delimiter "`t" -NoTypeInformation -Encoding utf8
Write-Output "Wrote $($rows.Count) rows to $target"
