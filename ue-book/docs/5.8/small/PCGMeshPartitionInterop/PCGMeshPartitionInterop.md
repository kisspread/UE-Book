# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区PCG桥接 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、PCG节点） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

这个插件的核心功能是建立 **PCG（程序化内容生成）框架** 与 **Mesh Partition（网格分区）系统** 之间的双向数据桥梁。它解决了两个关键问题：

1.  **数据读取 (PCG -> Mesh Partition)**：允许 PCG 图表查询 Mesh Partition 系统中的几何体信息（如地形、大型建筑）。通过射线检测或空间查询，PCG 可以获取网格表面的位置、法线、UV 坐标等属性，从而在正确的位置和朝向上生成点、实例或其它内容。
2.  **数据写入 (PCG -> Mesh Partition)**：允许 PCG 图表通过生成并应用 **修改器 (Modifier)** 来反向影响 Mesh Partition 系统。例如，使用 PCG 生成的点来移动网格顶点、写入权重通道数据、或植入投影网格实例，从而实现程序化的地形塑形、纹理绘制或细节添加。

简而言之，它让 PCG 不仅能“读取”大型程序化网格世界，还能“写入”并改变这个世界。

## 使用场景

*   **程序化地形与环境生成**：你使用 Mesh Partition 创建了一个大型可编辑地形。现在想用 PCG 在上面程序化地生成树木、岩石或道路。你需要 **PCG Query** 节点来采样地形表面位置，以确保生成物附着在地面上。
*   **程序化地形塑形**：你希望根据某种规则（如噪声函数、或依据已有的植被分布）动态调整地形高度或形状。你可以使用 PCG 生成点，然后通过 **Mesh Partition Write** 节点将这些点作为源/目标位置，驱动网格顶点移动。
*   **程序化纹理/权重绘制**：你正在制作一个支持多层纹理混合的地形。希望 PCG 能根据生物群落、海拔等规则，自动将混合权重（如“草地”、“岩石”通道的权重）绘制到地形网格上。这可以通过 **Sculpt Layer Write** 或 **Write** 节点的通道写入功能实现。
*   **动态投影与实例化**：需要在地形表面特定区域（如道路、平台）上投影网格或实例化物体。使用 **Projection Spawner** 或 **Patch Instance Spawner** 节点，根据 PCG 点的属性来放置和控制这些修改器实例。

## 蓝图用法

插件的核心蓝图 API 集中在数据采样和 PCG 节点上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sample Point` | 在 Mesh Partition 数据上采样一个点，返回位置、法线等 | `UPCGMeshPartitionData` |
| `Create Point Data` | 将 Mesh Partition 数据（在指定边界内）转换为 PCG 点数据 | `UPCGMeshPartitionData` |

### 核心 PCG 节点（设置类）

这些类在 PCG 图表编辑器中作为节点使用：

| 功能分类 | 节点设置类 | 节点名（在编辑器中） |
|---|---|---|
| **查询数据** | `UPCGQuerySettings` | Mesh Partition Query |
| **查询地形段** | `UPCGGetMeshTerrainSectionSettings` | Get Mesh Terrain Section |
| **获取通道纹理** | `UPCGGetMeshTerrainSectionChannelTexturesSettings` | Get Mesh Terrain Section Channel Textures |
| **获取植被类型** | `UPCGGetMeshPartitionGrassTypesSettings` | Get Mesh Partition Grass Types |
| **获取像素尺寸** | `UPCGGetMeshPartitionTexelSizesSettings` | Get Mesh Partition Texel Sizes |
| **烘焙网格纹理** | `UPCGGBakeMeshTerrainSectionMeshSettings` | Bake Mesh Terrain Section Mesh |
| **写入顶点/通道** | `UPCGWriteSettings` | Mesh Partition Write |
| **雕刻层写入** | `UPCGSculptLayerWriteSettings` | Mesh Partition Sculpt Layer Write |
| **生成投影修改器** | `UPCGProjectionSpawnerSettings` | Mesh Partition Projection Instance Spawner |
| **生成斑块修改器** | `UPCGPatchInstanceSpawnerSettings` | Mesh Partition Patch Instance Spawner |

### 使用示例（蓝图描述）

**示例：在地形表面采样位置来放置物体**

1.  在 PCG 图表中，添加一个 **Get Mesh Terrain Section** 节点来获取地形段数据。
2.  将其输出连接到一个 **Get Mesh Terrain Section Channel Textures** 节点，以获取纹理信息。
3.  添加一个 **Mesh Partition Query** 节点。
4.  配置 `Query Params`：设置 `Query Type` 为 `Final` 以获取最终网格。在 `Attributes` 分类下，勾选 `bGetImpactPoint` 和 `bGetImpactNormal` 以获取命中点的世界位置和法线。
5.  使用 `Sample Point` 函数（在代码中）或通过后续的 **Create Point Data** 节点，将查询结果转换为 PCG 点。
6.  将这些点用于生成物体（如 Static Mesh Spawner），确保物体放置在地形表面并朝向正确。

## C++ 用法

### 头文件引入

```cpp
#include "PCGMeshPartitionData.h" // 核心数据类
#include "PCGMeshPartitionQuery.h" // 查询节点相关
#include "PCGMeshPartitionWrite.h" // 写入节点相关
```

### 基本用法

从测试用例或使用场景中，我们通常需要先获取 `UPCGMeshPartitionData`，然后采样或创建点数据。

```cpp
// 假设我们有一个已经初始化好的 UPCGMeshPartitionData* MeshPartitionData
// （例如，通过 FPCGMeshPartitionElementContext 获得）

// 1. 设置查询参数
MeshPartition::FPCGQueryParams QueryParams;
QueryParams.QueryType = MeshPartition::EPCGQueryType::Final;
QueryParams.bGetImpactPoint = true;
QueryParams.bGetImpactNormal = true;

// 2. 采样单个点
FPCGPoint SampledPoint;
FTransform SampleTransform = FTransform(FVector(1000, 500, 0)); // 世界坐标系下的一个位置
FBox SampleBounds = FBox(SampleTransform.GetLocation() - FVector(100), SampleTransform.GetLocation() + FVector(100));

// 采样函数会执行射线检测或其他查询
if (MeshPartitionData->SamplePoint(SampleTransform, SampleBounds, SampledPoint, nullptr))
{
    // 使用 SampledPoint.Transform.GetLocation() 获取命中位置
    // 使用 SampledPoint.Transform.GetRotation() 获取法线方向（假设法线存储在旋转中）
}

// 3. 创建整个区域的点数据
FBox QueryBounds = FBox(FVector(-5000, -5000, 0), FVector(5000, 5000, 10000));
const UPCGPointData* PointData = MeshPartitionData->CreatePointData(Context, QueryBounds);

if (PointData)
{
    const TArray<FPCGPoint>& Points = PointData->GetPoints();
    for (const FPCGPoint& Point : Points)
    {
        // 遍历所有生成在指定边界内的点
    }
}
```
*来源推断：基于 `PCGMeshPartitionData.h` 中 `SamplePoint` 和 `CreatePointData` 的声明。*

### 进阶用法

C++ 中更常见的用途是与 PCG 框架深度集成，特别是当需要自定义 PCG 节点或处理修改器资源时。核心在于通过 `GetPCGMegaMeshModifierResource` 等辅助函数管理修改器组件的生命周期。

```cpp
#include "MeshPartitionPCGUtils.h" // 包含修改器资源管理

// 在一个自定义的 PCG Element 中，你可能需要获取或创建一个修改器资源
UPCGManagedModifierResource* ModifierResource = GetPCGMegaMeshModifierResource<UPCGManagedModifierResource>(Context, SettingsCrc, ModifierType, Priority, bSupportsComponentReset);

if (ModifierResource)
{
    // 获取或设置实际的修改器组件
    MeshPartition::UModifierComponent* ModComp = ModifierResource->GetComponent();
    if (!ModComp)
    {
        // 如果组件不存在，可能需要创建
        // ... 创建逻辑 ...
        ModifierResource->Initialize(NewModComp, SettingsCrc);
    }

    // 使用 ModifierComponent 进行网格修改操作
    // ... ModComp->SetSomeParameter(...); ...
}
```
*来源：基于 `MeshPartitionPCGUtils.h` 中 `UPCGManagedModifierResource` 的声明和使用模式推断。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义 Actor 中集成 PCG 组件，并触发一个使用 `PCGMeshPartitionQuery` 节点的 PCG 图表。

```cpp
// MyPCGActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PCGComponent.h"
#include "MyPCGActor.generated.h"

UCLASS()
class AMyPCGActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPCGActor();

protected:
    virtual void BeginPlay() override;

    // PCG 组件，用于驱动程序化生成
    UPROPERTY(VisibleAnywhere, Category = "PCG")
    TObjectPtr<UPCGComponent> PCGComponent;

    // 触发 PCG 生成的函数
    UFUNCTION(BlueprintCallable, Category = "PCG")
    void TriggerPCGGeneration();
};

// MyPCGActor.cpp
#include "MyPCGActor.h"
#include "PCGGraph.h"
#include "PCGSubsystem.h"

AMyPCGActor::AMyPCGActor()
{
    PCGComponent = CreateDefaultSubobject<UPCGComponent>(TEXT("PCGComponent"));
    PCGComponent->SetIsPartitioned(false); // 根据需要设置
    // 设置一个包含 “Mesh Partition Query” 节点的 PCG 图表资产
    // PCGComponent->SetGraph(LoadObject<UPCGGraph>(nullptr, TEXT("/Game/PCGGraphs/PG_MyMeshPartitionQuery")));
}

void AMyPCGActor::BeginPlay()
{
    Super::BeginPlay();
    // 游戏开始时可以自动生成，或由其他逻辑触发
    // PCGComponent->Generate();
}

void AMyPCGActor::TriggerPCGGeneration()
{
    if (PCGComponent && PCGComponent->GetGraph())
    {
        // 清理并重新生成，确保应用最新的 Mesh Partition 数据
        PCGComponent->Cleanup();
        PCGComponent->Generate();
    }
}
```

## 模块依赖

使用此插件时，你的游戏模块需要在 `.Build.cs` 文件中添加以下独特依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架核心模块 |
| `MeshPartition` | 网格分区系统核心模块 |
| `PCGGeometryScriptInterop` | PCG 与 Geometry Script 的桥接，可能用于网格处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复烘焙节点读取未驻留 RHI 资源导致的崩溃。 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增“烘焙地形段网格”节点，可将网格渲染为纹理。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 在获取地形段节点中，跟踪最终层以在修改器变化时刷新。 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复将压缩纹理绑定为 UAV 导致的 GPU 崩溃。 |

### 维护评价

*   **创建时间**：插件于 **2026年3月** 创建，非常新。
*   **维护活跃度**：**非常活跃**。从提交记录看，在 **2026年5月** 仍有密集的功能开发（新增节点）和关键性 Bug 修复。
*   **状态**：**实验性**（`IsExperimentalVersion: true`），且**默认禁用**（`EnabledByDefault: false`）。这表明它是 Epic 内部正在积极开发但尚未稳定的前沿功能。
*   **推荐度**：适合对最新 PCG 与网格分区集成技术有探索兴趣，或正在开发需要该特定功能的项目的开发者。由于处于实验阶段，在生产项目中使用需谨慎，可能面临 API 变更、不完善或性能问题。建议关注其后续的版本迭代。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
*   [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop/Tests) （如果存在）