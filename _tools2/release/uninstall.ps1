# 80 Days 汉化补丁卸载：从 80 Days_Data\_cn_backup 恢复原版，删除汉化自带的文件
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$F = Join-Path $here 'files'
Write-Host '==== 80 Days 汉化补丁 卸载（恢复英文原版） ====' -ForegroundColor Cyan
$Game = 'F:\Games\80 Days'
$in = Read-Host "游戏目录（直接回车使用 $Game）"
if ($in) { $Game = $in.Trim('"') }
$bk = Join-Path $Game '80 Days_Data\_cn_backup'
if (-not (Test-Path $bk)) { Write-Host "没有找到备份 $bk；可在 GOG Galaxy 里“验证/修复”恢复原版。" -ForegroundColor Red; Read-Host '按回车退出'; exit 1 }
Get-ChildItem -LiteralPath $bk -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($bk.Length + 1)
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $Game $rel) -Force
    Write-Host "已恢复：$rel"
}
# 汉化自带的新增文件（manifest 里原版MD5 为 “-” 的那些）整条删掉
$man = Join-Path $F 'manifest.txt'
if (Test-Path $man) {
    Get-Content $man -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object {
        $a = $_ -split "`t"
        if ($a[1] -eq '-') {
            $p = Join-Path $Game $a[0]
            if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force; Write-Host "已删除：$($a[0])" }
        }
    }
}
# 运行期生成的诊断文件
Get-ChildItem -LiteralPath $Game -Filter 'cn_prewarm_missing_*.txt' -File -ErrorAction SilentlyContinue | Remove-Item -Force
foreach ($n in @('cn_untranslated.txt')) { $p = Join-Path $Game $n; if (Test-Path $p) { Remove-Item $p -Force } }
Remove-Item -LiteralPath $bk -Recurse -Force
Write-Host '已恢复英文原版。' -ForegroundColor Green
Read-Host '按回车退出'
