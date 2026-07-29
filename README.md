# 399 的 Skills

个人 Codex Skills 集合，用于在多个设备和 Agent 之间统一管理、安装和更新自定义 Skill。

## Skill 目录

| Skill | 用途 |
|---|---|
| [`normalize-recipe`](skills/normalize-recipe/) | 将视频总结、图文教程、转录稿或零散烹饪笔记整理为规范的 Obsidian 食谱 |

## 仓库结构

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── references/
```

每个 `skills/<skill-name>/` 都是可以独立安装的完整 Skill。仓库根目录的本文件负责提供总目录和使用说明；各 Skill 不额外维护 README，其用途、触发场景和运行规则分别记录在 `SKILL.md` 与 `agents/openai.yaml` 中。

## 安装

通过 Codex 的 `skill-installer` 从 GitHub 安装指定目录：

```text
仓库：399/399-skills
路径：skills/normalize-recipe
```

安装多个 Skill 时，可以一次提供多个 `skills/<skill-name>` 路径。

## 管理约定

1. 只在本仓库中编辑 Skill，并把仓库作为唯一来源。
2. 一个 Skill 使用一个独立目录，目录名与 `SKILL.md` 中的 `name` 一致。
3. 新增 Skill 后更新上方目录表。
4. 不在 Skill 目录中添加与运行无关的 README、更新日志或安装指南。
5. 使用 Git 提交记录变更；需要固定版本时使用 Git 标签。
6. 更新仓库后，将相应 Skill 重新同步或安装到各设备。
