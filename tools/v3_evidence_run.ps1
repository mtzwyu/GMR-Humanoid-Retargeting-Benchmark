# Chay MOT lan do V3 trong cua so console hien thi (de chup anh bang chung)
# Khoi dong: Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','<duong dan>\v3_evidence_run.ps1'
$ErrorActionPreference = 'Continue'
$py = if ($env:GMR_PYTHON) { $env:GMR_PYTHON } else { Join-Path $env:USERPROFILE "miniconda3\envs\gmr\python.exe" }
$root = Split-Path -Parent $PSScriptRoot   # tools/ nam trong <repo>/tools
$gmr  = Join-Path $root "third_party\GMR"
$pkl  = Join-Path $root "results\pkl\g1_walk1_subject1_evidence.pkl"
$log  = Join-Path $root "results\logs\v3_walk1_subject1_evidence.log"
$frames = 7840
$duration = 261.333

Write-Host "================ GMR V3 - do runtime (bang chung) ================" -ForegroundColor Cyan
Write-Host ("May      : " + $env:COMPUTERNAME + " | Windows 11 | Intel i5-12450HX | CPU-only")
Write-Host ("Thoi diem: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ("Env      : conda gmr | " + $py)
Write-Host ("Input    : lafan1/walk1_subject1.bvh  (7840 frame, 30 fps, 261,3 s)")
Write-Host ("Lenh     : python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/g1_walk1_subject1_evidence.pkl")
Write-Host ("Thu muc  : " + $gmr)
Write-Host "Dang chay (khong --rate_limit)..."
Set-Location $gmr

$m = Measure-Command {
    & $py scripts/bvh_to_robot.py --bvh_file ..\data\lafan1\walk1_subject1.bvh --format lafan1 `
        --robot unitree_g1 --save_path $pkl *> $log
}
$code = $LASTEXITCODE
$ms = [math]::Round($m.TotalSeconds * 1000 / $frames, 3)
$rtf = [math]::Round($duration / $m.TotalSeconds, 3)

Write-Host ""
Write-Host ("KET QUA  exit=" + $code)
Write-Host ("TotalSeconds    = " + $m.TotalSeconds)
Write-Host ("wall_clock_s    = " + [math]::Round($m.TotalSeconds, 3))
Write-Host ("ms_per_frame    = " + $ms)
Write-Host ("realtime_factor = " + $rtf + "   (261,33 s motion / wall)")
Write-Host ("Xong luc: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))

[pscustomobject]@{
    mode = 'no_rate_limit'; phase = 'measure_4'; robot = 'unitree_g1'
    input = 'lafan1:walk1_subject1.bvh'; frames = $frames; motion_duration_s = $duration
    wall_clock_s = [math]::Round($m.TotalSeconds, 3); ms_per_frame = $ms
    realtime_factor = $rtf; exit_code = $code
    cmd = 'python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/g1_walk1_subject1_evidence.pkl'
    log = 'results/logs/v3_walk1_subject1_evidence.log'
} | Export-Csv -Path (Join-Path $root "results\_v3_evidence.csv") -NoTypeInformation -Encoding UTF8
