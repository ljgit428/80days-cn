# 80 Days 汉化补丁安装：校验原版文件 -> 备份 -> 用 xdelta3 打补丁 -> 校验结果
param([string]$Game)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$F = Join-Path $here 'files'
Write-Host '==== 80 Days 简体中文汉化补丁 安装 ====' -ForegroundColor Cyan
if (-not $Game) {
    $Game = 'F:\Games\80 Days'
    foreach ($c in @('C:\GOG Games\80 Days', 'D:\GOG Games\80 Days', 'C:\Program Files (x86)\GOG Galaxy\Games\80 Days')) { if (Test-Path "$c\80 Days.exe") { $Game = $c } }
    $in = Read-Host "游戏目录（含 80 Days.exe 的文件夹，直接回车使用 $Game）"
    if ($in) { $Game = $in.Trim('"') }
}
if (-not (Test-Path (Join-Path $Game '80 Days.exe'))) { Write-Host "找不到 $Game\80 Days.exe" -ForegroundColor Red; Read-Host '按回车退出'; exit 1 }
$list = Get-Content (Join-Path $F 'manifest.txt') -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object {
    $a = $_ -split "`t"; [pscustomobject]@{ Rel = $a[0]; Orig = $a[1]; New = $a[2]; Patch = $a[3]; State = '' } }
function MD5($p) { (Get-FileHash -LiteralPath $p -Algorithm MD5).Hash.ToLower() }
$bad = @()
foreach ($x in $list) {
    $p = Join-Path $Game $x.Rel
    if ($x.Orig -eq '-') { $x.State = 'copy'; continue }
    if (-not (Test-Path -LiteralPath $p)) { $bad += "$($x.Rel)（缺失）"; continue }
    $h = MD5 $p
    if ($h -eq $x.New) { $x.State = 'done' } elseif ($h -eq $x.Orig) { $x.State = 'todo' } else { $bad += $x.Rel }
}
if ($bad.Count) {
    Write-Host '以下文件与补丁对应的 GOG 原版不一致，无法安装：' -ForegroundColor Red
    $bad | ForEach-Object { Write-Host "  $_" }
    Write-Host '请确认是 GOG 版 80 Days；可先在 GOG Galaxy 里“验证/修复”恢复原版后再装。'
    Read-Host '按回车退出'; exit 1
}
$bk = Join-Path $Game '80 Days_Data\_cn_backup'
foreach ($x in $list) {
    $p = Join-Path $Game $x.Rel
    switch ($x.State) {
        'done' { Write-Host "已是汉化版：$($x.Rel)" }
        'copy' { Copy-Item -LiteralPath (Join-Path $F $x.Patch) -Destination $p -Force; Write-Host "复制：$($x.Rel)" }
        'todo' {
            $b = Join-Path $bk $x.Rel; New-Item -ItemType Directory -Force -Path (Split-Path $b) | Out-Null
            if (-not (Test-Path -LiteralPath $b)) { Copy-Item -LiteralPath $p -Destination $b }
            $tmp = "$p.cn_tmp"
            & (Join-Path $F 'xdelta3.exe') -d -f -s $p (Join-Path $F $x.Patch) $tmp
            if ($LASTEXITCODE -ne 0 -or (MD5 $tmp) -ne $x.New) { Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue; throw "打补丁失败：$($x.Rel)" }
            Move-Item -LiteralPath $tmp -Destination $p -Force
            Write-Host "已汉化：$($x.Rel)"
        }
    }
}
Write-Host ''
Write-Host '安装完成！启动游戏即可。原版文件已备份到 80 Days_Data\_cn_backup。' -ForegroundColor Green
Read-Host '按回车退出'
