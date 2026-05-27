# Datasmith Importer

> Importer for Datasmith files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据智能导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 插件的核心并非简单的文件导入器，而是一个用于从各种外部数据源（如 CAD、BIM 软件）获取并管理 Datasmith 场景的框架。它主要解决以下问题：
1.  **实时同步**：通过 DirectLink 技术，允许 Unreal Engine 实时接收来自支持该协议的桌面软件（如 Revit, SketchUp）的设计变更，无需手动重新导入。
2.  **统一数据源管理**：将本地文件（如 .udatasmith 文件）和通过 DirectLink 连接的远程数据源抽象为统一的 `FExternalSource` 对象，为上层导入和同步逻辑提供一致的接口。
3.  **作为导入系统的后端**：它为 Unreal Editor 的标准导入/重导入流程提供了一个特定的“翻译器”（Translator），使其能够理解并处理来自这些外部数据源的 Datasmith 格式数据。

## 使用场景

- 你正在使用 Autodesk Revit、SketchUp、3ds Max 等软件进行建筑设计或工业建模 → 通过 DirectLink 实现模型在 UE 中的实时预览和更新。
- 你有一系列由 Datasmith Exporter 导出的 `.udatasmith` 文件，需要将其作为资产批量导入到 UE 项目中。
- 你需要开发一个自定义的连接器，将非标准或内部设计工具的三维数据以 Datasmith 格式引入 Unreal Engine。

## 蓝图用法

当前分析的 `DatasmithExternalSource` 模块主要处理底层数据源连接与场景加载，其核心类（如 `FDatasmithFileExternalSource`、`FDatasmithDirectLinkExternalSource`）均为 C++ 类，未在提供的头文件中发现 `UFUNCTION(BlueprintCallable)` 标记的蓝图 API。此模块的功能通常在 C++ 层或被更高层的 `DatasmithImporter` 模块封装调用。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithExternalSourceModule.h"
```

### 基本用法

该模块的核心是提供 `FExternalSource` 的具体实现。作为使用者，你可能需要根据需求继承或实例化这些类。

**示例：创建一个自定义的文件外部数据源（概念）**

```cpp
// 假设你需要支持一种新的文件格式作为 Datasmith 源。
// 你可以参考 FDatasmithFileExternalSource 的设计模式。
#include "DatasmithExternalSourceModule.h"
#include "ExternalSource.h" // 来自 ExternalSource 模块

class FMyCustomFileSource : public UE::DatasmithImporter::FDatasmithFileExternalSource
{
public:
    explicit FMyCustomFileSource(const FSourceUri& InSourceUri)
        : FDatasmithFileExternalSource(InSourceUri)
    {}

    // 重写加载逻辑以处理你的自定义格式
    virtual TSharedPtr<IDatasmithScene> LoadImpl() override
    {
        // 在此处解析你的文件格式，并转换为 IDatasmithScene
        TSharedPtr<IDatasmithScene> MyScene = /* ... 你的解析逻辑 ... */;
        return MyScene;
    }

    // 可以重写其他方法，如 GetSourceName, GetCapabilities 等
};
```
*来源：文件 `Private/DatasmithFileExternalSource.h` 展示了 `FDatasmithFileExternalSource` 的接口，`LoadImpl` 是加载文件内容的关键虚函数。*

### 进阶用法

结合 DirectLink 实现实时数据源接收。

```cpp
#include "DatasmithExternalSourceModule.h"
#include "DatasmithDirectLinkExternalSource.h"

// FDatasmithDirectLinkExternalSource 通过 DirectLink 协议接收场景。
// 通常不需要直接继承，而是通过 URI 解析器创建实例。
// 使用示例：当编辑器解析一个 directlink:// 开头的 URI 时，FDatasmithFileUriResolver 会创建此类的实例。

// 你可以创建自己的 URI 解析器来扩展支持的协议。
#include "DatasmithFileUriResolver.h" // 参考现有解析器

class FMyCustomUriResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    virtual bool CanResolveUri(const FSourceUri& URI) const override
    {
        // 判断是否能处理该 URI，例如 myapp:// 协议
        return URI.GetScheme() == TEXT("myapp");
    }

    virtual TSharedPtr<FExternalSource> GetOrCreateExternalSource(const FSourceUri& URI) const override
    {
        // 根据 URI 创建对应的外部数据源对象
        return MakeShared<FMyCustomFileSource>(URI);
    }

    virtual FName GetScheme() const override { return TEXT("myapp"); }
};

// 在模块启动时注册你的解析器
void FMyGameModule::StartupModule()
{
    if (UE::DatasmithImporter::FDatasmithExternalSourceModule::IsAvailable())
    {
        // 假设有注册机制（需查阅更完整的模块文档）
        // MyResolver 注册...
    }
}
```
*来源：`Private/DatasmithFileUriResolver.h` 展示了 URI 解析器的接口，`FDatasmithDirectLinkExternalSource.h` 展示了 DirectLink 数据源的实现。*

## Demo 示例

以下是一个最小化的自定义 Datasmith 文件数据源的示例。

**MyCustomDatasmithSource.h**
```cpp
#pragma once

#include "DatasmithFileExternalSource.h"

// 自定义数据源：用于处理扩展名为“.myformat”的文件，并将其转换为 Datasmith 场景。
class FMyCustomDatasmithSource : public UE::DatasmithImporter::FDatasmithFileExternalSource
{
public:
    explicit FMyCustomDatasmithSource(const FSourceUri& InSourceUri)
        : FDatasmithFileExternalSource(InSourceUri)
    {}

    // 核心：实现你自己的加载逻辑
    virtual TSharedPtr<IDatasmithScene> LoadImpl() override;

    // 可选：提供更友好的名称
    virtual FString GetSourceName() const override { return TEXT("MyCustomSource"); }

    // 可选：声明此源的能力
    virtual FExternalSourceCapabilities GetCapabilities() const override;
};
```

**MyCustomDatasmithSource.cpp**
```cpp
#include "MyCustomDatasmithSource.h"
#include "IDatasmithSceneElements.h" // Datasmith SDK 头文件

TSharedPtr<IDatasmithScene> FMyCustomDatasmithSource::LoadImpl()
{
    // 1. 从 FilePath (继承自 FDatasmithFileExternalSource) 获取文件路径
    const FString& FileToLoad = GetSourceUri().GetPath();

    // 2. 实现你的文件解析逻辑（此处为伪代码）
    TSharedPtr<IDatasmithScene> NewScene = /* 例如：FDatasmithSceneFactory::CreateScene(TEXT("MyScene")) */;

    // 3. 解析文件并将内容填充到 NewScene 中
    // ... 读取文件，创建 MeshActor, Material 等 Datasmith 元素并添加到场景 ...

    // 4. 返回构建好的场景
    return NewScene;
}

FExternalSourceCapabilities FMyCustomDatasmithSource::GetCapabilities() const
{
    FExternalSourceCapabilities Caps;
    Caps.bSupportsLiveUpdate = false; // 此自定义格式不支持实时更新
    return Caps;
}
```

## 模块依赖

此插件模块依赖链较复杂，且与其他 Datasmith 模块高度耦合。使用者在使用 `DatasmithExternalSource` 功能时，通常通过 `DatasmithImporter` 模块进行访问。

| 模块 | 用途 |
|---|---|
| `DatasmithSDK` | 核心 Datasmith 数据结构和场景接口 |
| `DirectLink` | DirectLink 协议实现，用于实时同步 |
| `ExternalSource` | 外部数据源的抽象基类和接口 |
| `DatasmithTranslator` | Datasmith 格式解析和场景翻译接口 |

*注意：实际项目中可能需要根据具体功能添加其他依赖，如 `DatasmithImporter` 模块本身。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 弃用了接受 `bIncludeNestedObjects` 参数的 `GetObjects*` 和 `ForEachObjectWithOuter` 函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了在 `PreEditChange`/`PostEditChange` 中修改纹理属性的代码，确保正确包装。 |
| 2026-03-05 | `1adb9f68` | New material translator work: ... | 新的材质翻译器相关工作。 |

### 维护评价

- **活跃维护**：从提交记录看，该插件在过去 3 个月内有持续的代码提交，内容涉及代码清理、警告修复、新功能开发和 API 更新。
- **企业级支持**：作为 `Engine/Plugins/Enterprise/` 下的插件，它属于 Epic Games 官方支持的企业级功能，有长期维护的保障。
- **持续演进**：最近的提交表明其正在适配引擎的新日志系统、清理旧 API 依赖并开发新的材质处理功能。
- **推荐使用**：对于需要与 CAD/BIM 软件进行数据交互的项目，该插件是官方推荐且维护良好的解决方案。它并非实验性功能，但需要手动在项目中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例] (可能位于 `Engine/Tests/DatasmithImporter/` 或插件内部，需根据具体版本确认)