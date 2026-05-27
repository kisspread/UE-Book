# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（组件资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件解决了程序化内容生成框架 (PCG) 与网格分区系统 (Mesh Partition) 之间的数据互通问题。它的核心目的是：**让 PCG 能够高效地采样、查询和使用由 Mesh Partition 系统生成的网格数据**。

具体来说，当您使用 Mesh Partition 系统从一个大型源网格（如地形或巨型建筑模型）中“分区”并构建出多个较小的、优化的网格（Sections）后，PCG 通常需要在这些网格的表面或体积内进行采样（例如放置植被、石头）。如果没有互操作性，PCG 可能无法直接获取这些已构建网格的精确几何数据（如位置、法线、曲率）来进行计算。

这个插件通过提供适配器组件，在构建完成后为网格数据创建优化的内部表示（如动态网格及其空间索引树），从而允许 PCG 系统在编辑器和运行时直接、高效地访问这些数据。

## 使用场景

- **开放世界地形管理**：您使用 Mesh Partition 将一个巨大的地形网格分割成多个区块（Chunks），并希望 PCG 系统能自动在每个区块的表面根据法线、坡度等信息放置正确的植被和岩石。
- **程序化城市生成**：您有一个由大型预制件（如整个街区）组成的网格，通过 Mesh Partition 进行优化和分区。您希望 PCG 在这些分区后的建筑表面精确地生成窗户、广告牌、空调外机等元素。
- **任何需要 PCG 访问预构建的、分区后网格数据的场景**：只要您的内容管线涉及先用 Mesh Partition 处理网格，再用 PCG 在其上生成内容，就需要此插件。

## 蓝图用法

该插件主要通过一个特定的组件来扩展 Mesh Partition 的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mesh Partition PCG Adapter Component` | 一个修饰器组件，添加到使用 Mesh Partition 的 Actor 上。它在网格构建完成后，自动为 PCG 系统准备所需的数据缓存（FDynamicMesh 和空间查询树）。 | `UPCGAdapterComponent` |

### 使用示例（蓝图描述）

1.  在您的场景中，确保有一个使用了 `Mesh Partition` 组件的 Actor（例如一个大型静态网格体 Actor）。
2.  在该 Actor 的组件列表中，添加 `Mesh Partition PCG Adapter Component`。
3.  当 Mesh Partition 系统完成网格的构建和分区后，此适配器组件会自动运行，为每个生成的网格区块创建 PCG 可用的数据。
4.  在您的 PCG 图中，使用标准的 PCG 节点（如 `Surface Sampler`，`Get Mesh Data` 等）进行采样时，它们将能够自动检测到由该适配器生成的数据，并将其作为采样源。

## C++ 用法

在 C++ 中，主要的集成点是 `UPCGAdapterComponent`，您通常需要以编程方式将其实例添加到运行 Mesh Partition 的 Actor 上。

### 头文件引入

```cpp
#include "MeshPartitionPCGAdapterComponent.h"
```

### 基本用法

以下代码片段展示了如何在代码中创建并配置该适配器组件（基于 `UPCGAdapterComponent` 的职责推断）：

```cpp
// 假设我们有一个 AActor* ActorUsingMeshPartition，它已经添加了 MeshPartition 组件
// 并且已经设置好了源网格和分区设置。

// 在构造函数或初始化函数中添加适配器组件
UPCGAdapterComponent* PCGAdapter = NewObject<UPCGAdapterComponent>(ActorUsingMeshPartition);
PCGAdapter->RegisterComponent(); // 如果需要立即注册

// 通常，适配器组件的配置（如属性）在蓝图中完成更直观。
// 它的 PostBuildSectionMesh 回调会在 Mesh Partition 完成每个区块构建后由系统自动调用。
```

### 进阶用法

该适配器的主要工作发生在其 `PostBuildSectionMesh` 虚函数中。如果您需要扩展其功能，可以创建子类：

```cpp
// MyCustomPCGAdapter.h
#pragma once
#include "MeshPartitionPCGAdapterComponent.h"
#include "MyCustomPCGAdapter.generated.h"

UCLASS(meta=(BlueprintSpawnableComponent, DisplayName = "My Custom PCG Adapter"))
class UMyCustomPCGAdapter : public UPCGAdapterComponent
{
    GENERATED_BODY()

public:
    virtual void PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh) override
    {
        // 首先调用父类实现，完成标准的 PCG 数据缓存生成
        Super::PostBuildSectionMesh(InSection, InBuiltMesh);

        // 在此添加自定义逻辑，例如：
        // - 为每个区块的网格计算额外的自定义属性。
        // - 触发自定义的后处理流程。
        UE_LOG(LogTemp, Log, TEXT("Custom processing after mesh build for section: %s"), *InSection->GetName());
    }
};
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在代码中使用该适配器组件。

```cpp
// MyMeshPartitionActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMeshPartitionActor.generated.h"

class UMeshPartitionComponent;
class UPCGAdapterComponent;

UCLASS()
class AMyMeshPartitionActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMeshPartitionActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UMeshPartitionComponent* MeshPartitionComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UPCGAdapterComponent* PCGAdapterComponent;
};
```

```cpp
// MyMeshPartitionActor.cpp
#include "MyMeshPartitionActor.h"
#include "MeshPartitionComponent.h" // 来自 MeshPartition 插件
#include "MeshPartitionPCGAdapterComponent.h"

AMyMeshPartitionActor::AMyMeshPartitionActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建 Mesh Partition 组件
    MeshPartitionComponent = CreateDefaultSubobject<UMeshPartitionComponent>(TEXT("MeshPartition"));
    RootComponent = MeshPartitionComponent;

    // 创建 PCG 适配器组件，它会自动附加到同一个 Actor 上
    PCGAdapterComponent = CreateDefaultSubobject<UPCGAdapterComponent>(TEXT("PCGAdapter"));
    // 适配器组件需要与 Mesh Partition 组件协同工作，无需额外附加
}

void AMyMeshPartitionActor::BeginPlay()
{
    Super::BeginPlay();
    // 在 BeginPlay 时，如果网格已经构建完成，适配器可能已经准备好了数据。
    // 更多初始化逻辑可在此添加。
}
```

## 模块依赖

从插件的 `.uplugin` 和构建文件推断，要使用此插件，您的模块需要依赖以下 **独特** 的模块：

| 模块 | 用途 |
|---|---|
| `MeshPartition` | 提供网格分区系统的核心功能，如 `UMeshPartitionComponent` 和 `FMeshData`。 |
| `PCG` | 提供程序化内容生成框架的核心类和上下文。 |
| `PCGMeshPartitionInterop` | 本插件的运行时模块，提供核心适配器逻辑。 |
| `PCGMeshPartitionInteropEditor` | 本插件的编辑器模块，提供数据可视化、设置和编辑器特定功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复了BakeMesh相关节点读取已销毁的RHI资源导致的崩溃。 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 增加了“烘焙网格地形剖面网格”节点。 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 优化了“获取网格地形剖面”节点，在修饰器更改时能正确刷新。 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复了将压缩纹理错误地绑定为UAV导致的GPU崩溃。 |

### 维护评价

- **状态**：**活跃维护中**。
- **创建时间**：创建于 2026 年 3 月，至今不足 1 年，是一个非常新的插件。
- **更新频率**：近期（2026年5月）有多次功能性更新和 bug 修复，显示正在积极开发和完善。
- **实验性**：该插件被明确标记为 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`。这意味着它功能可能尚未稳定，API 可能变化，Epic 不建议在生产环境中作为核心功能依赖。请仅在实验性项目或愿意承担更新风险的场景中使用。
- **推荐**：对于需要在 **实验性项目** 中实现 PCG 与网格分区数据互操作的开发者，可以尝试使用并关注其更新。对于追求稳定性的项目，建议观望或将其视为参考实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG 框架通用文档)