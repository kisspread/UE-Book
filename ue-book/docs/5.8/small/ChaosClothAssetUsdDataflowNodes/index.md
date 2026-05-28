# Chaos Cloth Asset USD Dataflow Nodes

> Dataflow nodes for importing USD Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产 USD 导入数据流节点 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetUsdDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) | |

## 用途

此插件为 Unreal Engine 的 **Chaos 布料模拟系统**提供了一个 **Dataflow 节点**，专门用于从第三方服装制作软件（如 CLO、Marvelous Designer）生成的 **USD (Universal Scene Description) 文件**中导入布料资产。它解决了将外部设计数据高效、准确地集成到引擎布料模拟工作流中的问题。通过此插件，用户可以在 Dataflow 图表中直接配置导入设置，并一键生成用于模拟和渲染的布料网格数据，是连接设计工具与 UE5 实时布料模拟的关键桥梁。

## 使用场景

- 你正在使用 CLO 或 Marvelous Designer 等服装设计软件为角色创建布料 → 使用此插件将设计导出为 USD，并在 UE5 的 Dataflow 系统中一键导入，自动生成模拟和渲染网格。
- 你需要对导入的 USD 布料数据进行精细控制 → 使用此节点可以选择性地导入模拟网格或渲染网格，并设置 UV 缩放等参数。
- 你希望在布料模拟工作流中实现自动化或可重复的资产导入流程 → 将此 Dataflow 节点集成到你的数据管线中。

## 蓝图用法

此插件的核心是一个 Dataflow 节点（`FChaosClothAssetUSDImportNode_v3`），它通过结构体暴露属性，供 Dataflow 图表使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USDImport` | 导入指定 USD 文件，并输出布料集合（ClothCollection） | `FChaosClothAssetUSDImportNode_v3` |
| `Reimport USD File` | 重新导入指定的 USD 文件并重新生成中间资产 | `FChaosClothAssetUSDImportNode_v3` |
| `Reload Sim Static Mesh` | 仅重新加载导入的模拟静态网格体（不重新导入 USD） | `FChaosClothAssetUSDImportNode_v3` |
| `Reload Render Static Mesh` | 仅重新加载导入的渲染静态网格体（不重新导入 USD） | `FChaosClothAssetUSDImportNode_v3` |

### 使用示例（蓝图描述）

1.  在 **Dataflow 图表**中，搜索并添加 **“USD Import”** 节点（属于 “Cloth” 类别）。
2.  在节点细节面板中，设置 **“USD File”** 属性，指向一个有效的 USD 文件。
3.  根据需要勾选 **“Import Sim Mesh”** 和 **“Import Render Mesh”** 以控制导入数据类型。
4.  如果导入渲染网格，可进一步设置 **“Import With Opacity”** 以支持透明材质（需项目设置中启用半透明）。
5.  节点的 **“Collection”** 输出引脚将生成一个 `FManagedArrayCollection`，其中包含了从 USD 文件解析出的布料模拟和渲染数据。将此引脚连接到后续的布料处理节点（如布料模拟、渲染节点）即可。

## C++ 用法

此插件主要通过 Dataflow 系统工作，C++ 用法主要集中在理解其核心结构体和辅助工具类上。

### 头文件引入

```cpp
#include "ChaosClothAsset/USDImportNode_v3.h"
// 以下为内部使用，一般不需要直接引用
#include "ChaosClothAsset/UsdPrimAttributeAccessor.h"
```

### 基本用法

核心导入逻辑封装在 `FChaosClothAssetUSDImportNode_v3` 结构体中。以下是如何在代码中使用它的概念性示例（实际使用通常在 Dataflow 图表编辑器中）：
```cpp
// 注意：通常不会直接实例化此节点，而是通过 Dataflow 编辑器创建。
// 以下代码仅为演示其内部工作原理。
#include "ChaosClothAsset/USDImportNode_v3.h"

// 假设已经有一个 Dataflow 图表上下文
// FChaosClothAssetUSDImportNode_v3 ImportNode(Parameters);
// ImportNode.UsdFile.FilePath = TEXT("/Game/MyCloth.usd");
// ImportNode.bImportSimMesh = true;
// ImportNode.bImportRenderMesh = true;
// 
// // 触发评估以执行导入
// UE::Dataflow::FContext Context;
// ImportNode.Evaluate(Context, nullptr);
// 
// // 评估后，可以访问其内部数据，如 ImportedSimStaticMesh 等。
```
*来源：源码分析自 `USDImportNode_v3.h` 中的 `Evaluate` 方法及属性定义。*

### 进阶用法

插件内部使用 `FUsdPrimAttributeAccessor` 工具类来高效、安全地从 USD Prim 中读取各种类型的属性（如 `uint32`, `float`, `FVector3f`）。这个类处理了 USD 到 Unreal 的坐标系转换（Z-up vs Y-up）。
```cpp
#include "ChaosClothAsset/UsdPrimAttributeAccessor.h"
#if USE_USD_SDK
    // 假设我们有一个表示布料部件的 USD Prim
    FUsdPrim ClothPrim = ...; 
    
    // 创建访问器，并指定 USD 文件的向上轴向（通常为 Z 轴）
    UE::Chaos::ClothAsset::FUsdPrimAttributeAccessor Accessor(ClothPrim, EUsdUpAxis::ZAxis);
    
    // 读取一个浮点属性，例如布料的厚度
    float ClothThickness = Accessor.GetValue<float>(TEXT("cloth:thickness"), 0.1f);
    
    // 读取一个向量数组，例如网格的顶点位置（经过坐标系转换）
    TArray<FVector3f> VertexPositions = Accessor.GetArray<FVector3f>(TEXT("points"));
#endif
```
*来源：`UsdPrimAttributeAccessor.h` 中的类定义和模板特化。*

## Demo 示例

以下是一个最小化的示例，展示如何创建一个自定义的 Dataflow 节点来封装 USD 导入功能（实际应用通常直接使用 `USDImport` 节点，这里为演示结构）。

**USDImporterNodeDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Dataflow/DataflowNode.h"

USTRUCT(Meta = (DataflowCloth))
struct FUSDImporterNodeDemo : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FUSDImporterNodeDemo, "USD Importer Demo", "Cloth", "Demo USD Importer")

    UPROPERTY(EditAnywhere, Category = "Demo", Meta = (DisplayName = "USD File Path"))
    FString UsdFilePath;

    UPROPERTY(meta = (DataflowOutput))
    FManagedArrayCollection OutputCollection;

    FUSDImporterNodeDemo(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

**USDImporterNodeDemo.cpp**
```cpp
#include "USDImporterNodeDemo.h"
// 包含插件提供的导入节点头文件以复用其功能
#include "ChaosClothAsset/USDImportNode_v3.h"

FUSDImporterNodeDemo::FUSDImporterNodeDemo(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    // 注册输出引脚
    RegisterOutputConnection(&OutputCollection);
}

void FUSDImporterNodeDemo::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 在此演示中，我们简单地委托给实际的 USD 导入节点逻辑
    // 实际项目中，这里会调用导入库或工具类
    if (!UsdFilePath.IsEmpty())
    {
        // 创建一个临时的导入节点实例来执行操作
        FChaosClothAssetUSDImportNode_v3 TempImporter(
            UE::Dataflow::FNodeParameters::MakeEmpty()); // 简化参数
        
        TempImporter.UsdFile.FilePath = UsdFilePath;
        TempImporter.bImportSimMesh = true;
        TempImporter.bImportRenderMesh = false; // 仅演示模拟网格

        UE::Dataflow::FContext DummyContext;
        TempImporter.Evaluate(DummyContext, nullptr);
        
        // 将其生成的集合复制到我们的输出引脚
        // 注意：实际使用需要正确处理错误和异步操作
        Context.SetOutputValue(TempImporter.Collection, OutputCollection);
    }
    else
    {
        // 输出空集合
        FManagedArrayCollection EmptyCollection;
        Context.SetOutputValue(EmptyCollection, OutputCollection);
    }
}
```

## 模块依赖

从 `.uplugin` 文件中的 `Plugins` 依赖项可以看出，要使用此插件，你的项目需要启用以下插件。

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | Chaos 布料资产核心模块，提供基础布料数据结构和功能。 |
| `ChaosClothAssetDataflowNodes` | Chaos 布料资产的 Dataflow 节点库，此插件是它的扩展。 |
| `Dataflow` | Unreal 的 Dataflow 框架，用于构建数据处理图表。 |
| `USDImporter` | USD 文件导入的核心功能库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | USD 交换系统新增对 ChaosCloth 资产的支持。 |
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | Chaos 布料资产模块脱离测试阶段。 |
| 2026-04-17 | `49f946b4` | [Dataflow] | Dataflow 相关更新（未详细说明）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了重复符号的链接错误。 |

### 维护评价

- **创建时间**：该插件非常新，创建于 **2025年12月**，至今不到一年。
- **维护状态**：**活跃维护中**。从 git 历史看，最近几个月有持续的功能更新（如与 USD 交换系统的集成、脱离 beta）和错误修复。
- **功能状态**：插件模块已正式脱离 beta 阶段，表明其核心功能已趋于稳定。
- **推荐使用**：**推荐**。对于需要在 Chaos 布料工作流中集成 USD 数据的项目，这是一个官方提供的、活跃维护的专用工具，值得采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现）