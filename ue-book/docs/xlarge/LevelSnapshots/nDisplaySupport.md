# Level Snapshots

> （.uplugin 的 Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 插件为 Unreal Engine 提供了一套完整的关卡状态保存与恢复系统。它允许开发者在编辑器中创建当前关卡状态的“快照”，并可以在之后将关卡恢复到该快照的状态。这解决了在虚拟制作、关卡设计迭代和多人协作中，需要快速、可靠地保存和切换复杂场景配置的核心问题。与简单的撤销/重做不同，快照可以跨会话保存，并且可以精确控制恢复哪些对象或属性。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙拍摄过程中，需要快速切换不同的场景布局、光照或道具配置。使用 Level Snapshots 可以保存每个镜头的完美设置，并在需要时一键恢复。
- **关卡设计迭代**：设计师想要尝试一个大胆的布局改动，但又不想丢失当前稳定版本。可以先创建快照，然后进行实验。如果实验失败，可以轻松恢复。
- **多人协作与审核**：团队成员可以创建并分享特定场景状态的快照，用于代码审查、设计评审或作为里程碑存档。
- **自动化测试**：在自动化测试中，可以先保存关卡初始状态，运行测试后恢复，确保测试环境的一致性。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Snapshot` | 为当前关卡创建一个新的快照资产。 | `ULevelSnapshot` |
| `Apply Snapshot` | 将指定的快照应用到当前关卡，恢复其状态。 | `ULevelSnapshot` |
| `Apply Snapshot Filtered` | 使用过滤器选择性地应用快照中的部分对象或属性。 | `ULevelSnapshot` |
| `Get Snapshot Info` | 获取快照的元数据信息，如创建时间、描述等。 | `ULevelSnapshot` |
| `Set Snapshot Description` | 为快照设置描述性文本。 | `ULevelSnapshot` |
| `Create Filter` | 创建一个新的快照过滤器实例。 | `ULevelSnapshotFilter` |
| `Add Actor Filter` | 向过滤器中添加一个基于 Actor 的过滤规则。 | `ULevelSnapshotFilter` |
| `Add Property Filter` | 向过滤器中添加一个基于属性的过滤规则。 | `ULevelSnapshotFilter` |

### 使用示例（蓝图描述）

1.  **创建快照**：在关卡编辑器中，通过右键菜单或工具栏按钮调用 `Create Snapshot` 节点。在蓝图中，可以获取当前世界上下文 (`Get World`)，然后调用 `ULevelSnapshot::CreateSnapshot`。
2.  **应用快照**：获取之前创建的 `ULevelSnapshot` 资产引用，然后调用 `Apply Snapshot` 节点。这会将整个关卡状态回滚到快照时刻。
3.  **选择性恢复**：首先创建一个 `ULevelSnapshotFilter` 对象。使用 `Add Actor Filter` 节点指定只恢复特定的 Actor（例如，只恢复灯光 Actor）。然后调用 `Apply Snapshot Filtered` 节点，并传入该过滤器。这样，只有符合过滤条件的对象会被恢复。

## C++ 用法

### 头文件引入

```cpp
#include "LevelSnapshot.h"
#include "LevelSnapshotFilter.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和应用一个简单的快照。

```cpp
// 假设在某个 Actor 或 GameMode 的函数中
void AMyActor::SaveCurrentState()
{
    UWorld* World = GetWorld();
    if (World)
    {
        // 创建快照
        ULevelSnapshot* Snapshot = ULevelSnapshot::CreateSnapshot(World, TEXT("MyBackupSnapshot"));
        if (Snapshot)
        {
            // 可以设置描述
            Snapshot->SetDescription(TEXT("保存了当前关卡的完整状态"));
            UE_LOG(LogTemp, Log, TEXT("快照已创建: %s"), *Snapshot->GetName());
        }
    }
}

void AMyActor::RestoreSavedState()
{
    // 假设 MySnapshot 是之前保存的 ULevelSnapshot 资产指针
    if (MySnapshot)
    {
        UWorld* World = GetWorld();
        if (World)
        {
            // 应用快照
            MySnapshot->ApplySnapshot(World);
            UE_LOG(LogTemp, Log, TEXT("关卡已恢复到快照状态"));
        }
    }
}
```

### 进阶用法

使用过滤器进行选择性恢复。

```cpp
void AMyActor::RestoreOnlyLights()
{
    if (MySnapshot)
    {
        UWorld* World = GetWorld();
        if (World)
        {
            // 创建过滤器
            ULevelSnapshotFilter* Filter = NewObject<ULevelSnapshotFilter>();

            // 添加规则：只恢复 APointLight 类型的 Actor
            FLevelSnapshotActorFilter ActorFilter;
            ActorFilter.ActorClass = APointLight::StaticClass();
            Filter->AddActorFilter(ActorFilter);

            // 添加规则：对于所有恢复的 Actor，只恢复其 “Intensity” 属性
            FLevelSnapshotPropertyFilter PropertyFilter;
            PropertyFilter.PropertyName = GET_MEMBER_NAME_CHECKED(ULightComponent, Intensity);
            Filter->AddPropertyFilter(PropertyFilter);

            // 应用带过滤器的快照
            MySnapshot->ApplySnapshotFiltered(World, Filter);
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个自定义的 Actor 来保存和恢复快照。

**MySnapshotActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySnapshotActor.generated.h"

class ULevelSnapshot;

UCLASS()
class MYPROJECT_API AMySnapshotActor : public AActor
{
    GENERATED_BODY()

public:
    AMySnapshotActor();

    UFUNCTION(BlueprintCallable, Category = "Snapshot")
    void SaveSnapshot();

    UFUNCTION(BlueprintCallable, Category = "Snapshot")
    void LoadSnapshot();

private:
    UPROPERTY()
    TWeakObjectPtr<ULevelSnapshot> SavedSnapshot;
};
```

**MySnapshotActor.cpp**
```cpp
#include "MySnapshotActor.h"
#include "LevelSnapshot.h"
#include "Engine/World.h"

AMySnapshotActor::AMySnapshotActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySnapshotActor::SaveSnapshot()
{
    UWorld* World = GetWorld();
    if (World)
    {
        SavedSnapshot = ULevelSnapshot::CreateSnapshot(World, TEXT("DemoSnapshot"));
        if (SavedSnapshot.IsValid())
        {
            UE_LOG(LogTemp, Warning, TEXT("快照已保存！"));
        }
    }
}

void AMySnapshotActor::LoadSnapshot()
{
    if (SavedSnapshot.IsValid())
    {
        UWorld* World = GetWorld();
        if (World)
        {
            SavedSnapshot->ApplySnapshot(World);
            UE_LOG(LogTemp, Warning, TEXT("快照已加载！"));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("没有可用的快照！"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | 为 FoliageSupport 模块提供对植被系统（Foliage）的编辑器支持，用于保存和恢复植被实例的状态。 |
| `nDisplay` | 为 nDisplaySupport 模块提供对 nDisplay 多显示器渲染系统的支持，用于处理 nDisplay Actor 的快照。 |

## 维护状态

### 近期更新

```
- 7581937adfb2 修复了使用 include-what-you-use 编译 UnrealGame 的问题。修复了循环包含（主要是移除了 UnrealTypes.h 中的 StrProperty.h 包含）。在一些地方添加了 iwyu 注解。
- decc598618ad [回退] - CL32587777 - CIS 编译错误 #jira UE-210862 #rnx [供参考] Steve.Robb 原始 CL 描述 ----------------------------------------------------------------- 添加了缺失的包含。
- f3292013fafa 添加了缺失的包含。
```

### 维护评价

Level Snapshots 插件创建于 2021 年初，相对年轻。从最近的提交记录来看，最后一次实质性功能更新未知，但近期（2024年）的提交主要集中在**编译修复和头文件包含**上，表明 Epic 仍在维护其编译兼容性，以确保它能跟随引擎版本更新。

**优点**：
-   解决了虚拟制作和关卡设计中的一个明确痛点。
-   架构模块化，支持通过过滤器进行精细控制。
-   有官方支持，代码质量有保障。

**缺点/限制**：
-   标记为 **Beta 版本** (`IsBetaVersion: true`)，意味着 API 可能不稳定，功能可能不完整。
-   默认未启用 (`EnabledByDefault: false`)，需要用户手动在插件管理器中启用。
-   所有模块类型均为 `UncookedOnly`，意味着此插件**仅在编辑器中可用**，无法在打包后的游戏中运行。

**推荐**：对于在编辑器中进行虚拟制片或需要复杂场景状态管理的团队，**推荐使用**。但应意识到其 Beta 状态，避免在关键生产流水线中过度依赖其内部 API，并做好未来 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots/Tests)