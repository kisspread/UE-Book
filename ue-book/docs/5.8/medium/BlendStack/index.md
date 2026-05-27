# Blend Stack

> Blend Stack API（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混合栈 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlendStack` (Runtime), `BlendStackEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack) | |

## 用途

BlendStack 提供一套栈式动画混合 API，用于在动画图中按栈结构管理多个动画层的混合逻辑。该插件最初位于 Experimental 目录，后迁移至 Animation 分类，与 PoseSearch 动画搜索系统配合使用，支持运动匹配（Motion Matching）场景下的多层动画叠加与同步。

核心设计思路是将动画混合操作组织为栈结构，每一层可以独立控制混合权重、同步组等参数，简化复杂角色动画的状态切换与过渡逻辑。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [BlendStack](BlendStack.md) | Runtime | 核心混合栈动画节点与运行时逻辑 |
| [BlendStackEditor](BlendStackEditor.md) | UncookedOnly | 编辑器工具，提供混合栈节点的编辑器支持 |

## 使用场景

- 你在使用 Motion Matching / PoseSearch 需要多层动画结果混合叠加 → 用 BlendStack
- 你需要在 AnimGraph 中实现栈式动画层管理（类似动画状态机但更灵活）→ 用 BlendStack
- 你需要为多个 BlendStack 节点设置同步组（Sync Group）保持动画节奏一致 → 用 BlendStack
- 你是内容创作者，只需蓝图动画图，无需 C++ 开发 → 可能不需要此插件（需编程接入）

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏迁移至 UE_LOGF 格式 |
| 2026-01-27 | `62ce2078` | BlendStack - logging errors in FAnimNode_BlendStack_Standalone::InternalBlendTo if inconsistent an E | 修复内部混合时配置不一致的错误日志 |
| 2026-01-22 | `1d9e2356` | BlendStack - sync group support for follower blendstacks | 新增跟随者 BlendStack 的同步组支持 |
| 2026-01-09 | `520bb55e` | PoseSearch - fix for misspelled words | 修正拼写错误 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名以遵循最新规范 |

### 维护评价

**活跃维护**。插件创建于 2024 年初，从 Experimental 迁移至正式 Animation 目录，表明已通过审核。最近 3 个月内持续有功能性更新（同步组支持、错误处理改进），说明仍在积极开发中。25 个源文件属于中等规模，代码量可控。

⚠️ **注意**：该插件 `EnabledByDefault=false`，需要手动在项目设置中启用，或在 .uproject 中添加插件声明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/BlendStack)
- [官方文档]()（无）