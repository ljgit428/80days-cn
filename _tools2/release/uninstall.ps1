# 80 Days 汉化补丁卸载：从 80 Days_Data\_cn_backup 恢复原版，删除 CNText.dll
$ErrorActionPreference = 'Stop'
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
$dll = Join-Path $Game '80 Days_Data\Managed\CNText.dll'
if (Test-Path $dll) { Remove-Item $dll -Force }
Remove-Item -LiteralPath $bk -Recurse -Force
Write-Host '已恢复英文原版。' -ForegroundColor Green
Read-Host '按回车退出'
