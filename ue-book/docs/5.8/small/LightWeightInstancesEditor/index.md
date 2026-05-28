# Light Weight Instances Editor (DEPRECATED)

> Light Weight Instances provide the flexibility and interaction of actors while having performance similar to instanced meshes. This plugin is now DEPRECATED. Use InstancedActors for similar functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 轻量实例编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器菜单扩展） |
| 模块 | `LightWeightInstancesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-06-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/LightWeightInstancesEditor) | |

## 用途

⚠️ **此插件已废弃（DEPRECATED），请使用 `InstancedActors` 插件替代。**

本插件为"轻量实例（Light Weight Instances）"提供编辑器端支持。轻量实例的核心理念是：将普通 Actor 转换为类似实例化静态网格体（Instanced Static Mesh）的轻量表示，从而在保持 Actor 交互能力的同时获得接近实例化渲染的性能。

具体来说，本插件在编辑器的关卡视口右键菜单中添加了"转换为轻量实例"的选项，允许开发者批量将选中的同类 Actor 转换为 Light Weight Instances。它本身不包含轻量实例的运行时逻辑，仅提供编辑器工作流支持。

## 使用场景

⚠️ 以下场景请使用 `InstancedActors` 替代：

- 场景中有大量相同类型的 Actor（如树木、石头、路灯），需要提升性能但仍需保留交互能力 → ~~用 LightWeightInstancesEditor~~ → 用 **InstancedActors**
- 需要批量将现有 Actor 转换为实例化表示 → 用 **InstancedActors**

## 蓝图用法

本插件不暴露任何蓝图节点。其功能完全通过编辑器扩展菜单实现：

### 核心功能

在关卡视口中选中多个同类 Actor → 右键 → 选择转换选项 → 自动转换为 Light Weight Instances。

> ⚠️ 所有选中的 Actor 必须是同一类型，否则转换不会执行。

## C++ 用法

本插件的 API 极为简单，仅提供编辑器模块入口。

### 头文件引入

```cpp
#include "LightWeightInstancesEditor.h"
```

### 核心 API

| 函数 | 说明 |
|---|---|
| `ConvertActorsToLWIsUIAction(const TArray<AActor*> InActors)` | 将传入的 Actor 数组转换为轻量实例，所有 Actor 必须为同类型 |
| `CreateLevelViewportContextMenuExtender(...)` | 创建关卡视口右键菜单的扩展项 |

### 基本用法

本插件作为编辑器模块自动注册菜单扩展，无需手动调用。如需了解内部实现：

```cpp
// 模块会在启动时自动注册菜单扩展
// 关键逻辑在 ConvertActorsToLWIsUIAction 中：
// 检查所有选中 Actor 是否为同一类型，是则进行转换
```

## Demo 示例

本插件功能过于简单（仅编辑器菜单扩展），不提供独立 Demo。使用方式：

1. 在编辑器中启用 `LightWeightInstancesEditor` 插件
2. 在场景中选中多个**同类** Actor
3. 右键 → 选择转换为 Light Weight Instances

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等），额外依赖 `DataLayerEditor`。

| 模块 | 用途 |
|---|---|
| `DataLayerEditor` | 数据层编辑器支持（可能是转换过程中涉及数据层操作） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移至新版 UE_LOGF |
| 2025-12-18 | `23d96f6e` | Deprecated LigthWeightInstances | 标记轻量实例为废弃 |
| 2025-12-18 | `5d2acff8` | [Backout] - CL49403711 | 回退之前的改动 |
| 2025-12-18 | `1a58e93b` | Deprecated LigthWeightInstances | 标记轻量实例为废弃（首次尝试） |
| 2023-06-14 | `d1f48fc5` | Fix implicit capture of this using [=] deprecated in C++20 | 修复 C++20 中隐式捕获 this 的弃用警告 |

### 维护评价

**⚠️ 已废弃，不建议使用。**

- 该插件自 2021 年创建以来从未有过功能性更新，仅有的改动都是编译兼容性修复（C++20 兼容、日志宏迁移）
- 2025-12-18 被正式标记为废弃（DEPRECATED），替代方案为 `InstancedActors`
- `.uplugin` 中 `DeprecatedEngineVersion: 5.8`，`Installed: false`，`IsBetaVersion: true`
- **请勿在新项目中使用此插件**，已有项目应迁移到 `InstancedActors`

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/LightWeightInstancesEditor)
- 替代插件：`InstancedActors`（`Engine/Plugins/Experimental/InstancedActors`）