"""CutPost 脚本入口（AI 工具调用，用户不需要手敲）。

    new <本期文件夹>                    开新一期（逐项问期号、栏目、嘉宾…）
    article <本期文件夹或episode.json>   生成公众号推文
    show add <名字> <节目配置文件夹>     登记一个节目
    show list                           列出已登记的节目
    where                               打印项目路径（给 AI 工具找提示词和文档）
"""
import argparse, os, sys

from . import shows, article, new, __version__

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # skill 根目录


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(prog='cutpost', description='CutPost AI：AI 剪播客 + 自动出公众号推文')
    ap.add_argument('--version', action='version', version=__version__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('new', help='开新一期，生成 episode.json')
    p.add_argument('folder')

    p = sub.add_parser('article', help='生成公众号推文 article.html')
    p.add_argument('episode', help='本期文件夹，或 episode.json 路径')
    p.add_argument('--draft', help='article_draft.json（默认在本期文件夹里）')
    p.add_argument('-o', '--out', help='输出文件夹（默认本期文件夹）')

    p = sub.add_parser('show', help='管理节目配置')
    ss = p.add_subparsers(dest='action', required=True)
    a = ss.add_parser('add'); a.add_argument('name'); a.add_argument('folder')
    ss.add_parser('list')

    sub.add_parser('where', help='打印项目路径')

    a = ap.parse_args(argv)
    if a.cmd == 'new':
        new.run(a.folder)
    elif a.cmd == 'article':
        ep = a.episode
        if os.path.isdir(ep):
            ep = os.path.join(ep, 'episode.json')
        article.run(ep, a.draft, a.out)
    elif a.cmd == 'show':
        if a.action == 'add':
            shows.add_show(a.name, a.folder)
        else:
            for k, v in shows.list_shows().items():
                print(f'{k}\t{v}')
    elif a.cmd == 'where':
        print(f'项目: {ROOT}\n文档: {os.path.join(ROOT, "docs")}\n提示词: {os.path.join(ROOT, "prompts")}\n配置: {shows.CONFIG}')


if __name__ == '__main__':
    main()
