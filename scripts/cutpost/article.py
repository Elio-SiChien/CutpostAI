"""把一期节目的推文渲染成可以直接粘贴进微信公众号编辑器的 HTML。

两份输入，人填的和 AI 写的分开:
    episode.json        人在开剪时指定：show、ep（期号）、series、hosts、guests、end_card
    article_draft.json  AI 根据录音写：topic、intro、chapters、sections、note
期号只从 episode.json 读，程序从不自动编号。

只用 Python 标准库；装了 Pillow 会自动压缩图片，没装也能用。
"""
import base64, html, json, mimetypes, os, re, sys

from . import shows

HUMAN_FIELDS = ['show', 'ep', 'hosts', 'guests']
AI_FIELDS = ['topic', 'intro', 'chapters', 'sections']


def esc(s):
    return html.escape(str(s), quote=False)


def fill(tpl, **kw):
    # 只替换 {name} 占位，不碰内联样式里的其它字符
    for k, v in kw.items():
        tpl = tpl.replace('{' + k + '}', v)
    return tpl


def image_src(path, base_dir, max_w=1080):
    """本地图片 → data URI（公众号编辑器粘贴时会自动转存到素材库）；https 地址原样使用。"""
    if not path:
        return ''
    if re.match(r'^(https?:|data:)', path):
        return path
    p = path if os.path.isabs(path) else os.path.join(base_dir, path)
    if not os.path.exists(p):
        sys.exit(f'找不到图片: {p}')
    mime = mimetypes.guess_type(p)[0] or 'image/jpeg'
    try:
        from PIL import Image, ImageOps
        import io
        im = Image.open(p)
        if getattr(im, 'is_animated', False) or mime == 'image/gif':
            raise ImportError  # 动图原样保留
        im = ImageOps.exif_transpose(im).convert('RGB')
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)))
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=85)
        data, mime = buf.getvalue(), 'image/jpeg'
    except ImportError:
        data = open(p, 'rb').read()
        if len(data) > 2_000_000:
            print(f'提示: {os.path.basename(p)} 有 {len(data)//1024} KB，建议压缩到 2MB 以内', file=sys.stderr)
    return f'data:{mime};base64,' + base64.b64encode(data).decode()


def notice(text):
    """粘贴后需要手动处理的位置。用普通彩色文字（带边框的框会被公众号编辑器过滤掉）。"""
    return ('<p style="margin:12px 0;text-align:center;color:#d4380d;font-size:14px;font-weight:bold">'
            f'【{esc(text)}】</p>')


def load(episode_path, draft_path):
    ep = json.load(open(episode_path, encoding='utf-8'))
    dr = json.load(open(draft_path, encoding='utf-8'))
    miss = [k for k in HUMAN_FIELDS if k not in ep]
    if miss:
        sys.exit(f'episode.json 缺少（需要人来填）: {miss}')
    if not str(ep.get('ep') or '').strip().isdigit():
        sys.exit('episode.json 里没有期号 ep（例如 "ep": 33）。期号需要人来指定，程序不会自动编号。')
    miss = [k for k in AI_FIELDS if k not in dr and k not in ep]
    if miss:
        sys.exit(f'article_draft.json 缺少: {miss}')
    c = dict(dr)
    c.update({k: v for k, v in ep.items() if v not in (None, '')})  # 人填的优先
    return c


def render(c, base_dir):
    show = shows.load(shows.resolve(c['show'], base_dir))
    tpl_dir = os.path.join(show['_dir'], show.get('template', 'template'))
    frag = lambda n: open(os.path.join(tpl_dir, 'fragments', n + '.html'), encoding='utf-8').read()
    base = open(os.path.join(tpl_dir, 'base.html'), encoding='utf-8').read()

    series_key = c.get('series')
    series = show['series'].get(series_key) if series_key else None
    if series_key and series is None:
        sys.exit(f'节目 {show["name"]} 没有栏目 {series_key}，可选: {list(show["series"])}')
    series = series or {'name': '', 'intro': []}

    for i, ch in enumerate(c['chapters']):
        if not re.fullmatch(r'\d{1,2}:\d{2}(:\d{2})?', ch.get('time', '')):
            sys.exit(f'第 {i+1} 个章节时间格式不对: {ch.get("time")}（应为 mm:ss）')

    intro = ''.join(fill(frag('intro_p'), text=esc(t)) + frag('blank_p') for t in series.get('intro', []) + c['intro'])

    guests = ''
    for g in c['guests']:
        fields = ''.join(fill(frag('guest_field'), label=esc(f['label']), value=esc(f['value'])) for f in g.get('fields', []))
        photo = fill(frag('guest_photo'), photo=image_src(g['photo'], base_dir)) if g.get('photo') else ''
        guests += photo + fill(frag('guest'), name=esc(g['name']), fields=fields)

    chapters = ''.join(fill(frag('chapter'), time=esc(ch['time']), title=esc(ch['title'])) for ch in c['chapters'])

    body = ''
    for sec in c['sections']:
        paras = ''.join(fill(frag('body_p'), text=esc(p)) for p in sec['paragraphs'])
        body += fill(frag('body_section'), heading=esc(sec['heading']), paragraphs=paras)
    if c.get('note'):
        body += fill(frag('body_p'), text=esc(c['note']))

    fmt = dict(show=show['name'], ep=c['ep'], series=series['name'], topic=c['topic'])
    heading = show['heading_format'].format(**fmt) if series['name'] else c['topic']
    title = c.get('article_title') or show['title_format'].format(**fmt)
    if not series['name']:
        title = title.replace('——', '').replace('：：', '：')

    out = base
    if c.get('end_card'):
        out = out.replace('<!--@@ENDCARD@@-->', image_src(c['end_card'], base_dir))
    else:
        print('提示: 没有提供编尾卡片 end_card，结尾留了提示文字', file=sys.stderr)
        out = re.sub(r'<img [^>]*<!--@@ENDCARD@@-->[^>]*>', notice('编尾卡片：在这里插入本期编尾图片，然后删掉这行'), out)
    for k, v in {'AUDIO': notice('在这里插入本期音频，然后删掉这行'), 'EP': esc(c['ep']), 'TITLE': esc(heading),
                 'INTRO': intro, 'HOSTS': esc(c['hosts']), 'GUESTS': guests, 'CHAPTERS': chapters, 'BODY': body}.items():
        out = out.replace(f'<!--@@{k}@@-->', v)
    left = re.findall(r'<!--@@(\w+)@@-->', out)
    if left:
        sys.exit(f'模板里还有未填的占位: {left}')
    return title, out


PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{title}</title>
<style>
  body{{margin:0;background:#eef2f4;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
  .bar{{position:sticky;top:0;z-index:9;background:#1f5f75;color:#fff;padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
  .bar b{{font-size:15px}} .bar span{{font-size:13px;opacity:.85}}
  .bar button{{margin-left:auto;background:#ffca00;color:#1f2d33;border:0;border-radius:6px;padding:9px 16px;font-size:15px;font-weight:600;cursor:pointer}}
  .meta{{max-width:414px;margin:16px auto 0;padding:0 16px;font-size:13px;color:#456}}
  .meta code{{background:#fff;padding:2px 6px;border-radius:4px;user-select:all}}
  .phone{{max-width:414px;margin:12px auto 40px;background:#fff;padding:20px 16px;box-sizing:border-box;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
</style></head><body>
<div class="bar"><b>CutPost 推文预览</b><span>点按钮复制正文 → 公众号编辑器里粘贴（Ctrl+V）</span>
<button id="copy">复制正文</button></div>
<div class="meta">标题（单独复制到标题栏）：<code>{title}</code></div>
<div class="phone"><div id="wx-article">{body}</div></div>
<script>
document.getElementById('copy').onclick = async function () {{
  var el = document.getElementById('wx-article'), btn = this;
  try {{
    await navigator.clipboard.write([new ClipboardItem({{
      'text/html': new Blob([el.innerHTML], {{type: 'text/html'}}),
      'text/plain': new Blob([el.innerText], {{type: 'text/plain'}})
    }})]);
  }} catch (e) {{
    var r = document.createRange(); r.selectNodeContents(el);
    var s = getSelection(); s.removeAllRanges(); s.addRange(r);
    document.execCommand('copy'); s.removeAllRanges();
  }}
  btn.textContent = '已复制 ✓'; setTimeout(function () {{ btn.textContent = '复制正文'; }}, 2000);
}};
</script></body></html>
"""


def run(episode, draft=None, out=None):
    base_dir = os.path.dirname(os.path.abspath(episode))
    draft = draft or os.path.join(base_dir, 'article_draft.json')
    c = load(episode, draft)
    title, body = render(c, base_dir)
    out = out or base_dir
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'article_body.html'), 'w', encoding='utf-8').write(body)
    open(os.path.join(out, 'article.html'), 'w', encoding='utf-8').write(PAGE.format(title=esc(title), body=body))
    print('已生成:', os.path.join(out, 'article.html'))
