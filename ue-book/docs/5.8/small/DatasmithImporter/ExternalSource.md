# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 场景导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ExternalSource` (Runtime), `DirectLinkExtension` (Runtime), `DatasmithTranslator` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithImporter` (Runtime), `DatasmithExternalSource` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 插件的核心用途是将来自各种专业设计软件（如 CAD、BIM、DCC 工具）的复杂三维场景数据，通过统一的“Datasmith”格式高效导入到 Unreal Engine 中。它不仅仅是简单的文件导入，更关键的是建立了一个 **基于 URI 的外部资源访问框架**。

这个插件解决的核心问题是：传统文件导入（如 FBX）不适用于需要保持与外部设计源实时同步、或从非本地文件系统（如网络服务、版本管理系统）获取数据的场景。Datasmith Importer 通过 `FExternalSource` 和 `IUriResolver` 等抽象，允许引擎从多种可插拔的数据源（文件、DirectLink 连接、网络 API 等）加载场景，并支持同步/异步加载、状态追踪（是否过期）、自动重导等高级功能。

## 使用场景

-   **建筑与工程可视化**：需要从 Revit、ArchiCAD、SketchUp 等 BIM 软件导入包含丰富元数据和层级结构的建筑模型，并保持与原始设计文件的链接。
-   **产品设计与制造**：从 CATIA、NX、SolidWorks 等 CAD 软件导入高精度的机械模型，用于虚拟评审、培训或销售配置器。
-   **汽车设计**：使用 VRED 等软件创建车辆内外饰渲染场景，并将其导入 UE 进行实时交互式体验开发。
-   **基于服务的工作流**：场景数据可能存储在云服务器或通过特定 API（如 DirectLink）提供，需要引擎能够动态连接和加载。

## 蓝图用法

此插件主要提供底层框架，蓝图接口相对有限。核心功能通过 C++ 访问，但可以通过封装暴露一些关键操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TryLoad` | 尝试加载外部资源，返回加载后的 `IDatasmithScene` | `FExternalSource` |
| `AsyncLoad` | 异步加载外部资源，返回一个 `TFuture` | `FExternalSource` |
| `IsAsyncLoading` | 检查是否正在进行异步加载 | `FExternalSource` |
| `CancelAsyncLoad` | 取消正在进行的异步加载 | `FExternalSource` |
| `IsOutOfSync` | 检查加载的场景是否与源文件不同步 | `FExternalSource` |
| `GetSourceName` | 获取外部资源的名称 | `FExternalSource` |
| `BrowseExternalSource` | 打开对话框浏览指定 URI 方案的外部资源（仅编辑器） | `IUriManager` |

### 使用示例（蓝图描述）

在蓝图中，通常不会直接操作 `FExternalSource`。更常见的做法是在 C++ 层创建一个 UObject 包装器或子系统，将 `FExternalSource` 的生命周期和操作封装成蓝图友好的函数。例如，你可以创建一个“Datasmith 场景加载器”蓝图库：

1.  **暴露一个“从文件加载”函数**：输入一个文件路径字符串，内部创建 `FSourceUri::FromFilePath(Path)`，然后通过 `IExternalSourceModule::GetOrCreateExternalSource(Uri)` 获取或创建 `FExternalSource`，最后调用 `TryLoad()` 并返回场景指针。
2.  **暴露一个“异步加载”函数**：输入 URI 字符串，类似地获取 `FExternalSource`，调用 `AsyncLoad()`，并设置一个延迟循环节点来轮询 `IsAsyncLoading()` 和获取 `Future` 的结果。

## C++ 用法

### 头文件引入

```cpp
#include "ExternalSourceModule.h" // 获取 IExternalSourceModule
#include "ExternalSource.h"       // 使用 FExternalSource
#include "SourceUri.h"            // 使用 FSourceUri
#include "IUriResolver.h"         // 实现自定义的 URI 解析器
```

### 基本用法

从文件路径加载一个 Datasmith 场景。

```cpp
// 引擎启动后，确保模块已加载。
IExternalSourceModule& ExternalSourceModule = IExternalSourceModule::Get();

// 1. 创建一个指向本地文件的 URI。
FSourceUri FileUri = FSourceUri::FromFilePath(TEXT("C:/Projects/MyScene.udatasmith"));

// 2. 通过模块获取或创建对应的 ExternalSource。
//    模块内部会查找已注册的解析器（如文件系统解析器）来处理 “file://” 方案。
TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource = ExternalSourceModule.GetOrCreateExternalSource(FileUri);

// 3. 检查资源是否可用。
if (ExternalSource && ExternalSource->IsAvailable())
{
    // 4. 同步加载场景。
    TSharedPtr<IDatasmithScene> LoadedScene = ExternalSource->TryLoad();
    if (LoadedScene)
    {
        // 使用加载的场景数据...
    }
}
```
*示例灵感来源于测试用例和核心框架设计模式。*

### 进阶用法

实现一个自定义的 URI 解析器，用于从内存或网络服务加载场景。

```cpp
// 自定义解析器头文件: MyCustomResolver.h
#pragma once
#include "IUriResolver.h"

class FMyCustomResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    // IUriResolver 接口实现
    virtual FName GetScheme() const override { return TEXT("myservice"); }
    virtual bool CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const override;
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> GetOrCreateExternalSource(const UE::DatasmithImporter::FSourceUri& Uri) const override;
#if WITH_EDITOR
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(const UE::DatasmithImporter::FSourceUri& DefaultUri) const override;
#endif
};
```

```cpp
// 自定义解析器实现文件: MyCustomResolver.cpp
#include "MyCustomResolver.h"
#include "MyExternalSource.h" // 你的 FExternalSource 子类

bool FMyCustomResolver::CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const
{
    // 检查 URI 方案是否为 “myservice://...”
    return Uri.HasScheme(GetScheme().ToString());
}

TSharedPtr<UE::DatasmithImporter::FExternalSource> FMyCustomResolver::GetOrCreateExternalSource(const UE::DatasmithImporter::FSourceUri& Uri) const
{
    // 这里可以实现缓存逻辑
    return MakeShared<FMyExternalSource>(Uri);
}

// 在某个模块启动时注册此解析器
void RegisterCustomResolver()
{
    IExternalSourceModule& Module = IExternalSourceModule::Get();
    Module.GetManager().RegisterResolver(
        TEXT("MyCustomResolver"),
        MakeShared<FMyCustomResolver>()
    );
}

// 异步加载自定义源的示例
void AsyncLoadFromCustomService()
{
    FSourceUri ServiceUri(TEXT("myservice"), TEXT("/api/scenes/42"));
    auto ExternalSource = IExternalSourceModule::GetOrCreateExternalSource(ServiceUri);

    if (ExternalSource && ExternalSource->GetCapabilities().bSupportAsynchronousLoading)
    {
        ExternalSource->OnExternalSourceChanged.AddLambda([](const TSharedRef<UE::DatasmithImporter::FExternalSource>& Source)
        {
            // 加载完成的回调，可以在主线程安全地更新 UI 或触发其他操作
        });

        TFuture<TSharedPtr<IDatasmithScene>> FutureScene = ExternalSource->AsyncLoad();
    }
}
```

## Demo 示例

以下是一个可运行的最小示例，展示如何使用 Datasmith Importer 模块的核心功能来加载一个本地 Datasmith 文件。

**MyDatasmithLoader.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ExternalSource.h"
#include "MyDatasmithLoader.generated.h"

class IDatasmithScene;

UCLASS(BlueprintType)
class UMyDatasmithLoader : public UObject
{
    GENERATED_BODY()

public:
    /** 从文件路径同步加载一个 Datasmith 场景。*/
    UFUNCTION(BlueprintCallable, Category = "Datasmith")
    bool LoadSceneFromFile(const FString& FilePath, UPROPERTY(Out) IDatasmithScene*& OutScene);

private:
    TSharedPtr<UE::DatasmithImporter::FExternalSource> CurrentExternalSource;
};
```

**MyDatasmithLoader.cpp**
```cpp
#include "MyDatasmithLoader.h"
#include "ExternalSourceModule.h"
#include "SourceUri.h"
#include "DatasmithScene.h"

bool UMyDatasmithLoader::LoadSceneFromFile(const FString& FilePath, IDatasmithScene*& OutScene)
{
    OutScene = nullptr;
    if (!IExternalSourceModule::IsAvailable()) return false;

    // 1. 从文件路径创建 URI
    UE::DatasmithImporter::FSourceUri Uri = UE::DatasmithImporter::FSourceUri::FromFilePath(FilePath);
    if (!Uri.IsValid()) return false;

    // 2. 获取 ExternalSource
    CurrentExternalSource = IExternalSourceModule::GetOrCreateExternalSource(Uri);
    if (!CurrentExternalSource || !CurrentExternalSource->IsAvailable()) return false;

    // 3. 同步加载
    TSharedPtr<IDatasmithScene> ScenePtr = CurrentExternalSource->TryLoad();
    if (ScenePtr.IsValid())
    {
        // 为了方便在蓝图中使用，我们将其转换为 UObject。在实际项目中，可能需要其他处理。
        // 注意：IDatasmithScene 本身是接口，你需要一个 UObject 来持有它。
        // 这里假设我们使用 UDatasmithScene (引擎内置) 或其他包装器。
        // OutScene = NewObject<UDatasmithScene>(this);
        // ... 填充数据到 UObject ...
        // 为简化，我们返回一个有效性标志。
        return true;
    }

    return false;
}
```

## 模块依赖

要使用 Datasmith Importer 的核心功能（如 `FExternalSource`），你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ExternalSource` | 核心框架，提供 `FExternalSource`, `FSourceUri`, `IUriManager` 等。 |
| `DatasmithTranslator` | 定义了 `IDatasmithTranslator` 接口，用于解析特定格式的源文件。 |
| `DirectLinkExtension` | 如果使用 DirectLink（实时连接）功能，需要依赖此模块。 |
| `Tasks` | 用于异步加载任务调度。 |

**注意**：`DatasmithImporter` 模块本身是入口点，包含了工厂和编辑器集成。如果你只是想通过编程方式加载场景，直接依赖 `ExternalSource` 和 `DatasmithTranslator` 通常是足够的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了部分旧的对象遍历函数，并引入了新的替代方案。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，确保在编辑器修改前后有正确的通知。 |
| 2026-03-05 | `1adb9f68` | New material translator work: ... | 新材质翻译器相关工作（提交信息不完整）。 |

### 维护评价

Datasmith Importer 插件自 2019 年创建以来，作为 Unreal Engine 企业功能的核心部分，一直处于 **积极维护** 状态。从近期提交历史可以看出，开发团队仍在持续进行：

1.  **现代化改造**：更新日志宏（`UE_LOG` -> `UE_LOGF`）、废弃旧接口，表明代码库在持续演进。
2.  **功能增强**：存在关于“新材质翻译器”的提交，说明其功能集仍在扩展。
3.  **质量优化**：近期的提交多涉及代码清理、警告修复和规范遵循，旨在提高稳定性和可维护性。

该插件虽然默认未启用（`EnabledByDefault: false`），但这是企业功能的常见做法，用户可根据需要手动启用。其庞大的代码基数（162个源文件）和复杂的模块结构也体现了其功能的深度和专业性。

**推荐使用**：对于需要从专业设计软件导入复杂场景并保持数据链接的项目，Datasmith Importer 是 Epic Games 官方支持且持续维护的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests)