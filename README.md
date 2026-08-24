# 399 的 Skills

个人 Skills 集合，用于在多个设备和 Agent 之间统一管理、安装和更新自定义 Skill。

仓库按使用场景分为两个区域：

- `skills/`：日常与通用 Skill，例如个人知识整理、生活内容处理和通用工具能力。
- `work-skills/`：工作 Skill，面向办公文档、会议、周报、项目进展和企业协作场景，和日常 Skill 分开维护。

## 日常与通用 Skill

| Skill | 用途 |
|---|---|
| [`normalize-recipe`](skills/normalize-recipe/) | 将视频总结、图文教程、转录稿或零散烹饪笔记整理为规范的 Obsidian 食谱 |
| [`scrapling`](skills/scrapling/) | 基于 Scrapling 框架的网页抓取能力——支持静态页面、隐身模式（绕过 Cloudflare）、动态 JS 渲染、多页爬虫 |

## 工作 Skill

| Skill | 用途 |
|---|---|
| [`daily-work-assistant`](work-skills/daily-work-assistant/) | 日常办公辅助：以飞书文档为主要事实源，完成文档整理、会议纪要与待办、周报和项目进展汇总、资料检索与来源追溯 |

`daily-work-assistant` 只保存通用工作流、输出规则和文档模板，不保存个人办公文档链接、公司内部资料或账号凭据。具体办公入口和动态事实继续在各自工作目录或飞书中维护，避免把私有资料提交到 Skill 仓库。

## 仓库结构

```text
399-skills/
├── skills/                       # 日常与通用 Skill
│   └── <skill-name>/
└── work-skills/                  # 工作 Skill
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/               # 可选，Agent 配置
        ├── assets/               # 可选，输出模板和静态资源
        ├── scripts/              # 可选，可执行脚本
        └── references/           # 可选，详细规则与参考文档
```

每个 `<分类>/<skill-name>/` 都是可以独立安装的完整 Skill。仓库根目录的本文件负责提供总目录和使用说明；各 Skill 不额外维护 README，其用途、触发场景和运行规则记录在 `SKILL.md` 及其配套资源中。

## 安装

通过支持 GitHub 路径安装的 Skill 安装器，指定仓库和 Skill 路径。

日常 Skill 示例：

```text
仓库：399/399-skills
路径：skills/normalize-recipe
```

工作 Skill 示例：

```text
仓库：399/399-skills
路径：work-skills/daily-work-assistant
```

安装多个 Skill 时，可以一次提供多个独立路径。安装后，工作 Skill 可根据用户当前工作目录中的入口文档定位飞书等动态资料，但不应要求仓库内包含这些私人入口。

## 工作 Skill 维护方式

1. 工作相关 Skill 统一放在 `work-skills/`，不与 `skills/` 下的日常和通用 Skill 混放。
2. 工作 Skill 只沉淀可复用的方法、规则和模板，不提交真实会议内容、工单数据、客户信息、企业文档链接或凭据。
3. 具体项目的文档入口、人员分工和内部约定保留在项目本地目录或企业协作平台中。
4. 修改工作 Skill 后，先做静态安全检查和结构验证，再提交到仓库并同步到本地安装目录。
5. `daily-work-assistant` 的后续实际使用反馈，优先修改 `work-skills/daily-work-assistant/`，再同步已安装版本。

## 通用管理约定

1. 把本仓库作为 Skill 的版本来源；本地安装副本用于运行，不作为长期维护源。
2. 一个 Skill 使用一个独立目录，目录名与 `SKILL.md` 中的 `name` 一致。
3. 新增、删除或移动 Skill 后同步更新本 README 的对应目录表。
4. 不在 Skill 目录中添加与运行无关的 README、更新日志或安装指南。
5. 使用 Git 提交记录变更；需要固定版本时使用 Git 标签。
6. 更新仓库后，将相应 Skill 重新同步或安装到各设备。
