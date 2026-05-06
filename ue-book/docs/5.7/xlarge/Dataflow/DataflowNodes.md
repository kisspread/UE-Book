# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流节点 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据流节点代码及蓝图资产） |
| 模块 | `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) | |

## 用途

DataflowNodes 是实验性 Dataflow 系统的一部分，提供了一系列用于编辑器内数据流图的节点。这些节点允许用户在数据流图中操作 **FManagedArrayCollection**（几何集合）、骨骼、蒙皮权重、顶点属性等，实现程序化几何处理、骨架装配、权重编辑等功能。它解决了传统手动装配流程难以复用和自动化的问题，使艺术家和技术美术能够在可视化节点图中组合、验证和导出几何与骨架数据。

## 使用场景

- **程序化几何生成与绑定**：在数据流图中读取静态/骨架网格体，提取顶点属性，调整骨骼或蒙皮权重，然后输出给下游节点或终端。
- **角色自定义系统**：通过节点替换或修改骨骼属性、蒙皮数据，实现动态角色装配。
- **编辑器内数据流调试**：利用 DebugDraw 功能可视化骨骼、顶点选择等，方便调试复杂数据流。
- **集合属性操作**：增删改查几何集合中的属性（如顶点标量、骨骼索引、权重），支持批量处理。

## 蓝图用法

DataflowNodes 中的节点主要在 **Dataflow 图编辑器** 中使用，通过拖拽节点并连接输入输出来构建流程。以下为核心节点的分组说明。

> **注意**：这些节点并不直接暴露为蓝图函数库，而是作为数据流图的节点单元，可在 *Dataflow Asset* 内部使用。

### 集合属性操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeAttributeKey` | 将字符串组名和属性名组合为 `FCollectionAttributeKey` | `FMakeAttributeKeyDataflowNode` |
| `BreakAttributeKey` | 将属性键拆分为组名和属性名字符串 | `FBreakAttributeKeyDataflowNode` |
| `AddScalarVertexProperty` | 向集合添加标量顶点属性（支持权重映射） | `FDataflowCollectionAddScalarVertexPropertyNode`（位于同一模块） |
| `EditSkeletonBones` | 编辑骨骼属性，支持调试绘制和骨骼选择 | `FDataflowCollectionEditSkeletonBonesNode` |
| `EditSkinWeights` | 编辑蒙皮权重，支持读取/写入骨骼索引和权重 | `FDataflowCollectionEditSkinWeightsNode` |

### 通用输入节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StaticMesh` | 获取一个外部静态网格体对象作为数据流输入 | `FGetStaticMeshDataflowNode` |
| `GetStaticMeshBoundingBox` | 计算静态网格体的包围盒、中心与尺寸 | `FGetStaticMeshBoundingBoxDataflowNode` |
| `SkeletalMesh` | 获取一个外部骨骼网格体对象作为数据流输入 | `FGetSkeletalMeshDataflowNode` |
| `Skeleton` | 获取一个外部骨骼对象作为数据流输入 | `FGetSkeletonDataflowNode` |
| `SelectionSet` | 手动指定整数索引集合 | `FSelectionSetDataflowNode` |
| `FloatOverride` | 从上下文覆盖浮点数值 | `FFloatOverrideDataflowNode` |

### 输出/终端节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSkinningSkeletalMesh` | 为集合设置用于蒙皮的骨骼网格体 | `FDataflowCollectionSetSkinningSkeletalMesh` |
| `SkeletonAssetTerminal` | 将结果骨骼写入并保存为资产 | `FSkeletonAssetTerminalNode` |

### 使用示例（蓝图描述）

1. **获取骨骼网格体并编辑骨骼**：  
   - 拖入 `SkeletalMesh` 节点，选择目标网格体。  
   - 连接其输出到 `EditSkeletonBones` 的 `Collection` 输入（需先通过其他节点将网格体转换为集合）。  
   - 在 `EditSkeletonBones` 节点上调整骨骼属性，其输出可继续连接至终端节点保存。

2. **添加顶点标量属性**：  
   - 准备一个几何集合（如通过 `GeometryCollection` 节点）。  
   - 连接至 `AddScalarVertexProperty` 节点，设置属性名和分组。  
   - 节点输出包含新属性的集合，可继续用于蒙皮或渲染。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowNodesPlugin.h"           // 模块入口
#include "Dataflow/DataflowCollectionEditSkinWeightsNode.h"
#include "Dataflow/DataflowCollectionEditSkeletonBonesNode.h"
#include "Dataflow/DataflowSkeletalMeshNodes.h"
#include "Dataflow/DataflowTools.h"                 // 工具函数
```

### 基本用法

创建和评估一个 `FGetSkeletalMeshDataflowNode` 节点，获取骨骼网格体。

```cpp
// 创建节点参数
UE::Dataflow::FNodeParameters Params;
Params.Owner = nullptr; // 通常为拥有此图的 UObject
Params.Context = MakeShareable(new UE::Dataflow::FContext());

// 创建节点实例
FGetSkeletalMeshDataflowNode Node(Params);

// 设置属性：选择要获取的网格体
Node.PropertyName = FName("MySkeletalMesh");

// 评估节点（触发 Evaluate）
Node.Evaluate(*Params.Context, nullptr);
// 此时 Node.SkeletalMesh 指向外部引用的网格体（需先通过 SetAssetProperty 绑定）

// 另一个例子：使用工具函数清理名称
FString DirtyName = " vertex.weights ";
UE::Dataflow::FDataflowTools::MakeCollectionName(DirtyName);
// DirtyName 变为 "vertexweights"
```

*来源：基于 `Public/Dataflow/DataflowSkeletalMeshNodes.h` 和 `Public/Dataflow/DataflowTools.h` 推断。*

### 进阶用法

使用 `FDataflowCollectionEditSkinWeightsNode` 读取并修改集合蒙皮权重。

```cpp
// 创建编辑蒙皮权重节点
FDataflowCollectionEditSkinWeightsNode SkinNode(Params);

// 提供输入集合（假设已填充）
FManagedArrayCollection InputCollection;
// ... 填充集合数据 ...

SkinNode.Collection = InputCollection;
SkinNode.BoneIndicesName = TEXT("BoneIndices");
SkinNode.BoneWeightsName = TEXT("BoneWeights");
SkinNode.VertexGroup.Name = FGeometryCollection::VerticesGroup;

// 评估节点
SkinNode.Evaluate(*Params.Context, nullptr);

// 输出集合将包含修改后的蒙皮数据
FManagedArrayCollection OutputCollection = SkinNode.Collection;

// 读取顶点蒙皮数据（内部使用了 FDataflowVertexSkinWeightData）
const int32 VertexNum = OutputCollection.NumElements(FGeometryCollection::VerticesGroup);
// 可通过集合属性访问骨骼索引/权重数组
```

*来源：`Public/Dataflow/DataflowCollectionEditSkinWeightsNode.h`。*

## Demo 示例

以下是一个最小 C++ 示例，演示如何在 **Runtime** 模块中使用 DataflowNodes 创建一个 `FGetSkeletalMeshDataflowNode` 并输出骨骼网格体。

**SkeletalMeshGetter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Dataflow/DataflowCore.h"
#include "Dataflow/DataflowSkeletalMeshNodes.h"

class FSkeletalMeshGetter
{
public:
    void GetSkeletalMesh(UObject* Outer, const USkeletalMesh*& OutMesh)
    {
        UE::Dataflow::FNodeParameters Params;
        Params.Owner = Outer;
        Params.Context = MakeShareable(new UE::Dataflow::FContext());

        FGetSkeletalMeshDataflowNode Node(Params);
        Node.PropertyName = FName("TargetMesh");
        // 实际使用中需通过 SetAssetProperty 绑定外部资产
        Node.SetAssetProperty(const_cast<USkeletalMesh*>(Outer)); // 仅为示例
        Node.Evaluate(*Params.Context, nullptr);
        OutMesh = Node.SkeletalMesh;
    }
};
```

**SkeletalMeshGetter.cpp**
```cpp
#include "SkeletalMeshGetter.h"
#include "Engine/SkeletalMesh.h"

// 使用示例
void TestGetSkeletalMesh()
{
    USkeletalMesh* TargetMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/MyCharacter.MyCharacter"));
    if (TargetMesh)
    {
        FSkeletalMeshGetter Getter;
        const USkeletalMesh* Result = nullptr;
        Getter.GetSkeletalMesh(TargetMesh, Result);
        // Result 即为通过 Dataflow 节点获取的网格体
    }
}
```

> **注意**：实际项目中节点需要与 Dataflow 资产和图绑定，此处仅为演示节点 API 使用模式。

## 模块依赖

使用 `DataflowNodes` 模块时，你的模块需要在 `Build.cs` 中添加以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `DataflowCore` | 提供基础数据流图框架（`FDataflowNode`, `FContext`） |
| `DataflowEngine` | 提供针对于引擎环境的数据流节点注册和连接类型 |
| `DynamicMesh` | 提供 `FDynamicMesh3` 动态网格数据结构，用于网格体转换 |
| `GeometryCollection` | 提供 `FManagedArrayCollection` 几何集合及渲染 facade |
| `SkeletalMeshDescription` | 骨骼网格体描述和转换工具 |
| `StaticMeshDescription` | 静态网格体描述支持 |

**其他常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd 等已在引擎中默认包含，无需额外声明。

## 维护状态

### 近期更新

- 2025-11-18 `296af658` — Dataflow : make sure we mark the dataflow package dirty when the tools are commiting their values  
- 2025-10-16 `8b858c13` — Unshelved from pending changelist '46933319':（未提供详细摘要）  
- 2025-10-03 `7f04ddbd` — Dataflow : fix cancelled close request causing the preview actor to be deleted and subsequent calls  
- 2025-10-03 `71e223a6` — Dataflow:（未提供详细摘要）  
- 2025-10-02 `aba7c452` — Disable the dataflow slow task progress notification for now as this is causing UI focus issues

### 维护评价

- **创建时间**：2025-10-02，年龄约 2 个月，属于非常新的插件。  
- **近期更新**：最后一次功能性更新在 2025-11-18，修复了包脏状态问题，表明仍在积极维护。  
- **实验性状态**：`IsExperimentalVersion=true`，API 和行为可能发生较大变化。  
- **已知问题**：无官方列出，但作为实验性功能，可能存在未覆盖的边缘情况。  
- **推荐使用**：适合在 5.7 以上版本中探索程序化装配工作流，生产项目需谨慎评估稳定性。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow)
- [测试用例（模块内）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow/Source/DataflowNodes)（部分节点含内部测试代码）