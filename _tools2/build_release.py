# 生成可公开发布的补丁：只含 xdelta 差异补丁 + 自制的 CNText.dll，不含任何原版游戏文件
# 用法: python build_release.py   （需要 _xd\xdelta3-3.1.0-x86_64.exe；先保证游戏目录里是最新汉化版）
import os, hashlib, shutil, subprocess, zipfile
ROOT = r'D:\git\project\80 days CN'; GAME = r'F:\Games\80 Days'; ORIG = os.path.join(ROOT, 'ORIGINAL_BACKUP')
XD = os.path.join(ROOT, '_xd', 'xdelta3-3.1.0-x86_64.exe')
SRC = os.path.join(ROOT, '_tools2', 'release')
OUT = os.path.join(ROOT, 'release_build', '80Days_CN_Patch'); F = os.path.join(OUT, 'files')
OWN = {r'80 Days_Data\Managed\CNText.dll'}          # 汉化自制文件，直接附带
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(F)
rows = []
for dp, dn, fn in os.walk(os.path.join(GAME, '80 Days_Data')):
    for f in fn:
        p = os.path.join(dp, f); rel = os.path.relpath(p, GAME)
        if '_cn_backup' in rel or rel.endswith(('.log', '.cn_tmp')): continue
        o = os.path.join(ORIG, rel)
        if rel in OWN:
            shutil.copy2(p, os.path.join(F, f)); rows.append((rel, '-', md5(p), f)); continue
        if not os.path.exists(o): continue
        if os.path.getsize(o) == os.path.getsize(p) and md5(o) == md5(p): continue
        name = rel.replace('80 Days_Data\\', '').replace('\\', '_') + '.xdelta'
        subprocess.run([XD, '-e', '-9', '-f', '-B', str(1 << 28), '-s', o, p, os.path.join(F, name)], check=True)
        rows.append((rel, md5(o), md5(p), name))
        print(rel, os.path.getsize(p), '->', os.path.getsize(os.path.join(F, name)))
with open(os.path.join(F, 'manifest.txt'), 'w', encoding='utf-8', newline='\n') as w:
    w.write('# 相对路径\t原版MD5\t汉化后MD5\t补丁文件\n'); w.writelines('\t'.join(r) + '\n' for r in rows)
shutil.copy2(XD, os.path.join(F, 'xdelta3.exe'))
for n in os.listdir(SRC):
    s = os.path.join(SRC, n); d = os.path.join(OUT, n)
    if n.endswith('.ps1'): open(d, 'w', encoding='utf-8-sig', newline='\r\n').write(open(s, encoding='utf-8').read())
    elif n.endswith('.txt'): open(d, 'w', encoding='utf-8-sig', newline='\r\n').write(open(s, encoding='utf-8').read())
    else: shutil.copy2(s, d)
z = os.path.join(ROOT, 'release_build', '80Days_CN_Patch_v1.0.zip')
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for dp, dn, fn in os.walk(OUT):
        for f in fn: p = os.path.join(dp, f); zf.write(p, os.path.relpath(p, os.path.dirname(OUT)))
print('zip', z, os.path.getsize(z))
