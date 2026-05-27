# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

虽然 `.uplugin` 描述为“Datasmith 文件导入器”，但 `DatasmithTranslator` 模块的核心是一个**可扩展的翻译器（Translator）架构**。它定义了一套通用接口（`IDatasmithTranslator`）和管理机制（`FDatasmithTranslatorManager`），允许第三方开发者创建自定义的“翻译器”来支持新的 CAD、BIM 或其他三维格式。其根本目的是**扩展 Unreal Engine 的 Datasmith 管线**，使其能够导入官方未直接支持的文件格式，或为现有格式提供优化的导入逻辑。

简单来说，Datasmith 本身是一个数据管道，而 `DatasmithTranslator` 是这个管道的**插件插座**，让你能插入新的“转换头”来处理各种来源的数据。

## 使用场景

-   **你的设计软件（如特定版本的 SolidWorks, CATIA, 或自研 CAD 工具）输出的文件格式，官方 Datasmith 不支持** → 你需要基于 `DatasmithTranslator` 模块开发一个自定义翻译器。
-   **你希望优化从某个特定 CAD 软件（如 Revit, SketchUp, Cinema 4D）导入的资产（材质、网格、动画）的质量或效率** → 你可以创建一个翻译器来覆盖默认的 `DatasmithNativeTranslator` 行为。
-   **你需要将自定义的、非标准的场景描述格式转换为 UE 可用的资产** → 你可以利用翻译器框架解析你的格式，并将其转换为 `IDatasmithScene` 对象。
-   **作为插件开发者，你想为你的 UE 插件提供从特定文件类型直接导入资产的能力** → 你可以将翻译器作为插件的一部分进行注册。

## 蓝图用法

该模块主要提供 C++ 接口，没有直接暴露给蓝图的运行时函数。其主要功能（注册/查询翻译器）在编辑器工具链（如内容浏览器的“导入”功能）中被调用。开发者通过 C++ 实现 `IDatasmithTranslator` 接口并进行注册，随后编辑器的导入流程会自动发现和使用这些翻译器。

### 核心节点
*无直接蓝图节点。*

## C++ 用法

本模块的核心是定义翻译器接口和管理系统。

### 头文件引入

```cpp
#include "DatasmithTranslator.h"
#include "DatasmithTranslatorManager.h"
#include "DatasmithSceneSource.h"
#include "DatasmithTranslatableSource.h"
```

### 基本用法：实现并注册一个自定义翻译器

首先，创建一个继承自 `IDatasmithTranslator` 的类，并实现其关键虚函数。

```cpp
// MyCADTranslator.h
#pragma once

#include "DatasmithTranslator.h"

class FMyCADTranslator : public IDatasmithTranslator
{
public:
    virtual ~FMyCADTranslator() override = default;

    // 返回翻译器唯一名称
    virtual FName GetFName() const override
    {
        return FName(TEXT("MyCADTranslator"));
    }

    // 初始化时声明支持的文件格式
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT("mycad"), TEXT("My CAD Files (*.mycad)")));
    }

    // 验证源文件
    virtual bool IsSourceSupported(const FDatasmithSceneSource& Source) override
    {
        // 可在此进行更详细的文件头检查等
        return Source.GetSourceFileExtension().Equals(TEXT("mycad"), ESearchCase::IgnoreCase);
    }

    // 核心：将源文件解析为 Datasmith 场景
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        const FString& FilePath = GetSource().GetSourceFile();
        // ... 使用你的解析库读取 .mycad 文件，构建 IDatasmithScene ...
        return true;
    }

    // 加载网格负载（如果需要自定义网格数据加载逻辑）
    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // ... 根据 MeshElement 的元数据，生成对应的网格数据 ...
        return true;
    }

    // 可选：提供额外的导入选项 UI
    virtual void GetSceneImportOptions(TArray<TObjectPtr<UDatasmithOptionsBase>>& Options) override
    {
        // 创建并添加一个自定义的选项 Uobject
        // Options.Add(Datasmith::MakeOptionsObjectPtr<UMyCADImportOptions>());
    }
};
```

然后，在你的模块启动时注册这个翻译器。

```cpp
// MyCADTranslatorModule.cpp
#include "MyCADTranslator.h"
#include "Modules/ModuleManager.h"

class FMyCADTranslatorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 注册翻译器，使其对管理器可见
        Datasmith::RegisterTranslator<FMyCADTranslator>();
    }

    virtual void ShutdownModule() override
    {
        // 注销翻译器
        Datasmith::UnregisterTranslator<FMyCADTranslator>();
    }
};

IMPLEMENT_MODULE(FMyCADTranslatorModule, MyCADTranslator);
```

### 进阶用法：使用翻译器管理器和处理流程

```cpp
#include "DatasmithTranslatorManager.h"
#include "DatasmithSceneSource.h"
#include "DatasmithTranslatableSource.h"

// 1. 查询管理器支持的所有格式
void ListSupportedFormats()
{
    FDatasmithTranslatorManager& Manager = FDatasmithTranslatorManager::Get();
    const TArray<FString>& Formats = Manager.GetSupportedFormats();
    for (const FString& Format : Formats)
    {
        UE_LOG(LogTemp, Log, TEXT("Supported: %s"), *Format);
    }
}

// 2. 手动查找并使用翻译器加载场景
bool ImportCustomFile(const FString& FilePath)
{
    FDatasmithSceneSource Source;
    Source.SetSourceFile(FilePath);

    // 使用高层封装类 FDatasmithTranslatableSceneSource 管理生命周期
    FDatasmithTranslatableSceneSource TranslatableSource(Source);
    if (!TranslatableSource.IsTranslatable())
    {
        UE_LOG(LogTemp, Error, TEXT("No translator found for file: %s"), *FilePath);
        return false;
    }

    TSharedRef<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
    bool bLoadOk = TranslatableSource.Translate(Scene);

    if (bLoadOk)
    {
        // ... 使用 IDatasmithScene 进行后续的资产创建 (UDatasmithSceneImportData) ...
    }
    return bLoadOk;
}
```

## Demo 示例

一个最小化、可编译的自定义翻译器插件结构示例。

**MinimalTranslator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithTranslator.h"

class FMinimalTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override;
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override;
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override;
};
```

**MinimalTranslator.cpp**
```cpp
#include "MinimalTranslator.h"
#include "DatasmithScene.h"
#include "DatasmithMesh.h"

FName FMinimalTranslator::GetFName() const
{
    return FName(TEXT("MinimalTranslator"));
}

void FMinimalTranslator::Initialize(FDatasmithTranslatorCapabilities& OutCapabilities)
{
    OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT("mini"), TEXT("Minimal Files (*.mini)")));
}

bool FMinimalTranslator::LoadScene(TSharedRef<IDatasmithScene> OutScene)
{
    // 假设我们创建一个包含一个简单立方体的场景
    TSharedRef<IDatasmithMeshElement> MeshElement = IDatasmithScene::Factory::CreateMeshElement(TEXT("Cube"));

    // 你可以在这里为 MeshElement 设置属性，或重写 LoadStaticMesh 来提供自定义网格数据
    // 例如: MeshElement->SetFile(...);

    OutScene->AddMesh(MeshElement);
    return true;
}

// 在模块启动时注册：Datasmith::RegisterTranslator<FMinimalTranslator>();
```

## 模块依赖

从源码分析，`DatasmithTranslator` 模块主要依赖于 Datasmith 的核心场景描述类型。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 `IDatasmithScene`, `IDatasmithMeshElement` 等核心场景元素接口和类型。 |
| `MeshDescription` | 用于处理、转换和验证 3D 网格数据 (`FMeshDescription`)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. | 废弃了接受 bIncludeNestedObjects 参数的 GetObjects*/ForEachObjectWithOuter 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，按需包装在 PreEditChange/PostEditChange 中。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器工作：… |

### 维护评价

该模块创建于2019年，已有约7年历史，属于 UE 的核心企业级功能。**目前处于活跃维护状态**。从近期提交记录看（最近一次更新在2026年5月），Epic 持续进行代码优化、API 清理和编译器警告修复，表明该模块是稳定且受支持的。

它不是一个频繁添加新特性的“前沿”模块，而是 Datasmith 管线的基石，维护重点在于**稳定性和兼容性**。代码中存在一些已弃用的函数（如 Cloth 导入），表明 API 在演进。对于需要扩展 Datasmith 格式支持的开发者来说，这是一个**可靠且推荐使用**的基础框架。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests)（注：`DatasmithTranslator` 模块本身可能没有独立的单元测试，其功能通常由 `DatasmithImporter` 插件整体的集成测试覆盖。）