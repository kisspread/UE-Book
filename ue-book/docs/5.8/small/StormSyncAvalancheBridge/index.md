# Storm Sync Motion Design Bridge

> Plugin bridge between Motion Design Plugin and Storm Sync to provide in-editor integration to synchronize assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计同步桥接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StormSyncAvaBridge` (Runtime), `StormSyncAvaBridgeEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge) | |

## 用途
此插件作为 **Motion Design**（动态设计，又称 Avalanche）插件与 **Storm Sync** 插件之间的桥梁。其核心目的是在虚幻编辑器中为使用 Motion Design 工作流的用户，提供与 Storm Sync 资产同步系统的集成能力。它允许用户在 Motion Design 的编辑器界面中直接进行资产的同步操作，简化了在虚拟制片和动态图形内容创建过程中管理大量素材资产的流程。

## 使用场景
- 当你在使用 **Motion Design** 插件进行虚拟制片的动态图形、LED 墙视觉效果或实时视觉内容创作时。
- 你同时启用了 **Storm Sync** 插件来管理跨项目或团队的资产版本与同步。
- 你希望在一个统一的编辑器界面（Motion Design 面板）内，快速触发资产的检查、同步或更新操作，而无需切换窗口或使用命令行工具。

## 蓝图用法
此插件主要提供编辑器集成与工具，其 API 主要服务于 C++ 模块间的交互。在蓝图中直接调用的函数较少，核心功能通过编辑器工具和按钮暴露。

### 核心节点
本插件未发现直接暴露给蓝图的核心功能节点。其功能通常通过编辑器 UI（如 Motion Design 面板中的按钮）触发，或由其他系统（如 Storm Sync）在底层调用。

## C++ 用法
详细 API 请参阅各模块文档：[StormSyncAvaBridge](StormSyncAvaBridge.md), [StormSyncAvaBridgeEditor](StormSyncAvaBridgeEditor.md)。

## 模块依赖
从 Build.cs 分析，此插件无特殊、不常见的模块依赖。它依赖于 Motion Design (Avalanche) 和 Storm Sync 插件提供的核心接口。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 适配引擎日志宏更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次代码清理的错误。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一个引起问题的提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 适配核心委托接口变更，修复注册问题。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | Motion Design 插件摘除测试版标签，标志其稳定性。 |

### 维护评价
此插件自 **2025年5月** 创建，作为 Motion Design 插件套件的一部分。近期（2026年4月）仍有更新，主要用于适配引擎内部接口变更（如日志宏和核心委托），表明它仍在跟随引擎主线进行维护，但并非功能性的重大更新。考虑到其创建时间和最近一次实质性功能更新（移除Beta标签）的时间，它处于**维护中**状态，但更新频率不高。作为 Motion Design 工作流的一个特定集成件，只要主插件 (Motion Design, Storm Sync) 活跃，它就有其存在价值。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSyncAvalancheBridge)
- [官方文档]() （暂无）
- [模块文档：StormSyncAvaBridge](StormSyncAvaBridge.md)
- [模块文档：StormSyncAvaBridgeEditor](StormSyncAvaBridgeEditor.md)