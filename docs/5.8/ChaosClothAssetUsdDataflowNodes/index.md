# Chaos Cloth Asset USD Dataflow Nodes

> Dataflow nodes for importing USD Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++源码） |
| 模块 | `ChaosClothAssetUsdDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) | |

## 用途

此插件提供了一套数据流（Dataflow）节点，专门用于将第三方服装构造软件（如 CLO3D、Marvelous Designer）导出的 USD（Universal Scene Description）布料资产导入到 Unreal Engine 5 中。它解决了将复杂的布料模拟网格（Sim Mesh）和渲染网格（Render Mesh）数据从外部工具无缝集成到 UE5 的 Chaos 布料物理系统和渲染管线中的问题。该插件是 `ChaosClothAsset` 和 `ChaosClothAssetDataflowNodes` 插件的扩展，专注于 USD 格式的导入工作流。

## 使用场景

- 你是一名技术美术或角色美术，使用 CLO3D 或 Marvelous Designer 设计并模拟了服装，需要将设计结果（包括物理模拟数据）导入 UE5 进行最终渲染和实时模拟。
- 你的工作流程依赖于数据流图（Dataflow Graph）来自动化资产处理和布料设置，需要一个节点来读取和处理 USD 格式的布料数据。
- 你需要将 USD 文件中的布料网格数据（可能包含模拟网格和渲染网格）解析并转换为 UE5 的 `FManagedArrayCollection` 格式，以便后续的布料资产构建节点使用。

## 蓝图用法

此插件主要提供数据流节点，而非传统的蓝图函数。其核心功能通过数据流图编辑器中的节点暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USDImport` | 从指定的 USD 文件导入布料数据（模拟网格和/或渲染网格），并输出为 `FManagedArrayCollection`。 | `FChaosClothAssetUSDImportNode_v3` |

### 使用示例（数据流图描述）

1.  在数据流图编辑器中，从“Cloth”类别下找到并添加 **“Cloth USD Import”** 节点。
2.  在节点的细节面板中，设置 **“USD File”** 属性，指向你的 `.usd` 或 `.usda` 文件。
3.  根据需要勾选 **“Import Sim Mesh”** 和 **“Import Render Mesh”** 来选择导入模拟网格、渲染网格或两者。
4.  （可选）如果导入的渲染网格需要透明度，勾选 **“Import With Opacity”**（需要项目设置中启用半透明）。
5.  将节点的 **“Collection”** 输出引脚连接到下游的布料处理节点（如 `ClothCollectionToAsset`）。
6.  如果需要重新导入，可以点击节点上的 **“Reimport USD File”** 按钮。如果只想重新加载已生成的中间静态网格资产，可以使用 **“Reload Sim Static Mesh”** 或 **“Reload Render Static Mesh”** 按钮。

## C++ 用法

### 头文件引入

```cpp
// 引入数据流节点基类
#include "Dataflow/DataflowNode.h"
// 引入布料资产相关的数据流节点（如果需要继承或使用其类型）
#include "ChaosClothAsset/USDImportNode_v3.h"
// 引入自定义属性定制（如果需要）
#include "ChaosClothAsset/ImportFilePathCustomization.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建一个 `FChaosClothAssetUSDImportNode_v3` 节点实例并配置其参数。这通常在自定义数据流节点或测试中使用。

```cpp
// 来源: 基于 USDImportNode_v3.h 的结构推断
#include "ChaosClothAsset/USDImportNode_v3.h"

// 假设在一个数据流评估上下文中
void CreateAndConfigureUSDImportNode()
{
    // 创建节点参数和GUID
    UE::Dataflow::FNodeParameters Params;
    FGuid NodeGuid = FGuid::NewGuid();

    // 实例化USD导入节点
    FChaosClothAssetUSDImportNode_v3 USDImportNode(Params, NodeGuid);

    // 配置导入参数
    USDImportNode.bImportSimMesh = true;
    USDImportNode.bImportRenderMesh = true;
    USDImportNode.bImportWithOpacity = false;

    // 设置USD文件路径 (FChaosClothAssetImportFilePath 是一个自定义结构体)
    FChaosClothAssetImportFilePath FilePath;
    FilePath.FilePath = TEXT("/Game/Characters/Clothes/MyDress.usd");
    USDImportNode.UsdFile = FilePath;

    // 注意：实际的评估（Evaluate）通常由数据流图自动调用。
    // 手动评估需要构造一个合适的 FContext。
    // UE::Dataflow::FContext Context;
    // USDImportNode.Evaluate(Context, nullptr);
}
```

### 进阶用法

插件内部使用 `FUsdPrimAttributeAccessor` 来从 USD Prim 中读取自定义属性。虽然这个类主要用于插件内部，但了解其模式有助于理解 USD 数据的处理方式。

```cpp
// 来源: UsdPrimAttributeAccessor.h
#include "ChaosClothAsset/UsdPrimAttributeAccessor.h"
#include "UsdWrappers/UsdPrim.h"

// 假设你已经通过 USD SDK 获取了一个 UsdPrim
void ReadCustomAttributesFromUsdPrim(const FUsdPrim& MyUsdPrim)
{
    // 创建访问器，假设USD文件的上轴是Z轴
    UE::Chaos::ClothAsset::FUsdPrimAttributeAccessor PrimAccessor(MyUsdPrim, EUsdUpAxis::ZAxis);

    // 读取一个名为“cloth:stiffness”的浮点数属性，如果不存在则返回默认值1.0
    float Stiffness = PrimAccessor.GetValue<float>(TEXT("cloth:stiffness"), 1.0f);

    // 读取一个名为“cloth:vertex_mass”的浮点数数组
    TArray<float> VertexMasses = PrimAccessor.GetArray<float>(TEXT("cloth:vertex_mass"));

    // 读取数组中的第一个值，如果数组为空则返回默认值0.0
    float FirstMass = PrimAccessor.GetArrayValue<float>(TEXT("cloth:vertex_mass"), 0.0f, 0);

    // 使用读取到的数据...
    UE_LOG(LogTemp, Log, TEXT("Cloth Stiffness: %f, First Vertex Mass: %f"), Stiffness, FirstMass);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示了如何创建一个继承自 `FDataflowNode` 的自定义节点，并在其中使用 `FChaosClothAssetUSDImportNode_v3` 的逻辑概念。

```cpp
// MyCustomClothImportNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"
#include "MyCustomClothImportNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyCustomClothImportNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomClothImportNode, "MyCustomImport", "Cloth", "My Custom Cloth Import")

public:
    // 输出：布料集合
    UPROPERTY(meta = (DataflowOutput))
    FManagedArrayCollection Collection;

    // 输入：USD文件路径（简化版）
    UPROPERTY(EditAnywhere, Category = "Import")
    FString UsdFilePath;

    FMyCustomClothImportNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyCustomClothImportNode.cpp
#include "MyCustomClothImportNode.h"
#include "ChaosClothAsset/USDImportNode_v3.h" // 为了使用其内部逻辑或类型

FMyCustomClothImportNode::FMyCustomClothImportNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    // 注册输入输出
    RegisterOutputConnection(&Collection);
}

void FMyCustomClothImportNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 在这里实现你的自定义导入逻辑。
    // 你可以参考 FChaosClothAssetUSDImportNode_v3::Evaluate 的实现，
    // 但针对你的特定需求进行简化或修改。

    // 示例：创建一个空的布料集合作为输出
    TSharedRef<FManagedArrayCollection> ClothCollection = MakeShared<FManagedArrayCollection>();

    // ... 你的USD解析和数据填充逻辑 ...

    // 将结果设置到输出
    Context.SetValue(Collection, ClothCollection);
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下插件提供的模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供核心的布料资产类型和数据结构。 |
| `ChaosClothAssetDataflowNodes` | 提供基础的布料数据流节点框架和相关类型。 |
| `Dataflow` | 提供数据流图系统的核心框架。 |
| `USDImporter` | 提供 USD 文件解析和资产导入的基础功能。 |

## 维护状态

### 近期更新

- 2026-04-21 `600f5cce` [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. (将布料资产模块移出beta状态)
- 2026-04-17 `49f946b4` [Dataflow] (数据流相关更新)
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF. (将日志宏迁移到UE_LOGF)

### 维护评价

该插件创建于 2026 年初，是一个相对较新的组件。从最近的提交记录来看，它在 2026 年 4 月仍有活跃的更新，包括重要的状态变更（移出 beta）和代码维护（日志宏迁移）。这表明该插件正在被积极维护，并且是 Chaos 布料资产工具链中一个稳定且持续发展的部分。鉴于其明确的用途和与 Epic 核心布料系统的集成，推荐在需要 USD 布料导入工作流的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)