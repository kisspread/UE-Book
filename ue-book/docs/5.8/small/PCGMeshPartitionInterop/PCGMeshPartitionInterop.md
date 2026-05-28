# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | PCG 网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

本插件是 **PCG（程序化内容生成框架）** 与 **Mesh Partition（网格分区/大网格地形）** 之间的桥梁层。它允许你在 PCG 图中直接采样、编辑和驱动 Mesh Partition 地形系统。

核心功能包括：

1. **查询（Query）**：通过射线投射采样 Mega Mesh 的表面数据，获取高度、法线、UV 等信息，并将结果转换为 PCG 点数据
2. **写入（Write）**：通过 PCG 点数据驱动 Mega Mesh 顶点位移和权重通道写入
3. **雕刻层写入（Sculpt Layer Write）**：基于 PCG 数据创建 Sculpt Layer 修饰器，对地形进行精细变形
4. **投影实例生成（Projection Spawner）**：在 Mega Mesh 上投射网格实例（如岩石、碎片等）
5. **补丁实例生成（Patch Instance Spawner）**：在 Mega Mesh 表面生成补丁状修饰区域
6. **地形截面工具**：获取 Mesh Terrain Section 的 Actor 引用、通道纹理、草地类型、纹素尺寸等元数据
7. **烘焙工具**：将地形截面网格烘焙为纹理

简而言之：没有这个插件，PCG 无法感知或操作 Mesh Partition 地形；有了它，PCG 图可以完整地查询和编辑大网格地形。

## 使用场景

- 你有一个基于 Mesh Partition 的大网格地形系统，想用 PCG 在上面程序化放置植被、岩石、装饰物 → 用 **Mesh Partition Query** 节点采样地形表面
- 你想用 PCG 点数据驱动地形顶点位移（如压平道路、隆起山丘）→ 用 **Mesh Partition Write** 或 **Sculpt Layer Write** 节点
- 你想在地形上程序化投影网格实例（如散布碎石模型到地形表面）→ 用 **Projection Instance Spawner** 节点
- 你想获取 Mesh Terrain Section 的通道纹理用于后续 PCG 处理 → 用 **Get Mesh Terrain Section Channel Textures** 节点
- 你想从 Mesh Partition 材质定义中提取草地类型信息 → 用 **Get Mesh Partition Grass Types** 节点

## 蓝图用法

本插件的所有 PCG 节点都是 `UPCGSettings` 的子类，以蓝图类型暴露。它们不出现在普通蓝图函数列表中，而是作为 **PCG 图编辑器中的节点** 使用。

### 核心节点

| 节点（PCG 图中显示名） | 说明 | 所在类 |
|---|---|---|
| **Mesh Partition Query** | 射线采样 Mega Mesh 表面，输出 PCG 点数据 | `UPCGQuerySettings` |
| **Mesh Partition Write** | 将 PCG 点的位置/通道数据写入 Mega Mesh 顶点 | `UPCGWriteSettings` |
| **Mesh Partition Sculpt Layer Write** | 创建 Sculpt Layer 修饰器，基于 PCG 点数据变形地形 | `UPCGSculptLayerWriteSettings` |
| **Mesh Partition Projection Instance Spawner** | 在 Mega Mesh 上投射网格实例 | `UPCGProjectionSpawnerSettings` |
| **Mesh Partition Patch Instance Spawner** | 在 Mega Mesh 表面生成补丁修饰器 | `UPCGPatchInstanceSpawnerSettings` |
| **Get Mesh Terrain Section** | 获取与生成体积重叠的所有地形截面 | `UPCGGetMeshTerrainSectionSettings` |
| **Get Mesh Terrain Section Actor** | 获取地形截面对应的 Actor 软引用 | `UPCGGetMeshTerrainSectionActorSettings` |
| **Get Mesh Terrain Section Channel Textures** | 输出地形截面的烘焙通道纹理 | `UPCGGetMeshTerrainSectionChannelTexturesSettings` |
| **Bake Mesh Terrain Section Mesh** | 将地形截面网格通过 UV 展开烘焙为纹理 | `UPCGGBakeMeshTerrainSectionMeshSettings` |
| **Get Mesh Partition Grass Types** | 从 Mesh Partition 材质定义提取草地类型 | `UPCGGetMeshPartitionGrassTypesSettings` |
| **Get Mesh Partition Texel Sizes** | 获取通道纹理和材质缓存的纹素尺寸 | `UPCGGetMeshPartitionTexelSizesSettings` |

### Mesh Partition Query 节点参数

| 参数 | 类型 | 说明 |
|---|---|---|
| QueryType | 枚举 | 采样模式：`Base`（基础修饰器前）、`Intermediate`（中间层+子优先级）、`IntermediateLayer`（中间层）、`Final`（最终构建结果，运行时有效） |
| LayerName | FName | `Intermediate`/`IntermediateLayer` 模式下的目标层名称 |
| SubPriority | double | `Intermediate` 模式下的子优先级 |
| bInclusive | bool | 是否包含目标层/子优先级 |
| RayOrigin/Direction/Length | FVector/double | 射线参数（可选覆盖） |
| Channels | TArray\<FName\> | 要采样的通道列表 |
| bGetImpactPoint/Normal/Distance/FaceIndex/UVCoords | bool | 是否输出额外属性 |
| bRecomputeVertexNormals | bool | 是否重算顶点法线 |
| bAcceptAnyHitSection | bool | 是否接受任意命中截面（加速采样） |
| MegaMeshOverride | TSoftObjectPtr | 限定查询的 Mega Mesh Actor |

### 使用示例（PCG 图描述）

**采样地形并放置物体**：
1. 创建 **Mesh Partition Query** 节点
2. 设置 `QueryType = Final`，启用 `bGetImpactNormal` 用于旋转对齐
3. 连接 Query 的输出到 **Static Mesh Spawner** 节点
4. Spawner 使用 ImpactNormal 属性来旋转放置的物体，使其贴合地形表面

**驱动地形变形**：
1. 创建一组生成点（如通过 Noise 节点）
2. 连接到 **Mesh Partition Write** 节点
3. 设置 `SourcePositionsAttribute` 和 `DestinationPositionsAttribute`
4. Write 节点会生成 `SimpleWrite` 类型的修饰器，将顶点从源位置移动到目标位置

**投射网格实例到地形**：
1. 准备 Dynamic Mesh 输入（要投射的网格资产）和变换点
2. 连接到 **Projection Instance Spawner** 节点
3. 设置 `BlendMode`（Set/Add/Multiply 等）和 `HeightFalloff` 参数
4. 节点会在指定的 Mega Mesh 上创建 `InstancedProjectionModifier`

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "PCGMeshPartitionInteropModule.h"
#include "Data/PCGMeshPartitionData.h"

// 需要 MeshPartition 模块
#include "MeshPartition/MeshPartition.h"
```

### 基本用法 — 手动创建 PCGMeshPartitionData

从 `Private/Data/PCGMeshPartitionData.h` 提取的数据使用模式：

```cpp
// 创建 PCG 网格分区数据，用于自定义采样逻辑
UPCGMeshPartitionData* MeshPartitionData = NewObject<UPCGMeshPartitionData>();

// 初始化数据，关联到 PCG 组件和世界
FPCGMeshPartitionElementContext* Context = /* 从 PCG 执行上下文获取 */;
MeshPartitionData->Initialize(
    Context,
    InWorld,
    FTransform::Identity,  // 变换
    WorldBounds,           // 世界空间包围盒
    LocalBounds            // 本地空间包围盒
);

// 配置查询参数
MeshPartitionData->QueryParams.QueryType = MeshPartition::EPCGQueryType::Final;
MeshPartitionData->QueryParams.bGetImpactPoint = true;
MeshPartitionData->QueryParams.bGetImpactNormal = true;

// 检查数据是否就绪
if (MeshPartitionData->IsDataReady())
{
    // 执行采样
    FPCGPoint OutPoint;
    UPCGMetadata* OutMetadata = nullptr;
    FTransform SampleTransform = FTransform::Identity;
    FBox SampleBounds = FBox(FVector(-100), FVector(100));
    MeshPartitionData->SamplePoint(SampleTransform, SampleBounds, OutPoint, OutMetadata);
}
```

### 基本用法 — 采样点数据转换

```cpp
// 从 MeshPartitionData 生成点数据（批量采样）
const UPCGPointData* PointData = MeshPartitionData->CreatePointData(
    Context, 
    Bounds  // 采样范围
);

// 或生成 PointArrayData（更高效的数据结构）
const UPCGPointArrayData* PointArrayData = MeshPartitionData->CreatePointArrayData(
    Context, 
    Bounds
);
```

### 进阶用法 — 自定义 PCG 节点操作 Mesh Partition

从多个测试用例和节点实现中提取的模式：

```cpp
// 模式：管理 Mesh Partition 修饰器组件的生命周期
// 参考 Private/MeshPartitionPCGUtils.h

// 获取或创建受 PCG 管理的修饰器资源
UE::MeshPartition::UPCGManagedModifierResource* Resource = 
    GetPCGManagedMegaMeshModifierResource(/* settings crc */);

// 通过模板获取特定类型的修饰器组件
auto* ModifierComponent = Resource->GetComponent<MeshPartition::USimpleWriteModifier>();

// 标记资源为已使用（防止被回收）
Resource->MarkAsUsed();
```

```cpp
// 模式：获取 Mesh Terrain Section 的通道纹理
// 参考 Private/Elements/PCGGetMeshTerrainSectionChannelTextures.h

// 在 PCG 执行元素内部，通道纹理的获取流程：
// 1. 解析选中的通道名称
// 2. 请求纹理流送
// 3. 等待流送完成
// 4. 执行 GPU 合成（多通道合并为 Texture2DArray）
// 5. 输出 UPCGTexture2DArrayData 或 UPCGTextureData
```

## Demo 示例

以下展示一个自定义 PCG 元素，使用 `UPCGMeshPartitionData` 查询地形表面数据：

```cpp
// MyCustomMeshPartitionSampling.h
#pragma once

#include "CoreMinimal.h"
#include "PCGSettings.h"
#include "PCGContext.h"
#include "Elements/PCGTypedElement.h"
#include "Data/PCGMeshPartitionData.h"

UCLASS(BlueprintType, ClassGroup = (Procedural))
class UMyCustomSamplingSettings : public UPCGSettings
{
    GENERATED_BODY()

#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName(TEXT("CustomMeshPartitionSampling")); }
    virtual FText GetDefaultNodeTitle() const override
    {
        return NSLOCTEXT("MyPlugin", "NodeTitle", "Custom Mesh Partition Sampling");
    }
    virtual EPCGSettingsType GetType() const override { return EPCGSettingsType::Spatial; }
#endif

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override { return {}; }
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override
    {
        return DefaultPointOutputPinProperties();
    }
    virtual FPCGElementPtr CreateElement() const override;

public:
    /** 采样网格的 Actor 引用 */
    UPROPERTY(EditAnywhere, Category = Settings)
    TSoftObjectPtr<AMeshPartition> TargetMegaMesh;
};

// MyCustomMeshPartitionSampling.cpp
#include "MyCustomMeshPartitionSampling.h"
#include "PCGContext.h"
#include "Data/PCGPointData.h"

class FMyCustomSamplingElement : public IPCGElement
{
public:
    virtual bool CanExecuteOnlyOnMainThread(FPCGContext* Context) const override { return true; }
    virtual bool IsCacheable(const UPCGSettings* InSettings) const override { return false; }

protected:
    virtual bool ExecuteInternal(FPCGContext* InContext) const override
    {
        const UMyCustomSamplingSettings* Settings = InContext->GetInputSettings<UMyCustomSamplingSettings>();
        if (!Settings) return true;

        // 创建 MeshPartition 数据用于查询
        UPCGMeshPartitionData* MeshData = NewObject<UPCGMeshPartitionData>();
        MeshData->QueryParams.QueryType = MeshPartition::EPCGQueryType::Final;
        MeshData->QueryParams.MegaMeshOverride = Settings->TargetMegaMesh;
        MeshData->QueryParams.bGetImpactPoint = true;
        MeshData->QueryParams.bGetImpactNormal = true;
        MeshData->QueryParams.bGetUVCoords = true;

        // 初始化并查询
        MeshData->Initialize(
            static_cast<FPCGMeshPartitionElementContext*>(InContext),
            InContext->SourceComponent.IsValid() ? InContext->SourceComponent->GetWorld() : nullptr,
            FTransform::Identity
        );

        if (MeshData->IsDataReady())
        {
            // 转换为点数据输出
            const UPCGPointData* PointData = MeshData->CreatePointData(
                InContext,
                MeshData->GetBounds()
            );

            // 输出到下游节点
            FPCGTaggedData& Output = InContext->OutputData.TaggedData.Emplace_GetRef();
            Output.Data = const_cast<UPCGPointData*>(PointData);
        }

        return true;
    }
};

FPCGElementPtr UMyCustomSamplingSettings::CreateElement() const
{
    return MakeShared<FMyCustomSamplingElement>();
}
```

## 模块依赖

本插件依赖以下三个插件（在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `PCG` | PCG 框架核心，提供 `UPCGSettings`、`UPCGData`、`IPCGElement` 等基类 |
| `MeshPartition` | Mesh Partition/大网格地形系统，提供 `AMeshPartition`、`UModifierComponent`、`FMeshData` 等核心类型 |
| `PCGGeometryScriptInterop` | PCG 与 Geometry Script 的互操作层 |

模块级特殊依赖（从头文件引用推断）：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架运行时 |
| `MeshPartition` | Mesh Partition 运行时核心 |
| `GeometryScriptCore` | 几何脚本核心，用于网格数据处理 |
| `RenderCore` / `Renderer` | 通道纹理 GPU 合成、烘焙渲染 |
| `DynamicMesh` | 动态网格数据类型（`UPCGDynamicMeshData`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复烘焙地形截面时读取未就绪 RHI 资源导致的崩溃 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增"烘焙地形截面网格"节点 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 修复地形截面节点在修饰器变更后未正确刷新 Final 层的问题 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复将压缩纹理绑定为 UAV 导致的 GPU 崩溃 |

### 维护评价

- **创建时间**：2026-03-05，非常新的插件（约 2 个月）
- **维护状态**：🟢 **活跃开发中**。5 月份集中进行了多项功能添加（烘焙节点）和重要 bug 修复（GPU 崩溃、RHI 资源崩溃、刷新问题）
- **实验性警告**：⚠️ 此插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 和功能可能随版本变动
- **稳定性**：虽然活跃开发，但近几次 commit 多为 crash 修复，表明该插件仍处于早期稳定化阶段
- **推荐**：适合对 Mesh Partition 系统有深度集成需求的项目。如果你只是简单使用 PCG，暂不需要此插件。如果你的项目依赖 Mesh Partition 地形并需要 PCG 驱动，这是必需的桥梁插件，但请注意 API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)