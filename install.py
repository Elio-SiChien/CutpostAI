"""把 CutPost AI 装成全局 skill（由 AI 工具在用户说“安装/更新 cutpost”时运行）。

复制到:
    ~/.claude/skills/cutpost   Claude Code
    ~/.agents/skills/cutpost   Codex
只复制文件，不安装任何依赖。已登记的节目在 ~/.cutpost/，不受影响。
"""
import os, shutil

SRC = os.path.dirname(os.path.abspath(__file__))
SKIP = shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'article.html', 'article_body.html', '.env')
home = os.path.expanduser('~')
for d in ['.claude', '.agents']:
    dst = os.path.join(home, d, 'skills', 'cutpost')
    if os.path.abspath(dst) == SRC:
        continue
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst, ignore=SKIP)
    print('已安装:', dst)
print('完成。Claude Code 里输入 /cutpost，Codex 里输入 $cutpost，或者直接说“用 cutpost 做这期推文”。')
