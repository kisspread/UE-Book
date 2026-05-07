# UE-Book

Unreal Engine 开发者知识库 — 内置插件文档、开源工具收录、引擎更新追踪。

🌐 **[kisspread.github.io/UE-Book](https://kisspread.github.io/UE-Book/)**

## 模块

| 模块 | 说明 |
|------|------|
| 内置插件 | 800+  UE 插件的使用文档，AI 生成 + 人工校审 |
| 开源库 | 150+ 第三方工具/库收录，[提交收录](https://github.com/kisspread/UE-Book/issues/new?template=library-submission.yml) |
| 最近更新 | 引擎周报（AI 自主分析）+ 月报（翻译自 [UpdateTracker](https://github.com/pafuhana1213/UnrealEngine-UpdateTracker)） |

## 🤖 AI Agent 搜索

UE-Book 内置了搜索索引，**AI Agent（Claude Code、Hermes、Codex 等）可以一句话安装**，直接在对话中查询 UE 知识库：

> 帮我安装 UE-Book 搜索：https://raw.githubusercontent.com/kisspread/UE-Book/master/install.md

安装后，Agent 能搜索 870+ 插件文档、引擎更新周报/月报、155+ 开源库，并自动深入阅读原文。

### 效果演示

```
用户：我想要让 AI 帮我操作 Niagara，引擎有提供接口吗？

Agent：搜索 "AI Niagara 操作 接口" →
  命中 NiagaraToolsets ─ "A collection of tool calls allowing
  an AI assistant the ability to interact with Niagara."
  ★ Epic 2026年4月刚加的，5.8 Experimental

  命中 ExampleCustomDataInterface ─ 官方自定义数据接口示例
  命中 NiagaraInsights ─ 性能调试洞察

Agent：深入阅读 raw markdown → 整合回答 →
  有的，引擎有专门接口：NiagaraToolsets。它提供构造蓝图包装器、
  读写用户变量、资产发现等 Tool Call，AI 可直接调用操作 Niagara。
```

## 自动化

所有内容通过 GitHub Actions 自动维护：

- **插件文档** — 手动触发 LLM 生成
- **引擎周报** — 每周一自动抓取 `ue5-main` 提交分析
- **引擎月报** — 每周检测上游月报并翻译
- **开源库收录** — 提交 Issue 自动审核写入
- **站点部署** — 以上任一更新后自动构建发布
- **搜索索引** — 部署时自动生成，Agent 下载即用
