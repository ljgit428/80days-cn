# 场景/预制体里写死的界面文字（菜单按钮、设置项、提示框、制作人员标题等）
# 用法: python apply_ui.py   —— 以 patched/pre_ui 里的首次备份为源，可重复执行
import UnityPy, os, sys, io, json, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
ROOT = r'D:\git\project\80 days CN'
GAME = r'F:\Games\80 Days\80 Days_Data'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hashkey import H
_p = os.path.join(ROOT, 'translation', 'ui_scene.json')   # 本地明文（不入库）；没有就用哈希键版本
HASHED = not os.path.exists(_p)
M = json.load(open(os.path.join(ROOT, 'translation', 'hashed', 'ui_scene.json') if HASHED else _p, encoding='utf-8'))
K = H if HASHED else (lambda s: s)
pre = os.path.join(ROOT, 'patched', 'pre_ui'); os.makedirs(pre, exist_ok=True)
gen = TypeTreeGenerator('2018.4.30f1'); gen.load_local_game(r'F:\Games\80 Days')
FILES = ['level0', 'level1', 'level7', 'sharedassets1.assets']
total = 0
for name in FILES:
    src = os.path.join(pre, name)
    if not os.path.exists(src):
        for extra in glob.glob(os.path.join(GAME, name + '*')):
            shutil.copy(extra, os.path.join(pre, os.path.basename(extra)))
    shutil.copy(src, os.path.join(GAME, name))   # 先还原成原始版本，再在游戏目录里加载（依赖文件要在同目录）
    env = UnityPy.load(os.path.join(GAME, name)); env.typetree_generator = gen
    n = 0
    for o in env.objects:
        if o.type.name != 'MonoBehaviour': continue
        try: t = o.read_typetree()
        except Exception: continue
        ch = False
        for k in ('m_text', 'content'):
            v = t.get(k)
            if isinstance(v, str) and K(v) in M:
                t[k] = v if M[K(v)] == '@=' else M[K(v)]; ch = True
        if ch:
            o.save_typetree(t); n += 1
    if n:
        outdir = os.path.join(ROOT, 'patched', 'ui'); os.makedirs(outdir, exist_ok=True)
        env.save(out_path=outdir)
        shutil.copy(os.path.join(outdir, name), os.path.join(GAME, name))
    print(name, 'replaced', n); total += n
print('ui total', total)
