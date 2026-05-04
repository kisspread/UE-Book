# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件的核心功能是为 **Mesh Partition** 系统构建的网格提供与 **PCG (Procedural Content Generation) 框架** 的互操作性。它解决了一个具体问题：当使用 Mesh Partition 系统生成大型、复杂的环境网格（如地形、建筑群）后，如何让 PCG 框架能够高效地在这些网格的表面上进行采样（例如，撒点生成植被、岩石、装饰物等）。

插件通过一个关键组件 `UPCGAdapterComponent` 实现此功能。该组件作为 Mesh Partition 系统的修改器（Modifier），在网格构建完成后，会自动在最终的 Actor 上生成一个 `UPCGDataComponent`。这个数据组件内部缓存了构建好的 `FDynamicMesh` 及其空间索引（`FDynamicMeshAABBTree`），为 PCG 框架在编辑器和运行时进行表面采样提供了必要的数据结构和加速查询支持。

## 使用场景

-   **大型开放世界环境构建**：你使用 Mesh Partition 系统生成了一个由多个区块（Section）组成的庞大世界网格，现在需要使用 PCG 在这个世界的地表、建筑外墙等表面上程序化地放置树木、草丛、路灯或垃圾等资产。
-   **运行时动态内容生成**：你的游戏需要在运行时，基于玩家位置或游戏逻辑，动态地在由 Mesh Partition 生成的复杂网格表面上生成内容（如动态刷新的资源点、敌人刷新点）。
-   **需要精确表面采样**：PCG 框架默认的采样可能无法精确贴合 Mesh Partition 生成的复杂几何体，使用此插件可以确保采样点严格位于网格表面。

## 蓝图用法

该插件主要通过组件形式使用，其核心功能封装在 `UPCGAdapterComponent` 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mesh Partition PCG Adapter Component` | 作为组件添加到 Actor。它会自动监听 Mesh Partition 的构建事件，并在构建完成后生成 PCG 数据。 | `UPCGAdapterComponent` |

### 使用示例（蓝图描述）

1.  在你的 Mesh Partition Actor（或其子类）的蓝图中，添加 `Mesh Partition PCG Adapter Component` 组件。
2.  该组件无需额外配置。当 Mesh Partition 系统完成网格构建（例如，在编辑器中点击“构建”或游戏运行时完成生成）后，`UPCGAdapterComponent` 会自动执行 `PostBuildSectionMesh`。
3.  此时，该 Actor 上会自动生成一个 `UPCGDataComponent`，其中包含了构建好的动态网格数据。
4.  之后，你可以在任何 PCG 图表（Graph）中，使用 `Get PCG Data` 等节点引用该 Actor，PCG 框架便能利用缓存的网格数据进行表面采样。

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionPCGAdapterComponent.h"
```

### 基本用法

在 C++ 中，你可以直接创建或引用 `UPCGAdapterComponent`。通常，你不需要手动调用其方法，它作为修改器组件会自动响应 Mesh Partition 的构建流程。

```cpp
// 在某个 Actor 的构造函数或初始化函数中
UPCGAdapterComponent* PCGAdapter = CreateDefaultSubobject<UPCGAdapterComponent>(TEXT("PCGAdapter"));
// 该组件会自动注册为 Mesh Partition 的修改器，并在网格构建后生成 PCG 数据。
```

### 进阶用法

如果你需要自定义 PCG 数据生成后的逻辑，可以继承 `UPCGAdapterComponent` 并重写相关虚函数。例如，你可能想在 PCG 数据生成后触发一个自定义事件。

```cpp
// MyPCGAdapterComponent.h
#pragma once
#include "MeshPartitionPCGAdapterComponent.h"
#include "MyPCGAdapterComponent.generated.h"

UCLASS()
class UMyPCGAdapterComponent : public UPCGAdapterComponent
{
    GENERATED_BODY()

public:
    // 重写此函数，在 Mesh Partition 构建完成后添加自定义逻辑
    virtual void PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh) override;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPCGDataReady);

    // 蓝图可绑定的事件，当 PCG 数据准备好后广播
    UPROPERTY(BlueprintAssignable, Category = "PCG")
    FOnPCGDataReady OnPCGDataReady;
};

// MyPCGAdapterComponent.cpp
#include "MyPCGAdapterComponent.h"

void UMyPCGAdapterComponent::PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh)
{
    // 首先调用父类实现，确保 PCG 数据组件被正确生成
    Super::PostBuildSectionMesh(InSection, InBuiltMesh);

    // 执行自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("PCG Data has been generated for section: %s"), *InSection->GetName());

    // 广播事件
    OnPCGDataReady.Broadcast();
}
```

## Demo 示例

以下是一个最小示例，展示如何创建一个使用 PCG 适配器组件的 Actor。

```cpp
// MyMeshPartitionActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMeshPartitionActor.generated.h"

class UPCGAdapterComponent;

UCLASS()
class AMyMeshPartitionActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMeshPartitionActor();

    // 假设这里有一个 Mesh Partition 的主组件（例如 UMeshPartitionComponent）
    // UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh Partition")
    // UMeshPartitionComponent* MeshPartitionComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PCG")
    UPCGAdapterComponent* PCGAdapterComponent;
};

// MyMeshPartitionActor.cpp
#include "MyMeshPartitionActor.h"
#include "MeshPartitionPCGAdapterComponent.h"

AMyMeshPartitionActor::AMyMeshPartitionActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建 Mesh Partition 主组件（示例，具体类名取决于你的 Mesh Partition 实现）
    // MeshPartitionComponent = CreateDefaultSubobject<UMeshPartitionComponent>(TEXT("MeshPartition"));

    // 创建 PCG 适配器组件
    PCGAdapterComponent = CreateDefaultSubobject<UPCGAdapterComponent>(TEXT("PCGAdapter"));
    // 该组件会自动将其自身注册为 Mesh Partition 系统的修改器。
}
```

## 模块依赖

从插件的 `.uplugin` 文件和模块结构推断，使用此插件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架核心模块，提供 PCG 数据、图表、采样等基础功能。 |
| `MeshPartition` | Mesh Partition 系统核心模块，提供网格分区、构建和修改器组件基类。 |
| `PCGGeometryScriptInterop` | 提供 PCG 与 Geometry Script（动态网格）之间的互操作支持，是本插件功能实现的基础之一。 |

## 维护状态

### 近期更新

由于未提供具体的 Git 日志，无法列出近期的 commit 记录。插件创建于 2026 年 3 月，标记为实验性（`IsExperimentalVersion: true`）且默认未启用（`EnabledByDefault: false`）。

### 维护评价

-   **年龄与状态**：插件创建约 2 年，属于较新的实验性功能。
-   **活跃度**：作为实验性插件，其开发和维护状态可能较为活跃，但也可能随时发生重大变更或被废弃。由于缺乏近期更新记录，无法准确判断其当前活跃度。
-   **已知限制**：作为实验性功能，其 API 和行为可能不稳定，不建议在需要长期稳定支持的项目中作为核心依赖。
-   **推荐度**：如果你正在使用 Mesh Partition 和 PCG 框架，并且需要它们之间的互操作，可以尝试使用此插件。但需做好应对 API 变更的准备，并密切关注 Epic 的更新日志。对于生产环境，建议评估其稳定性或寻找替代方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
-   [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG 框架通用文档)