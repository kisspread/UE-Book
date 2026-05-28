# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 是 Epic Games 企业级数据导入框架的核心组件，专门用于将各种 CAD、BIM 和 3D 设计软件的场景数据导入 Unreal Engine。它不是一个简单的文件导入器，而是一个完整的**异构数据源抽象框架**。

本插件解决的核心问题：
- **统一数据源访问**：通过 URI 协议（`file://`、自定义协议）统一访问不同来源的 3D 场景数据
- **异步加载支持**：大型 CAD 模型加载耗时，需要异步处理避免阻塞编辑器
- **数据同步检测**：自动检测源文件是否过期（`IsOutOfSync`），支持自动重导入
- **可扩展架构**：通过 `IUriResolver` 接口支持自定义数据源后端

ExternalSource 模块作为整个框架的基础抽象层，定义了 `FExternalSource`、`FSourceUri`、`IUriResolver` 等核心类型。

## 使用场景

- 你正在使用 Revit、SketchUp、SolidWorks 等 CAD/BIM 软件 → 通过 Datasmith 导入复杂场景
- 你需要从文件系统导入 `.udatasmith` 文件 → 使用 `file://` URI 方案
- 你需要通过 DirectLink 实时同步 CAD 软件中的模型变更 → 使用 DirectLinkExtension 模块
- 你正在构建自定义数据源集成 → 实现 `IUriResolver` 接口注册自定义 URI 方案
- 你需要在编辑器中浏览和管理外部数据源 → 使用 `BrowseExternalSource` 功能

## 蓝图用法

ExternalSource 模块主要是 C++ 运行时 API，不直接暴露蓝图节点。蓝图交互主要通过上层 DatasmithImporter 模块提供的 Import 操作完成。

### 核心节点

该模块没有直接的蓝图可调用节点，但上层模块提供以下蓝图功能：

| 功能 | 说明 | 所在模块 |
|---|---|---|
| Datasmith Import | 通过文件浏览器导入 Datasmith 文件 | DatasmithImporter |
| Datasmith Reimport | 重新导入已有的 Datasmith 资产 | DatasmithImporter |

## C++ 用法

### 头文件引入

```cpp
#include "ExternalSourceModule.h"
#include "ExternalSource.h"
#include "SourceUri.h"
#include "IUriManager.h"
#include "IUriResolver.h"
```

### 基本用法：获取外部数据源

从 URI 创建并加载 Datasmith 场景：

```cpp
#include "ExternalSourceModule.h"
#include "SourceUri.h"
#include "ExternalSource.h"

// 从文件路径创建 URI
FSourceUri SourceUri = FSourceUri::FromFilePath(TEXT("/path/to/scene.udatasmith"));

// 通过模块获取外部数据源
TSharedPtr<FExternalSource> ExternalSource = IExternalSourceModule::GetOrCreateExternalSource(SourceUri);

if (ExternalSource.IsValid() && ExternalSource->IsAvailable())
{
    // 同步加载场景
    TSharedPtr<IDatasmithScene> Scene = ExternalSource->Load();
    if (Scene.IsValid())
    {
        // 使用加载的场景进行后续处理
        FString SceneName = ExternalSource->GetSceneName();
    }
}
```

### 异步加载用法

```cpp
#include "ExternalSource.h"

// 检查是否支持异步加载
FExternalSourceCapabilities Capabilities = ExternalSource->GetCapabilities();
if (Capabilities.bSupportAsynchronousLoading)
{
    // 启动异步加载
    TFuture<TSharedPtr<IDatasmithScene>> FutureScene = ExternalSource->AsyncLoad();
    
    // 绑定完成回调
    FutureScene.Then([ExternalSource](TFuture<TSharedPtr<IDatasmithScene>> Result)
    {
        TSharedPtr<IDatasmithScene> Scene = Result.Get();
        if (Scene.IsValid())
        {
            // 异步加载完成，处理场景
        }
    });
}
```

### 注册自定义 URI 解析器

```cpp
#include "IUriResolver.h"
#include "IUriManager.h"

// 实现自定义 URI 解析器
class FMyCustomResolver : public IUriResolver
{
public:
    virtual TSharedPtr<FExternalSource> GetOrCreateExternalSource(const FSourceUri& Uri) const override
    {
        // 根据 URI 创建对应的 ExternalSource 实例
        return MakeShared<FMyCustomExternalSource>(Uri);
    }
    
    virtual bool CanResolveUri(const FSourceUri& Uri) const override
    {
        return Uri.HasScheme(TEXT("myprotocol"));
    }
    
    virtual FName GetScheme() const override
    {
        return FName(TEXT("myprotocol"));
    }
    
#if WITH_EDITOR
    virtual TSharedPtr<FExternalSource> BrowseExternalSource(const FSourceUri& DefaultUri) const override
    {
        // 实现浏览对话框
        return nullptr;
    }
#endif
};

// 注册解析器
TSharedRef<FMyCustomResolver> Resolver = MakeShared<FMyCustomResolver>();
IExternalSourceModule::Get().GetManager().RegisterResolver(FName(TEXT("MyResolver")), Resolver);
```

### 监听数据源变更

```cpp
#include "ExternalSource.h"

// 注册数据源变更回调（用于自动重导入）
ExternalSource->OnExternalSourceChanged.AddLambda(
    [](const TSharedRef<FExternalSource>& ChangedSource)
    {
        // 源数据已更新，执行重导入逻辑
        UE_LOG(LogExternalSource, Log, TEXT("Source changed: %s"), *ChangedSource->GetSourceName());
    }
);
```

## Demo 示例

以下是一个完整的自定义 ExternalSource 实现示例：

### MyCustomExternalSource.h

```cpp
#pragma once

#include "ExternalSource.h"

namespace UE::DatasmithImporter
{
    /**
     * 自定义外部数据源示例
     * 演示如何继承 FExternalSource 实现自定义数据加载逻辑
     */
    class FMyCustomExternalSource : public FExternalSource
    {
    public:
        explicit FMyCustomExternalSource(const FSourceUri& InSourceUri);

        // FExternalSource 接口实现
        virtual FString GetSourceName() const override;
        virtual bool IsAvailable() const override;
        virtual bool IsOutOfSync() const override;
        virtual FMD5Hash GetSourceHash() const override;
        virtual FExternalSourceCapabilities GetCapabilities() const override;
        virtual TSharedPtr<IDatasmithScene> GetDatasmithScene() const override;
        virtual FString GetFallbackFilepath() const override;

    protected:
        virtual TSharedPtr<IDatasmithScene> LoadImpl() override;
        virtual bool StartAsyncLoad() override;

    private:
        TSharedPtr<IDatasmithScene> CachedScene;
        FMD5Hash LastSourceHash;
    };
}
```

### MyCustomExternalSource.cpp

```cpp
#include "MyCustomExternalSource.h"

namespace UE::DatasmithImporter
{
    FMyCustomExternalSource::FMyCustomExternalSource(const FSourceUri& InSourceUri)
        : FExternalSource(InSourceUri)
    {
    }

    FString FMyCustomExternalSource::GetSourceName() const
    {
        return GetSourceUri().GetPath().ToString();
    }

    bool FMyCustomExternalSource::IsAvailable() const
    {
        // 检查数据源是否可用（例如：检查文件是否存在）
        return true;
    }

    bool FMyCustomExternalSource::IsOutOfSync() const
    {
        // 检查数据源是否已更新（例如：比较文件修改时间或哈希）
        return false;
    }

    FMD5Hash FMyCustomExternalSource::GetSourceHash() const
    {
        return LastSourceHash;
    }

    FExternalSourceCapabilities FMyCustomExternalSource::GetCapabilities() const
    {
        FExternalSourceCapabilities Caps;
        Caps.bSupportSynchronousLoading = true;
        Caps.bSupportAsynchronousLoading = true;
        return Caps;
    }

    TSharedPtr<IDatasmithScene> FMyCustomExternalSource::GetDatasmithScene() const
    {
        return CachedScene;
    }

    FString FMyCustomExternalSource::GetFallbackFilepath() const
    {
        // 对于文件系统数据源，返回文件路径
        return GetSourceUri().GetPath().ToString();
    }

    TSharedPtr<IDatasmithScene> FMyCustomExternalSource::LoadImpl()
    {
        // 实现同步加载逻辑
        // 1. 从数据源读取场景数据
        // 2. 创建 IDatasmithScene
        // 3. 缓存并返回场景
        
        CachedScene = MakeShared<FDatasmithScene>();
        // ... 加载逻辑
        
        TriggerOnExternalSourceChanged();
        return CachedScene;
    }

    bool FMyCustomExternalSource::StartAsyncLoad()
    {
        // 实现异步加载逻辑
        // 使用 Async() 或 FThread 启动后台加载任务
        Async(EAsyncExecution::ThreadPool, [this]()
        {
            // 在后台线程执行加载
            TSharedPtr<IDatasmithScene> LoadedScene = LoadImpl();
            
            // 回到主线程触发回调
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                TriggerOnExternalSourceChanged();
            });
        });
        
        return true;
    }
}
```

## 模块依赖

从 Build.cs 分析，ExternalSource 模块的独特依赖：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心类型定义（IDatasmithScene、IDatasmithTranslator） |
| `DatasmithTranslator` | 翻译器接口，用于解析各种文件格式 |

其他常见依赖（Core、CoreUObject、Engine 等）已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃带 bIncludeNestedObjects 参数的 GetObjects/ForEachObjectWithOuter 函数 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，正确使用 PreEditChange/PostEditChange 包装 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器相关工作 |

### 维护评价

**状态：活跃维护** ✅

- **创建时间**：2019 年 10 月（约 7 年历史）
- **最近更新**：最近 6 个月内有多次实质性更新（浮点精度修复、日志系统迁移、API 废弃标记）
- **活跃程度**：Epic Games 持续维护，属于企业版 Datasmith 套件核心组件
- **已知限制**：
  - 需要手动启用（`EnabledByDefault=false`）
  - 主要面向企业用户，与 CAD/BIM 软件配合使用
- **推荐程度**：如果你需要导入 CAD/BIM 数据，这是官方推荐方案；对于普通游戏开发场景不需要使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [ExternalSource 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/ExternalSource)