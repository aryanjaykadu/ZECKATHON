$companies = @('bse','cdsl','cams','kfin')
$subfolders = @('annual_reports','quarterly_results','investor_presentations','earnings_transcripts','shareholding')
foreach ($c in $companies) {
  foreach ($s in $subfolders) {
    New-Item -ItemType Directory -Force -Path "data/raw/$c/$s" | Out-Null
  }
}
$industryDirs = @('data/raw/industry/derivatives_turnover','data/raw/industry/amfi','data/raw/industry/demat')
$otherDirs = @('data/raw/prices','data/raw/regulation/sebi','data/raw/macro')
foreach ($d in ($industryDirs + $otherDirs)) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
}
Write-Output 'Folders created.'
