# In lai bang chung cua LAN CHAY run6 (so dung cho bao cao) de chup anh doi chieu.
# Dung: Start-Process powershell -ArgumentList '-NoExit','-File','tools\show_run6_evidence.ps1'
$root = Split-Path -Parent $PSScriptRoot
$log  = Join-Path $root "results\logs\v3_walk1_subject1_run6.log"
$csv  = Join-Path $root "results\v3_runtime.csv"

Write-Host "=========== GMR V3 - bang chung lan chay run6 ===========" -ForegroundColor Cyan
Write-Host ("May      : " + $env:COMPUTERNAME + " | Windows 11 | Intel i5-12450HX | CPU-only")
Write-Host ("Xem luc  : " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ("Env      : conda gmr | " + $py)
Write-Host ""

$row = Import-Csv $csv | Where-Object { $_.phase -eq 'measure_5' }
Write-Host "LENH CUA LAN CHAY run6 (cot cmd trong results/v3_runtime.csv):" -ForegroundColor Yellow
Write-Host ("  " + $row.cmd)
Write-Host ""
Write-Host "DONG END TRONG CHINH FILE LOG CUA LAN CHAY (results/logs/v3_walk1_subject1_run6.log):" -ForegroundColor Yellow
Get-Content $log -Tail 1 | ForEach-Object { Write-Host ("  " + $_) }
Write-Host ""
Write-Host "DONG TUONG UNG TRONG results/v3_runtime.csv:" -ForegroundColor Yellow
Write-Host ("  phase={0}  wall_clock_s={1}  ms_per_frame_process={2}  realtime_factor={3}" -f $row.phase, $row.wall_clock_s, $row.ms_per_frame_process, $row.realtime_factor)
Write-Host ""
Write-Host "SO CHOT CUA BAO CAO: mean n=5 = 17,349 ms/frame, CV 2,13 phan tram, 33,333/17,349 = 1,92x" -ForegroundColor Green
Write-Host "  -> dong END tren day la cua MOT lan chay (measure_5), dung lam bang chung." -ForegroundColor Green
