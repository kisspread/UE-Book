# Level Snapshots

> Level Snapshots Editor module for managing, comparing, and selectively restoring level state.

| 属性 | 值 |
|---|---|
| 中文名 | 关卡快照 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、蓝图过滤器工厂） |
| 模块 | `FoliageSupport` (Runtime), `LevelSnapshotFilters` (Runtime), `LevelSnapshots` (Runtime), `LevelSnapshotsEditor` (Runtime), `nDisplaySupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 解决的是**关卡非破坏性编辑**的问题。在虚拟制片和复杂项目中，关卡可能包含数百个 Actor，多人协作或反复修改时容易丢失已有的工作成果。这个插件提供了类似"版本控制"的功能：

1. **快照捕获**：将当前关卡的完整状态（Actor 层级、组件、属性值）保存为一个资产文件
2. **差异对比**：将快照与当前关卡进行逐 Actor、逐属性级别的对比，直观展示新增、删除、修改的内容
3. **选择性恢复**：用户可以通过勾选/取消勾选的方式，精确控制要恢复哪些 Actor 的哪些属性
4. **高级过滤系统**：支持 AND/OR 组合逻辑的过滤器，可以精确控制哪些对象参与对比和恢复
5. **专用编辑器 UI**：包含快照浏览器、过滤器编辑面板、结果对比面板的完整编辑器界面

插件默认未启用且标记为 Beta，主要面向虚拟制片工作流。

## 使用场景

- 你在做虚拟制片项目，需要在每次拍摄前保存关卡"已知良好状态" → 用 Level Snapshots 保存快照
- 多个美术同时编辑同一个关卡，需要对比和合并各自的修改 → 用快照对比查看差异
- 你需要实验性地修改关卡，但希望随时能精确回退 → 用选择性恢复只回退特定属性
- 你需要按规则批量筛选哪些 Actor 参与恢复 → 用过滤器系统（AND/OR 逻辑）
- 你在做 nDisplay 或 Foliage 密集的场景，需要特殊处理 → 插件提供了 FoliageSupport 和 nDisplaySupport 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TakeLevelSnapshotAndSaveToDisk` | 创建关卡快照并保存到磁盘，支持自定义文件名、路径、描述和重名处理 | `ULevelSnapshotsEditorFunctionLibrary` |
| `TakeAndSaveLevelSnapshotEditorWorld` | 简化版：为当前编辑器世界创建快照并保存 | `ULevelSnapshotsEditorFunctionLibrary` |
| `GenerateThumbnailForSnapshotAsset` | 为已注册的快照资产截取编辑器视口画面作为缩略图 | `ULevelSnapshotsEditorFunctionLibrary` |

### 使用示例

**基本快照创建工作流：**

1. 拖入一个 `TakeLevelSnapshotAndSaveToDisk` 节点
2. WorldContextObject 连接你的关卡世界上下文（通常是 GameMode 或 Level Blueprint 的 Self）
3. 设置 FileName 为快照名称（如 `"PreShootBackup"`）
4. 设置 FolderPath 为保存目录（如 `"/Game/LevelSnapshots/Shoot01"`）
5. 设置 Description 为描述文字
6. bShouldCreateUniqueFileName 设为 true 防止覆盖已有快照
7. 返回值为 `ULevelSnapshot*`，可存储供后续使用

**快捷版本（编辑器世界）：**

直接调用 `TakeAndSaveLevelSnapshotEditorWorld`，只需提供文件名、路径和描述即可。

## C++ 用法

### 头文件引入

```cpp
// 快照核心功能
#include "LevelSnapshots/LevelSnapshot.h"

// 编辑器函数库（用于创建快照）
#include "LevelSnapshotsEditorFunctionLibrary.h"

// 过滤器系统
#include "LevelSnapshots/Filtering/LevelSnapshotFilter.h"
```

### 基本用法

从 `TakeSnapshotUtil.h` 和 `LevelSnapshotsEditorFunctionLibrary.h` 提取的 API：

```cpp
// 方法一：通过编辑器函数库（BlueprintCallable API）
#include "LevelSnapshotsEditorFunctionLibrary.h"

// 创建并保存快照
ULevelSnapshot* Snapshot = ULevelSnapshotsEditorFunctionLibrary::TakeLevelSnapshotAndSaveToDisk(
    WorldContextObject,
    TEXT("MySnapshot"),           // 文件名
    TEXT("/Game/LevelSnapshots"), // 保存路径
    TEXT("拍摄前备份"),            // 描述
    true                          // 自动生成唯一文件名
);

// 为快照生成缩略图
ULevelSnapshotsEditorFunctionLibrary::GenerateThumbnailForSnapshotAsset(Snapshot);
```

**来源**: `Source/LevelSnapshotsEditor/Public/LevelSnapshotsEditorFunctionLibrary.h`

### 进阶用法

使用过滤器系统控制快照行为：

```cpp
// 基于 NegatableFilter / ConjunctionFilter / FilterPreset 的过滤逻辑
// 来源: Private/Data/Filters/NegatableFilter.h, ConjunctionFilter.h, LevelSnapshotsFilterPreset.h

// 创建一个可否定的过滤器包装
UNegatableFilter* NegatableFilter = UNegatableFilter::CreateNegatableFilter(MyChildFilter);
NegatableFilter->SetFilterBehaviour(EFilterBehavior::Negate); // 反转过滤结果
NegatableFilter->SetIsIgnored(false);                         // 确保过滤器生效

// 使用析取范式（DNF）预设管理复杂过滤逻辑
// FilterPreset 内部是 OR-of-ANDs 结构：(A && !B) || (C && D)
ULevelSnapshotsFilterPreset* FilterPreset = /* ... */;
UConjunctionFilter* AndGroup1 = FilterPreset->CreateChild();
UNegatableFilter* ConditionA = AndGroup1->CreateChild(UMyFilterClass::StaticClass());

UConjunctionFilter* AndGroup2 = FilterPreset->CreateChild();
// 继续添加条件...
```

**过滤器层级结构：**
- `ULevelSnapshotsFilterPreset`（OR 层）→ 包含多个 `UConjunctionFilter`
- `UConjunctionFilter`（AND 层）→ 包含多个 `UNegatableFilter`
- `UNegatableFilter`（包装层）→ 包装一个 `ULevelSnapshotFilter`，支持取反和忽略

**来源**: `Private/Data/Filters/LevelSnapshotsFilterPreset.h`, `ConjunctionFilter.h`, `NegatableFilter.h`

## Demo 示例

### 快照管理器组件

一个可挂载到 Actor 上的组件，提供快照创建和管理功能：

**LevelSnapshotManagerComponent.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LevelSnapshotManagerComponent.generated.h"

class ULevelSnapshot;
class ULevelSnapshotsFilterPreset;

UCLASS(ClassGroup=(LevelSnapshots), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API ULevelSnapshotManagerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    ULevelSnapshotManagerComponent();

    // 创建快照并保存到磁盘
    UFUNCTION(BlueprintCallable, Category = "Level Snapshots")
    ULevelSnapshot* CreateSnapshot(const FString& Description);

    // 获取最近创建的快照
    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Level Snapshots")
    ULevelSnapshot* GetLastSnapshot() const { return LastSnapshot; }

private:
    UPROPERTY()
    TObjectPtr<ULevelSnapshot> LastSnapshot;

    int32 SnapshotCounter = 0;
};
```

**LevelSnapshotManagerComponent.cpp**

```cpp
#include "LevelSnapshotManagerComponent.h"
#include "LevelSnapshotsEditorFunctionLibrary.h"

ULevelSnapshotManagerComponent::ULevelSnapshotManagerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

ULevelSnapshot* ULevelSnapshotManagerComponent::CreateSnapshot(const FString& Description)
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return nullptr;
    }

    SnapshotCounter++;

    const FString FileName = FString::Printf(TEXT("Snapshot_%04d"), SnapshotCounter);
    const FString FolderPath = TEXT("/Game/LevelSnapshots/AutoSaved");

    LastSnapshot = ULevelSnapshotsEditorFunctionLibrary::TakeLevelSnapshotAndSaveToDisk(
        World, FileName, FolderPath, Description, /*bShouldCreateUniqueFileName=*/ true
    );

    if (LastSnapshot)
    {
        ULevelSnapshotsEditorFunctionLibrary::GenerateThumbnailForSnapshotAsset(LastSnapshot);
        UE_LOG(LogTemp, Log, TEXT("快照已创建: %s - %s"), *FileName, *Description);
    }

    return LastSnapshot;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSnapshots` | 核心快照数据结构、序列化和恢复逻辑 |
| `LevelSnapshotFilters` | 过滤器资产类型（LevelSnapshotFilter、BlueprintFilter） |
| `FoliageEdit` | FoliageSupport 模块专用，处理植被 Actor 的快照支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复 VP 相关的 EngineAssetDefinitions 插件引用警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整 VP 资产分类并迁移到新路径 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 格式 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为追踪通道和其他位置添加描述信息 |

### 维护评价

- **年龄**：约 5 年（2021 年创建）
- **仍处于 Beta 状态**，默认未启用
- **近期更新均为基础设施维护**（编译警告修复、UE_LOG 迁移、资产分类调整），没有功能性更新
- 插件代码体量较大（319 个源文件），编辑器 UI 代码复杂且高度自定义
- **模块全部标记为 Runtime**，但实际主要在编辑器中使用（包含大量编辑器专用 Slate Widget）
- **推荐程度**：如果你在做虚拟制片项目且需要关卡版本管理功能，这个插件值得尝试，但需要注意它仍是 Beta 状态，API 可能变动。对于简单需求，考虑使用关卡自带的备份功能或外部版本控制

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
- 官方文档（无）
- 测试用例（未在插件目录内发现）