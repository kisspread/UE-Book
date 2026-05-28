# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据交换导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个企业级插件，用于将多种第三方三维设计软件（如 Revit、SketchUp、3ds Max、Cinema 4D 等）的工程文件直接导入到 Unreal Engine 中。它通过**翻译器（Translator）**架构工作：该插件提供一个通用的翻译器接口（`IDatasmithTranslator`），并包含多种特定软件的翻译器实现（如 Revit、SketchUp 的材质选择器等）。其核心价值在于将 CAD/BIM 软件中的复杂场景、材质、网格和动画数据高效、准确地转换为 UE 可用的资产，解决了 UE 原生导入工具对专业设计软件格式支持不足的问题。

## 使用场景

- 你在使用 **Autodesk Revit** 进行建筑信息模型（BIM）设计，需要将完整的建筑模型（包含材质、层次结构）导入 UE 进行实时可视化或 VR 审查。
- 你在使用 **SketchUp** 快速建模，希望将模型（包括材质属性）无缝导入 UE 制作建筑漫游或产品展示。
- 你需要将 **Cinema 4D** 或 **3ds Max** 中创建的复杂三维场景（网格、动画）导入 UE 进行影视预览或虚拟制片。
- 你需要一个统一的流程，将来自不同 CAD 软件的模型批量导入 UE，并希望材质和网格数据得到合理转换与优化。

## 蓝图用法

该插件主要通过 C++ 接口提供服务，蓝图中主要使用其导入功能，通常通过编辑器菜单或命令触发，而非直接调用蓝图节点。核心导入操作封装在 `DatasmithImporter` 模块中，该模块提供了资产导入器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Datasmith Import` | 编辑器命令，通过文件浏览器选择 `.udatasmith`、`.skp`、`.rvt` 等支持的文件进行导入。 | 菜单项 |

### 使用示例（蓝图描述）

在内容浏览器中右键，选择 `Import`，在文件类型中选择 Datasmith 支持的格式（如 `.udatasmith`），然后按照向导完成导入。此过程由 `DatasmithImporter` 模块自动调用相应的翻译器处理。

## C++ 用法

核心使用场景是编写自定义的 `IDatasmithTranslator` 实现，以支持新的文件格式。

### 头文件引入

```cpp
#include "DatasmithTranslator.h"
#include "DatasmithTranslatorManager.h"
```

### 基本用法

从提供的头文件中，我们可以看到核心接口是 `IDatasmithTranslator`。以下是如何注册一个自定义翻译器的示例。

```cpp
// MyCustomTranslator.h
#pragma once
#include "DatasmithTranslator.h"

class FMyCustomTranslator : public IDatasmithTranslator
{
public:
    // 必须重写：返回唯一的翻译器名称
    virtual FName GetFName() const override
    {
        return TEXT("MyCustomTranslator");
    }

    // 初始化时声明支持的文件格式
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(".myformat"), TEXT("My Custom Format")));
    }

    // 核心方法：加载场景数据到 IDatasmithScene
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 解析文件，填充 OutScene
        // ...
        return true;
    }

    // 可选：加载网格负载
    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement, FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // 根据 MeshElement 提供网格数据
        // ...
        return true;
    }
};
```

```cpp
// MyCustomTranslator.cpp
#include "MyCustomTranslator.h"
#include "DatasmithTranslator.h" // 提供 Datasmith::RegisterTranslator

// 模块启动时注册
void FMyCustomTranslatorModule::StartupModule()
{
    Datasmith::RegisterTranslator<FMyCustomTranslator>();
}

// 模块关闭时注销
void FMyCustomTranslatorModule::ShutdownModule()
{
    Datasmith::UnregisterTranslator<FMyCustomTranslator>();
}
```
*来源文件：`Public/DatasmithTranslator.h`*

### 进阶用法

使用 `FDatasmithTranslatorManager` 来查询支持的格式或手动选择翻译器。

```cpp
#include "DatasmithTranslatorManager.h"

// 获取所有支持的文件格式描述
const TArray<FString>& SupportedFormats = FDatasmithTranslatorManager::Get().GetSupportedFormats();

// 根据文件源选择合适的翻译器
FDatasmithSceneSource Source;
Source.SetSourceFile(TEXT("/path/to/model.rvt"));
TSharedPtr<IDatasmithTranslator> Translator = FDatasmithTranslatorManager::Get().SelectFirstCompatible(Source);

if (Translator.IsValid())
{
    // 使用翻译器加载场景
    TSharedRef<IDatasmithScene> Scene = MakeShared<FDatasmithScene>(); // 假设的场景实现
    bool bSuccess = Translator->LoadScene(Scene);
}
```
*来源文件：`Public/DatasmithTranslatorManager.h`*

## Demo 示例

一个最小的自定义翻译器模块示例，仅支持加载场景名称。

### MyTranslator.h
```cpp
#pragma once
#include "DatasmithTranslator.h"

class FMyTranslator : public IDatasmithTranslator
{
public:
    virtual FName GetFName() const override { return TEXT("MyTranslator"); }
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        OutCapabilities.SupportedFileFormats.Add(FFileFormatInfo(TEXT(".demo"), TEXT("Demo Format")));
    }
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 假设从 .demo 文件解析出场景名
        OutScene->SetName(TEXT("MyDemoScene"));
        return true;
    }
};
```

### MyTranslatorModule.cpp
```cpp
#include "Modules/ModuleManager.h"
#include "MyTranslator.h"
#include "DatasmithTranslator.h"

class FMyTranslatorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        Datasmith::RegisterTranslator<FMyTranslator>();
    }

    virtual void ShutdownModule() override
    {
        Datasmith::UnregisterTranslator<FMyTranslator>();
    }
};

IMPLEMENT_MODULE(FMyTranslatorModule, MyTranslator);
```

## 模块依赖

你的模块需要依赖 `DatasmithTranslator` 模块来使用其接口。

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | 提供核心的翻译器接口 (`IDatasmithTranslator`) 和管理器，是开发自定义翻译器的必需依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的代码警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了包含 `bIncludeNestedObjects` 参数的 `GetObjects*`/`ForEachObjectWithOuter` 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理代码，根据要求将更改纹理属性的操作封装在 `PreEditChange`/`PostEditChange` 中。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器工作： |

### 维护评价

Datasmith Importer 是一个历史悠久且持续维护的企业级插件。从近期提交记录看，它仍在进行代码清理、错误修复和新功能开发（如材质翻译器工作），表明**处于活跃维护状态**。该插件默认禁用（`EnabledByDefault: false`），表明它是可选的企业功能。鉴于其长期存在和持续更新，它是一个稳定且推荐使用的工具，特别适用于建筑、工程和建筑行业（AEC）以及工业设计领域。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests) （如果存在）