# MetaHumanRuntime

> Deprecated plugin now redirected to MetaHumanSDK

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 运行时（已废弃） |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯重定向插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime) | |

## 用途

**此插件已废弃，请勿使用。**

MetaHumanRuntime 曾是 MetaHuman 角色的运行时组件插件，用于在 UE 中驱动 MetaHuman 的动画和控制。在 2024 年 8 月，其全部功能已迁移至 `MetaHumanSDK` 插件（重命名为 `MetaHumanSDKRuntime`）。当前版本仅保留 `.uplugin` 文件作为重定向入口，实际依赖 `MetaHumanSDK` 插件。

**存在意义**：为仍引用 `MetaHumanRuntime` 的旧项目提供向后兼容——启用该插件会自动加载 `MetaHumanSDK`，避免 "missing dependency" 错误。

## 使用场景

**不应在新项目中使用此插件。** 仅适用于：

- 从旧版本 UE 升级的项目中存在对 `MetaHumanRuntime` 的硬依赖，短期内无法移除

**正确做法**：直接使用 `MetaHumanSDK` 插件。

## 蓝图用法

无。该插件不包含任何模块、蓝图函数或资产。

## C++ 用法

无。该插件不包含任何源文件或模块。

### 头文件引入

不适用。

### 基本用法

不适用。如需 MetaHuman 运行时功能，请使用 `MetaHumanSDK`：

```cpp
// 使用 MetaHumanSDK 代替
#include "MetaHumanSDKRuntime.h"
```

## Demo 示例

不适用。此插件无任何代码或资产可供演示。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` | 实际功能插件，本插件仅作为重定向依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-16 | `62f8cc0c` | Unable to load plugin, missing dependency MetaHumanRuntime | 修复依赖缺失问题，添加重定向机制 |
| 2024-08-19 | `79003ad1` | Move MetaHumanRuntime plugin to MetaHumanSDK plugin and rename it to MetaHumanSDKRuntime | 功能迁移至 MetaHumanSDK，本插件变为废弃壳 |
| 2024-08-08 | `ea519b5c` | [MH-12702] Unreal Editor crashes after Playing a Level with an Optimized MetaHuman with MetaHuman Co | 修复带优化 MetaHuman 时编辑器崩溃问题 |
| 2024-07-31 | `8e8004fd` | MetaHuman component for UE improvements | MetaHuman 组件在 UE 中的改进 |
| 2024-07-24 | `bd22b183` | Fixed issue for control rigs not running on body parts | 修复控制绑定在身体部位不运行的问题 |

### 维护评价

**⚠️ 已废弃 — 不推荐使用。**

- **生命周期极短**：从 2024-06-10 创建到 2024-08-19 被废弃，仅存活约 2 个月
- **已正式迁移**：全部功能已移至 `MetaHumanSDK`，本插件仅保留兼容性重定向
- **无源码残留**：当前版本包含 0 个源文件、0 个模块
- **实验性状态**：标记为 `IsExperimentalVersion`，从未达到正式发布
- **最后一次改动**（2024-09-16）仅为修复依赖加载问题，非功能性更新

建议直接使用 `MetaHumanSDK` 插件，并在迁移完成后从项目依赖中移除 `MetaHumanRuntime`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime)
- [MetaHumanSDK（替代插件）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanSDK)
- 官方文档：无
- 测试用例：无