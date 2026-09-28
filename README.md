# 孙哥模式 · sun-ge

> 概念可以大，第一步可以小。

一个受孙宇晨公众形象启发的娱乐角色扮演 Skill。保留短句、反问、注意力经济和“孙学”的戏剧感，用来聊天、点评、写文案、做嘴替，也帮你把一个想法落成行动。

这是非官方的虚构演绎，不代表孙宇晨本人；新写的台词不冒充真实语录。

## 快速安装

需要 Git 和 Python 3.9+，无第三方 Python 依赖、无需 API key。以下命令适用于 macOS / Linux；Windows 请使用 Python 3.9+ 的 `py -3` 替代 `python3`。

```bash
git clone https://github.com/Clawborn/sun-ge-skill.git
cd sun-ge-skill
python3 scripts/install.py --agent codex
```

最后一行按你使用的客户端选 **一个**：

| 客户端 | 安装命令 | 默认目标目录 |
| --- | --- | --- |
| Codex | `python3 scripts/install.py --agent codex` | `~/.agents/skills/sun-ge/` |
| Claude Code | `python3 scripts/install.py --agent claude` | `~/.claude/skills/sun-ge/` |
| OpenClaw | `python3 scripts/install.py --agent openclaw` | `~/.openclaw/skills/sun-ge/` |

默认目录依据 [Codex Skills](https://developers.openai.com/codex/skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[OpenClaw Skills](https://docs.openclaw.ai/tools/skills) 文档。客户端自定义配置可能改变加载范围；脚本不会修改客户端配置。

想先看目标路径，追加 `--dry-run`。项目内安装、豆包或其他自定义目录用 `--dest`，参数包含最终的 `sun-ge` 文件夹：

```bash
python3 scripts/install.py --dest /path/to/project/.agents/skills/sun-ge
python3 scripts/install.py --dest /path/to/project/.claude/skills/sun-ge
# 豆包旧版路径示例：先确认你当前版本确实读取此目录
python3 scripts/install.py --dest ~/.doubao/agent_mode/workspace/.user_skills/sun-ge
```

脚本仅复制 `SKILL.md`、`references/`、`agents/`，不安装仓库历史、测试或安装脚本。相同内容重复安装不改文件；目标已有不同内容则停止，避免覆盖手改版本。目标是符号链接也会停止，请通过原来的安装管理器更新。

### 不用脚本也能装

从 GitHub 下载并解压 ZIP，创建客户端 Skill 目录下的 `sun-ge` 文件夹，把仓库根目录的 `SKILL.md`、整个 `references` 和 `agents` 文件夹复制进去。**仓库根目录就是 Skill 源码，没有额外的 `sun-ge/` 子目录。**

最终结构必须是 `<Skill目录>/sun-ge/SKILL.md`，不要套成 `sun-ge/sun-ge-skill-main/SKILL.md`。已有安装先备份，别直接覆盖。

## 确认装好了

安装脚本会对复制结果逐文件做 SHA-256 校验；这只证明文件正确落盘。随后新建客户端会话：

- **Codex**：在 Skill 列表中找到“孙哥模式”，或输入 `$sun-ge 帮我写一句高调但不油腻的开业文案`。
- **Claude Code**：输入 `/sun-ge 帮我写一句高调但不油腻的开业文案`。
- **OpenClaw**：先用 `openclaw skills list` 检查 `sun-ge`，再说“用孙哥模式聊聊我正在做的项目”。

预期首次回应带简短的“孙哥模式 · 娱乐演绎”标记，然后直接完成请求。说“退出角色，正常回答”应停止扮演。

找不到时，检查 `sun-ge/SKILL.md` 是否存在、目录是否在当前客户端的扫描范围、同名 Skill 是否被另一安装位置覆盖，以及是否被客户端禁用。**普通问到孙宇晨、投资或创业，不会强行切换角色。**

## 更新与回退

在本仓库目录执行（把 `codex` 换成你的客户端；自定义安装继续用原来的 `--dest`）：

```bash
git pull --ff-only
python3 scripts/install.py --agent codex --update --dry-run
python3 scripts/install.py --agent codex --update
```

更新替换整个已安装 Skill，包括旧文件和本地修改；先自动将原目录保存为目标旁边的 `sun-ge-backup-<唯一编号>.zip`，并输出路径。备份是 ZIP，避免被扫描成另一个 Skill。保留 ZIP 即可保留旧版及本地修改。

回退时：先把当前 `sun-ge` 移到 Skill 扫描范围外，再将备份解压到原父目录（ZIP 内自带 `sun-ge/`），新建会话重新检查。卸载时同样将这个 `sun-ge` 文件夹移出扫描范围；不要移动或删除整个 skills 目录。

## 六种玩法

| 想做什么 | 可以这样说 |
| --- | --- |
| 骂醒拖延 | “孙哥，我拖了两个月还没发第一条视频，骂醒我，再给我今晚的一步。” |
| 点评热点 | “用孙学视角点评这段新闻，先分清事实和猜测：……” |
| 高调文案 | “孙哥，帮我写开业朋友圈，三版，别编营业额。” |
| 嘴替 | “同事把他的任务推给我，帮我回一句，有锋芒但能当面说。” |
| 创业建议 | “孙哥，我每周只有五小时，怎么验证这个产品有没有人要？” |
| 名场面改编 | “用夸张检讨信的风格，写一段迟到检讨。标明虚构改编。” |

可以随时加“狠一点”“少点梗”“认真分析”“只给一句”。角色风格服从你的任务和格式要求。

## 文件结构与素材状态

```text
sun-ge-skill/
├── SKILL.md                 # 核心行为、六种玩法与按需阅读入口
├── agents/openai.yaml       # Codex 显示名称与默认提示
├── references/              # 风格指南、人物背景、语录和孙学素材
├── scripts/install.py       # 标准库安装器：预览、备份、校验
└── tests/                   # 安装回归测试与人工行为验收用例
```

人物档案、语录和孙学资料保留了旧仓库素材，但**没有逐条核验**。历史数字、职务、争议和引语使用前须查原始出处；无法确认的只作风格灵感。风格指南中的新例句均为原创演绎。

本 Skill 不构成投资等专业建议，不授权自动发帖、私信或交易。敢讲观点，也要能纠正事实。

维护者可运行 `python3 -m unittest discover -s tests -v` 检查安装器，按 [行为验收用例](tests/behavior.md) 检查真实客户端输出。不同模型的角色表现需要实际试用判断。
