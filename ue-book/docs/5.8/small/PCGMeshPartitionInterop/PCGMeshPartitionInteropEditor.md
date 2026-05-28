# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、数据可视化） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

该插件是 **PCG 框架** 与 **网格分区（Mesh Partition）系统** 之间的桥梁。它的核心作用是将网格分区系统构建的几何体数据（如复杂地形网格）暴露给 PCG 系统，使得 PCG 节点（如采样、生成）可以直接基于这些网格的精确空间信息（位置、法线、密度等）进行操作，而无需用户手动转换数据。

具体来说，它解决的问题是：当使用“网格分区”系统将大型网格或地形分解为多个部分后，PCG 系统无法直接感知这些分区后的网格数据。此插件通过在网格分区的 Actor 上附加一个特定的适配器组件（`UPCGAdapterComponent`），在构建网格后，该组件会生成并缓存一个 `FDynamicMesh` 和对应的 `FAABBTree`。这些数据随后能被 PCG 系统用于运行时和编辑器内的精确采样。

## 使用场景

- **大型地形PCG生成**：你正在使用网格分区系统处理一片巨大的地形或城市网格，需要在其上根据坡度、朝向等精确几何信息生成植被、岩石或建筑装饰物。
- **网格感知内容生成**：你希望 PCG 节点能够直接“知道”一个复杂模型的表面形状，以便将物体贴合地放置在曲面上，而不是仅仅依赖简单的包围盒或表面点。
- **需要高精度PCG采样**：标准的PCG体积或表面采样器无法满足你对精度的要求，你需要访问底层的动态网格数据进行更复杂的逻辑判断。

## 蓝图用法

此插件的蓝图交互主要集中在**编辑器配置**和**组件行为**层面，核心运行时逻辑通常由PCG节点隐式调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshTerrainSectionDataPinColor` | （编辑器设置）配置PCG节点中“网格地形截面”数据类型引脚的颜色 | `UPCGMeshPartitionInteropEditorSettings` |

### 使用示例（蓝图描述）

1.  **在Actor上添加组件**：
    - 在场景中，为你通过网格分区系统生成的 Actor（或其子 Actor）添加 `UPCGAdapterComponent` 组件。
    - 该组件本身不需要在蓝图中调用，它的主要工作在网格分区构建流程的后处理阶段自动完成。

2.  **配置编辑器设置**：
    - 打开项目设置（Editor Preferences） -> Plugins -> PCG Mesh Partition Interop Editor Settings。
    - 可以调整 `Mesh Terrain Section Data Pin Color` 的颜色，这会影响PCG蓝图节点中相关数据引脚的显示颜色，便于区分。

3.  **与PCG图配合**：
    - 在 PCG 图表中，使用诸如 `Get Mesh Terrain Section` 或 `Bake Mesh Terrain Section Mesh` 等节点（由相关插件提供），这些节点能够自动发现并利用由 `UPCGAdapterComponent` 提供的缓存网格数据进行采样或烘焙。

## C++ 用法

该插件的C++接口主要供引擎内部或高级开发者在创建自定义网格分区修改器或PCG数据扩展时使用。

### 头文件引入

```cpp
#include "PCGMeshPartitionInteropEditorModule.h"
// 核心适配器组件头文件，注意其所在模块和编辑器限定
#include "MeshPartitionPCGAdapterComponent.h"
```

### 基本用法

以下示例展示了如何在一个自定义的网格分区修改器组件中，利用 `UPCGAdapterComponent` 的设计模式来附加PCG数据。

```cpp
// 来源：推断自 Public/MeshPartitionPCGAdapterComponent.h 的接口设计
// 假设你在编写自己的网格分区修改器

#include "MeshPartition/MeshData.h"
#include "MeshPartition/ModifierComponent.h"

UCLASS()
class UMyCustomMeshModifier : public MeshPartition::UModifierComponent
{
    GENERATED_BODY()

public:
    // 网格构建完成后的回调，类似于UPCGAdapterComponent::PostBuildSectionMesh
    virtual void PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh) override
    {
        // 1. 在这里，你可以访问构建完成的网格数据 InBuiltMesh
        // 2. 进行自定义处理，例如为PCG准备额外的元数据
        // 3. 最终，你可能需要创建一个类似FPCGMeshTerrainSectionData的资产
        //    并将其附加到 InSection Actor 上，以便PCG系统识别
        Super::PostBuildSectionMesh(InSection, InBuiltMesh);
    }

    virtual TArray<FBox> ComputeBounds() const override
    {
        // 返回组件影响的世界空间边界
        return Super::ComputeBounds();
    }
};
```

### 进阶用法

集成PCG可视化系统。该插件实现了自定义的PCG数据可视化器，这在开发PCG扩展时是常见模式。

```cpp
// 来源：Private/Visualizations/PCGMeshTerrainSectionDataVisualization.h
#include "PCGContext.h"
#include "PCGDataVisualization.h"

class FMyCustomPCGDataVisualization : public IPCGDataVisualization
{
public:
    virtual FPCGTableVisualizerInfo GetTableVisualizerInfoWithDomain(const UPCGData* Data, const FPCGMetadataDomainID& DomainID) const override
    {
        FPCGTableVisualizerInfo Info;
        // 1. 将输入的 UPCGData* 转换为你自己的数据类型，如 const UPCGMyData* MyData = Cast<UPCGMyData>(Data);
        // 2. 定义表格列，用于在编辑器“PCG数据表格”中显示信息
        // Info.HeaderNames.Add(TEXT("Attribute1"));
        // Info.HeaderNames.Add(TEXT("Position"));
        // 3. 填充行数据
        // for (const auto& Point : MyData->GetPoints())
        // {
        //     TArray<FString> Row;
        //     Row.Add(Point.Attribute1);
        //     Row.Add(Point.Transform.GetLocation().ToString());
        //     Info.Rows.Add(MoveTemp(Row));
        // }
        return Info;
    }

    // ExecuteDebugDisplay 用于绘制3D调试信息，如点、线
    virtual void ExecuteDebugDisplay(FPCGContext* Context, const UPCGSettingsInterface* SettingsInterface, const UPCGData* Data, AActor* TargetActor) const override {}
};
```

## Demo 示例

一个展示如何创建一个最小化的网格分区PCG适配器组件。

**PCGAdapterComponentDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MeshPartition/ModifierComponent.h"
#include "PCGAdapterComponentDemo.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UPCGAdapterComponentDemo : public MeshPartition::UModifierComponent
{
    GENERATED_BODY()

public:
    UPCGAdapterComponentDemo();

    virtual void PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh) override;
    virtual TArray<FBox> ComputeBounds() const override;
};
```

**PCGAdapterComponentDemo.cpp**
```cpp
#include "PCGAdapterComponentDemo.h"
#include "MeshPartition/MeshData.h"
// 假设存在一个函数可以将网格数据转为PCG可读格式
// #include "PCGMeshPartitionInterop/PCGMeshTerrainSectionData.h"

UPCGAdapterComponentDemo::UPCGAdapterComponentDemo()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UPCGAdapterComponentDemo::PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh)
{
    Super::PostBuildSectionMesh(InSection, InBuiltMesh);
    
    // 核心逻辑：将构建好的网格数据转换并存储，供PCG系统使用
    // 例如：
    // FPCGMeshTerrainSectionData* SectionData = NewObject<FPCGMeshTerrainSectionData>(InSection);
    // SectionData->InitializeFromMeshData(InBuiltMesh);
    // 将 SectionData 附加到 Actor 的元数据或作为子对象管理。
    
    UE_LOG(LogTemp, Log, TEXT("PCGAdapterDemo: Mesh built with %d vertices. Preparing for PCG."), InBuiltMesh.Vertices.Num());
}

TArray<FBox> UPCGAdapterComponentDemo::ComputeBounds() const
{
    // 返回一个大致的边界盒，实际应根据缓存的网格数据计算
    return { FBox(FVector(-1000, -1000, -100), FVector(1000, 1000, 100)) };
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG框架核心，提供数据、节点、上下文等基础类型 |
| `MeshPartition` | 网格分区系统核心，提供 `UModifierComponent`, `FMeshData` 等基础类 |
| `PCGGeometryScriptInterop` | 提供与几何体脚本交互的功能，可能用于网格数据处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复烘焙网格属性/地形截面节点因读取不支持的RHI资源导致的崩溃 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增“烘焙网格地形截面”PCG节点 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的警告 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 在“获取网格地形截面”节点中跟踪最终层键值，以便修改器变化时刷新 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复因将压缩纹理绑定为不支持的UAV导致的GPU崩溃 |

### 维护评价

该插件**正处于活跃的实验性开发阶段**。创建于2026年3月，非常新。最近一个月（2026年5月）有多次更新，内容集中在**新增核心PCG节点**和**修复关键运行时/GPU崩溃**上，表明团队正在积极完善其功能并提升稳定性。

由于其`.uplugin`中明确标记为`IsExperimentalVersion: true`且`EnabledByDefault: false`，这意味着API和功能在未来版本中可能发生不兼容的变化。目前**仅推荐用于实验性项目或技术预研**，不建议在需要长期稳定维护的项目中使用。但鉴于其与PCG主框架的紧密集成和近期的活跃开发，它是一个值得关注的功能预览。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- 测试用例：目前未在提供的信息中发现插件专属的测试文件，相关功能测试可能集成在PCG框架的主测试套件中。