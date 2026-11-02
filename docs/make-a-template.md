# 给自己的节目做推文模板

推文模板 = 一个“节目配置文件夹”：

```
my-show/
├── show.json          节目名、栏目、标题格式
└── template/
    ├── base.html      整篇推文的固定部分 + 占位标记
    └── fragments/     会重复的小块
```

## base.html 里的占位标记
| 标记 | 替换成 |
|---|---|
| `<!--@@AUDIO@@-->` | 「在这里插入音频」提示 |
| `<!--@@EP@@-->` | 期号数字 |
| `<!--@@TITLE@@-->` | 「栏目——主题」（格式见 show.json 的 heading_format） |
| `<!--@@INTRO@@-->` | 栏目固定导语 + 本期导语 |
| `<!--@@HOSTS@@-->` | 主持人 |
| `<!--@@GUESTS@@-->` | 嘉宾卡片（每位：guest_photo + guest） |
| `<!--@@CHAPTERS@@-->` | 章节时间轴 |
| `<!--@@BODY@@-->` | 文字版正文 |
| `<!--@@ENDCARD@@-->` | 写在某个 `<img src="…">` 里，替换成编尾卡片图片 |

## fragments/
| 文件 | 可用占位 |
|---|---|
| `intro_p.html` | `{text}` |
| `blank_p.html` | 空行 |
| `guest_photo.html` | `{photo}` |
| `guest.html` | `{name}` `{fields}` |
| `guest_field.html` | `{label}` `{value}` |
| `chapter.html` | `{time}` `{title}` |
| `body_section.html` | `{heading}` `{paragraphs}` |
| `body_p.html` | `{text}` |

可以照 `shows/hydro90/`（真实节目，秀米风格）或 `shows/demo/`（最简模板）改。

## 从已发布的推文生成模板
最省事的办法：用浏览器插件 SingleFile 保存一篇已发布的推文，交给 AI（在 Claude Code / Codex 里 @ 这个文件并说）：
「按 docs/make-a-template.md，把这篇推文做成节目模板」。AI 找到正文（`id="js_content"`），
把图片地址换回 `data-src` 里的微信图床地址，把每期会变的地方换成上面的标记和片段。
所有样式必须写在标签的 `style` 里（公众号会去掉 `<style>` 和 class）。

做好后对 AI 说「把这个文件夹登记成我的节目」即可（内部执行 `scripts/run.py show add <名字> <文件夹>`）。
