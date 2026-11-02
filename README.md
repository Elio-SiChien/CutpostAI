# ✂️ CutPost AI

**AI 剪播客 + 自动出公众号推文。** 录完节目，把音频和嘉宾信息交给 AI：剪好的音频、给嘉宾审核的文字稿、可以直接粘贴进微信公众号的推文，一次出齐。

CutPost 是一个技能包（skill），在 Claude Code 和 Codex 里都能用。你只需要说话，不用敲命令。

## 能做什么
- 🎙 **AI 剪播客**：转录、去口癖、删冗余，出第一版（开发中）
- 🔁 **按审核意见改版**：嘉宾写“12:30 那段删掉”，AI 出新版本和修改对照表；每版都从原始音频重剪，可追溯、可回滚（开发中）
- 📰 **自动出推文**：用你已发布的推文当模板，每期自动填嘉宾卡片、章节时间轴、文字版；复制粘贴进公众号，不用再开秀米 ✅
- 🗂 **多节目、多栏目**：一个节目一套模板，一个节目多个栏目

## 安装
把这个文件夹交给 Claude Code 或 Codex，说一句：

> 安装这个 skill：`<CutPost 文件夹路径>`

装好就能用。自带示范节目 **Hydro90会客室**（`shows/hydro90`），不用任何配置就能生成它的推文。

## 使用
在 Claude Code 或 Codex 里：

| 你说 | CutPost 做 |
|---|---|
| `/cutpost` 新一期（Codex 里用 `$cutpost`） | 问你期号、栏目、嘉宾、照片、编尾卡片 |
| 用 cutpost 做这期的公众号推文 | 根据文字稿写推文，生成 `article.html` |
| 用 cutpost 生成 hydro90 的示例推文 | 试用示范节目 |
| 把这个文件夹登记成我的节目 | 登记你自己的节目模板 |
| 更新 cutpost | 重新安装最新版 |

生成后打开 `article.html` → 点「复制正文」→ 粘贴进公众号编辑器。

## 做自己的节目
照着示范节目 [shows/hydro90](shows/hydro90/README.md) 改：复制文件夹 → 改 `show.json` 的节目名和栏目 → 让 AI 用你已发布的一篇推文生成模板。
详细说明见 [docs/make-a-template.md](docs/make-a-template.md)；`shows/demo` 是最简模板。

## 目录
| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能说明（AI 读这个） |
| `shows/hydro90/` | 示范节目：Hydro90会客室（模板、三个栏目、示例期） |
| `shows/demo/` | 最简模板 |
| `scripts/` | 脚本（只用 Python 标准库） |
| `prompts/` | 需要 AI 完成的步骤的提示词 |
| `docs/` | 详细流程、做模板 |

## 致谢
剪辑部分将基于 [podcastcut-skills-oss](https://github.com/luoyuweidu1/podcastcut-skills-oss)（MIT）的剪辑脚本。

## License
MIT
