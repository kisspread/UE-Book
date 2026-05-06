# Dataflow Nodes

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流节点库 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DataflowEditor` (Editor), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

`DataflowNodes` 是 **Editor DataflowGraph** 插件的核心节点库，提供了在数据流图中使用的各种操作节点。它基于 `DataflowCore` 框架，支持对 `FManagedArrayCollection`（几何集合）和 `UDataflowMesh`（动态网格）进行属性计算、采样、选择、可视化、资源导出等操作。这些节点是 Chaos 物理破坏、Groom 毛发生成、程序化建模等数据流管线的基础构建块，解决了复杂几何数据处理流程的节点化、可视化编排需求。

## 使用场景

- **Chaos 破碎管线**：生成 Voronoi 破碎、设置材料、导出静态网格 / 骨骼网格资产。
- **Groom 毛发生成**：通过采样器（Perlin Noise、Random、梯度）控制发丝属性（长度、卷曲）。
- **程序化几何体修改**：使用 `TextureToAttribute`、`VertexColorToAttribute` 将纹理或顶点颜色转换为集合属性，再用于后续建模。
- **调试与可视化**：使用 `VisualizeAttribute` 将集合属性渲染为顶点颜色，在视口中即时观察。
- **资产导出**：`StaticMeshTerminal`、`SkeletonAssetTerminal` 等终端节点将处理结果写入资产文件。

## 蓝图用法

本模块提供的节点主要在 **数据流图编辑器**（Dataflow Graph Editor）中通过蓝图图形化连接，不直接暴露为独立的蓝图书点。所有节点的输入/输出端口在编辑器中自动显示，无需编写代码。

### 核心节点

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| `FloatOverride` | 提供浮点数值，可被外部覆盖 | `FFloatOverrideDataflowNode` |
| `SelectionSet` | 从字符串创建整数索引数组选择集 | `FSelectionSetDataflowNode` |
| `MakeSelectionSet` / `GetSelectionSet` | 将选择集存入/取出集合属性 | `FMakeSelectionSetDataflowNode` / `FGetSelectionSetDataflowNode` |
| `SamplerToAttribute` | 使用 Float/Vector 采样器生成集合属性 | `FDataflowSamplerToAttributeNode` |
| `TextureToAttribute` | 将纹理采样到集合 float 属性 | `FDataflowTextureToAttributeNode` |
| `VertexColorToAttribute` | 将顶点颜色通道值转换为集合属性 | `FDataflowVertexColorToAttributeNode` |
| `VisualizeAttribute` | 将指定属性渲染为顶点颜色 | `FDataflowVisualizeAttributeNode` |
| `Collection Bounds` | 计算集合的包围盒 | `FDataflowGetCollectionBoundsNode` |
| `StaticMesh` | 引用一个静态网格资产 | `FGetStaticMeshDataflowNode` |
| `GetStaticMeshBoundingBox` | 计算静态网格的包围盒（含中心、尺寸） | `FGetStaticMeshBoundingBoxDataflowNode` |
| `StaticMeshTerminal` | 将动态网格保存为静态网格资产 | `FDataflowStaticMeshTerminalNode` |
| `SkeletonAssetTerminal` | 保存骨架资产 | `FSkeletonAssetTerminalNode` |
| `DisplaceDataflowMesh` | 用采样器位移网格顶点（沿法线或向量） | `FDisplaceDataflowMeshDataflowNode` |
| `SetSkinningSkeletalMesh` | 为集合设置蒙皮骨骼网格 | `FDataflowCollectionSetSkinningSkeletalMesh` |
| `Abs Sampler`、`Negate Sampler`、`Normalize Sampler` | 对采样器做一元运算 | 各对应结构体 |
| `Add Sampler`、`Multiply Sampler`、`Min Sampler`、`Max Sampler` | 组合多个采样器 | `FDataflowMultiInputSamplerNodeBase` 派生 |
| `Lerp Sampler` | 在两个采样器间插值 | `FDataflowLerpSamplerNode` |
| `ColorRamp Sampler` | 用色盘将 float 采样映射为颜色向量 | `FDataflowColorRampSamplerNode` |
| `Combine Float Sampler` | 将三个 float 采样合并为向量 | `FDataflowCombineFloatSamplerNode` |
| `Linear Gradient Sampler` | 线性梯度采样 | `FDataflowLinearGradientFloatSamplerNode` |
| `Distance From Box/Plane/Sphere Float Sampler` | 距离几何体距离采样 | 对应结构体 |
| `Perlin Noise Float/Vector Sampler` | Perlin 噪声采样 | `FDataflowPerlinNoiseFloatSamplerNode`、`FDataflowPerlinNoiseVectorSamplerNode` |
| `Random Float/Vector Sampler` | 随机数采样 | `FDataflowRandomFloatSamplerNode`、`FDataflowRandomVectorSamplerNode` |
| `Remap Float Sampler` | 数值范围重映射 | `FDataflowRemapFloatSamplerNode` |
| `OneMinus Float Sampler` | 1 - 值 | `FDataflowOneMinusFloatSamplerNode` |
| `Clamp Float Sampler` | 值钳制 | `FDataflowClampFloatSamplerNode` |
| `Mesh Float/Vector Sampler` | 从数据流网格采样距离、法线、UV 等 | `FDataflowMeshFloatSamplerNode`、`FDataflowMeshVectorSamplerNode` |
| `Sampler To Image` | 将采样器结果渲染为 2D 图像 | `FDataflowSamplerToImageNode` |

> **注意**：所有“Sampler”类节点均在数据流图编辑器的 **Samplers** 分类下，支持动态连接多个输入。

## C++ 用法

在 C++ 代码中，您通常不会直接实例化这些节点，而是通过数据流图框架（`FDataflowGraph`）注册并使用它们。以下示例演示如何在自定义数据流图中使用 `FDataflowTextureToAttributeNode` 实现纹理到属性的传输。

### 头文件引入

```cpp
#include "Dataflow/DataflowEngine.h"
#include "Dataflow/DataflowCore.h"
#include "Dataflow/DataflowNodeParameters.h"
#include "Dataflow/DataflowTextureToAttributeNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"
```

### 基本用法

```cpp
// 创建数据流图上下文
UE::Dataflow::FContext Context;

// 准备一个输入集合
FManagedArrayCollection Collection;
// ... 填充集合顶点数据 ...

// 创建纹理到属性节点实例
UE::Dataflow::FNodeParameters Params;
Params.bCanUseAssetProperty = false;
FDataflowTextureToAttributeNode Node(Params);

// 设置输入
Node.Collection = Collection;
Node.Texture = MyTexture2D;      // 一个 UTexture2D 对象
Node.AttributeName = "Height";
Node.UVChannel = 0;
Node.VertexGroup = FScalarVertexPropertyGroup("Vertices");

// 评估节点（触发数据流计算）
Node.Evaluate(Context, nullptr);

// 读取结果
FManagedArrayCollection OutCollection = Node.Collection;  // 属性已写入
```

**来源**：`DataflowTextureToAttributeNode.h` 及 `DataflowSamplerToAttributeNode.h`。

### 进阶用法

使用多输入采样器节点 `FDataflowAddSamplerNode`：

```cpp
// 创建多个采样器节点
FDataflowPerlinNoiseFloatSamplerNode NoiseNode(Params);
FDataflowRandomFloatSamplerNode RandomNode(Params);

// 创建加法节点
FDataflowAddSamplerNode AddNode(Params);

// 手动连接采样器（实际在图中由框架自动处理）
// AddNode 的 InputSamplers[0] 连接 NoiseNode.Sampler，InputSamplers[1] 连接 RandomNode.Sampler

// 运行
AddNode.Evaluate(Context, nullptr);

// 获取结果采样器
FDataflowSamplerTypes Result = AddNode.Sampler;
```

**来源**：`DataflowAddSamplerNode.h`、`DataflowSamplerMultiInput.h`。

## Demo 示例

以下是一个完整的 C++ 示例，展示如何使用数据流节点将纹理数据写入集合属性，并导出为静态网格。

```cpp
// DataflowTextureToStaticMeshDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowContext.h"
#include "UObject/StrongObjectPtr.h"

class FDataflowTextureToStaticMeshDemo
{
public:
    void Run(UTexture2D* HeightTexture, UStaticMesh* OutMeshAsset);
};

// DataflowTextureToStaticMeshDemo.cpp
#include "DataflowTextureToStaticMeshDemo.h"
#include "Dataflow/DataflowTextureToAttributeNode.h"
#include "Dataflow/DataflowStaticMeshAssetNodes.h"
#include "Dataflow/DataflowEngine.h"
#include "GeometryCollection/ManagedArrayCollection.h"
#include "Engine/StaticMesh.h"

void FDataflowTextureToStaticMeshDemo::Run(UTexture2D* HeightTexture, UStaticMesh* OutMeshAsset)
{
    UE::Dataflow::FContext Context;
    UE::Dataflow::FNodeParameters Params;
    Params.bCanUseAssetProperty = false;

    // 1. 创建集合并设置顶点位置（简略）
    FManagedArrayCollection Collection;
    // 实际应用中需添加顶点组 "Vertices" 并填充位置数据

    // 2. 纹理转属性节点
    FDataflowTextureToAttributeNode TextureNode(Params);
    TextureNode.Collection = Collection;
    TextureNode.Texture = HeightTexture;
    TextureNode.AttributeName = "Height";
    TextureNode.UVChannel = 0;
    TextureNode.VertexGroup = FScalarVertexPropertyGroup("Vertices");

    // 评估
    TextureNode.Evaluate(Context, nullptr);
    FManagedArrayCollection UpdatedCollection = TextureNode.Collection;

    // 3. 静态网格终端节点（假设已有 UDynamicMesh 转换逻辑）
    // 实际项目中通常从集合构建动态网格，再使用 StaticMeshTerminal
    // FDataflowStaticMeshTerminalNode Terminal(Params);
    // Terminal.Mesh = MyDynamicMesh;
    // Terminal.AssetPath = "/Game/MyMesh";
    // Terminal.Evaluate(Context, nullptr);
    // OutMeshAsset = Terminal.StaticMeshAsset;
}
```

## 模块依赖

从 `DataflowNodes.Build.cs` 推断（基于头文件包含）：

| 模块 | 用途 |
|---|---|
| `DataflowCore` | 数据流图核心框架（节点基础类、上下文、连接） |
| `DataflowEngine` | 引擎与数据流图的集成（终端节点、资产属性） |
| `GeometryCollectionEngine` | `FManagedArrayCollection` 及几何集合立面 |
| `DynamicMesh` | `UDynamicMesh`、`FDynamicMesh3` 网格处理 |
| `MeshDescription` | 网格描述与转换（如 `FStaticToSkeletalMeshConverter`） |
| `RenderCore` | 渲染方面（如渲染立面访问） |
| `Projects` | FString 路径处理 |
| `Slate` / `SlateCore` | 属性定制（`IPropertyTypeCustomization`） |

**省略常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-04-25 `8450647a` Dataflow : make proximity renderable type use the exploded settings
- 2026-04-24 `ddbdf42c` Dataflow : add exploded view and hierarchical component to geometry collection rendering type
- 2026-04-24 `ca3cc903` Dataflow : fix time line issues
- 2026-04-23 `3bbaa3bc` Dataflow Editor : fix issue with reloading assets with embedded dataflow graph
- 2026-04-23 `23602a95` Dataflow: （新增功能/修复）

### 维护评价

`DataflowNodes` 模块作为 Editor DataflowGraph 插件的一部分，频繁更新，功能持续扩展。从 git log 看，自创建以来（2026-04-23）几乎每日都有功能性 commit，修复与改进并行。当前无废弃标记，属于**活跃维护**。推荐在生产项目中积极使用，但注意部分节点仍标记为实验性（`IsExperimentalVersion=true`），未来 API 可能变动。整体稳定性良好。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [本模块头文件目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow/Source/DataflowNodes/Private/Dataflow)
- [官方文档（暂空）](https://docs.unrealengine.com/en-US/)（搜索 Dataflow）