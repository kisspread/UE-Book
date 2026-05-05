# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith Importer 是一个用于将外部设计数据（如 CAD、BIM 模型）导入 Unreal Engine 的框架。其核心是一个基于 **URI（统一资源标识符）** 的通用外部数据源管理系统。它不仅仅是一个简单的文件导入器，而是提供了一个可扩展的架构，允许通过不同的“解析器”（Resolver）从各种来源（本地文件、DirectLink 实时连接、云服务等）获取和加载数据。这个插件解决了从多样化的设计软件生态中高效、可靠地获取和同步复杂场景数据的问题。

## 使用场景

- 你在使用 Revit、SketchUp、3ds Max 等专业设计软件，并需要将模型实时或批量导入到 UE 中进行可视化、仿真或评审。
- 你需要建立一个从设计软件到 UE 的实时同步工作流（通过 DirectLink）。
- 你的项目需要从自定义的内部数据管理系统（如 PLM、资产库）中拉取设计数据。

## 蓝图用法

DatasmithImporter 插件主要提供 C++ 接口和编辑器工具。其核心的 `ExternalSource` 模块定义了底层框架，而上层的 `DatasmithImporter` 模块提供了具体的导入工厂和编辑器集成。蓝图中通常通过 Datasmith 导入对话框或资产操作来使用，直接暴露给蓝图的节点较少。主要的交互发生在编辑器 UI 和 C++ 代码中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateExternalSource` | 根据 URI 获取或创建一个外部数据源对象 | `IExternalSourceModule` / `IUriManager` |
| `BrowseExternalSource` | 打开一个对话框，用于浏览和选择特定 URI 方案的外部源 | `IUriManager` |

### 使用示例（蓝图描述）

由于核心功能是 C++ 框架，蓝图中通常不直接操作 `FExternalSource`。更常见的用法是：
1.  在编辑器中，通过“导入”按钮或右键菜单选择 Datasmith 文件（`.udatasmith`）。
2.  插件内部会使用 `FSourceUri::FromFilePath` 将文件路径转换为 URI。
3.  然后通过 `IUriManager` 查找合适的 `IUriResolver`（例如 `DatasmithNativeTranslator` 模块中的解析器）来创建 `FExternalSource` 并加载场景。

## C++ 用法

### 头文件引入

```cpp
#include "ExternalSourceModule.h"
#include "IUriManager.h"
#include "IUriResolver.h"
#include "SourceUri.h"
#include "ExternalSource.h"
```

### 基本用法

**1. 获取 URI 管理器并检查 URI 是否可解析**

```cpp
// 来源：基于 IUriManager.h 和 IExternalSourceModule.h 的接口设计
if (IExternalSourceModule::IsAvailable())
{
    IUriManager& UriManager = IExternalSourceModule::Get().GetManager();
    UE::DatasmithImporter::FSourceUri MyUri(TEXT("file"), TEXT("/Game/MyModel.udatasmith"));

    if (UriManager.CanResolveUri(MyUri))
    {
        // 此 URI 可以被某个已注册的解析器处理
        TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource = UriManager.GetOrCreateExternalSource(MyUri);
        if (ExternalSource.IsValid())
        {
            // 处理外部源...
        }
    }
}
```

**2. 从文件路径创建 URI**

```cpp
// 来源：基于 SourceUri.h 的静态方法
FString FilePath = FPaths::ProjectContentDir() + TEXT("Models/Chair.rvt");
UE::DatasmithImporter::FSourceUri FileUri = UE::DatasmithImporter::FSourceUri::FromFilePath(FilePath);
// FileUri 的 Scheme 将是 “file”，Path 是文件的绝对路径
```

### 进阶用法

**实现并注册自定义的 URI 解析器**

```cpp
// 来源：基于 IUriResolver.h 的接口定义
class FMyCustomResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    virtual FName GetScheme() const override { return FName(TEXT("myapp")); }

    virtual bool CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const override
    {
        return Uri.HasScheme(TEXT("myapp"));
    }

    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> GetOrCreateExternalSource(const UE::DatasmithImporter::FSourceUri& Uri) const override
    {
        // 根据 URI 的路径和查询参数，创建并返回一个代表自定义数据源的 FExternalSource 子类实例
        // ...
        return MakeShared<FMyCustomExternalSource>(Uri);
    }

#if WITH_EDITOR
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(const UE::DatasmithImporter::FSourceUri& DefaultUri) const override
    {
        // 实现一个文件浏览器或自定义对话框，让用户选择数据源
        // ...
        return nullptr;
    }
#endif
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    if (IExternalSourceModule::IsAvailable())
    {
        IUriManager& UriManager = IExternalSourceModule::Get().GetManager();
        TSharedRef<FMyCustomResolver> Resolver = MakeShared<FMyCustomResolver>();
        UriManager.RegisterResolver(Resolver->GetScheme(), Resolver);
    }
}

// 在模块关闭时注销
void FMyModule::ShutdownModule()
{
    if (IExternalSourceModule::IsAvailable())
    {
        IUriManager& UriManager = IExternalSourceModule::Get().GetManager();
        UriManager.UnregisterResolver(FName(TEXT("myapp")));
    }
}
```

## Demo 示例

一个最小化的自定义 URI 解析器实现。

**MyCustomResolver.h**
```cpp
#pragma once

#include "IUriResolver.h"
#include "ExternalSource.h"

class FMyCustomExternalSource : public UE::DatasmithImporter::FExternalSource
{
public:
    explicit FMyCustomExternalSource(const UE::DatasmithImporter::FSourceUri& InUri)
        : UE::DatasmithImporter::FExternalSource(InUri)
    {}

    // ... 实现所有纯虚函数，如 GetSourceName, IsAvailable, GetDatasmithScene 等
};

class FMyCustomResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    virtual FName GetScheme() const override;
    virtual bool CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const override;
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> GetOrCreateExternalSource(const UE::DatasmithImporter::FSourceUri& Uri) const override;
#if WITH_EDITOR
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(const UE::DatasmithImporter::FSourceUri& DefaultUri) const override;
#endif
};
```

**MyCustomResolver.cpp**
```cpp
#include "MyCustomResolver.h"
#include "ExternalSourceModule.h"

FName FMyCustomResolver::GetScheme() const
{
    return FName(TEXT("myapp"));
}

bool FMyCustomResolver::CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const
{
    return Uri.HasScheme(TEXT("myapp"));
}

TSharedPtr<UE::DatasmithImporter::FExternalSource> FMyCustomResolver::GetOrCreateExternalSource(const UE::DatasmithImporter::FSourceUri& Uri) const
{
    // 这里可以添加缓存逻辑
    return MakeShared<FMyCustomExternalSource>(Uri);
}

#if WITH_EDITOR
TSharedPtr<UE::DatasmithImporter::FExternalSource> FMyCustomResolver::BrowseExternalSource(const UE::DatasmithImporter::FSourceUri& DefaultUri) const
{
    // 可以打开一个自定义对话框让用户选择“myapp”数据源
    // 例如：FMyAppBrowserDialog Dialog;
    // if (Dialog.ShowModal() == ...)
    // {
    //     return GetOrCreateExternalSource(Dialog.GetSelectedUri());
    // }
    return nullptr;
}
#endif
```

## 模块依赖

从模块名称和功能推断，使用此插件或其子模块可能需要以下依赖。具体依赖关系需查阅各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和接口 |
| `DirectLink` | DirectLink 实时同步协议的核心库 |
| `DatasmithContent` | Datasmith 导入后生成的资产类型（如 `UDatasmithAssetImportData`） |

## 维护状态

### 近期更新

```
- cbf22b5a20dd Replace some usages of FORCEINLINE with inline in Datasmith modules.
- 0aaf98a1a0b5 Fixed some 'deprecated' FString usage.
- 28609e6f3c58 Removal of TEXT used in static_asserts (redundant in ANSI/wide modes, broken in UTF-8 mode).
```

最近的提交主要是代码清理和编译兼容性修复，没有新功能或重大重构。

### 维护评价

Datasmith Importer 是一个成熟的企业级插件，自 2019 年创建以来一直是 UE 中处理专业设计数据的核心方案。虽然近期更新以维护性修复为主，但这通常意味着其核心功能已经稳定。作为 Epic Games 官方维护的“Enterprise”类别插件，其长期支持和兼容性是有保障的。**推荐使用**，特别是对于建筑、工程和施工（AEC）以及产品设计可视化领域。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest 模块)