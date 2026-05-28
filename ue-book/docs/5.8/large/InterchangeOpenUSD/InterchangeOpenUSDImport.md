# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | Interchange USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、管道配置） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

Interchange OpenUSD 插件为 Unreal Engine 的 Interchange 框架提供了对 OpenUSD 文件（`.usd`、`.usda`、`.usdc`、`.usdz`）的翻译和导入支持。它不仅仅是一个简单的文件读取器，而是一个完整的 USD 资产导入解决方案。

该插件基于 **Schema Handler（模式处理器）** 架构构建。它将 USD 中不同的 Prim 类型（如 Mesh、Material、Light、Camera、SkelRoot 等）映射到对应的处理器。每个处理器负责将特定类型的 USD 数据转换为 Interchange 能够理解的标准化节点（`UInterchangeBaseNode` 及其子类）。这种模块化设计使得：
1.  **职责清晰**：每种 USD 数据类型由独立的处理器处理。
2.  **可扩展**：开发者可以注册自己的自定义处理器来支持私有的 USD Schema 或自定义数据转换逻辑。
3.  **可配置**：用户可以在导入设置中调整处理器的顺序、启用状态以及特定于材质的渲染上下文。

它解决了在 Unreal Engine 中高质量、可配置地导入包含复杂层次结构、动画、材质和特定 USD 特性（如 Variant Sets 用于 LOD、PointInstancer 用于实例化）的 USD 资产的挑战。

## 使用场景

-   你的美术团队使用 Maya、Houdini 或 Blender 等 DCC 工具创建了角色、场景或道具，并以 USD 格式导出。你需要将这些资产导入 Unreal Engine 进行游戏开发或影视制作。
-   你需要导入的 USD 文件包含复杂的材质网络（如 UsdPreviewSurface 或 MaterialX）、骨骼动画、毛发（Groom）或体积数据（OpenVDB）。
-   你希望控制 USD 资产的导入过程，例如：只导入特定 Prims 子树、配置子网格体的合并方式（Collapsing）、选择材质渲染上下文、或处理 LOD 变体集。
-   你需要在导入后通过 Interchange 管道对生成的资产节点进行后处理，例如修改材质属性或调整场景层次。

## 蓝图用法

该插件主要通过 `UInterchangeUSDTranslator` 和 `UInterchangeUsdTranslatorSettings` 类在蓝图中暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取当前 USD 翻译器的设置对象，用于在导入前修改参数。 | `UInterchangeUSDTranslator` |
| `Translate` | 执行 USD 文件的翻译，将 USD 数据转换为 Interchange 节点。通常由导入系统自动调用。 | `UInterchangeUSDTranslator` |
| `Translate Prim` | 翻译单个 USD Prim 及其子 Prim。可用于需要自定义遍历逻辑的场景。 | `UInterchangeUSDTranslator` |
| `Get/StageId` | 获取当前 USD Stage 在 `UsdUtils` 缓存中的 ID。 | `UInterchangeUsdContext` |
| `Set/StageId` | 设置要导入的 USD Stage。允许通过 Stage ID 导入通过 Python 等脚本准备好的 Stage。 | `UInterchangeUsdContext` |

### 使用示例（蓝图描述）

1.  **配置导入设置**：在触发文件导入前，通过蓝图获取 `UInterchangeUsdTranslatorSettings` 对象。
    *   设置 `GeometryPurpose` 位掩码，决定导入哪些用途的几何体（渲染、代理等）。
    *   设置 `MaterialPurpose`，指定材质绑定的目的。
    *   调整 `PointInstancerCollapsing` 来控制如何处理 PointInstancer。
    *   启用 `bTranslatePrimAttributes` 并设置 `AttributeRegexFilter` 来将 USD 属性导入为资产元数据。
    *   在 `CustomHandlerEntries` 中重排或禁用处理器。
2.  **执行导入**：将配置好的设置对象传递给 Interchange 导入流程，或直接调用翻译器的 `Translate` 函数。

## C++ 用法

该插件的核心功能是通过 C++ 模式处理器架构实现的，适用于需要深度集成或扩展导入逻辑的场景。

### 头文件引入

```cpp
#include "InterchangeUSDTranslator.h"
#include "InterchangeUsdContext.h"
#include "SchemaHandlers/SchemaHandlerRegistry.h"
```

### 基本用法

1.  **注册自定义模式处理器**（来自 `FSchemaHandlerRegistry` 的设计）：
    ```cpp
    // MyCustomSchemaHandler.h
    #pragma once
    #include "SchemaHandlers/SchemaHandler.h"

    class FMyCustomSchemaHandler : public UE::Interchange::USD::FSchemaHandler
    {
    public:
        virtual const FString& GetHandlerName() const override;
        virtual const FString& GetTargetSchemaName() const override; // e.g., “CustomSchema”
        virtual bool OnTranslate(
            const UE::FUsdPrim& Prim,
            UE::Interchange::USD::FTraversalInfo& TraversalInfo,
            UE::Interchange::USD::FHandlerAccumulatedInfo& AccumulatedInfo,
            UInterchangeUsdContext& UsdContext
        ) override;
    };

    // 在你的模块 StartupModule() 中注册
    void FMyModule::StartupModule()
    {
        UE::Interchange::USD::FSchemaHandlerRegistry::Register<FMyCustomSchemaHandler>();
    }
    ```

2.  **程序化控制翻译**（来自 `UInterchangeUSDTranslator`）：
    ```cpp
    #include "InterchangeUSDTranslator.h"
    #include "InterchangeBaseNodeContainer.h"

    // 创建一个节点容器来存放翻译结果
    UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();

    // 创建翻译器实例
    UInterchangeUSDTranslator* Translator = NewObject<UInterchangeUSDTranslator>();

    // （可选）配置设置
    UInterchangeUsdTranslatorSettings* Settings = Translator->GetSettings();
    Settings->PrimsToImport = { TEXT("/World/MyCharacter") }; // 只导入特定子树
    Translator->SetSettings(Settings);

    // 翻译 USD 文件（SourceData 需要从文件创建）
    // Translator->Translate(*NodeContainer);

    // 翻译完成后，NodeContainer 中包含了所有转换后的 Interchange 节点。
    ```

### 进阶用法

-   **与 USD Stage 交互**：通过 `UInterchangeUsdContext` 直接访问底层的 `UE::FUsdStage`，可以在翻译器或处理器内部调用 USD SDK 进行更底层的操作。
-   **自定义 Payload 处理**：通过重写 `FSchemaHandler` 的 `OnGet...PayloadData` 系列函数，可以介入或后处理各种资产数据（网格体、纹理、动画等）的生成过程。
-   **LOD 变体处理**：插件内部使用 `SchemaHandlerUtils` 中的函数（如 `GetLODMesh`）处理基于 Variant Set 的 LOD。自定义处理器需要遵循 `FTraversalInfo::bInsideLODVariant` 等状态来正确处理 LOD 数据。

## Demo 示例

以下是一个最小的 C++ 示例，展示如何使用 `UInterchangeUSDTranslator` 导入一个 USD 文件并遍历生成的节点。

**MyUSDImporter.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UInterchangeBaseNodeContainer;

class FMyUSDImporter
{
public:
    void ImportUSDFile(const FString& USDFilePath);
    void ProcessNodes(const UInterchangeBaseNodeContainer* NodeContainer);
};
```

**MyUSDImporter.cpp**
```cpp
#include "MyUSDImporter.h"
#include "InterchangeUSDTranslator.h"
#include "InterchangeBaseNodeContainer.h"
#include "InterchangeManager.h" // 通常由Interchange系统内部使用

void FMyUSDImporter::ImportUSDFile(const FString& USDFilePath)
{
    // 创建一个节点容器来存储翻译结果
    UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();

    // 创建并配置USD翻译器
    UInterchangeUSDTranslator* Translator = NewObject<UInterchangeUSDTranslator>();

    // 可选：修改导入设置
    if (UInterchangeUsdTranslatorSettings* Settings = Translator->GetSettings())
    {
        Settings->bTranslatePrimAttributes = true;
        Settings->AttributeRegexFilter = TEXT(“^(myAttribute|userDefined).*$”);
        Settings->KindsToCollapse = static_cast<int32>(EUsdDefaultKind::Component);
    }

    // 注意：在实际的 Interchange 流程中，源数据(SourceData)和翻译(Translate)调用由 Interchange Manager 管理。
    // 此处为演示原理。实际使用应通过 Interchange 的标准导入流程。
    // bool bSuccess = Translator->Translate(*NodeContainer);

    // if (bSuccess)
    // {
    //     ProcessNodes(NodeContainer);
    // }
}

void FMyUSDImporter::ProcessNodes(const UInterchangeBaseNodeContainer* NodeContainer)
{
    if (!NodeContainer) return;

    // 遍历所有生成的节点
    for (auto It = NodeContainer->GetCreateNodeIterator(); It; ++It)
    {
        const UInterchangeBaseNode* Node = It->Value;
        if (Node)
        {
            UE_LOG(LogTemp, Log, TEXT(“Translated Node: %s (UID: %s) (Class: %s)”),
                *Node->GetDisplayLabel(),
                *Node->GetUniqueID(),
                *Node->GetClass()->GetName());
            // 可以根据 Node->GetClass() 进一步处理不同类型的节点，如 UInterchangeMeshNode, UInterchangeMaterialNode 等。
        }
    }
}
```

## 模块依赖

要使用此插件，你的模块需要在 `.Build.cs` 文件中添加以下依赖项：

| 模块 | 用途 |
|---|---|
| `Interchange` | Interchange 框架的核心模块。 |
| `InterchangeImport` | Interchange 的导入相关基础设施。 |
| `UnrealUSDWrapper` | 提供对 USD SDK 的封装（`FUsdPrim`, `FUsdStage` 等）。 |
| `USDClasses` | 包含与 USD 相关的 UObject 类（如 `UInterchangeUsdContext`）。 |

**示例 `.Build.cs` 片段**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    “Interchange”,
    “InterchangeImport”,
    “UnrealUSDWrapper”,
    “USDClasses”
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 预生成改进：实现对骨架和物理资产的跟踪。 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | 修复了对 USDZ 文件处理的错误。 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | 预生成改进：为 MaterialX 翻译器生成的节点正确标记对应的 Prim 路径。 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复了实例内部材质无法正确去重的错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 的代码警告。 |

### 维护评价

该插件目前处于**实验性阶段**（`IsExperimentalVersion = true`）且**默认未启用**，表明其 API 和功能可能在未来版本中发生变化。从近期的 Git 提交记录（2026年5月）来看，它仍在被**积极开发和维护**中，主要工作集中在改进“USD Pregen”（预生成）流程，修复特定文件格式（USDZ）的处理，并优化材质去重等细节问题。

鉴于其复杂的架构和对 USD 标准的全面支持，它是 UE 中导入 USD 资产的核心解决方案。然而，由于其**实验性**状态，在生产环境中使用时需要做好应对 API 变化和潜在问题的准备。推荐用于需要高质量、可配置 USD 导入的项目，并建议密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [官方文档]() (无官方文档链接)
- [测试用例]() (未提供具体测试文件路径)