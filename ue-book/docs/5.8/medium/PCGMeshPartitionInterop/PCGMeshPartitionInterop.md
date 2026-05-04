# Procedural Content Generation Framework (PCG) Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

这个插件是 **PCG 框架**与 **Mesh Partition（Mega Mesh）系统**之间的桥梁。它解决的核心问题是：如何在 PCG 图中对 Mega Mesh 进行采样查询和程序化编辑。

具体来说，它提供了以下能力：

1. **查询 Mega Mesh**：通过射线投射从 Mega Mesh 表面采样数据（位置、法线、UV、权重通道等），将结果转换为 PCG 点数据，供后续 PCG 节点使用
2. **写入 Mega Mesh**：将 PCG 点数据中的位置偏移和权重通道值写回 Mega Mesh 的顶点，实现程序化地形编辑
3. **生成修改器**：在 PCG 图中动态创建 Mesh Partition 修改器（Patch 实例、投影实例、雕刻层），实现更复杂的网格变形
4. **变更监听**：当 Mega Mesh 的某个构建层发生变化时，自动触发 PCG 图的重新执行，实现响应式工作流

简而言之，没有这个插件，PCG 图无法直接与 Mega Mesh 交互；有了它，你可以在 PCG 中采样地形表面、放置植被、修改地形形状，并在地形变化时自动更新。

## 使用场景

- 你在使用 Mega Mesh 构建大型地形，需要在 PCG 中根据地形表面放置植被/道具 → 使用 **Mega Mesh Query** 节点采样表面
- 你需要通过 PCG 程序化地修改 Mega Mesh 顶点位置（如道路压平、河流侵蚀） → 使用 **Mega Mesh Write** 节点
- 你需要在 Mega Mesh 上生成 Patch 实例（如散布岩石、草地簇） → 使用 **Mega Mesh Patch Instance Spawner** 节点
- 你需要将一个网格投影到 Mega Mesh 表面（如将桥梁模型投影到地形） → 使用 **Mega Mesh Projection Instance Spawner** 节点
- 你需要在 Mega Mesh 上进行雕刻层写入（移动顶点并写入权重通道） → 使用 **Mega Mesh Sculpt Layer Write** 节点
- 你希望 Mega Mesh 的修改自动触发 PCG 图重新执行 → 使用 Selection Key 监听机制

## 蓝图用法

本插件主要通过 PCG 图节点使用，核心节点均为 `UPCGSettings` 子类，可在 PCG 编辑器中直接拖拽使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mega Mesh Query` | 从 Mega Mesh 表面射线采样，输出点数据（位置、法线、UV、权重等） | `UPCGQuerySettings` |
| `Mega Mesh Write` | 将 PCG 点数据的位置偏移和权重写入 Mega Mesh 顶点 | `UPCGWriteSettings` |
| `Mega Mesh Sculpt Layer Write` | 通过雕刻层修改器移动顶点并写入权重通道 | `UPCGSculptLayerWriteSettings` |
| `Mega Mesh Patch Instance Spawner` | 在 Mega Mesh 上生成 Patch 实例修改器 | `UPCGPatchInstanceSpawnerSettings` |
| `Mega Mesh Projection Instance Spawner` | 将网格投影到 Mega Mesh 表面生成修改器实例 | `UPCGProjectionSpawnerSettings` |

### 查询类型（EPCGQueryType）

| 类型 | 说明 | 运行时可用 |
|---|---|---|
| `Base` | 采样 Mega Mesh 的基础修改器（应用任何程序化修改之前） | ❌ |
| `Intermediate` | 采样到指定构建层和子优先级的中间状态 | ❌ |
| `IntermediateLayer` | 采样到指定构建层（不考虑子优先级）的中间状态 | ❌ |
| `Final` | 采样最终构建完成的 Mega Mesh（所有程序化修改之后） | ✅ |

### 使用示例（蓝图描述）

**场景：从 Mega Mesh 表面采样放置植被**

1. 在 PCG 图中添加一个 **Mega Mesh Query** 节点
2. 设置 `QueryParams`：
   - `QueryType` 设为 `Final`（采样最终结果）
   - `bGetImpactPoint = true`（获取命中位置）
   - `bGetImpactNormal = true`（获取命中法线，用于旋转）
   - `Channels` 添加需要的权重通道名称
3. 将 Query 节点的输出连接到 Surface Sampler 或其他生成节点
4. 输出的点数据包含表面位置、法线和通道权重，可直接用于植被散布

**场景：通过 PCG 修改 Mega Mesh 地形**

1. 准备包含源位置和目标位置的点数据（如从道路样条生成）
2. 添加 **Mega Mesh Write** 节点
3. 设置 `SourcePositionsAttribute` 和 `DestinationPositionsAttribute` 指向点数据中的属性
4. 设置 `Channels` 指定要写入的权重通道
5. 节点执行后会创建修改器组件，将顶点从源位置移动到目标位置

## C++ 用法

### 头文件引入

```cpp
#include "Data/PCGMeshPartitionData.h"
#include "Elements/PCGMeshPartitionQuery.h"
#include "Elements/PCGMeshPartitionWrite.h"
#include "MeshPartitionPCGUtils.h"
#include "MeshPartitionPCGDataComponent.h"
```

### 基本用法

**获取 PCG 管理的 Mega Mesh 修改器**（来自 `MeshPartitionPCGUtils.h`）

```cpp
// 在自定义 PCG Element 中获取或复用一个 Mega Mesh 修改器
// 来源: Private/MeshPartitionPCGUtils.h

#include "MeshPartitionPCGUtils.h"

// 在 PrepareDataInternal 中使用
bool bModifierWasReset = false;
MeshPartition::FGetPCGManagedMegaMeshModifierParams Params;
Params.PCGContext = Context;
Params.Element = this;
Params.MegaMesh = TargetMegaMeshActor;
Params.Layer = FName("MyLayer");
Params.Priority = 0.0;

// 获取指定类型的修改器，自动管理生命周期
UMyModifierClass* Modifier = UE::MeshPartition::Utils::GetPCGManagedMegaMeshModifier<UMyModifierClass>(
    Params, bModifierWasReset);

if (bModifierWasReset)
{
    // 修改器被重置，需要重新配置
    Modifier->ConfigureFromContext(Context);
}
```

**从点数据中提取顶点位置和权重**（来自 `MeshPartitionPCGUtils.h`）

```cpp
// 来源: Private/MeshPartitionPCGUtils.h

#include "MeshPartitionPCGUtils.h"

TArray<FVector3d> SourcePositions;
TArray<FVector3d> DestinationPositions;
TArray<TPair<FName, TArray<float>>> Weights;

UE::MeshPartition::Utils::FGatherNewVertexDataFromPointDataInputParams InputParams;
InputParams.PointInputs = PointDataInputs;  // 从 PCG 输入 pin 获取
InputParams.ChannelsIn = { FName("Grass"), FName("Rock") };
InputParams.SourcePositionsAttribute = TEXT("SourcePositions");
InputParams.DestPositionsAttribute = TEXT("DestinationPositions");
InputParams.ContextForLogging = Context;

bool bSuccess = UE::MeshPartition::Utils::GatherNewVertexDataFromPointData(
    InputParams,
    SourcePositions,
    &DestinationPositions,
    Weights);
```

### 进阶用法

**查找最近的 Mega Mesh Actor**（来自 `MeshPartitionPCGUtils.h`）

```cpp
// 来源: Private/MeshPartitionPCGUtils.h
// 当 PCG 图需要自动找到对应的 Mega Mesh 时使用

#include "MeshPartitionPCGUtils.h"

// 根据执行源（通常是 PCG Volume）的边界找到最近的 Mega Mesh
AMeshPartition* ClosestMesh = UE::MeshPartition::Utils::FindClosestMegaMesh(ExecutionSource);
if (ClosestMesh)
{
    // 使用找到的 Mega Mesh 进行后续操作
}
```

**使用 UPCGDataComponent 缓存网格数据**（来自 `Public/MeshPartitionPCGDataComponent.h`）

```cpp
// 来源: Public/MeshPartitionPCGDataComponent.h
// UPCGDataComponent 缓存已构建的 Mega Mesh 数据，避免重复转换

#include "MeshPartitionPCGDataComponent.h"

// 获取缓存的网格数据
TSharedPtr<const FMeshData> MeshData = DataComponent->GetMesh();

// 获取空间加速结构（异步构建）
TSharedPtr<FMeshABBTree3> Spatial = DataComponent->GetSpatial();

// 检查空间树是否构建完成
Tasks::FTask SpatialTask = DataComponent->GetSpatialBuildTask();
```

## Demo 示例

以下展示如何创建一个自定义 PCG Element，从 Mega Mesh 采样数据并写回修改：

```cpp
// MyMegaMeshModifierElement.h
#pragma once

#include "PCGSettings.h"
#include "Elements/PCGMeshPartitionModifierSpawnerElementBase.h"
#include "Elements/PCGTimeSlicedElementBase.h"

#include "MyMegaMeshModifierElement.generated.h"

UCLASS(BlueprintType, ClassGroup = (Procedural))
class UMyMegaMeshModifierSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName(TEXT("MyMegaMeshModifier")); }
    virtual FText GetDefaultNodeTitle() const override 
    { 
        return NSLOCTEXT("MyMegaMeshModifier", "Title", "My Mega Mesh Modifier"); 
    }
    virtual EPCGSettingsType GetType() const override { return EPCGSettingsType::Generic; }
#endif

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override 
    { 
        return Super::DefaultPointInputPinProperties(); 
    }
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override 
    { 
        return Super::DefaultPointOutputPinProperties(); 
    }
    virtual FPCGElementPtr CreateElement() const override;

public:
    UPROPERTY(EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    double Priority = 0.0;

    UPROPERTY(EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    FName Type = TEXT("MyModifier");
};

// MyMegaMeshModifierElement.cpp
#include "MyMegaMeshModifierElement.h"
#include "MeshPartitionPCGUtils.h"

struct FMyExecutionContext
{
    bool bSkipDueToReuse = false;
};

struct FMyIterationContext
{
    AActor* TargetActor = nullptr;
};

class FMyMegaMeshModifierElement 
    : public MeshPartition::TPCGMegaMeshModifierSpawnerElementBase<
        TPCGTimeSlicedElementBase<FMyExecutionContext, FMyIterationContext>>
{
protected:
    virtual bool PrepareDataInternal(FPCGContext* Context) const override
    {
        auto* MyContext = static_cast<FPCGTimeSlicedContext<FMyExecutionContext, FMyIterationContext>*>(Context);
        
        MeshPartition::FGetPCGManagedMegaMeshModifierParams Params;
        Params.PCGContext = Context;
        Params.Element = this;
        
        bool bModifierWasReset = false;
        auto* Modifier = UE::MeshPartition::Utils::GetPCGManagedMegaMeshModifier<
            MeshPartition::UModifierComponent>(UModifierComponent::StaticClass(), Params, bModifierWasReset);
        
        if (!Modifier)
        {
            return false;
        }
        
        MyContext->GetExecutionContext().bSkipDueToReuse = !bModifierWasReset;
        return true;
    }

    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        auto* MyContext = static_cast<FPCGTimeSlicedContext<FMyExecutionContext, FMyIterationContext>*>(Context);
        
        if (MyContext->GetExecutionContext().bSkipDueToReuse)
        {
            return true;  // 修改器未变化，跳过执行
        }
        
        // 执行实际的修改逻辑...
        return true;
    }
};

FPCGElementPtr UMyMegaMeshModifierSettings::CreateElement() const
{
    return MakeShared<FMyMegaMeshModifierElement>();
}
```

## 模块依赖

本插件依赖以下插件（在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `PCG` | PCG 框架核心，提供节点图、数据流、执行引擎 |
| `MeshPartition` | Mega Mesh 系统，提供网格分区、修改器、构建管线 |
| `PCGGeometryScriptInterop` | PCG 与 Geometry Script 的互操作，提供动态网格数据类型 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

由于该插件创建于 2026-03-05，属于全新插件，暂无历史 commit 记录可查。

### 维护评价

- **创建时间**：2026-03-05，非常新的插件
- **实验性标记**：`IsExperimentalVersion = true`，`EnabledByDefault = false`，明确标记为实验性
- **代码规模**：29 个源文件，结构完整，包含 Runtime 和 Editor 两个模块
- **API 成熟度**：代码中有大量 `#if WITH_EDITOR` 保护和 TODO 注释，表明 API 尚不稳定
- **功能完整度**：覆盖了查询、写入、Patch 生成、投影、雕刻层写入等核心场景

**综合评价**：这是一个处于**早期实验阶段**的插件。虽然功能覆盖面较广，但 API 可能在后续版本中发生重大变化。代码中的注释（如 SculptLayerWrite 中关于节点拆分的讨论）表明设计仍在迭代中。

⚠️ **警告**：此插件标记为实验性，不建议在生产环境中使用。API 和行为可能在后续 UE 版本中发生不兼容变更。

**推荐**：如果你正在探索 Mega Mesh + PCG 的工作流，可以尝试使用；但不要将其作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)