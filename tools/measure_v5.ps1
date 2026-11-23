# Do V5 sim2sim — 1 warm-up + 3 lan do cho MOI robot, PM01 chay DAU TIEN de loai tru thermal (RV-15)
# RV-14: moi lan chay ghi them dong END wall_s=... ms_per_frame_process=... rtf=... vao chinh file log
# RV-17: cot thoi gian dat ten ms_per_frame_process (do ca tien trinh, khong phai rieng retarget())
# RV-24: ho tro chay bo sung (Warmup 0, StartIndex > 1) cho robot co CV > 5%
# Dung: powershell -File measure_v5.ps1 -RobotList "engineai_pm01,booster_t1_29dof,unitree_g1" -Measured 3
param([string]$RobotList = 'engineai_pm01,booster_t1_29dof,unitree_g1', [int]$Measured = 3, [int]$Warmup = 1, [int]$StartIndex = 1, [switch]$Append)
$ErrorActionPreference = 'Continue'
$py = if ($env:GMR_PYTHON) { $env:GMR_PYTHON } else { Join-Path $env:USERPROFILE "miniconda3\envs\gmr\python.exe" }
$root = Split-Path -Parent $PSScriptRoot   # tools/ nam trong <repo>/tools
$gmr  = Join-Path $root "third_party\GMR"
$motion = 'walk1_subject1'
$bvh  = "..\data\lafan1\$motion.bvh"
$frames = 7840
$duration = [math]::Round($frames / 30.0, 3)
$logdir = Join-Path $root "results\logs"
$raw    = Join-Path $root "results\v5_raw.csv"
$Robots = $RobotList -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
New-Item -ItemType Directory -Force $logdir, (Join-Path $root "results\pkl") | Out-Null
Set-Location $gmr

function Get-Temp {
    $gpu = 'n/a'
    try {
        $g = (& nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>$null) -join ''
        $g = ($g -replace '[^0-9\.]', '')
        if ($g) { $gpu = [math]::Round([double]$g, 1) }
    } catch { }
    $cpu = 'n/a'
    try {
        $t = (Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop |
                Measure-Object -Property CurrentTemperature -Maximum).Maximum
        $cpu = [math]::Round($t / 10.0 - 273.15, 1)
    } catch { }
    return "cpu=$cpu;gpu=$gpu"
}

$all = @()
foreach ($robot in $Robots) {
    for ($k = 1; $k -le ($Warmup + $Measured); $k++) {
        $idx   = $StartIndex + $k - 1
        $phase = if ($k -le $Warmup) { 'warmup' } else { "measure_$($StartIndex + $k - $Warmup - 1)" }
        $pkl   = Join-Path $root "results\pkl\v5_${robot}_${motion}_run$idx.pkl"
        $log   = Join-Path $logdir "v5_${robot}_${motion}_run$idx.log"
        $cmd   = "python scripts/bvh_to_robot.py --bvh_file $bvh --format lafan1 --robot $robot --save_path ../../results/pkl/v5_${robot}_${motion}_run$idx.pkl"
        $t0 = Get-Temp
        Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] START $robot $phase (temp $t0)"
        $m = Measure-Command {
            & $py scripts/bvh_to_robot.py --bvh_file $bvh --format lafan1 --robot $robot --save_path $pkl *> $log
        }
        $code = $LASTEXITCODE
        $t1 = Get-Temp
        $wall = [math]::Round($m.TotalSeconds, 3)
        $ms   = [math]::Round($m.TotalSeconds * 1000 / $frames, 3)
        $rtf  = [math]::Round($duration / $m.TotalSeconds, 3)
        "END wall_s=$wall ms_per_frame_process=$ms rtf=$rtf frames=$frames exit=$code temp_start=$t0 temp_end=$t1 at=$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" |
            Out-File -FilePath $log -Append -Encoding Unicode
        Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] END $robot $phase wall=$wall exit=$code ($t1)"

        $all += [pscustomobject]@{
            robot = $robot; run = $idx; phase = $phase; input = "lafan1:$motion.bvh"
            frames = $frames; motion_duration_s = $duration; wall_clock_s = $wall
            ms_per_frame_process = $ms; realtime_factor = $rtf; exit_code = $code
            temp_start = $t0; temp_end = $t1
            out_pkl = "results/pkl/v5_${robot}_${motion}_run$idx.pkl"
            cmd = $cmd; log = "results/logs/v5_${robot}_${motion}_run$idx.log"
        }
    }
}

if ($Append -and (Test-Path $raw)) {
    $tmp = Join-Path $root "results\_v5_new.csv"
    $all | Export-Csv -Path $tmp -NoTypeInformation -Encoding UTF8
    Get-Content $tmp | Select-Object -Skip 1 | Add-Content -Path $raw -Encoding UTF8
    Remove-Item $tmp
} else {
    $all | Export-Csv -Path $raw -NoTypeInformation -Encoding UTF8
}
Write-Output "DONE"
