# Do runtime V3 cho GMR - CHa»ˆ chaº¿ da»™ khA´ng --rate_limit (xem RV-13: ca» --rate_limit khA´ng do dÆ°a»£c throughput)
# RV-14: ma»—i laº§n chaº¡y ghi thAªm dA²ng END wall_s=... ms_per_frame=... rtf=... vA o CHANH file log ca»§a laº§n dA³
# DA¹ng: powershell -File measure_v3.ps1 [-Warmup 1] [-Measured 3] [-StartIndex 1]
param([int]$Warmup = 1, [int]$Measured = 3, [int]$StartIndex = 1)
$ErrorActionPreference = 'Continue'
$py = if ($env:GMR_PYTHON) { $env:GMR_PYTHON } else { Join-Path $env:USERPROFILE "miniconda3\envs\gmr\python.exe" }
$root = Split-Path -Parent $PSScriptRoot   # tools/ nam trong <repo>/tools
$gmr  = Join-Path $root "third_party\GMR"
$motion = 'walk1_subject1'
$bvh  = "..\data\lafan1\$motion.bvh"
$frames = 7840
$duration = [math]::Round($frames / 30.0, 3)
$logdir = Join-Path $root "results\logs"
$raw    = Join-Path $root "results\v3_raw.csv"
New-Item -ItemType Directory -Force $logdir, (Join-Path $root "results\pkl") | Out-Null
Set-Location $gmr

$all = @()
for ($k = 1; $k -le ($Warmup + $Measured); $k++) {
    $idx   = $StartIndex + $k - 1
    $phase = if ($k -le $Warmup) { 'warmup' } else { "measure_$($k - $Warmup)" }
    $pkl   = Join-Path $root "results\pkl\g1_${motion}_run$idx.pkl"
    $log   = Join-Path $logdir "v3_${motion}_run$idx.log"
    $cmd   = "python scripts/bvh_to_robot.py --bvh_file $bvh --format lafan1 --robot unitree_g1 --save_path ../../results/pkl/g1_${motion}_run$idx.pkl"
    Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] START run$idx $phase"
    $m = Measure-Command {
        & $py scripts/bvh_to_robot.py --bvh_file $bvh --format lafan1 --robot unitree_g1 --save_path $pkl *> $log
    }
    $code = $LASTEXITCODE
    $wall = [math]::Round($m.TotalSeconds, 3)
    $ms   = [math]::Round($m.TotalSeconds * 1000 / $frames, 3)
    $rtf  = [math]::Round($duration / $m.TotalSeconds, 3)
    # RV-14: ghi ket qua vao chinh file log cua lan chay
    "END wall_s=$wall ms_per_frame=$ms rtf=$rtf frames=$frames exit=$code at=$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" |
        Out-File -FilePath $log -Append -Encoding Unicode
    Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] END run$idx $phase wall=$wall exit=$code"

    $all += [pscustomobject]@{
        run = $idx; phase = $phase; robot = 'unitree_g1'
        input = "lafan1:$motion.bvh"; frames = $frames
        motion_duration_s = $duration; wall_clock_s = $wall
        ms_per_frame_process = $ms; realtime_factor = $rtf; exit_code = $code
        cmd = $cmd; log = "results/logs/v3_${motion}_run$idx.log"
    }
}

if (Test-Path $raw) {
    $all | Export-Csv -Path (Join-Path $root "results\_v3_new.csv") -NoTypeInformation -Encoding UTF8
    Get-Content (Join-Path $root "results\_v3_new.csv") | Select-Object -Skip 1 |
        Add-Content -Path $raw -Encoding UTF8
    Remove-Item (Join-Path $root "results\_v3_new.csv")
} else {
    $all | Export-Csv -Path $raw -NoTypeInformation -Encoding UTF8
}
Write-Output "DONE"

