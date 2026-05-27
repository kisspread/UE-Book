# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 是 Unreal Engine 的企业级数据导入管线，用于将来自多种 CAD/BIM/DCC 软件（如 Revit、SketchUp、3ds Max、CATIA 等）的工业设计数据转换并导入为 UE 场景资产。其核心机制基于 **URI（统一资源标识符）** 体系来抽象外部数据源的访问方式，使得上层导入器不需要关心数据来自本地文件、数据库还是远程服务。

本插件解决的核心问题是：**工业设计软件的模型格式繁多且复杂，需要一套统一的抽象层来管理外部数据源的发现、缓存、加载和同步更新**。`ExternalSource` 模块作为底层基础，提供了 URI 解析、外部数据源管理和异步/同步加载能力，是整个 Datasmith 导入管线的根基。

## 使用场景

- 你需要从 Revit、SketchUp、CATIA 等工业软件导入模型到 Unreal Engine → 启用 DatasmithImporter
- 你需要通过 DirectLink 协议与其他应用实时同步场景数据 → 启用 DatasmithImporter，DirectLink 相关模块会自动工作
- 你需要自定义数据源（如从自研资产管理系统加载数据）→ 实现 `IUriResolver` 接口注册到 URI 管理器
- 你需要在编辑器中浏览和选择外部 Datasmith 源文件 → 使用 `IUriManager::BrowseExternalSource`

## 蓝图用法

本模块（ExternalSource）主要面向 C++ 扩展，不直接暴露蓝图节点。上层模块 DatasmithImporter 提供了蓝图可调用的导入功能。

### 核心概念

DatasmithImporter 的工作流通过以下核心概念串联：

| 概念 | 说明 | 所在类 |
|---|---|---|
| `FSourceUri` | 统一资源标识符，引用外部数据源 | `UE::DatasmithImporter::FSourceUri` |
| `FExternalSource` | 外部数据源抽象，负责加载和缓存场景 | `UE::DatasmithImporter::FExternalSource` |
| `IUriResolver` | URI 解析器接口，将 URI 映射为具体的 ExternalSource | `UE::DatasmithImporter::IUriResolver` |
| `IUriManager` | URI 管理器，统一管理所有已注册的 Resolver | `UE::DatasmithImporter::IUriManager` |

### 使用示例（蓝图描述）

Datasmith 导入在编辑器中主要通过 **Content Browser → Import** 或 **Datasmith 工具栏按钮** 触发。选择 `.udatasmith` 文件后，引擎会自动通过 URI 管理器解析文件路径，创建 ExternalSource 并加载场景。用户无需手动处理 URI 或 ExternalSource。

## C++ 用法

### 头文件引入

```cpp
#include "ExternalSourceModule.h"
#include "SourceUri.h"
#include "ExternalSource.h"
#include "IUriManager.h"
#include "IUriResolver.h"
```

### 基本用法：通过 URI 获取外部数据源

```cpp
#include "ExternalSourceModule.h"
#include "SourceUri.h"
#include "ExternalSource.h"

// 来源：基于 IUriManager::GetOrCreateExternalSource 和 FSourceUri 的设计

// 1. 构造一个文件 URI
UE::DatasmithImporter::FSourceUri SourceUri = UE::DatasmithImporter::FSourceUri::FromFilePath(
    TEXT("C:/Models/Building.udatasmith")
);

// 2. 通过模块接口获取或创建 ExternalSource
if (IExternalSourceModule::IsAvailable())
{
    TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource =
        IExternalSourceModule::GetOrCreateExternalSource(SourceUri);
    
    if (ExternalSource.IsValid() && ExternalSource->IsAvailable())
    {
        // 3. 同步加载场景
        TSharedPtr<IDatasmithScene> Scene = ExternalSource->TryLoad();
        if (Scene.IsValid())
        {
            // 场景加载成功，可以用于导入
            FString SceneName = ExternalSource->GetSceneName();
        }
    }
}
```

> 来源：`ExternalSourceModule.h`、`SourceUri.h`、`ExternalSource.h` 中的接口设计

### 异步加载外部数据源

```cpp
#include "ExternalSourceModule.h"
#include "ExternalSource.h"

// 来源：基于 FExternalSource::AsyncLoad / FExternalSourceCapabilities 的设计

TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource =
    IExternalSourceModule::GetOrCreateExternalSource(SourceUri);

if (ExternalSource.IsValid())
{
    UE::DatasmithImporter::FExternalSourceCapabilities Caps = ExternalSource->GetCapabilities();
    
    if (Caps.bSupportAsynchronousLoading)
    {
        // 异步加载，返回 TFuture
        TFuture<TSharedPtr<IDatasmithScene>> Future = ExternalSource->AsyncLoad();
        
        // 可以检查是否正在加载
        bool bLoading = ExternalSource->IsAsyncLoading();
        
        // 如需取消
        // ExternalSource->CancelAsyncLoad();
    }
    else if (Caps.bSupportSynchronousLoading)
    {
        // 退化为同步加载
        TSharedPtr<IDatasmithScene> Scene = ExternalSource->Load();
    }
}
```

> 来源：`ExternalSource.h` 中 `FExternalSourceCapabilities`、`AsyncLoad()`、`Load()` 方法

### 注册自定义 URI 解析器

```cpp
#include "ExternalSourceModule.h"
#include "IUriResolver.h"
#include "IUriManager.h"
#include "SourceUri.h"

// 来源：基于 IUriResolver 接口和 IUriManager::RegisterResolver 的设计

// 1. 实现自定义的 URI 解析器
class FMyCustomResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    virtual FName GetScheme() const override
    {
        return FName(TEXT("mycloud"));
    }
    
    virtual bool CanResolveUri(const UE::DatasmithImporter::FSourceUri& Uri) const override
    {
        return Uri.HasScheme(TEXT("mycloud"));
    }
    
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> GetOrCreateExternalSource(
        const UE::DatasmithImporter::FSourceUri& Uri) const override
    {
        // 创建并返回自定义的 ExternalSource 实现
        // ...
        return nullptr;
    }
    
#if WITH_EDITOR
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(
        const UE::DatasmithImporter::FSourceUri& DefaultUri) const override
    {
        // 实现浏览器对话框
        return nullptr;
    }
#endif
};

// 2. 注册解析器
if (IExternalSourceModule::IsAvailable())
{
    UE::DatasmithImporter::IUriManager& Manager = IExternalSourceModule::Get().GetManager();
    
    TSharedRef<FMyCustomResolver> Resolver = MakeShared<FMyCustomResolver>();
    Manager.RegisterResolver(FName(TEXT("MyCloudResolver")), Resolver);
    
    // 验证注册成功
    const TArray<FName>& Schemes = Manager.GetSupportedSchemes();
    // Schemes 现在包含 "mycloud"
    
    // 使用自定义 scheme 的 URI
    UE::DatasmithImporter::FSourceUri MyUri(TEXT("mycloud"), TEXT("server/project/model.udatasmith"));
    TSharedPtr<UE::DatasmithImporter::FExternalSource> Source = Manager.GetOrCreateExternalSource(MyUri);
    
    // 取消注册
    Manager.UnregisterResolver(FName(TEXT("MyCloudResolver")));
}
```

> 来源：`IUriResolver.h`、`IUriManager.h` 中的接口定义

### 进阶用法：监听数据源变更

```cpp
#include "ExternalSource.h"

// 来源：FExternalSource::OnExternalSourceChanged 委托

TSharedPtr<UE::DatasmithImporter::FExternalSource> ExternalSource =
    IExternalSourceModule::GetOrCreateExternalSource(SourceUri);

// 注册变更回调（用于自动重导入等场景）
ExternalSource->OnExternalSourceChanged.AddLambda(
    [](const TSharedRef<UE::DatasmithImporter::FExternalSource>& ChangedSource)
    {
        // 源数据已更新，可以触发重导入
        UE_LOG(LogExternalSource, Log, TEXT("Source updated: %s"), 
            *ChangedSource->GetSourceUri().ToString());
    }
);

// 检查源是否过时需要重新加载
if (ExternalSource->IsOutOfSync())
{
    // 重新加载
    TSharedPtr<IDatasmithScene> UpdatedScene = ExternalSource->TryLoad();
}
```

> 来源：`ExternalSource.h` 中 `OnExternalSourceChanged`、`IsOutOfSync()` 方法

## Demo 示例

一个完整的自定义 URI 解析器实现，展示如何扩展 Datasmith 导入管线支持自定义数据源。

```cpp
// MyCustomExternalSource.h
#pragma once

#include "ExternalSource.h"
#include "SourceUri.h"

class FMyCustomExternalSource : public UE::DatasmithImporter::FExternalSource
{
public:
    explicit FMyCustomExternalSource(const UE::DatasmithImporter::FSourceUri& InUri)
        : FExternalSource(InUri)
    {
    }

    virtual FString GetSourceName() const override
    {
        return GetSourceUri().GetPath().Len() > 0 
            ? FString(GetSourceUri().GetPath()) 
            : TEXT("Custom Source");
    }

    virtual bool IsAvailable() const override
    {
        // 根据实际情况判断源是否可用
        return GetSourceUri().IsValid();
    }

    virtual bool IsOutOfSync() const override
    {
        return false; // 简化示例
    }

    virtual FMD5Hash GetSourceHash() const override
    {
        return FMD5Hash();
    }

    virtual UE::DatasmithImporter::FExternalSourceCapabilities GetCapabilities() const override
    {
        return { true, false }; // 支持同步加载，不支持异步
    }

    virtual TSharedPtr<IDatasmithScene> GetDatasmithScene() const override
    {
        return CachedScene;
    }

    virtual FString GetFallbackFilepath() const override
    {
        return GetSourceUri().GetPath().Len() > 0
            ? FString(GetSourceUri().GetPath())
            : FString();
    }

protected:
    virtual TSharedPtr<IDatasmithScene> LoadImpl() override
    {
        // 实现你的加载逻辑
        // CachedScene = ...;
        return CachedScene;
    }

    virtual bool StartAsyncLoad() override
    {
        return false; // 不支持异步
    }

private:
    TSharedPtr<IDatasmithScene> CachedScene;
};
```

## 模块依赖

从 ExternalSource 模块的 Build.cs 推断，该模块依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | Datasmith 翻译器接口，用于将外部格式转换为 IDatasmithScene |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为新的 UE_LOGF 格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃带 bIncludeNestedObjects 参数的遍历函数，引入新 API |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，确保正确使用编辑回调包装 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 材质翻译器新功能开发 |

### 维护评价

**活跃维护中** ✅

- 创建于 2019 年，已有约 6 年历史，属于 Enterprise 插件的核心组件
- 最近的提交（2026年5月）显示仍在持续更新，包括代码质量改进（日志迁移、编译警告修复）和功能开发（新材质翻译器）
- 作为 Epic Games 官方维护的 Enterprise 插件，长期稳定支持
- `EnabledByDefault = false`，需要在项目设置中手动启用
- 8 个模块的设计反映了高度模块化的架构，便于按需裁剪
- **推荐使用**：如果你的项目需要从工业设计软件导入数据，这是官方唯一推荐的方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)