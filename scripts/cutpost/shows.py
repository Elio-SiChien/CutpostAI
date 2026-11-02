"""节目配置（show）的查找与读取。

一个“节目”= 一个文件夹，里面有:
    show.json        节目名、栏目（series）、标题格式
    template/        推文模板（base.html + fragments/*.html）

节目可以用名字引用：名字 → 文件夹 的对应关系保存在 ~/.cutpost/config.json，
用 `show add <名字> <文件夹>` 登记。也可以直接写文件夹路径。
"""
import json, os, sys

CONFIG = os.path.join(os.path.expanduser('~'), '.cutpost', 'config.json')
BUILTIN = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'shows')


def load_config():
    try:
        return json.load(open(CONFIG, encoding='utf-8'))
    except FileNotFoundError:
        return {'shows': {}}


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    json.dump(cfg, open(CONFIG, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def add_show(name, folder):
    folder = os.path.abspath(folder)
    if not os.path.exists(os.path.join(folder, 'show.json')):
        sys.exit(f'{folder} 里没有 show.json，不是节目配置文件夹')
    cfg = load_config()
    cfg.setdefault('shows', {})[name] = folder
    save_config(cfg)
    print(f'已登记节目 {name} → {folder}')


def list_shows():
    found = {}
    if os.path.isdir(BUILTIN):
        for n in sorted(os.listdir(BUILTIN)):
            if os.path.exists(os.path.join(BUILTIN, n, 'show.json')):
                found[n] = os.path.join(BUILTIN, n)
    found.update(load_config().get('shows', {}))  # 用户登记的同名节目优先
    return found


def resolve(show, base_dir='.'):
    """show 可以是登记过的名字，也可以是文件夹路径（相对 base_dir）。"""
    if not show:
        sys.exit('episode.json 里缺少 show（节目名或节目配置文件夹）')
    cand = show if os.path.isabs(show) else os.path.join(base_dir, show)
    if os.path.exists(os.path.join(cand, 'show.json')):
        return os.path.abspath(cand)
    shows = list_shows()
    if show in shows:
        return shows[show]
    sys.exit(f'找不到节目 “{show}”。已登记: {list(shows) or "无"}。用 `show add <名字> <文件夹>` 登记。')


def load(show_dir):
    s = json.load(open(os.path.join(show_dir, 'show.json'), encoding='utf-8'))
    s.setdefault('title_format', '{show}EP{ep}：{series}——{topic}')
    s.setdefault('heading_format', '{series}——{topic}')
    s.setdefault('series', {})
    s['_dir'] = show_dir
    return s
