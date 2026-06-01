# Motion Design Scene State Integration

> 

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AvalancheSceneState` (Runtime), `AvalancheSceneStateBlueprint` (UncookedOnly), `AvalancheSceneStateEditor` (Editor) |
| 实验性 | ⚫️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState) | |

## 用途

AvalancheSceneState 是 **Avalanche 动态设计系统** 与 **Scene State 场景状态框架** 之间的集成插件。它解决的核心问题是：在 Motion Design（动态设计/广播图文包装）工作流中，如何通过 Scene State 蓝图来管理和驱动场景的状态切换。

该插件从 `Experimental` 目录迁移到 `VirtualProduction`，属于 Epic 虚拟制作物料的一部分。它为 Motion Design 用户提供了：

- 自定义的 `UAvaSceneStateBlueprint` 蓝图类型，扩展了 Scene State 的蓝图能力
- 任务（Task）Schema 系统，定义哪些 Scene State 任务在 Motion Design 上下文中是允许的
- 元数据驱动的任务分类（utility task 等），便于编辑器端筛选和组织

该插件**不适用于服务器**（Runtime 和 Blueprint 模块均在 TargetDenyList 中排除了 Server），这是典型的客户端/编辑器专用插件。

## 使用场景

- 你正在使用 **Avalanche** 制作广播图文、虚拟制作物料或实时 Motion Design 内容 → 用此插件集成 Scene State 来管理场景状态
- 你需要在 Motion Design 场景中定义状态切换逻辑（如：开场 → 图表展示 → 结尾）→ 使用 AvalancheSceneStateBlueprint 蓝图
- 你需要限制某些 Scene State 任务在 Motion Design 工作流中可用 → 使用 Schema 系统配置任务规则

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| — | （无公开 BlueprintCallable 函数，主要通过蓝图资产类型提供能力） | `UAvaSceneStateBlueprint` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中右键 → Blueprint → 选择 **Motion Design Scene State Blueprint** 作为父类
2. 在蓝图编辑器中配置 Scene State 的状态转换逻辑
3. 将该蓝图拖入场景或通过 Avalanche 的状态管理接口引用

> 注意：`AvalancheSceneStateBlueprint` 模块标记为 `UncookedOnly`，意味着相关蓝图功能仅在编辑器和未打包构建中可用。

## C++ 用法

### 头文件引入

```cpp
#include "AvaSceneStateBlueprint.h"
```

### 基本用法

```cpp
// UAvaSceneStateBlueprint 是 USceneStateBlueprint 的子类
// 主要用于编辑器扩展和蓝图资产类型注册
// 运行时使用 Scene State 原生 API 即可
```

### 进阶用法

该插件的 C++ 层面主要提供：
- 自定义蓝图类 `UAvaSceneStateBlueprint`（MinimalAPI，编辑器显示名 "Motion Design Scene State Blueprint"）
- Schema 系统用于定义任务类型规则
- 元数据系统用于分类任务（utility task 等）

实际的场景状态操作请参考 **SceneState** 插件的 C++ API。

## Demo 示例

```cpp
// AvaSceneStateBlueprint.h
// 该插件的公开 API 非常精简，主要通过蓝图资产类型工作
// 以下展示如何在代码中引用 Motion Design Scene State Blueprint

#include "AvaSceneStateBlueprint.h"

// 创建或加载一个 Motion Design Scene State Blueprint
UBlueprint* Blueprint = LoadObject<UAvaSceneStateBlueprint>(
    nullptr, 
    TEXT("/Game/MyMotionDesign/MySceneState")
);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 核心框架 |
| `SceneState` | 场景状态管理框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏 |
| 2026-02-22 | `977f0c20` | Motion Design Scene State: added an extra 'utility task' metadata + updating from deprecated api | 新增 utility task 元数据，更新已废弃 API |
| 2026-02-16 | `22f3bb17` | Motion Design Scene State: changed schema to only check for task type metadata in the task itself, n | 简化 Schema 逻辑，仅检查任务自身的类型元数据 |
| 2026-02-15 | `5c9f991d` | Motion Design Scene State: made some schema functions editor-only, and added metadata to tasks to ea | Schema 函数限制为编辑器专用，新增任务元数据 |
| 2026-02-03 | `d2e06058` | Motion Design Scene State: added schema to set the rules of which tasks are allowed. | 新增 Schema 系统定义允许的任务规则 |

### 维护评价

**活跃维护中** 🟢

- 插件创建于 2025-08-27，历史约 1 年
- 2026 年 2 月有密集的功能开发（Schema 系统、元数据支持）
- 2026 年 4 月有例行代码维护更新
- 标记为 `IsBetaVersion=true`，API 可能发生变化
- 属于 Virtual Production 管线的关键组件，Epic 持续投入
- **推荐使用**，但需注意 Beta 状态下 API 可能调整

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState)
- [Avalanche 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [SceneState 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/SceneState)