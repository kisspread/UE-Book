# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 工业数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个用于将多种专业设计和工业数据格式无损导入 Unreal Engine 5 的完整工具链。它不仅仅是一个文件导入器，更是一个强大的数据转换和实时同步框架。其核心价值在于：

1.  **格式兼容性**：能够理解并转换来自建筑（如 Revit）、工程（如 CATIA, NX）、工业设计（如 SolidWorks）、可视化（如 3ds Max, SketchUp）以及 VR/AR 应用程序的复杂 CAD、BIM 和 3D 资产数据。
2.  **数据保真度**：在导入过程中尽可能保留原始数据的层次结构、几何体、材质、元数据和实例信息，确保在 UE 中重现设计意图。
3.  **实时同步 (DirectLink)**：通过其 DirectLink 技术，支持与源应用程序（如 3ds Max）的实时双向链接，源文件的修改可以近乎实时地同步到 UE 场景中，极大提升了迭代效率。
4.  **可扩展性**：其模块化架构（DatasmithTranslator）允许为新的数据格式开发自定义的翻译器，扩展引擎的导入能力。

它解决了设计师、工程师和建筑师将复杂、高精度的专业软件资产无缝集成到 UE5 实时交互环境中的核心痛点。

## 使用场景

-   **建筑设计与可视化 (AEC)**：建筑师使用 Revit 完成设计后，通过 Datasmith 将整个 BIM 模型（包括墙体、门窗、家具、元数据）导入 UE5，用于创建建筑可视化、虚拟样板间和数字孪生。
-   **产品设计与营销**：工业设计师将 CATIA 或 SolidWorks 设计的复杂机械零件或产品模型导入 UE5，创建交互式的产品配置器、拆解动画或高质量的营销视频。
-   **媒体与娱乐 (M&E)**：将 3ds Max 或 Cinema 4D 中创建的详细场景、角色和环境资产导入 UE5，用于虚拟制片、动画制作或游戏开发，同时利用 DirectLink 保持与源 DCC 工具的同步。
-   **施工模拟与培训**：导入施工进度模型，用于模拟施工过程、进行安全培训或制作施工方案演示。

## 蓝图用法

Datasmith 的主要操作通常通过编辑器菜单和资产浏览器完成，但其部分核心功能和工作流控制也可通过蓝图脚本化。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Datasmith Import Task` | 创建一个配置 Datasmith 导入任务的对象，可设置源文件路径、导入设置等。 | `UDatasmithImportTask` |
| `Execute Datasmith Import Task` | 执行由 `UDatasmithImportTask` 定义的导入操作，可获取导入进度和结果。 | `UDatasmithImportTask` |
| `Get Direct Link Exporter` | 获取 DirectLink 导出器实例，用于管理从外部源应用程序的实时链接和数据拉取。 | `UDirectLink` |
| `Sync Direct Link Source` | 通过 DirectLink 从已连接的外部源（如 3ds Max）强制同步数据到 UE。 | `UDirectLink` |

### 使用示例（蓝图描述）

1.  **基本文件导入**：
    -   使用 “Create Datasmith Import Task” 节点创建一个新任务。
    -   设置任务对象的 `SourceFile` 属性为要导入的 `.udatasmith` 或支持的 CAD 文件路径。
    -   可选：设置 `ImportOptions` 来控制材质、几何体的处理方式。
    -   调用 “Execute Datasmith Import Task” 执行导入，并通过输出引脚检查是否成功。
2.  **DirectLink 实时同步**：
    -   使用 “Get Direct Link Exporter” 获取 DirectLink 系统实例。
    -   在场景中，需要确保有相应的 `ADatasmithAreaLightActor` 或通过其他方式标识要同步的资产。
    -   当外部源文件更新时，使用 “Sync Direct Link Source” 节点触发同步，更新的资产和材质将自动反映在 UE 场景中。

## C++ 用法

Datasmith 的深度集成通常在 C++ 模块中进行，特别是开发自定义翻译器或与引擎管线深度集成时。

### 头文件引入

```cpp
#include "DatasmithImporter.h" // 核心导入功能
#include "DatasmithTranslator.h" // 翻译器接口
#include "DirectLinkExtension.h" // DirectLink 功能
```

### 基本用法

以下示例演示了如何在 C++ 中编程式地触发一次 Datasmith 导入。

```cpp
// 来源: 基于 UDatsmithImportTask 的通用导入模式
#include "DatasmithImportOptions.h"
#include "DatasmithImportFactory.h"

void ImportMyDatasmithFile(const FString& InFilePath)
{
    // 1. 创建导入任务对象
    UDatasmithImportTask* ImportTask = NewObject<UDatasmithImportTask>();
    ImportTask->SourceFile = InFilePath;

    // 2. 配置导入选项（可选）
    UDatasmithImportOptions* Options = ImportTask->ImportOptions;
    // 例如，合并网格体
    // Options->bMergeMeshes = true;

    // 3. 创建工厂并执行导入
    UDatasmithImportFactory* ImportFactory = NewObject<UDatasmithImportFactory>();
    // ImportFactory 会处理资产创建、几何体和材质转换的核心逻辑
    FEditorDelegates::OnAssetPreImport.Broadcast(ImportFactory, nullptr, nullptr, FName(*InFilePath), nullptr);
    // ... (实际执行逻辑通常由编辑器上下文和资产处理管线封装)
    // 在编辑器上下文中，更常见的做法是使用 FAssetEditorManager 或 UAssetImportTask
}
```

### 进阶用法：实现一个自定义 Datasmith 翻译器

Datasmith 的强大之处在于其可扩展的翻译器架构。你可以为自定义文件格式编写一个翻译器。

```cpp
// 文件: MyCustomTranslator.h
#pragma once

#include "DatasmithTranslator.h"

class FMyCustomTranslator : public IDatasmithTranslator
{
public:
    // 翻译器是否支持该文件
    virtual bool LoadFile(const FString& Filename) override;

    // 将自定义格式数据转换为 IDatasmithSceneElement 树
    virtual TSharedPtr<IDatasmithScene> GetScene() override;

    // 实现其他接口方法...
};
```

```cpp
// 文件: MyCustomTranslator.cpp
#include "MyCustomTranslator.h"
#include "DatasmithSceneFactory.h"

bool FMyCustomTranslator::LoadFile(const FString& Filename)
{
    // 解析你的自定义文件格式，将数据加载到内存
    // 返回 true 表示支持该文件
    return true;
}

TSharedPtr<IDatasmithScene> FMyCustomTranslator::GetScene()
{
    // 使用 DatasmithSceneFactory 创建一个场景
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyScene"));

    // 遍历你加载的自定义数据，创建对应的 Datasmith 元素
    // 例如，创建一个网格体元素
    TSharedPtr<IDatasmithMeshElement> MeshElement = FDatasmithSceneFactory::CreateMesh(TEXT("MyMesh"));
    // 设置顶点、UV、材质槽等...
    Scene->AddMesh(MeshElement);

    return Scene;
}
```

## Demo 示例

一个最小的 C++ 类，演示如何注册并使用一个简单的 Datasmith 翻译器。

```cpp
// 文件: MyDatasmithDemo.h
#pragma once

#include "CoreMinimal.h"

class FMyDatasmithDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// 文件: MyDatasmithDemo.cpp
#include "MyDatasmithDemo.h"
#include "Modules/ModuleManager.h"
#include "DatasmithTranslatorManager.h"
#include "MyCustomTranslator.h" // 假设已实现如上的自定义翻译器

#define LOCTEXT_NAMESPACE "FMyDatasmithDemoModule"

void FMyDatasmithDemoModule::StartupModule()
{
    // 注册我们的自定义翻译器，让 Datasmith 系统知道它
    if (IDatasmithTranslatorManager* TranslatorManager = IDatasmithTranslatorManager::Get())
    {
        TranslatorManager->RegisterTranslator(MakeShareable(new FMyCustomTranslator()));
    }
}

void FMyDatasmithDemoModule::ShutdownModule()
{
    // 模块关闭时可以进行清理
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyDatasmithDemoModule, MyDatasmithDemo)
```

**说明**：此 Demo 仅为结构示例。`FMyCustomTranslator` 的实现需要完整处理你的目标文件格式。要运行此示例，你需要将其编译为一个独立的 UE5 模块或插件，并确保 `StartupModule` 在引擎启动时被调用。

## 模块依赖

要使用或扩展 Datasmith Importer 的功能，你的模块需要依赖以下特定模块（除了标准的 Core/Engine 模块外）：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 Datasmith 核心数据类型（如 `IDatasmithScene`, `IDatasmithMeshElement`）和工厂。 |
| `DatasmithTranslator` | 提供翻译器接口（`IDatasmithTranslator`），用于开发自定义数据源支持。 |
| `DatasmithImporter` | 提供核心的导入逻辑、资产工厂和编辑器集成，用于实现或调用导入功能。 |
| `DirectLink` | 提供 DirectLink 网络通信和实时同步的核心库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量转 float 导致的警告代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 UE_LOG 宏迁移至新式 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了使用 bIncludeNestedObjects 参数的旧版对象遍历函数，并引入了新的替代函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，确保在 PreEditChange/PostEditChange 中进行包装处理。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器工作。 |

### 维护评价

Datasmith Importer 是 Unreal Engine 工业和企业管线的基石之一。

-   **活跃维护**：尽管创建于2019年，但近期（2026年5月）仍有代码质量改进（修复警告）和基础设施升级（日志迁移、废弃旧API）的更新，表明它处于积极的维护和迭代中。
-   **稳定性与成熟度**：作为已存在约7年的核心企业功能，其基本架构稳定，主要更新集中在兼容性改进、性能优化和 API 现代化，而非剧烈的功能变更。
-   **推荐使用**：对于任何需要从 CAD、BIM 或主流 DCC 软件导入复杂资产到 UE5 的项目，Datasmith 是**强烈推荐且不可或缺**的工具。它经过了大量工业项目的验证。请注意，它默认未启用（`EnabledByDefault: false`），需要在插件管理器中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests) （如果存在）