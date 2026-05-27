# Chaos Cloth Asset USD Dataflow Nodes

> Dataflow nodes for importing USD Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料USD导入节点 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `ChaosClothAssetUsdDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) | |

## 用途

本插件为UE5的`ChaosClothAsset`（布料资产）系统提供Dataflow（数据流图）节点，其核心功能是**导入来自第三方服装建模软件（如Marvelous Designer, CLO3D）的USD格式布料资产**。它解决了一个具体的痛点：这些专业软件通过USD导出布料数据时，会使用自定义的“布料Schema”来存储模拟网格、渲染网格及相关的物理属性。标准的USD导入器无法识别这些数据。本插件提供的Dataflow节点专门用于解析这些带有布料Schema的USD文件，并将其中的网格和属性数据转换为UE内部的布料集合（`FManagedArrayCollection`），从而无缝接入基于Dataflow的布料模拟与渲染流程。

## 使用场景

- 你是一名角色美术或技术美术，使用Marvelous Designer或CLO3D制作了角色的服装布料。希望将服装的版片（Patterns）及模拟数据导入UE5，用于驱动`ChaosCloth`组件的实时物理模拟。
- 你的工作流基于UE5的“数据流图”来可视化地构建和修改布料资产。需要一个节点直接读取来自DCC软件的USD文件，并将数据注入到数据流中。

## 蓝图用法

该插件的核心是一个名为`USDImport`的Dataflow节点，它在Dataflow图编辑器中作为图块使用，而非传统的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USDImport` | 从指定的USD文件导入布料资产数据（模拟网格与/或渲染网格），并输出一个`FManagedArrayCollection`。 | `FChaosClothAssetUSDImportNode_v3` |

### 使用示例（Dataflow 图描述）

1.  **创建Dataflow图**：在资产编辑器或内容浏览器中，创建一个新的“Dataflow”资产。
2.  **添加节点**：在图编辑器中右键搜索“USDImport”或从“Cloth”类别下找到“Cloth USD Import”节点并添加到图中。
3.  **配置输入**：
    - 在节点的细节面板中，点击“USD File”属性旁的文件夹图标，选择你的USD布料文件（`.usd`, `.usda`, `.usdc`）。
    - 根据需要勾选“Import Sim Mesh”和“Import Render Mesh”来决定导入模拟网格、渲染网格或两者都导入。
    - 如果导入渲染网格，可进一步勾选“Import With Opacity”（需要项目设置中启用半透明）。
4.  **连接输出**：将节点的输出引脚（绿色，类型为`FManagedArrayCollection`）连接到Dataflow图的输出节点，或者连接到其他处理布料数据的Dataflow节点（例如，用于修改或预览）。
5.  **执行导入**：节点通常会自动评估。你也可以点击节点上的“Reimport USD File”按钮手动触发重新导入。导入后，生成的中间静态网格资产会保存在插件定义的包路径下，你还可以使用“Reload Sim Static Mesh”或“Reload Render Static Mesh”按钮仅重新加载这些中间资产，而无需重导整个USD文件。

## C++ 用法

本插件提供的主要功能是Dataflow节点，它们通过`FDataflowNode`派生结构体在C++中定义，并在Dataflow图编辑器中实例化。虽然不能像普通类一样直接`new`出来使用，但了解其结构有助于理解数据流和调试。

### 头文件引入

```cpp
// 通常不直接引入，节点由Dataflow框架管理。但如需在测试或特殊情况下引用相关类型：
#include "ChaosClothAsset/USDImportNode_v3.h"
```

### 基本用法

本插件的核心逻辑封装在`FChaosClothAssetUSDImportNode_v3`结构体中。以下是一个概念性的C++代码片段，展示其内部评估（`Evaluate`）函数可能执行的操作逻辑（源自源码分析，非直接测试用例）：

```cpp
// 伪代码，展示USDImport节点的评估逻辑
void FChaosClothAssetUSDImportNode_v3::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 1. 检查USD文件路径是否有效
    if (!UsdFile.FilePath.IsEmpty())
    {
        // 2. 使用USD SDK打开和解析USD文件 (核心依赖于 USDImporter 模块)
        // 3. 根据bImportSimMesh和bImportRenderMesh标志，提取对应的网格数据
        // 4. 将USD网格数据转换为引擎可用的FStaticMesh（作为中间资产）
        // 5. 将FStaticMesh中的顶点、索引、UV等数据导入FManagedArrayCollection
        // 6. 解析USD布料Schema中的自定义属性（如约束、材料属性）并存入Collection
        // 7. 将处理后的Collection通过Output引脚输出
        FManagedArrayCollection OutputCollection = /* ... 处理后的集合 ... */;
        Context.SetValue(Output, OutputCollection);
    }
}
```

### 进阶用法

- **自定义导入**：源码显示，节点内部区分了两种USD导入路径：`ImportUsdFile_Schemaless`和`ImportUsdFile`。前者用于旧的、无Schema的USD格式，后者用于带有正确布料Schema的USD。开发者在扩展或调试导入逻辑时需注意此区别。
- **属性访问器**：`FUsdPrimAttributeAccessor`是一个辅助类，用于方便地从USD Prim（基础图元）中读取不同类型（`uint32`, `float`, `FVector3f`等）的自定义属性值。它处理了USD和UE之间的坐标轴转换。
- **资产依赖**：节点在导入后会维护导入的静态网格（`ImportedSimStaticMesh`, `ImportedRenderStaticMesh`）及其依赖资产列表（`ImportedSimAssets`, `ImportedRenderAssets`）。在C++中操作这些中间资产时需要注意它们的生命周期。

## Demo 示例

由于本插件的功能完全集成在Dataflow图编辑器中，典型的使用方式是通过UI操作。以下是一个**可运行的C++测试用例场景描述**，它模拟了创建并评估一个USDImport节点的过程，展示了如何在代码层面驱动Dataflow：

```cpp
// FilePath: ChaosClothAssetUsdDataflowNodesTest.cpp (概念示例)
#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "Dataflow/DataflowGraph.h"
#include "Dataflow/DataflowContext.h"
#include "ChaosClothAsset/USDImportNode_v3.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FChaosClothAssetUSDImportNodeTest,
    "System.Dataflow.ChaosClothAsset.USDImport",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FChaosClothAssetUSDImportNodeTest::RunTest(const FString& Parameters)
{
    // 1. 创建一个Dataflow图
    TSharedPtr<UE::Dataflow::FGraph> Graph = MakeShared<UE::Dataflow::FGraph>();
    UE::Dataflow::FGraphContext Context;

    // 2. 添加一个USDImport节点实例
    FGuid NodeGuid = FGuid::NewGuid();
    UE::Dataflow::FNodeParameters NodeParams;
    FChaosClothAssetUSDImportNode_v3* ImportNode = new (Context.GetNodeAllocator()) FChaosClothAssetUSDImportNode_v3(NodeParams, NodeGuid);
    Graph->AddNode(ImportNode);

    // 3. 配置节点属性（模拟用户在细节面板的输入）
    const FString TestUsdFilePath = TEXT("/Game/TestAssets/ClothSample.usd");
    ImportNode->UsdFile.FilePath = TestUsdFilePath;
    ImportNode->bImportSimMesh = true;
    ImportNode->bImportRenderMesh = false;

    // 4. 评估节点（触发导入逻辑）
    Graph->Evaluate(Context);

    // 5. 获取输出并验证
    const FManagedArrayCollection* ResultCollection = Context.GetValue(ImportNode->Collection);
    if (TestTrue(TEXT("Should have a valid output collection after evaluation"), ResultCollection != nullptr))
    {
        // 验证集合是否包含模拟网格数据（例如顶点位置数组）
        TestTrue(TEXT("Collection should have vertex positions"),
            ResultCollection->HasAttribute<FVector3f>(TEXT("VertexPositions"), TEXT("SimMesh")));
    }

    return true;
}
```

## 模块依赖

要使用此插件，你的模块（特别是编辑器工具或需要操作Dataflow图的模块）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产核心类型（如 `FManagedArrayCollection`） |
| `ChaosClothAssetDataflowNodes` | 布料相关的基础Dataflow节点 |
| `Dataflow` | UE5的数据流图框架核心 |
| `USDImporter` | 底层的USD文件解析和导入功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | 为USD交换框架添加了对Chaos布料资产的支持。 |
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 将Chaos布料资产相关模块移出测试阶段（Beta）。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | Dataflow框架相关的更新（具体细节需查看子提交）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的`UE_LOG`宏迁移到新的`UE_LOGF`格式化日志宏。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了链接时出现的重复符号错误。 |

### 维护评价

本插件创建于**2025年12月**，属于较新的功能插件。从git记录看，在2026年4月仍有**活跃的维护和功能集成**，例如将其核心模块移出Beta，并与其他USD系统（Interchange）进行集成。最近一次更新在2026年4月底，表明其处于**活跃维护**状态。插件专注于解决USD布料资产导入的特定问题，功能明确，是Chaos布料资产工作流的重要组成部分。**推荐**在需要从DCC软件导入布料数据到UE5 Dataflow流程的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes/Tests) (推测路径，需确认)