"""Hydro90 专用：从已发布的公众号推文（SingleFile 保存的 .htm）抽取推文模板。

依赖秀米版式的具体结构（第几个区块是嘉宾、章节…），换成别的节目需要按 podcast-autopilot/docs/make-a-template.md 另做。

用法:
    python tools/extract_wechat_template.py <published.htm> <out_dir>

输出:
    <out_dir>/base.html           固定部分 + 占位标记 <!--@@NAME@@-->
    <out_dir>/fragments/*.html    可重复单元（嘉宾卡片、章节行、正文段落…），含 {name} 占位
只依赖 beautifulsoup4 + lxml（仅开发者重新抽模板时需要；日常生成推文不需要）。
"""
import re, sys, os
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, 'fragments'), exist_ok=True)
s = open(src, encoding='utf-8', errors='ignore').read()
soup = BeautifulSoup(s, 'lxml')
root = soup.find(id='js_content')

# 1) 图片：SingleFile 把 src 换成了 data URI，还原成微信 CDN 原地址，并去掉统计用属性
for img in root.find_all('img'):
    url = img.get('data-src')
    for k in list(img.attrs):
        if k not in ('style', 'alt'):
            del img[k]
    img['src'] = url
    img['style'] = 'vertical-align:middle;max-width:100%;width:100%;box-sizing:border-box;height:auto'

def marker(name):
    return soup.new_string(f'@@{name}@@')

def leaf(node, text):
    return node.find(lambda t: t.name == 'span' and t.has_attr('leaf') and t.get_text() == text)

# 2) 音频卡片 → 占位
audio = root.find('mp-common-mpaudio')
audio.replace_with(marker('AUDIO'))

# 3) 本期内容 容器
cont = None
for sec in root.find_all('section'):
    kids = [k for k in sec.children if getattr(k, 'name', None)]
    if len(kids) >= 20 and re.sub(r'\s+', '', kids[0].get_text()).startswith('#EP'):
        cont = sec
kids = [k for k in cont.children if getattr(k, 'name', None)]

# 期号 + 标题
ep_leaf = kids[0].find(lambda t: t.name == 'span' and t.has_attr('leaf') and re.fullmatch(r'P\d+', t.get_text() or ''))
ep_leaf.string = 'P@@EP@@'
title_leaf = kids[0].find(lambda t: t.name == 'span' and t.has_attr('leaf') and '——' in t.get_text())
title_leaf.string = '@@TITLE@@'

# 导语：保留外层，内容换成占位
intro_inner = kids[2].find('section')
intro_p_style = intro_inner.find('p')['style']
intro_inner.clear(); intro_inner.append(marker('INTRO'))

# 主持
hosts_leaf = leaf(kids[4], kids[4].find_all('span', attrs={'leaf': True})[-1].get_text())
hosts_leaf.string = '@@HOSTS@@'

# 嘉宾：kids[7]=照片 kids[8]=文字 kids[9]=空行 → 原型；删除 7..13
photo = str(kids[7])
photo = re.sub(r'src="[^"]+"', 'src="{photo}"', photo)
txt = kids[8]
name_leaf = [l for l in txt.find_all('span', attrs={'leaf': True}) if l.get_text().strip()][0]
name_leaf.string = '{name}'
field_ps = [p for p in txt.find_all('p') if p.find('strong') and p.find('strong').get_text() != '{name}' and '{name}' not in p.get_text()]
field_proto = str(field_ps[0])
field_proto = field_proto.replace(field_ps[0].find('strong').find('span').get_text(), '{label}', 1)
val = field_ps[0].find_all('span', attrs={'leaf': True})[-1].get_text()
field_proto = field_proto.replace(val, '：{value}', 1)
first = field_ps[0]
for p in field_ps[1:]:
    p.decompose()
first.replace_with(marker('FIELDS'))
open(os.path.join(out, 'fragments', 'guest_photo.html'), 'w', encoding='utf-8').write(photo)
guest_proto = str(txt) + str(kids[9])
open(os.path.join(out, 'fragments', 'guest.html'), 'w', encoding='utf-8').write(guest_proto.replace('@@FIELDS@@', '{fields}'))
open(os.path.join(out, 'fragments', 'guest_field.html'), 'w', encoding='utf-8').write(field_proto)
for k in kids[8:14]:
    k.decompose()
kids[7].replace_with(marker('GUESTS'))

# 章节：kids[17] 原型（时间点链接改为纯文本：粘贴后链接会失效，可在编辑器里用“插入时间点”重做）
ch = kids[17]
a = ch.find('a'); a.replace_with(soup.new_string('{time}'))
tl = [l for l in ch.find_all('span', attrs={'leaf': True}) if l.get_text().strip() and l.get_text() != '{time}'][-1]
tl.string = '{title}'
open(os.path.join(out, 'fragments', 'chapter.html'), 'w', encoding='utf-8').write(str(ch))
for k in kids[18:21]:
    k.decompose()
ch.replace_with(marker('CHAPTERS'))

# 正文（文字纯享版）：kids[27..] 全部替换
for k in kids[28:]:
    k.decompose()
kids[27].replace_with(marker('BODY'))

html = str(root)
html = re.sub(r'@@(\w+)@@', r'<!--@@\1@@-->', html)
html = re.sub(r'#imgIndex=\d+', '', html)
# 标题列：原稿是 flex:0 0 auto + inline-block，长标题会撑出版面 → 允许收缩、整行换行
j = html.find('<!--@@TITLE@@-->')
k = html.rfind('flex:0 0 auto', 0, j)
html = html[:k] + 'flex:1 1 0%' + html[k + len('flex:0 0 auto'):]
seg_start = html.rfind('<p ', 0, j)
seg = html[seg_start:j].replace('display:inline-block;text-indent:initial', 'display:inline;text-indent:initial').replace('text-align:center', 'text-align:left')
html = html[:seg_start] + seg + html[j:]
# 编尾卡片（结尾主持人信息图）每期更换：倒数第二张图
imgs = list(re.finditer(r'<img [^>]*>', html))
end = imgs[-2]
html = html[:end.start()] + re.sub(r'src="[^"]+"', 'src="<!--@@ENDCARD@@-->"', end.group(0)) + html[end.end():]
html = html.replace('P<!--@@EP@@-->', 'P<!--@@EP@@-->')
open(os.path.join(out, 'base.html'), 'w', encoding='utf-8').write(html)

# 导语段落 / 正文 的原型（与原推文同样的内联样式，结构改为合法 HTML）
open(os.path.join(out, 'fragments', 'intro_p.html'), 'w', encoding='utf-8').write(
    f'<p style="{intro_p_style}"><span leaf="">{{text}}</span></p>')
open(os.path.join(out, 'fragments', 'blank_p.html'), 'w', encoding='utf-8').write(
    f'<p style="{intro_p_style}"><span leaf=""><br/></span></p>')
open(os.path.join(out, 'fragments', 'body_section.html'), 'w', encoding='utf-8').write(
    '<section style="margin:0px;padding:0px;box-sizing:border-box">'
    '<p style="margin:0px;padding:0px;box-sizing:border-box"><strong style="box-sizing:border-box"><span leaf="">{heading}</span></strong></p>'
    '<section style="text-align:justify;box-sizing:border-box">'
    '<p style="white-space:normal;margin:0px;padding:0px;box-sizing:border-box"><span leaf=""><br/></span></p>'
    '{paragraphs}</section></section>')
open(os.path.join(out, 'fragments', 'body_p.html'), 'w', encoding='utf-8').write(
    '<p style="white-space:normal;margin:0px;padding:0px;box-sizing:border-box"><span leaf="">{text}</span></p>'
    '<p style="white-space:normal;margin:0px;padding:0px;box-sizing:border-box"><span leaf=""><br/></span></p>')
print('ok', len(html), 'markers:', re.findall(r'<!--@@(\w+)@@-->', html))
