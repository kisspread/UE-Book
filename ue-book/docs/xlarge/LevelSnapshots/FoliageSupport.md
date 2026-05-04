# Level Snapshots

> （Description 字段为空，基于源码分析：提供关卡状态快照的保存、对比与恢复功能，用于虚拟制片中快速记录和回退场景配置。）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、UI 资源） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 解决的核心问题是：**在编辑器中快速保存和恢复关卡中 Actor 的状态**。

在虚拟制片工作流中，场景配置（灯光、道具位置、摄像机参数等）经常需要反复调整和对比。Level Snapshots 允许你：

1. **拍摄快照**：将当前关卡中选定 Actor 的属性状态序列化保存
2. **对比差异**：将快照与当前关卡状态进行逐属性对比，高亮显示变更
3. **选择性恢复**：按 Actor 或按属性粒度恢复到快照时的状态，而非全量回滚
4. **过滤控制**：通过 Filter 系统精确控制哪些 Actor/属性参与快照和恢复

与简单的 Undo 不同，快照是持久化的，可以跨编辑器会话保留；与 Source Control 不同，它专注于关卡内 Actor 属性级别的细粒度管理。

## 使用场景

- 你在做虚拟制片，需要在不同灯光/场景配置之间快速切换 → 拍摄快照，随时恢复
- 你调整了大量 Actor 参数后想保留"之前的状态"作为参考 → 创建快照后继续编辑，随时对比
- 你需要只恢复场景中某几个 Actor 到之前的状态，不影响其他改动 → 选择性恢复
- 你的场景包含植被（Foliage），需要快照植被实例数据 → FoliageSupport 模块处理
- 你使用 nDisplay 多屏渲染，需要快照 nDisplay 相关配置 → nDisplaySupport 模块处理

## 模块架构

本插件由 5 个模块组成，按职责分层：

| 模块 | 类型 | 职责 |
|---|---|---|
| `LevelSnapshots` | UncookedOnly | 核心库：快照序列化、对比引擎、恢复逻辑 |
| `LevelSnapshotFilters` | UncookedOnly | 过滤系统：定义哪些 Actor/属性参与快照操作 |
| `LevelSnapshotsEditor` | UncookedOnly | 编辑器 UI：快照管理面板、对比视图、操作按钮 |
| `FoliageSupport` | UncookedOnly | 植被扩展：支持 Foliage Actor 的快照与恢复 |
| `nDisplaySupport` | UncookedOnly | nDisplay 扩展：支持 nDisplay 配置的快照（仅 Win64/Linux） |

## 蓝图用法

> ⚠️ 本插件主要为编辑器工具（UncookedOnly），蓝图 API 有限。近期 commit `fa44f78b14f2` 新增了通过 `UEngineSubsystem` 暴露的蓝图事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Level Snapshot 事件（通过 EngineSubsystem） | 监听快照拍摄/恢复等生命周期事件 | `UEngineSubsystem` 派生类 |

> 由于本插件为 UncookedOnly 类型，大部分 API 仅在编辑器中可用，不支持运行时蓝图调用。详细蓝图节点请参考编辑器内节点搜索 "Level Snapshot"。

## C++ 用法

### 头文件引入

```cpp
#include "LevelSnapshotsModule.h"
```

### 基本用法

```cpp
// 获取 LevelSnapshots 模块
ILevelSnapshotsModule& SnapshotModule = ILevelSnapshotsModule::Get();

// 通过模块接口创建快照、应用快照等操作
// 具体 API 参见 ILevelSnapshotsModule.h
```

### 进阶用法

快照系统的核心工作流：

```cpp
// 1. 创建快照 - 序列化当前关卡中匹配 Filter 的 Actor 状态
// 2. 对比快照 - 逐属性比较快照与当前状态
// 3. 应用恢复 - 选择性地将属性恢复到快照值

// Filter 系统用于控制参与操作的范围
// 参见 LevelSnapshotFilters 模块中的 ULevelSnapshotFilter 类
```

## Demo 示例

> 本插件为编辑器工具插件，主要通过编辑器 UI 操作。最小 C++ 集成示例：

```cpp
// MySnapshotTool.h
#pragma once

#include "CoreMinimal.h"
#include "LevelSnapshotsModule.h"

class FMySnapshotTool
{
public:
    void CaptureCurrentState();
    void RestoreToSnapshot();
};
```

```cpp
// MySnapshotTool.cpp
#include "MySnapshotTool.h"

void FMySnapshotTool::CaptureCurrentState()
{
    ILevelSnapshotsModule& Module = ILevelSnapshotsModule::Get();
    // 使用模块接口拍摄快照
}

void FMySnapshotTool::RestoreToSnapshot()
{
    ILevelSnapshotsModule& Module = ILevelSnapshotsModule::Get();
    // 使用模块接口恢复快照
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | FoliageSupport 模块依赖，用于植被实例的编辑操作支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- fa44f78b14f2 Expose some C++ LevelSnapshots events to Blueprint scripting via UEngineSubsystem
- ef796fe0a58c Reorganize Level Snapshots folder structure
- bba0759971a3 Fix foliage not restoring anymore in Level Snapshots and prevent if data is from 5.1. Warn if data is from before 5.1 and allow only with console variable (separate possible crash found)
```

### 维护评价

- **创建时间**：2021-02-03，约 4 年历史
- **近期活跃度**：有实质性功能更新（蓝图事件暴露）和重要 Bug 修复（植被恢复问题）
- **Beta 状态**：`IsBetaVersion=true`，API 可能发生变化
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **平台限制**：nDisplaySupport 仅支持 Win64 和 Linux

**综合评价**：插件处于活跃开发中，近期有功能扩展和关键修复。作为 Beta 版本，建议在生产环境中谨慎使用，注意 API 兼容性变化。对于虚拟制片工作流中的关卡状态管理需求，这是一个有价值的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- 官方文档：无（.uplugin 中 DocsURL 为空）