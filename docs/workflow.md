# 工作流（人和 AI 工具共用）

这份是给 AI 看的详细流程（用户只需要说话）。Claude Code、Codex 都按同一份流程操作。
步骤之间只通过文件交接。下文 `cutpost` = `python <SKILL_DIR>/scripts/run.py`，SKILL_DIR 是本 skill 所在文件夹。

## 第 0 步：开新一期 —— 先问用户
向用户逐项确认，**不要自己推断，期号只能由用户给**：节目、期号、栏目、主持人、嘉宾（姓名/介绍/照片）、编尾卡片、原始音频。

在对话里问完，按 `schemas/episode.example.json` 写 `<本期文件夹>/episode.json`。
（不用 AI 时，人也可以运行 `cutpost new <本期文件夹>` 逐项回答。）

## 第 1 步：剪辑（开发中）
转录 → 粗剪 → 精剪 → 出片 v1。产物：`audio_v1.*`、`transcript_v1.md`（时间戳对齐 v1）、`chapters_v1.txt`。

## 第 2 步：审核改版（开发中）
审核意见写进 `feedback_v1.md` → 生成 v2 和 `changelog_v2.md`（修改对照表）。
每一版都从“原始音频 + 剪辑决策表”重新剪，不在剪过的音频上二次剪，可追溯、可回滚。

## 第 3 步：公众号推文
1. 按 `prompts/article_draft.md` 写 `<本期文件夹>/article_draft.json`
2. `cutpost article <本期文件夹>`
3. 浏览器打开 `article.html` → 「复制正文」→ 公众号编辑器粘贴；标题单独复制
4. 在红字提示处插入本期音频、编尾卡片，删掉提示

音频改版后时间轴变了：更新 `chapters` 和受影响的段落，重新运行第 2 条即可。

## 约定
- 不安装新依赖：核心命令只用 Python 标准库（有 Pillow 会自动压缩图片，没有也能用）。
- `.env` 密钥、嘉宾照片、音频、文字稿不提交到 git。
- 修改意见默认只影响本期；用户明确说“以后都这样”才改节目配置。
