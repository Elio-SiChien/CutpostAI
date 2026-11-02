"""开新一期：逐项问人，生成 episode.json。期号等信息全部由人指定。

AI 工具（Claude Code / Codex）不要跑这个交互命令，而是在对话里问用户同样的问题，
再按 schemas/episode.example.json 的格式写 episode.json。
"""
import json, os, sys

from . import shows


def ask(q, default=None, required=True):
    while True:
        tip = f'（默认 {default}）' if default else ''
        v = input(f'{q}{tip}: ').strip() or (default or '')
        if v or not required:
            return v
        print('  这一项必须填。')


def run(folder):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, 'episode.json')
    if os.path.exists(path):
        sys.exit(f'{path} 已存在，直接编辑它即可。')
    known = shows.list_shows()
    if known:
        print('已登记的节目: ' + ', '.join(known))
    show_name = ask('节目（已登记的名字，或节目配置文件夹路径）', next(iter(known), None))
    show = shows.load(shows.resolve(show_name, folder))
    ep = ''
    while not ep.isdigit():
        ep = ask('期号 EP（只填数字）')
    series = ''
    if show['series']:
        keys = list(show['series'])
        print('栏目: ' + '  '.join(f'{i+1}) {show["series"][k]["name"]}' for i, k in enumerate(keys)))
        series = keys[int(ask('栏目编号', '1')) - 1]
    hosts = ask('主持人（多人用顿号隔开）')
    guests = []
    while True:
        name = ask(f'第 {len(guests)+1} 位嘉宾姓名（没有了直接回车）', required=False)
        if not name:
            if guests:
                break
            print('  至少要有一位嘉宾。'); continue
        fields = []
        print('  嘉宾介绍，每行一项，格式「标签：内容」，如「研究方向：复合极端事件」；空行结束')
        while True:
            line = input('  > ').strip()
            if not line:
                break
            label, _, value = line.replace(':', '：').partition('：')
            fields.append({'label': label.strip(), 'value': value.strip()})
        photo = ask('  照片文件名（放在本期文件夹里；没有就回车）', required=False)
        guests.append({'name': name, 'photo': photo, 'fields': fields})
    audio = ask('原始音频文件名（放在本期文件夹里；还没有就回车）', required=False)
    end_card = ask('编尾卡片图片文件名（没有就回车）', required=False)
    data = {'show': show_name, 'ep': int(ep), 'series': series, 'hosts': hosts, 'guests': guests,
            'audio': audio, 'end_card': end_card}
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('已保存', path)
