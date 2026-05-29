# Sound Cue Templates

> Collection of SoundCue Templates, which provide rapid design of common audio design workflows.

| 属性 | 值 |
|---|---|
| 中文名 | 音效模板 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、SoundCue 模板） |
| 模块 | `SoundCueTemplates` (Runtime), `SoundCueTemplatesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-07-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates) | |

## 用途

SoundCueTemplates 插件为音频设计师提供一套**可复用的 SoundCue 模板框架**。它解决的核心问题是：制作常见的音频设计模式（如随机播放、混合、淡入淡出等）时，需要从零开始搭建 SoundCue 图表，重复劳动多且容易出错。

通过模板机制，设计师可以从内容浏览器右键菜单直接创建预置好的 SoundCue 模板，快速获得一个可工作的基础结构，然后在此基础上调整参数。

## 使用场景

- 你需要快速创建一组随机音效变体（如脚步声、枪声）→ 使用随机模板
- 你想从内容浏览器右键直接生成常见音效结构 → 使用编辑器集成的模板创建流程
- 你希望团队内部统一音频设计规范 → 基于此框架自定义团队专属模板

## 模块列表

| 模块 | 类型 | 职责 |
|---|---|---|
| `SoundCueTemplates` | Runtime | 提供 SoundCue 模板基类和默认模板实现 |
| `SoundCueTemplatesEditor` | Editor | 内容浏览器右键菜单集成、模板创建流程 |

## 蓝图用法

本插件的模板在蓝图/编辑器中使用，通过内容浏览器右键菜单创建。

### 核心节点

模板创建主要通过编辑器 UI 完成，不暴露蓝图节点。SoundCue 模板创建后作为普通 SoundCue 资产使用。

## C++ 用法

### 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频创建菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 日志宏迁移至新格式 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 添加内联生成宏优化编译 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions | 优化右键音频操作的交互细节 |
| 2025-05-19 | `a60b2b5c` | Fixup API macros for merged modules, PURE_VIRTUAL does not need API export | 修复模块合并后的 API 导出宏问题 |

### 维护评价

**活跃维护** ✅

该插件虽然创建于 2019 年，但近期（2025-2026）仍有持续更新，主要集中在：
- 编辑器集成优化（右键菜单、内容浏览器音频菜单）
- 代码质量改进（日志宏迁移、编译优化）

⚠️ 注意：`.uplugin` 标记为 `IsBetaVersion: true` 且 `Installed: false`，表明此插件仍处于实验阶段，需要手动启用，API 可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundCueTemplates)
- [SoundCueTemplates 模块文档](SoundCueTemplates.md)
- [SoundCueTemplatesEditor 模块文档](SoundCueTemplatesEditor.md)