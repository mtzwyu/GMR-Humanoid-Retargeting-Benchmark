# Dựng results/v3_runtime.csv từ results/v3_raw.csv (cột ms_per_frame_process - RV-17)
$ErrorActionPreference = 'Stop'
$root = "C:\Users\xpaga\orca\workspaces\GMR-Humanoid-Retargeting-Benchmark\gmr-run"
$src  = Import-Csv (Join-Path $root "results\v3_raw.csv")
$note = 'input doi tu walk4_subject1 (clip khom lung, KI-01) sang walk1_subject1; khong dung --rate_limit'
$rows = foreach ($r in $src) {
    [pscustomobject]@{
        mode = 'no_rate_limit'; phase = $r.phase; robot = $r.robot
        input = $r.input; frames = $r.frames
        motion_duration_s = $r.motion_duration_s; wall_clock_s = $r.wall_clock_s
        ms_per_frame_process = $r.ms_per_frame_process; realtime_factor = $r.realtime_factor
        exit_code = $r.exit_code; cmd = $r.cmd; log = $r.log; note = $note
    }
}
$rows | Export-Csv -Path (Join-Path $root "results\v3_runtime.csv") -NoTypeInformation -Encoding UTF8

# Thong ke tren cac lan do (khong tinh warmup)
$meas = $src | Where-Object { $_.phase -like 'measure_*' } | ForEach-Object { [double]$_.ms_per_frame_process }
$mean = ($meas | Measure-Object -Average).Average
$sd   = if ($meas.Count -gt 1) { [math]::Sqrt((($meas | ForEach-Object { ($_ - $mean) * ($_ - $mean) } | Measure-Object -Sum).Sum) / ($meas.Count - 1)) } else { 0 }
$sorted = $meas | Sort-Object
$median = if ($sorted.Count % 2 -eq 1) { $sorted[[int](($sorted.Count - 1) / 2)] } else { ($sorted[$sorted.Count / 2 - 1] + $sorted[$sorted.Count / 2]) / 2 }
Write-Output ("rows={0} measured_n={1} mean={2:N3} median={3:N3} sd={4:N3} CV={5:N2}%" -f $rows.Count, $meas.Count, $mean, $median, $sd, (100 * $sd / $mean))
