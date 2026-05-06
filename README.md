# UE-Book

Unreal Engine 开发者知识库 — 内置插件文档、开源工具收录、引擎更新追踪。

🌐 **[kisspread.github.io/UE-Book](https://kisspread.github.io/UE-Book/)**

## 模块

| 模块 | 说明 |
|------|------|
| 内置插件 | 604 个 UE 插件的使用文档，AI 生成 + 人工校审 |
| 开源库 | 150+ 第三方工具/库收录，[提交收录](https://github.com/kisspread/UE-Book/issues/new?template=library-submission.yml) |
| 最近更新 | 引擎周报（AI 自主分析）+ 月报（翻译自 [UpdateTracker](https://github.com/pafuhana1213/UnrealEngine-UpdateTracker)） |

## 自动化

所有内容通过 GitHub Actions 自动维护：

- **插件文档** — 手动触发 LLM 生成
- **引擎周报** — 每周一自动抓取 `ue5-main` 提交分析
- **引擎月报** — 每周检测上游月报并翻译
- **开源库收录** — 提交 Issue 自动审核写入
- **站点部署** — 以上任一更新后自动构建发布
