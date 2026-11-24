# Dung results/v5_sim2sim.csv tu results/v5_raw.csv (12 dong: 3 robot × [warmup + 3 lan do])
# + 1 dong H1 blocked. Cot thoi gian: ms_per_frame_process (RV-17). So dof lay tu chinh pkl.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot   # tools/ nam trong <repo>/tools
$src  = Import-Csv (Join-Path $root "results\v5_raw.csv")
$dof  = @{ 'unitree_g1' = 29; 'booster_t1_29dof' = 27; 'engineai_pm01' = 24 }   # đo từ dof_pos của pkl

$rows = foreach ($r in $src) {
    [pscustomobject]@{
        robot = $r.robot; dof = $dof[$r.robot]; phase = $r.phase; run = $r.run
        input = $r.input; frames = $r.frames
        motion_duration_s = $r.motion_duration_s; wall_clock_s = $r.wall_clock_s
        ms_per_frame_process = $r.ms_per_frame_process; realtime_factor = $r.realtime_factor
        exit_code = $r.exit_code; temp_start = $r.temp_start; temp_end = $r.temp_end
        out_pkl = $r.out_pkl; cmd = $r.cmd; log = $r.log
        status = 'ok'
        note = if ([int]$r.run -ge 5) { 'chay bo sung 2 lan theo RV-24 vi CV > 5%' } else { 'khong dung --rate_limit; PM01 chay dau tien de loai tru thermal' }
    }
}
$rows += [pscustomobject]@{
    robot = 'unitree_h1'; dof = ''; phase = ''; run = ''
    input = 'lafan1:walk1_subject1.bvh'; frames = 0
    motion_duration_s = ''; wall_clock_s = ''
    ms_per_frame_process = ''; realtime_factor = ''
    exit_code = 2; temp_start = ''; temp_end = ''
    out_pkl = ''
    cmd = 'python scripts/bvh_to_robot.py --bvh_file ../data/lafan1/walk1_subject1.bvh --format lafan1 --robot unitree_h1 --save_path ...'
    log = 'results/logs/v5_h1_blocked.log'
    status = 'blocked'
    note = "KHONG CHAY DUOC tren duong BVH: 'argument --robot: invalid choice: unitree_h1' (exit 2); danh sach hop le: booster_t1_29dof, engineai_pm01, fourier_n1, pal_talos, stanford_toddy, unitree_g1, unitree_g1_with_hands, unitree_h2. README ghi cot BVH cua unitree_h1/h1_2 = TBD; khong co ik_configs bvh_*_to_h1.json; duong SMPL-X bi chan boi license"
}
$rows | Export-Csv -Path (Join-Path $root "results\v5_sim2sim.csv") -NoTypeInformation -Encoding UTF8

# Thong ke tung robot tren cac lan do
foreach ($robot in @('engineai_pm01', 'booster_t1_29dof', 'unitree_g1')) {
    $v = $src | Where-Object { $_.robot -eq $robot -and $_.phase -like 'measure_*' } | ForEach-Object { [double]$_.ms_per_frame_process }
    $mean = ($v | Measure-Object -Average).Average
    $sd   = if ($v.Count -gt 1) { [math]::Sqrt((($v | ForEach-Object { ($_ - $mean) * ($_ - $mean) } | Measure-Object -Sum).Sum) / ($v.Count - 1)) } else { 0 }
    $s = $v | Sort-Object
    $median = if ($s.Count % 2 -eq 1) { $s[[int](($s.Count - 1) / 2)] } else { ($s[$s.Count / 2 - 1] + $s[$s.Count / 2]) / 2 }
    Write-Output ("{0,-18} n={1} mean={2:N3} median={3:N3} sd={4:N3} CV={5:N2}% min={6:N3} max={7:N3}" -f $robot, $v.Count, $mean, $median, $sd, (100 * $sd / $mean), ($s[0]), ($s[-1]))
}
