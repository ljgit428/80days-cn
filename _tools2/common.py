# 80 Days 汉化公共模块：可翻译字符串的遍历规则（提取与回填共用同一套规则，保证一致）
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, 'extracted')

SKIP_KEYS = {'initial','linkPath','divert','func','get','var','name','buildingBlock','condition',
             'params','action','set','doFuncs','inlineOption','storyCustomContentClass','styleName'}
ACTION_TEXT = {'Incident':('text',),'SetClue':('text','speaker','retelling'),'ChangeTransportTitle':('title',)}

def is_identifier(s):
    s = s.strip()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', s): return False
    return '_' in s or bool(re.search(r'[a-z][A-Z]', s)) or bool(re.search(r'[A-Z]{2,}[a-z]', s))

FORCE = {'MechnicallyUnstable'}  # 看起来像 id 但实际会显示的串

def translatable(s):
    if s in FORCE: return True
    t = re.sub(r'<[^>]+>', '', s)
    return bool(re.search(r'[A-Za-z]', t)) and not is_identifier(s)

def walk_ink(el, cb, path=''):
    """cb(string, path) -> 新字符串或 None。返回替换后的元素。"""
    if isinstance(el, str):
        if path and translatable(el):
            r = cb(el, path)
            return el if r is None else r
        return el
    if isinstance(el, list):
        return [walk_ink(x, cb, path + '[]') for x in el]
    if isinstance(el, dict):
        out = {}
        for k, v in el.items():
            if k == 'userInfo' and el.get('action') in ACTION_TEXT and isinstance(v, dict):
                nv = dict(v)
                for f in ACTION_TEXT[el['action']]:
                    if isinstance(v.get(f), str) and translatable(v[f]):
                        r = cb(v[f], path + '/action.' + el['action'] + '.' + f)
                        if r is not None: nv[f] = r
                out[k] = nv
            elif k in SKIP_KEYS or k == 'userInfo':
                out[k] = v
            elif k == 'option':
                out[k] = walk_ink(v, cb, path + '/option') if isinstance(v, str) else v
            else:
                out[k] = walk_ink(v, cb, path + '/' + k)
        return out
    return el

# 数据文件：哪些键的字符串需要翻译
DATA_RULES = {
    'chaptertitles': {'titles'},
    'facts': None,  # 所有字符串值（键是城市名，不动）
    'itemsdata': {'name','pluralisedDescriptor','description','dialogue','setDisplayName','descriptionOfSet','regionText'},
    'cast': {'salute','questionAndAnswers','address'},
    'mapdata': {'name','marketName','description','clueRouteName','luggage rack','extra space',
                'journeyAdjective','descriptiveAdjective','descriptiveNoun'},
}

def walk_data(el, keys, cb, key=None, path=''):
    if isinstance(el, dict):
        return {k: walk_data(v, keys, cb, k, path + '/' + k) for k, v in el.items()}
    if isinstance(el, list):
        return [walk_data(x, keys, cb, key, path + '[]') for x in el]
    if isinstance(el, str) and (keys is None or key in keys) and translatable(el):
        r = cb(el, path)
        return el if r is None else r
    return el

def iter_sources():
    """产出 (文件名, 单元标识, 回调式遍历函数, 写回函数)"""
    pass
