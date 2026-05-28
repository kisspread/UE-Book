# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频工具和 MetaSound 扩展资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是 Epic 提供的一套实验性音频工具集，主要围绕 MetaSound 系统提供增强功能。该插件通过 MVVM（Model-View-ViewModel）架构模式为 MetaSound 图形编辑器提供数据绑定和视图模型支持，使得 MetaSound 的自定义节点类型（Pin Type）注册和编辑器行为更加模块化和可扩展。插件还支持 MetaSound 文档模板（Document Template）和字面量视图模型的事务操作，适合需要深度定制 MetaSound 编辑器工作流的音频开发者。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [TechAudioTools](TechAudioTools.md) | Runtime | 基础音频工具模块，提供通用音频工具和视图模型基类 |
| [TechAudioToolsMetaSound](TechAudioToolsMetaSound.md) | Runtime | MetaSound 运行时扩展，提供 MetaSound 字面量视图模型和文档模板功能 |
| [TechAudioToolsMetaSoundEditor](TechAudioToolsMetaSoundEditor.md) | Editor | MetaSound 编辑器扩展，提供自定义 Pin Type 注册和编辑器 UI 行为 |

## 使用场景

- 你需要为 MetaSound 节点图添加自定义输入/输出类型 → 使用 TechAudioToolsMetaSound 的 Pin Type 注册系统
- 你需要在 MetaSound 编辑器中创建自定义视图模型和数据绑定 → 使用 MVVM 架构的视图模型框架
- 你需要创建可复用的 MetaSound 文档模板 → 使用 MetaSound Document Template 功能
- 你需要对 MetaSound 字面量节点进行撤销/重做支持 → 使用事务化的 Literal Viewmodel

## 依赖说明

该插件依赖以下其他插件：

| 依赖插件 | 用途 |
|---|---|
| Metasound | MetaSound 运行时和编辑器基础，必须启用 |
| ModelViewViewModel (MVVM) | 提供 MVVM 架构支持，用于视图模型数据绑定 |

## 模块依赖

各模块除标准 Core/Engine/Slate 依赖外，还需要以下模块：

| 模块 | 用途 |
|---|---|
| MetasoundFrontend | MetaSound 前端数据结构和 API |
| ModelViewViewModel | MVVM 框架核心 |
| TechAudioTools | 基础音频工具（TechAudioToolsMetaSound 依赖） |
| TechAudioToolsMetaSound | MetaSound 运行时扩展（TechAudioToolsMetaSoundEditor 依赖） |
| MetasoundGraphCore | MetaSound 图形核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 Pin 类型注册和 MetaSound 编辑器相关行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退编译错误修复的提交 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 Pin 类型注册和编辑器行为（首次提交） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量视图模型添加撤销/重做事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound 文档模板 |

### 维护评价

- **创建时间**：2025 年 4 月，至今约 1 年
- **活跃程度**：非常活跃，最近一个月内有多次实质性更新
- **状态**：实验性插件（IsBetaVersion=true, IsExperimentalVersion=true），需手动启用
- **风险**：作为实验性插件，API 可能不稳定，未来版本可能有重大变更
- **推荐**：适合需要深度定制 MetaSound 编辑器的高级开发者，不建议在生产环境中依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [TechAudioTools 模块文档](TechAudioTools.md)
- [TechAudioToolsMetaSound 模块文档](TechAudioToolsMetaSound.md)
- [TechAudioToolsMetaSoundEditor 模块文档](TechAudioToolsMetaSoundEditor.md)