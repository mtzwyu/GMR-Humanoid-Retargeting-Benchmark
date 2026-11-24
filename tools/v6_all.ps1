# Chay 15 dieu kien V6 (N1..N4), moi dieu kien 1 lan. Khong mo viewer.
$ErrorActionPreference = 'Continue'
$py = if ($env:GMR_PYTHON) { $env:GMR_PYTHON } else { Join-Path $env:USERPROFILE "miniconda3\envs\gmr\python.exe" }
$root = Split-Path -Parent $PSScriptRoot   # tools/ nam trong <repo>/tools
$script = Join-Path $root "tools\v6_run.py"
$logdir = Join-Path $root "results\logs"
Set-Location (Join-Path $root "third_party\GMR")

$jobs = @(
    @('n1', 0.5,  'v6_n1_0p5deg'),
    @('n1', 1,    'v6_n1_1deg'),
    @('n1', 2,    'v6_n1_2deg'),
    @('n1', 5,    'v6_n1_5deg'),
    @('n2', 1,    'v6_n2_k1'),
    @('n2', 2,    'v6_n2_k2'),
    @('n2', 3,    'v6_n2_k3'),
    @('n2', 5,    'v6_n2_k5'),
    @('n3', 1,    'v6_n3_1pct'),
    @('n3', 5,    'v6_n3_5pct'),
    @('n3', 10,   'v6_n3_10pct'),
    @('n4', -20,  'v6_n4_m20pct'),
    @('n4', -10,  'v6_n4_m10pct'),
    @('n4', 10,   'v6_n4_p10pct'),
    @('n4', 20,   'v6_n4_p20pct')
)
foreach ($j in $jobs) {
    $mode = $j[0]; $lvl = $j[1]; $name = $j[2]
    $out = Join-Path $root "results\pkl\$name.pkl"
    $log = Join-Path $logdir "$name.log"
    Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] START $name"
    & $py $script --mode $mode --level $lvl --seed 0 --out $out *> $log
    Write-Output "[$((Get-Date).ToString('HH:mm:ss'))] END $name exit=$LASTEXITCODE"
}
Write-Output "DONE"
