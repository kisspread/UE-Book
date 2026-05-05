# Level Snapshots

> （.uplugin 的 Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 插件为 Unreal Engine 提供了一种快速保存和恢复关卡（Level）状态的机制。它允许开发者在编辑器中创建当前关卡的“快照”（Snapshot），记录所有 Actor 的属性、变换、组件状态等信息。随后，可以随时将关卡恢复到该快照记录的状态，或选择性地应用快照中的部分更改。

该插件主要解决虚拟制作（Virtual Production）和大型项目开发中的场景管理问题。例如，在拍摄现场或迭代设计时，需要频繁尝试不同的场景布局、灯光设置或 Actor 配置。Level Snapshots 提供了一种非破坏性、可快速回溯的工作流，避免了手动撤销或维护多个关卡副本的繁琐，极大地提升了场景迭代和版本控制的效率。

## 使用场景

- **虚拟制片现场**：在 LED 墙前拍摄时，需要快速切换不同的虚拟场景布局或灯光预设。使用 Level Snapshots 可以一键保存当前最佳设置，并在需要时瞬间恢复。
- **关卡设计迭代**：在设计复杂关卡时，尝试不同的敌人配置、道具摆放或环境效果。可以保存多个“实验性”快照，方便对比和回退。
- **多人协作与审查**：将关卡的特定状态（如“待审核版”、“最终灯光版”）保存为快照资产，便于在团队间分享和审查。
- **自动化测试与回归**：结合自动化测试，在测试前后保存和恢复关卡状态，确保测试环境的一致性。

## 蓝图用法

该插件主要通过 `ULevelSnapshotsEditorFunctionLibrary` 提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Take Level Snapshot And Save To Disk` | 创建一个新的关卡快照资产并保存到磁盘，同时捕获目标世界的状态。 | `ULevelSnapshotsEditorFunctionLibrary` |
| `Take And Save Level Snapshot Editor World` | 使用编辑器世界作为目标，调用 `TakeLevelSnapshotAndSaveToDisk` 的便捷函数。 | `ULevelSnapshotsEditorFunctionLibrary` |
| `Generate Thumbnail For Snapshot Asset` | 为已保存在注册表中的快照资产生成编辑器场景的缩略图。 | `ULevelSnapshotsEditorFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建并保存快照**：
    - 在蓝图中，调用 `Take And Save Level Snapshot Editor World` 节点。
    - 输入 `FileName`（如 “MySnapshot”）、`FolderPath`（如 “/Game/Snapshots”）和 `Description`（如 “初始布局”）。
    - 执行后，会在指定内容浏览器路径下生成一个 `ULevelSnapshot` 资产。

2.  **为快照生成缩略图**：
    - 获取一个已存在的 `ULevelSnapshot` 对象引用。
    - 调用 `Generate Thumbnail For Snapshot Asset` 节点，传入该引用。
    - 该快照资产的缩略图将被更新为当前编辑器视口的画面。

## C++ 用法

### 头文件引入

```cpp
#include "LevelSnapshotsEditorFunctionLibrary.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个关卡快照并保存。

```cpp
// 假设在某个编辑器工具或命令中
#include "LevelSnapshotsEditorFunctionLibrary.h"
#include "Engine/World.h"

void CreateMySnapshot()
{
    UWorld* EditorWorld = GEditor->GetEditorWorldContext().World();
    if (EditorWorld)
    {
        // 创建并保存快照到指定路径
        ULevelSnapshot* NewSnapshot = ULevelSnapshotsEditorFunctionLibrary::TakeLevelSnapshotAndSaveToDisk(
            EditorWorld,
            TEXT("MyCppSnapshot"),
            TEXT("/Game/Snapshots/CPP"),
            TEXT("通过C++创建的快照"),
            true // 如果名称重复则自动添加后缀
        );

        if (NewSnapshot)
        {
            UE_LOG(LogTemp, Log, TEXT("快照创建成功: %s"), *NewSnapshot->GetName());
            // 可以进一步操作快照，例如应用它
        }
    }
}
```

### 进阶用法

结合 `ULevelSnapshot` 对象本身的方法（需查阅完整 API），可以实现更精细的控制，例如应用快照、比较差异等。以下是一个概念性示例：

```cpp
// 假设已经有一个 ULevelSnapshot* SnapshotAsset
void ApplySnapshotWithFilter(ULevelSnapshot* SnapshotAsset)
{
    if (SnapshotAsset)
    {
        // 此处需要查阅 ULevelSnapshot 的完整 API
        // 例如，可能存在类似 ApplySnapshotToWorld 的函数
        // 并且可能支持传入一个 Filter 来选择性地应用
        // SnapshotAsset->ApplySnapshot(EditorWorld, SomeFilter);
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个编辑器命令来保存和应用快照。

**MySnapshotCommands.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "LevelSnapshotsEditorFunctionLibrary.h"

class FMySnapshotCommands
{
public:
    static void SaveCurrentState();
    static void RestoreLastState();

private:
    static ULevelSnapshot* LastSavedSnapshot;
};
```

**MySnapshotCommands.cpp**
```cpp
#include "MySnapshotCommands.h"
#include "Engine/World.h"
#include "Editor.h"

ULevelSnapshot* FMySnapshotCommands::LastSavedSnapshot = nullptr;

void FMySnapshotCommands::SaveCurrentState()
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (World)
    {
        // 保存快照，并覆盖之前的引用
        LastSavedSnapshot = ULevelSnapshotsEditorFunctionLibrary::TakeLevelSnapshotAndSaveToDisk(
            World,
            TEXT("TempRestorePoint"),
            TEXT("/Game/Snapshots/Temp"),
            TEXT("临时恢复点"),
            false // 覆盖同名文件
        );
    }
}

void FMySnapshotCommands::RestoreLastState()
{
    if (LastSavedSnapshot)
    {
        // 注意：实际应用快照的 API 需要查阅 ULevelSnapshot 类的完整定义
        // 此处为示意代码
        // LastSavedSnapshot->ApplyToCurrentWorld();
        UE_LOG(LogTemp, Warning, TEXT("应用快照功能需要查阅 ULevelSnapshot 的具体 API"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("没有可恢复的快照。请先保存状态。"));
    }
}
```

## 模块依赖

从提供的 Build.cs 信息和模块用途推断，使用此插件的核心功能（`LevelSnapshots` 模块）可能需要依赖以下模块。具体依赖关系请以实际 `LevelSnapshots.Build.cs` 文件为准。

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | `FoliageSupport` 模块依赖，用于支持对植被（Foliage）Actor 的快照功能。 |
| `nDisplay` | `nDisplaySupport` 模块依赖，用于支持 nDisplay 集群渲染场景的快照功能。 |

**注意**：`LevelSnapshots`、`LevelSnapshotFilters`、`LevelSnapshotsEditor` 核心模块的具体依赖未在提供信息中列出，通常会依赖 `Core`, `CoreUObject`, `Engine`, `UnrealEd` 等标准模块。

## 维护状态

### 近期更新

```
- bcfbca62540b Make Handled/Unhandled [[nodiscard]]
- 96a7c5492bb8 [LevelSnapshot] Tweaks for the overall size to better match AssetView length
- df1cc5402b3e Gather text from source, resolve macro has an empty source text (.cpp files)
```

### 维护评价

- **创建时间**：插件创建于 2021 年初，至今约 4 年。
- **最近更新**：最近的提交集中在代码质量改进（如添加 `[[nodiscard]]` 属性）和编辑器 UI 微调（资产视图尺寸适配），表明插件仍在维护中，但近期没有重大功能更新。
- **活跃度**：维护状态为“维护中”，但更新频率不高，主要以修复和优化为主。
- **实验性**：插件在 `.uplugin` 中被标记为 `IsBetaVersion: true`，且默认未启用（`EnabledByDefault: false`）。这意味着它可能尚未达到生产就绪状态，API 和功能在未来版本中可能会发生变化。
- **推荐使用**：**谨慎推荐**。该插件功能明确，对于虚拟制作和需要高级场景管理的工作流非常有价值。但由于其“实验性”状态，不建议在需要高度稳定性的核心生产管线中作为唯一依赖。建议在受控的环境或作为辅助工具进行试用和评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [测试用例]（未在提供信息中明确，通常位于 `Engine/Plugins/VirtualProduction/LevelSnapshots/Tests` 或 `Engine/Tests` 目录下）