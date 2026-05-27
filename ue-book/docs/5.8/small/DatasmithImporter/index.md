# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 工业设计导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个企业级的插件，用于将复杂的 CAD、BIM 及其他工业设计软件（如 Revit, SketchUp, 3ds Max, CATIA, SolidWorks 等）的数据高效地转换并导入到虚幻引擎中。它不仅仅是一个简单的文件导入器，而是一套完整的管线，包括对 Datasmith 格式文件的解析、对原始设计软件场景层级、材质、灯光的忠实转换，以及通过 DirectLink 协议实现实时数据同步的能力，主要服务于建筑、工程和施工 (AEC)、产品设计以及虚拟制片等专业领域。

## 使用场景

- 你需要将建筑设计师在 Revit 或 SketchUp 中创建的 BIM 模型导入虚幻引擎，用于建筑可视化（ArchViz）。
- 你需要将工程师在 CATIA, SolidWorks, NX 中设计的精密机械模型导入，用于产品展示、交互式手册或数字孪生。
- 你需要将影视或游戏资产从 3ds Max, Maya 等 DCC 软件中导出并保持场景结构、材质实例和灯光设置，用于虚拟制片或实时渲染。
- 你需要一个稳定的、支持增量更新的导入流程，当源设计文件更新时，能够快速将更改同步到虚幻引擎项目中。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| [DatasmithExternalSource](DatasmithExternalSource.md) | Runtime | 处理外部数据源（如 DirectLink 或文件）的接口与管理。 |
| [DatasmithImporter](DatasmithImporter.md) | Runtime | **核心模块**。负责解析 Datasmith 文件，创建并管理对应的 UE 资产（Mesh, Material, Texture 等）。 |
| [DatasmithNativeTranslator](DatasmithNativeTranslator.md) | Runtime | 原生格式（如 CAD）的翻译器实现，将特定格式转换为通用的 Datasmith 场景结构。 |
| [DatasmithTranslator](DatasmithTranslator.md) | Runtime | 翻译器的基础框架和接口定义，用于扩展支持新的数据格式。 |
| [DirectLinkExtension](DirectLinkExtension.md) | Runtime | 实现 DirectLink 通信协议，支持与其他软件（如 Revit, SketchUp）的实时数据交换。 |
| [DirectLinkExtensionEditor](DirectLinkExtensionEditor.md) | Runtime | DirectLink 的编辑器扩展，提供相关 UI 和工具。 |
| [DirectLinkTest](DirectLinkTest.md) | Runtime | DirectLink 功能的测试模块。 |
| [ExternalSource](ExternalSource.md) | Runtime | 外部源（文件系统、网络）的通用访问抽象层。 |

## 蓝图用法

蓝图节点主要集成在 `DatasmithImporter` 和 `DirectLinkExtension` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Datasmith Scene` | 从文件路径异步导入一个完整的 Datasmith 场景。 | `UDatasmithImporter` |
| `Import File` | 通用的文件导入节点，可用于触发 Datasmith 导入流程。 | `UAssetImportTask` |
| `Reimport File` | 对已导入的资产进行重新导入，以更新源文件的改动。 | `UAssetImportTask` |
| `Get DirectLink Manager` | 获取 DirectLink 管理器单例，用于管理实时连接。 | `UDirectLinkManager` |
| `Open DirectLink Connection` | 打开一个 DirectLink 连接会话，等待源软件的连接请求。 | `UDirectLinkManager` |

### 使用示例（蓝图描述）

在蓝图中，你可以创建一个 `UDatasmithImportOptions` 对象来设置导入选项（如光照贴图分辨率、材质映射等），然后使用“Import Datasmith Scene”节点，传入选项对象和场景文件的绝对路径。该节点会返回一个 `UDatasmithSceneImportData` 对象，包含导入状态和生成的资产列表。对于实时同步，通过“Get DirectLink Manager”获取管理器，然后使用“Open DirectLink Connection”并指定端口，蓝图便会开始监听来自源软件（如 Revit）的连接和数据更新。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithImporter.h"
#include "DirectLinkExtension.h"
```

### 基本用法

以下示例展示了如何使用 C++ 代码导入一个 Datasmith 场景文件。
*（基于 `DatasmithImporter` 模块核心类）*

```cpp
#include "IDatasmithImporter.h"
#include "DatasmithSceneFactory.h"

void ImportDatasmithSceneFromFile(const FString& FilePath)
{
    // 1. 创建场景对象
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(*FPaths::GetBaseFilename(FilePath));

    // 2. 创建并配置导入器
    FDatasmithSceneImporter Importer;
    Importer.SetScenePath(FPaths::GetPath(FilePath)); // 设置场景资产存放路径

    // 3. 从文件解析场景数据
    bool bSuccess = Importer.ImportScene(*FilePath, Scene.Get());

    if (bSuccess && Scene.IsValid())
    {
        // 4. 此时，`Scene` 对象包含了从文件解析出的所有元素（Meshes, Materials, Lights 等）
        // 通常，你需要配合 UE 的资产创建管线（如 FAssetRegistryModule）来将这些数据转换为实际的 UObjects。
        UE_LOG(LogDatasmithImport, Log, TEXT("Successfully parsed Datasmith scene: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogDatasmithImport, Error, TEXT("Failed to import Datasmith scene from: %s"), *FilePath);
    }
}
```

### 进阶用法

使用 `DirectLinkExtension` 建立一个实时同步连接。
*（基于 `DirectLinkExtension` 模块核心类）*

```cpp
#include "IDirectLinkManager.h"

void EstablishDirectLinkConnection()
{
    // 获取 DirectLink 管理器实例
    IDirectLinkManager& DirectLinkManager = FModuleManager::Get().LoadModuleChecked<IDirectLinkExtensionModule>(TEXT("DirectLinkExtension")).GetDirectLinkManager();

    // 定义连接端点名称
    const FString EndpointName = TEXT("MyUnrealEndpoint");

    // 创建一个新的 DirectLink 端点
    IDirectLinkEndpoint* Endpoint = DirectLinkManager.CreateEndpoint(*EndpointName);

    if (Endpoint)
    {
        // 监听来自其他端点（如 Revit 插件）的场景更新
        Endpoint->SetSceneUpdateCallback([EndpointName](const TSharedPtr<IDirectLinkScene>& ReceivedScene)
        {
            if (ReceivedScene.IsValid())
            {
                // 在这里处理接收到的实时场景更新
                UE_LOG(LogDirectLink, Log, TEXT("[%s] Received a scene update."), *EndpointName);
            }
        });

        UE_LOG(LogDirectLink, Log, TEXT("DirectLink endpoint '%s' created and listening."), *EndpointName);
    }
}
```

## Demo 示例

一个最小的、可编译的示例，演示如何加载 DatasmithImporter 模块并触发一次简单的导入检查。

**MyDatasmithDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDatasmithDemoActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDatasmithDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDatasmithDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Datasmith")
    FString DatasmithFilePath;
};
```

**MyDatasmithDemoActor.cpp**
```cpp
#include "MyDatasmithDemoActor.h"
#include "DatasmithImporterModule.h"

AMyDatasmithDemoActor::AMyDatasmithDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDatasmithDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查 DatasmithImporter 模块是否已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("DatasmithImporter")))
    {
        UE_LOG(LogTemp, Log, TEXT("DatasmithImporter module is loaded. Ready to import."));
        if (!DatasmithFilePath.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Datasmith file to import: %s"), *DatasmithFilePath);
            // 在这里调用更具体的导入逻辑
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DatasmithImporter module is not available."));
    }
}
```

## 模块依赖

使用此插件前，请确保你的 `.Build.cs` 文件中包含以下依赖。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和常量定义。 |
| `DatasmithContent` | 为导入的 Datasmith 资产提供的专用 UObject 和蓝图节点。 |
| `MeshDescription` | 处理网格体几何数据的中间层，Datasmith 导入器用它来构建 StaticMesh。 |
| `MaterialShaderQualitySettings` | 管理材质着色器质量，确保材质在不同平台上正确渲染。 |
| `Json` | 解析 Datasmith 场景文件中可能包含的 JSON 元数据。 |
| `HTTP` | 用于 DirectLink 等网络功能或访问外部数据源。 |
| `Slate`, `SlateCore`, `UMG` | 为 `DirectLinkExtensionEditor` 提供编辑器 UI 支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了使用 `bIncludeNestedObjects` 布尔参数的旧版 `GetObjects`/`ForEachObjectWithOuter` 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，确保在 `PreEditChange`/`PostEditChange` 中正确处理。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新增材质翻译器相关工作。 |

### 维护评价

Datasmith Importer 是一个成熟的企业级插件，创建于 2019 年（约 7 年前）。尽管历史较长，但根据最近的 Git 提交记录（截至 2026 年 5 月），它仍在**积极维护**中。近期的更新涵盖了编译警告修复、代码清理、API 更新（废弃旧函数）以及新功能（材质翻译器）的开发，表明 Epic 团队持续关注其稳定性与功能扩展。

**综合评价**：该插件功能强大且稳定，是连接工业设计软件与虚幻引擎的核心桥梁。虽然默认未启用（需要手动在插件面板开启），但对于建筑、产品设计等专业领域用户而言，它是**强烈推荐**使用的必备工具。没有迹象表明它被废弃，可以放心在生产项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests) （如果存在）