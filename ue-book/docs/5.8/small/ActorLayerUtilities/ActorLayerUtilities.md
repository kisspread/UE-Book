# Actor Layer Utilities

> Utilites for interacting with actor layers from blueprints

| 属性 | 值 |
|---|---|
| 中文名 | Actor层工具库 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorLayerUtilities` (Runtime), `ActorLayerUtilitiesEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities) | |

## 用途

此插件的核心作用是将 Unreal Engine 编辑器中 **Actor 层** (Layer) 的管理功能暴露给蓝图和 C++。在编辑器中，层是一种强大的组织工具，用于将关卡中的 Actor 进行逻辑分组（例如，将所有“敌人”放在一层，所有“可破坏物”放在另一层），以便于批量选择、显示/隐藏、锁定等操作。

这个插件填补了一个关键空白：**在游戏运行时 (Runtime)，蓝图无法直接访问或操作这些编辑器层**。通过 `ULayersBlueprintLibrary` 提供的接口，开发者可以在游戏逻辑（蓝图或 C++）中查询特定层中的所有 Actor，或者在运行时动态地将 Actor 添加到层/从层中移除。这使得“层”从一个纯粹的编辑器组织工具，变成了一个可用于驱动游戏逻辑的可编程属性。

## 使用场景

- 你在设计一个基于区域的关卡，使用编辑器层来划分“森林区”、“沼泽区”。在游戏运行时，你可以通过这个插件获取“森林区”层中的所有 Actor，并统一应用雾效或环境音效。
- 你需要在运行时动态生成一组 Actor（例如，一波敌人），并希望将它们归入一个特定的“层”，以便后续逻辑可以方便地对这整波敌人进行批量操作（如移除、暂停AI等）。
- 你正在开发一个编辑器工具，需要在编辑器扩展中（通过蓝图或 C++）与层进行交互，此插件的运行时模块 (`ActorLayerUtilities`) 也能在编辑器上下文中使用。

## 蓝图用法

该插件提供了一个静态函数库，所有功能都可以作为全局蓝图节点使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActors` | 获取指定 `ActorLayer` 中的所有 Actor 对象。需要提供 World 上下文。 | `ULayersBlueprintLibrary` |
| `AddActorToLayer` | 将一个指定的 Actor 添加到目标 `ActorLayer` 中。如果 Actor 已在该层中，则无操作。 | `ULayersBlueprintLibrary` |
| `RemoveActorFromLayer` | 将一个指定的 Actor 从目标 `ActorLayer` 中移除。如果 Actor 不在该层中，则无操作。 | `ULayersBlueprintLibrary` |

**数据结构**：
所有节点都使用 `FActorLayer` 结构体作为层标识符。该结构体只有一个 `Name` (FName) 属性，对应编辑器中创建的层名称。

### 使用示例（蓝图描述）

1.  **获取层内所有 Actor**：
    *   在蓝图中，右键搜索并添加 `GetActors` 节点。
    *   连接 `World Context Object`（通常连接到 `Self` 或场景中的某个 Actor）。
    *   创建一个 `FActorLayer` 变量，将其 `Name` 设置为你要查询的层名（例如 `"EnemyWave1"`）。
    *   将此变量连接到 `ActorLayer` 输入引脚。
    *   输出引脚 `Actors` 将返回一个包含该层所有 Actor 的数组。

2.  **动态添加 Actor 到层**：
    *   添加 `AddActorToLayer` 节点。
    *   将你想要添加的 Actor 引用连接到 `InActor`。
    *   同样，提供一个 `FActorLayer` 变量来指定目标层。

## C++ 用法

在 C++ 中使用需要引用插件模块。

### 头文件引入

```cpp
#include "ActorLayerUtilities.h"
```

### 基本用法

以下示例展示了如何在 C++ Actor 类中获取指定层中的所有 Actor。

```cpp
// 假设在某个 AActor 的派生类方法中
#include "ActorLayerUtilities.h"

void AMyActor::QueryLayerActors()
{
    // 定义我们要查询的层
    FActorLayer TargetLayer;
    TargetLayer.Name = FName(TEXT("Interactables"));

    // 获取该层中的所有 Actor
    TArray<AActor*> FoundActors = ULayersBlueprintLibrary::GetActors(this, TargetLayer);

    // 对获取到的 Actor 列表进行操作
    for (AActor* Actor : FoundActors)
    {
        if (Actor)
        {
            // 例如：禁用所有找到的 Actor
            Actor->SetActorHiddenInGame(true);
            UE_LOG(LogTemp, Log, TEXT("Disabled actor: %s from layer %s"), *Actor->GetName(), *TargetLayer.Name.ToString());
        }
    }
}
```

### 进阶用法

结合动态生成的 Actor 与层管理。

```cpp
void AMySpawner::SpawnAndAssignToLayer()
{
    // 动态生成一个 Actor (例如，一个拾取物)
    FActorSpawnParameters SpawnParams;
    AActor* SpawnedPickup = GetWorld()->SpawnActor<AActor>(APickup::StaticClass(), GetActorLocation(), FRotator::ZeroRotator, SpawnParams);

    if (SpawnedPickup)
    {
        // 定义目标层
        FActorLayer DynamicLayer;
        DynamicLayer.Name = FName(TEXT("RuntimeSpawned"));

        // 将生成的 Actor 添加到该层
        ULayersBlueprintLibrary::AddActorToLayer(SpawnedPickup, DynamicLayer);

        // 稍后，可以检查它是否在该层中，或从该层移除
        ULayersBlueprintLibrary::RemoveActorFromLayer(SpawnedPickup, DynamicLayer);
    }
}
```

## Demo 示例

一个最小的可编译示例，展示了如何在 Actor 的构造函数或 `BeginPlay` 中使用层工具库。

```cpp
// LayerDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "LayerDemoActor.generated.h"

UCLASS()
class ALayerDemoActor : public AActor
{
    GENERATED_BODY()
public:
    ALayerDemoActor();
    virtual void BeginPlay() override;
};

// LayerDemoActor.cpp
#include "LayerDemoActor.h"
#include "ActorLayerUtilities.h" // 关键头文件

ALayerDemoActor::ALayerDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ALayerDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个表示“Props”层的变量
    FActorLayer PropsLayer;
    PropsLayer.Name = FName(TEXT("Props"));

    // 1. 将自己添加到“Props”层
    ULayersBlueprintLibrary::AddActorToLayer(this, PropsLayer);

    // 2. 获取“Props”层中的所有 Actor
    TArray<AActor*> PropsActors = ULayersBlueprintLibrary::GetActors(this, PropsLayer);

    UE_LOG(LogTemp, Warning, TEXT("Found %d actors in the 'Props' layer."), PropsActors.Num());

    // 3. (可选) 将自己从层中移除
    ULayersBlueprintLibrary::RemoveActorFromLayer(this, PropsLayer);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 该插件功能较为基础，主要依赖 Unreal Engine 的核心模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化了内部依赖，移除了不必要的私有模块包含。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件目录的通用更新。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件目录的通用更新。 |
| 2022-10-26 | `b5b86c79` | This change is a strategical submit for a coming change that removes lots of includes in headers tha... | 为即将到来的大规模头文件清理做准备的策略性提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接，改用安全协议（如 https）。 |

### 维护评价

*   **创建时间**：插件于 2020 年随 UE5 源码引入，已有约 5 年历史。
*   **更新频率**：自 2023 年 5 月后，再无针对此插件目录的独立功能性提交。最近的几次更新均为大范围引擎重构（如头文件清理、链接优化）的附带改动。
*   **功能状态**：插件提供的功能（层查询、添加、移除）非常基础且稳定。自创建以来，其核心 API（`GetActors`, `AddActorToLayer`, `RemoveActorFromLayer`）从未改变。
*   **总结**：这是一个**维护中但基本处于功能冻结状态**的插件。它的代码简洁、功能明确，没有已知的严重问题。由于其功能的稳定性，Epic 可能认为其已足够完善，无需频繁更新。可以放心使用，但不要期待新功能。如果超过 1 年没有实质性更新，通常意味着功能已趋稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities)
- [官方文档]( ) （.uplugin 中未提供）
- [测试用例]( ) （未在提供的信息中发现）