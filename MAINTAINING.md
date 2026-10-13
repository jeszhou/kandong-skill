# 维护说明

- 写作规则只改 `references/中文写作规则.md` 一处。SKILL.md 只指向它，不复述。
- 页面结构只改 `assets/page-template.html`；样式每次现做，模板里的 CSS 只是起点。改了区块 id，同步改 `scripts/check_page.py` 的 `REQUIRED` 和 `PLACEHOLDERS`。
- 改完跑：`python3 scripts/check_page.py examples/乾卦六爻/page.html`，应输出 OK。
- 规则改编自 danyuchn/asd-ste100-skill（MIT），保留 LICENSE 里的原作者署名。
- `README.md` 是给人看的介绍。改了触发方式、安装方法或文件结构，同步改 README。改了样例页面，重截 `docs/screenshot.png`。
- 主副本在 `~/.claude/skills/kandong`（git 仓库），改完同步到 `~/.codex/skills` 和 `~/.agents/skills`。
