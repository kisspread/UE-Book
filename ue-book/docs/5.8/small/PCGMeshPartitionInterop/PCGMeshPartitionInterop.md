# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件旨在为 **PCG (Procedural Content Generation)** 框架与 **Mesh Partition (网格分区，又称 Mega Mesh)** 系统之间建立桥梁。它解决的核心问题是：**如何在 PCG 生成流程中程序化地采样、修改和查询由网格分区系统构建的大型网格（Mega Mesh）**。

Mesh Partition 系统用于管理大型、可变形的地形或建筑网格，并支持基于层的修改器栈。本插件通过提供专门的 PCG 节点和数据类型，允许 PCG 图：
1.  **查询** Mega Mesh 的表面信息（如高度、法线、权重通道），用于生成点集（如植被、道具）。
2.  **写入** 数据到 Mega Mesh 的修改器中，从而动态地变形或绘制权重。
3.  **监听** Mega Mesh 层的变更，以触发 PCG 图的重新生成。

它使得开放世界内容生成能够与动态修改的网格地形或建筑结构进行深度交互。

## 使用场景

-   你需要基于一个大型、可程序化修改的网格（如动态地形）生成植被或建筑群 → 使用 `Mesh Partition Query` 节点采样表面。
-   你需要通过 PCG 图将散布的物体“绘制”或“雕刻”到网格表面上 → 使用 `Mesh Partition Write` 或 `Sculpt Layer Write` 节点。
-   你需要将预制的网格模型（如岩石、树木模型）投影到 Mega Mesh 表面上，并遵循其法线 → 使用 `Projection Instance Spawner` 节点。
-   你的 PCG 流程需要在 Mega Mesh 的某个修改层完成后才能执行 → 使用基于层的监听选择键（`FPCGLayerSelectionKey`）。

## 蓝图用法

本插件的核心功能通过 **PCG 图节点** 在蓝图编辑器中使用。这些节点基于源码中的 `UPCGSettings` 类，提供了丰富的参数供调整。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mesh Partition Query` | 从 Mega Mesh 中采样表面数据（点、法线、通道）并输出为 PCG 点集。 | `UPCGQuerySettings` |
| `Mesh Partition Write` | 将 PCG 点数据写入到 Mega Mesh 的指定修改器中，用于移动顶点或设置权重通道。 | `UPCGWriteSettings` |
| `Mesh Partition Sculpt Layer Write` | 通过雕刻层修改器直接编辑 Mega Mesh 的顶点位置和权重通道。 | `UPCGSculptLayerWriteSettings` |
| `Projection Instance Spawner` | 将动态网格数据（如模型）作为实例投影到 Mega Mesh 表面上。 | `UPCGProjectionSpawnerSettings` |
| `Patch Instance Spawner` | 在 Mega Mesh 表面上基于点数据生成“补丁”形状的修改器实例。 | `UPCGPatchInstanceSpawnerSettings` |
| `Get Mesh Terrain Section` | 获取与生成体积重叠的网格地形分区数据。 | `UPCGGetMeshTerrainSectionSettings` |
| `Get Mesh Partition Grass Types` | 从网格分区定义的材质中读取景观草地类型信息。 | `UPCGGetMeshPartitionGrassTypesSettings` |
| `Bake Mesh Terrain Section Mesh` | 将网格地形分区的网格通过 UV 展开渲染到纹理中。 | `UPGBakeMeshTerrainSectionMeshSettings` |

### 使用示例（蓝图描述）

在 PCG 图中，典型流程如下：

1.  **采样并生成点**：添加一个 `Mesh Partition Query` 节点。在节点的 `QueryParams` 设置中，指定查询类型（如 `Base` 或 `Final`）、射线参数和所需通道。将其输出连接到需要基于表面生成内容的后续节点（如筛选器、点操作器）。
2.  **修改网格**：添加一个 `Mesh Partition Write` 节点。通过输入引脚连接一个包含点数据（或包含源/目标位置属性的属性集）的 PCG 数据流。在节点设置中指定要影响的 Mega Mesh Actor 和修改器参数。
3.  **响应变更**：对于需要实时更新的 PCG 图，在图的触发器或属性绑定中，可以设置监听由 `FPCGLayerSelectionKey` 或 `FPCGGlobalSelectionKey` 标识的事件，当对应的 Mega Mesh 层发生变化时自动重新生成图。

## C++ 用法

对于需要高级控制或集成到自定义系统中的情况，可以通过 C++ 使用本插件提供的数据类和组件。

### 头文件引入

```cpp
#include "PCGMeshPartitionInteropModule.h"
#include "PCGMeshPartitionData.h"
#include "PCGDataComponent.h"
```

### 基本用法

以下示例展示了如何手动创建和使用一个 `UPCGMeshPartitionData` 对象来执行查询。
```cpp
// 假设你已有一个 UWorld、变换和包围盒
UWorld* MyWorld = GetWorld();
FTransform MyTransform = ...;
FBox MyBounds = ...;

// 创建数据对象
UPCGMeshPartitionData* PartitionData = NewObject<UPCGMeshPartitionData>();

// 配置查询参数
MeshPartition::FPCGQueryParams& Params = PartitionData->QueryParams;
Params.QueryType = MeshPartition::EPCGQueryType::Final;
Params.bGetImpactPoint = true;
Params.bGetImpactNormal = true;
// ... 设置其他参数

// 初始化（内部会开始异步收集 Section 数据）
PartitionData->Initialize(nullptr /* InPCGContext */, MyWorld, MyTransform, MyBounds);

// 等待数据准备就绪（简化示例，实际需要检查 IsDataReady）
// 注意：在游戏线程中轮询或使用回调
if (PartitionData->IsDataReady())
{
    // 执行一次采样
    FPCGPoint SampledPoint;
    UPCGMetadata* SampledMetadata = nullptr;
    FTransform SampleTransform = ...;
    FBox SampleBounds = ...;
    
    bool bHit = PartitionData->SamplePoint(SampleTransform, SampleBounds, SampledPoint, SampledMetadata);
    if (bHit)
    {
        // 使用采样到的点数据
        FVector ImpactLocation = SampledPoint.Transform.GetLocation();
        // ... 处理其他属性
    }
}
```
*（参考 `Private/Data/PCGMeshPartitionData.h` 中的 `UPCGMeshPartitionData` 类定义）*

### 进阶用法

监听 Mega Mesh 的层变化事件，以触发自定义逻辑。
```cpp
#include "PCGMeshPartitionSelectionKey.h"

// 在某个需要监听的上下文类（如自定义的 PCG Settings 或 Manager）中
FPCGLayerSelectionKey MyListenerKey(
    MeshPartition::EPCGQueryType::Intermediate,
    FName("MyLayer"),
    0.0, // SubPriority
    false,
    EPCGLayerSelectionKeyType::Listener // 标记为监听键
);

// 注册到 PCG 的选择系统（具体 API 需参考 PCG 框架）
// 当名为 “MyLayer” 的层或更高层级发生修改时，PCG 框架会通过此键通知依赖的节点进行重新生成。
```
*（参考 `Private/Data/PCGMeshPartitionSelectionKey.h` 中的 `FPCGLayerSelectionKey` 定义）*

## Demo 示例

一个最小的 PCG 图操作示例，展示如何在 C++ 中配置并执行一个查询节点。
```cpp
// MegaMeshDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PCGMeshPartitionQuery.h"
#include "MegaMeshDemo.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMegaMeshDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    TSoftObjectPtr<AMeshPartition> TargetMegaMesh;

private:
    void ExecuteMeshQuery();

    UPROPERTY()
    TObjectPtr<UPCGQuerySettings> QuerySettings;
    
    UPROPERTY()
    TObjectPtr<FPCGMeshPartitionQueryElement> QueryElement;
};

// MegaMeshDemo.cpp
#include "MegaMeshDemo.h"
#include "MeshPartitionPCGUtils.h"

void UMegaMeshDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    ExecuteMeshQuery();
}

void UMegaMeshDemoComponent::ExecuteMeshQuery()
{
    if (!TargetMegaMesh.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("MegaMeshDemo: Target Mega Mesh is not valid."));
        return;
    }

    // 创建查询设置对象
    QuerySettings = NewObject<UPCGQuerySettings>(GetTransientPackage());
    QuerySettings->QueryParams.QueryType = MeshPartition::EPCGQueryType::Final;
    QuerySettings->QueryParams.bGetImpactPoint = true;

    // 创建执行元素
    QueryElement = new FPCGMeshPartitionQueryElement();

    // 创建执行上下文并初始化（需要手动管理生命周期）
    FPCGMeshPartitionElementContext* Context = static_cast<FPCGMeshPartitionElementContext*>(QueryElement->CreateContext());
    // ... 配置 Context（例如绑定到当前世界）

    // 执行查询（注意：实际执行是分帧和异步的，此为简化演示）
    QueryElement->ExecuteInternal(Context);
    
    // 从 Context 中获取结果
    if (Context->SurfaceData)
    {
        // 使用 QueryElement 生成的 SurfaceData 进行后续操作...
        // 例如，可以调用 SurfaceData->CreatePointData() 来获取查询结果点。
    }
    
    // 清理
    delete Context;
    QueryElement = nullptr;
}
```

## 模块依赖

要在你的模块中使用此插件的功能，需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心的 PCG 框架，所有 PCG 节点和数据类型的基础。 |
| `MeshPartition` | 网格分区（Mega Mesh）系统的核心模块，提供 `AMeshPartition`、修改器等基础类。 |
| `PCGGeometryScriptInterop` | 提供 PCG 与 Geometry Script 的互操作支持，本插件的某些几何处理功能可能依赖它。 |
| `PCGMeshPartitionInterop` | 本插件的运行时模块，包含数据类型、查询/写入元素等。如果你的模块需要在运行时与网格分区 PCG 数据交互，必须依赖此模块。 |
| `PCGMeshPartitionInteropEditor` | 本插件的编辑器模块。如果你的模块是一个编辑器工具，需要集成或扩展这些 PCG 节点，则依赖此模块。 |

**示例 Build.cs 片段**:
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "PCG",
    "MeshPartition",
    "PCGMeshPartitionInterop" // 如果需要运行时功能
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复了在烘焙网格属性或地形网格时，因读取未驻留RHI资源导致的崩溃。 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增“烘焙网格地形分区网格”节点，支持将网格渲染到纹理。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生的警告代码。 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 使“获取网格地形分区”节点能监听最终层修改器的变化以触发刷新。 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复了因将压缩纹理绑定为UAV（不支持）而导致的GPU崩溃。 |

### 维护评价

该插件于 **2026年3月** 创建，是**全新的实验性插件**。
从近期提交记录（截至2026年5月）来看，它正处于**非常活跃的开发阶段**。更新内容主要是**功能添加**（如新节点）和**稳定性修复**（关键崩溃修复、GPU兼容性问题）。

**注意事项**：
1.  **实验性**：该插件标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，这意味着其API和行为可能在未通知的情况下发生重大变更。
2.  **依赖关系**：它深度依赖同样可能处于实验阶段的 `MeshPartition` 插件。
3.  **推荐**：对于**研究、原型开发或内部项目**，如果希望利用PCG与大型可修改网格交互，可以谨慎尝试。对于**生产环境**，建议等待其从实验阶段毕业，或密切关注其变更日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop/Tests)（如果存在）