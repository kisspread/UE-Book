# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 资产交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质函数库、材质定义、解析器模块） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

## 用途

Interchange Framework 是 UE5 中用于替换和扩展传统资产导入（Import）和导出（Export）流程的现代化框架。它的核心目的是提供一个**统一、可扩展、高性能**的管线来处理各种外部文件格式（如 FBX、glTF、USD 等）。

**它解决的问题：**
1.  **统一管理**：为不同资产类型（静态网格、骨骼网格、材质、纹理、动画等）提供一致的导入导出接口。
2.  **高度可扩展**：通过“翻译器（Translator）”和“管线（Pipeline）”的模块化设计，开发者可以轻松添加对新文件格式的支持，或自定义特定资产的处理逻辑。
3.  **性能优化**：支持异步和分布式处理（通过 `InterchangeDispatcher`），可以显著提升大规模资产批量处理的效率。
4.  **数据解耦**：将文件解析（`Parser`）、场景图构建（`Nodes`）、工厂节点（`FactoryNodes`）和最终资产生成（`Factory`）分离，使流程更清晰、更易调试。

## 使用场景

*   **游戏开发项目**：需要频繁导入由 3D 艺术家（使用 Maya、Blender、3ds Max 等）制作的模型、动画和材质时。
*   **自动化流水线**：在构建服务器上批量导入和处理美术资产，Interchange 的异步和模块化特性非常适合集成到 CI/CD 流程中。
*   **自定义资产格式支持**：如果你的游戏或应用使用了独特的文件格式（如专有的场景描述文件），可以通过编写自定义的 `Translator` 和 `Pipeline` 来无缝集成到 UE5 中。
*   **USD/MDL 等高级格式支持**：为支持 Universal Scene Description (USD) 等工业标准格式提供底层框架和扩展点。

## 蓝图用法

Interchange 框架主要通过 C++ 进行扩展和配置，但核心的导入导出操作可以通过引擎编辑器的 UI 触发，或通过一些公开的蓝图/Python API 执行。以下是一些核心功能节点：

### 核心节点

| 节点 | 说明 | 所在类/系统 |
|---|---|---|
| `UInterchangeManager::ImportScene` | 触发整个场景的导入流程 | `UInterchangeManager` |
| `UInterchangeManager::ExportScene` | 触发整个场景的导出流程 | `UInterchangeManager` |
| `UInterchangeManager::ImportAsset` | 导入单个资产 | `UInterchangeManager` |
| `UInterchangeManager::ExportAsset` | 导出单个资产 | `UInterchangeManager` |
| `UInterchangePipelineBase` | 所有管线的基类，用于自定义导入导出步骤 | `UInterchangePipelineBase` |
| `UInterchangeTranslatorBase` | 所有翻译器的基类，负责解析特定文件格式 | `UInterchangeTranslatorBase` |
| `UInterchangeFactoryBase` | 所有工厂的基类，负责创建最终的 UE 资产 | `UInterchangeFactoryBase` |

### 使用示例（蓝图描述）

虽然完整的自定义需要 C++，但可以通过蓝图组合 Interchange 提供的预设来完成常见任务。
1.  **使用预设导入**：在“内容浏览器”中右键选择“Import”，在弹出的对话框中，Interchange 会提供一个可配置的“Pipeline Stack”。你可以从中选择或组合已有的管线（如处理 FBX 的默认管线、处理材质的管线等）。
2.  **蓝图触发批量导入**：你可以创建一个蓝图，使用 `UInterchangeManager` 的静态函数，传入文件路径列表和预配置的管线数组，来程序化地批量导入资产。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeManager.h"
#include "InterchangePipelineBase.h"
#include "InterchangeTranslatorBase.h"
```

### 基本用法：通过代码触发导入

以下示例展示了如何以编程方式导入一个 FBX 文件，并使用默认管线。

```cpp
// 文件路径: 示例代码，非特定测试文件
void ImportFBXWithInterchange(const FString& FBXFilePath, const FString& DestinationPath)
{
    // 1. 获取 Interchange 管理器单例
    UInterchangeManager& InterchangeManager = UInterchangeManager::Get();

    // 2. 配置导入参数
    FInterchangeImportParameters ImportParameters;
    ImportParameters.bIsReimport = false;
    // 可以在此处设置其他参数，如是否导入材质、动画等

    // 3. 创建一个导入任务
    // 传入源文件路径、目标资产路径、导入参数和需要使用的管线（nullptr表示使用默认管线栈）
    TSharedRef<FInterchangeImportContext> ImportContext = MakeShared<FInterchangeImportContext>(
        FBXFilePath,
        DestinationPath,
        ImportParameters,
        nullptr // 使用默认管线栈
    );

    // 4. 异步启动导入任务
    InterchangeManager.ImportAssetAsync(ImportContext, FOnInterchangeImportComplete::CreateLambda(
        [] (const FInterchangeImportContext& Context, bool bSuccess)
        {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Interchange import succeeded for: %s"), *Context.GetSourceFilename());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Interchange import failed for: %s"), *Context.GetSourceFilename());
            }
        }
    ));
}
```

### 进阶用法：创建自定义管线

一个自定义管线可以拦截和修改导入过程中的数据。

```cpp
// 文件路径: 基于 InterchangePipelines 模块中的模式
#include "InterchangePipelineBase.h"

UCLASS()
class UMyCustomPipeline : public UInterchangePipelineBase
{
    GENERATED_BODY()

public:
    // 重写执行函数，在这里处理 Interchange 场景图中的节点
    virtual void ExecutePipeline(FInterchangePipelineContext& PipelineContext) override
    {
        // 获取从翻译器生成的场景节点图
        UInterchangeBaseNodeContainer* NodeContainer = PipelineContext.GetBaseNodeContainer();
        if (!NodeContainer) return;

        // 遍历所有网格节点
        TArray<UInterchangeBaseNode*> MeshNodes;
        NodeContainer->GetNodes(UInterchangeMeshNode::StaticClass(), MeshNodes);
        for (UInterchangeBaseNode* Node : MeshNodes)
        {
            UInterchangeMeshNode* MeshNode = Cast<UInterchangeMeshNode>(Node);
            if (MeshNode)
            {
                // 示例：强制所有网格为双面渲染
                MeshNode->SetCustomDoubleSidedAttribute(true);

                // 示例：修改网格的资产名称
                FString OriginalName = MeshNode->GetDisplayLabel();
                MeshNode->SetDisplayLabel(FString::Printf(TEXT("Custom_%s"), *OriginalName));
            }
        }

        // 注意：通常还需要调用父类的 ExecutePipeline 以继续执行后续管线步骤
        Super::ExecutePipeline(PipelineContext);
    }
};
```

## Demo 示例

一个最小化的自定义翻译器框架。

**头文件 (MyCustomTranslator.h):**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeTranslatorBase.h"
#include "MyCustomTranslator.generated.h"

UCLASS(BlueprintType)
class UMyCustomTranslator : public UInterchangeTranslatorBase
{
    GENERATED_BODY()

public:
    // 该翻译器是否能翻译指定的源文件
    virtual bool CanImportSourceData(const FInterchangeSourceData& SourceData) const override;

    // 执行实际的翻译（解析）工作，将文件内容转换为 Interchange 节点图
    virtual bool Translate(UInterchangeBaseNodeContainer& BaseNodeContainer) const override;
};
```

**源文件 (MyCustomTranslator.cpp):**
```cpp
#include "MyCustomTranslator.h"

bool UMyCustomTranslator::CanImportSourceData(const FInterchangeSourceData& SourceData) const
{
    // 检查文件扩展名是否为 “.mycustomformat”
    return SourceData.GetFilename().EndsWith(TEXT(".mycustomformat"));
}

bool UMyCustomTranslator::Translate(UInterchangeBaseNodeContainer& BaseNodeContainer) const
{
    // 1. 读取源文件
    // TArray<uint8> FileContent;
    // FFileHelper::LoadFileToArray(FileContent, *GetSourceData().GetFilename());

    // 2. 解析文件内容，创建对应的 Interchange 节点
    // 例如，创建一个网格节点
    const FString MeshNodeUid = TEXT("MyCustomMesh");
    UInterchangeMeshNode* MeshNode = NewObject<UInterchangeMeshNode>(&BaseNodeContainer);
    MeshNode->InitializeNode(MeshNodeUid, TEXT("MyAwesomeMesh"), EInterchangeNodeContainerType::TranslatedAsset);
    BaseNodeContainer->SetupNode(MeshNode);

    // 3. 为网格节点设置几何数据（顶点、三角形等）
    // MeshNode->SetCustomVertexPositions(...);
    // ...

    // 4. 返回翻译是否成功
    return true;
}
```

**在模块中注册翻译器：**
需要在你的游戏或插件模块中注册这个翻译器，使其能被 Interchange 框架发现。
```cpp
// 在你的模块 StartupModule() 函数中
IInterchangeModule& InterchangeModule = FModuleManager::LoadModuleChecked<IInterchangeModule>(TEXT("Interchange"));
InterchangeModule.RegisterTranslator<UMyCustomTranslator>();
```

## 模块依赖

从各个子模块的 Build.cs 分析，Interchange 框架内部模块相互依赖复杂。对于外部使用者（你的游戏/插件模块）来说，主要依赖如下模块即可使用其核心功能：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 核心框架，提供 `UInterchangeManager` 和基础节点类型。 |
| `InterchangeImport` | 提供导入相关的功能和基础工厂类。 |
| `InterchangeExport` | 提供导出相关的功能。 |
| `InterchangeNodes` | 定义所有具体的场景节点类型（如网格、材质、纹理节点）。 |
| `InterchangePipelines` | 提供基础的管线类和一些默认管线实现。 |
| `InterchangeFactoryNodes` | 定义工厂节点，连接场景节点与最终的 UE 资产类型。 |
| `InterchangeCommonParser` | 提供通用的解析器接口。 |
| `GLTFCore` | glTF 格式的核心解析库。 |
| `InterchangeFbxParser` | FBX 格式的解析器。 |

*注：如果你需要实现自定义格式，`InterchangeCore`, `InterchangeNodes`, `InterchangeCommonParser` 和 `InterchangePipelines` 是主要依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为 USD 资产预生成实现了对骨架和物理资产的跟踪功能。 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复了 UE 5.8 中的本地化警告。 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重新导入时重置现有的LOD模型，以确保骨骼绑定和映射得到更新。 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 重新将 uFBX 解析器作为实验性功能启用。 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复了因导入对象列表中存在空指针而导致的崩溃。 |

### 维护评价

*   **活跃维护**：从最近的 Git 历史看，该插件仍在**积极维护中**。最近的提交（2026年5月）包含了新功能（USD 骨骼跟踪）、兼容性修复（本地化警告、重新导入逻辑）和稳定性改进（修复崩溃）。
*   **版本状态**：从元数据看，它既不是 Beta 也不是实验性版本，默认启用，表明其已达到生产就绪状态。
*   **规模与复杂度**：这是一个大型、复杂的框架模块（753个源文件），由 Epic Games 官方维护，是未来 UE 资产导入导出的主力系统。
*   **推荐使用**：**强烈推荐**在新项目或需要自定义资产处理流程的项目中使用 Interchange 框架，而不是旧的 UFactory 系统。它提供了更好的扩展性、性能和统一的处理逻辑。旧项目如果需要深度修改导入行为，也可以考虑迁移。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
*   官方文档: (元数据中 DocsURL 为空，可参考 UE 官方文档站或源码注释)