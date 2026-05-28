# Fab

> Fab Plugin

| 属性 | 值 |
|---|---|
| 中文名 | Fab 资产市场 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI 面板、设置资产、材质模板） |
| 模块 | `Fab` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-06-19 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Fab) | |

## 用途

Fab 插件是 Epic Games 在 UE5 编辑器中集成的 **资产市场面板**，允许开发者直接在编辑器内浏览、搜索、购买和导入来自 [Fab](https://www.fab.com/) 商城的资产。它替代了原先的 Quixel Bridge 插件，将 Megascans 资产和第三方资产的获取流程统一到一个内嵌的 Web 浏览器面板中。

该插件的核心职责包括：

1. **内嵌 Web 浏览器**：在编辑器中打开 Fab 商城的 Web 前端，支持原生渲染（Performance 模式）和离屏渲染（Standard 模式）
2. **资产下载**：通过 HTTP 直接下载或通过 BuildPatchServices（BPS）下载 Marketplace 资产/插件
3. **资产导入**：针对不同资产类型（3D 模型、材质、贴花、植物、MetaHuman、插件等）使用不同的导入管线
4. **拖拽放置**：支持从 Fab 面板直接拖拽资产到视口，自动下载并放置 Actor
5. **Epic 账号认证**：集成 EOS（Epic Online Services）认证系统，处理登录/登出/Token 刷新
6. **资产缓存**：缓存已下载的资产避免重复下载，支持手动清理
7. **Interchange 管线**：为 Megascans 资产提供专用的 Interchange 导入管线，处理 GLTF 解析、材质设置、LOD 配置等

## 使用场景

- 你需要从 Fab 商城导入免费的 Megascans 资产（扫描物体、材质、植被）→ 在编辑器中打开 Fab 面板，登录 Epic 账号，浏览并添加到项目
- 你需要快速预览放置 3D 资产到场景中 → 从 Fab 面板直接拖拽资产到视口，自动下载并放置占位 Actor
- 你需要安装 Fab 商城的 UE 插件 → 使用 "Install to Project" 或 "Install to Engine" 功能自动下载并通过 BPS 安装插件
- 你需要批量导入不同质量等级的 Megascans 资产 → 在设置中选择 preferred quality tier（Low/Medium/High/Raw）
- 你需要自定义 Megascans 导入所使用的父材质 → 在 Fab Megascans 设置中配置材质映射

## 蓝图用法

Fab 插件主要是编辑器功能，不直接暴露运行时蓝图 API。其主要交互入口是 `UFabBrowserApi`，但该类通过 WebBrowser 的 JavaScript 桥接与 Fab 前端通信，不是典型的蓝图使用场景。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetApiVersion` | 获取 Fab API 版本信息（UE版本、插件版本、平台等） | `UFabBrowserApi` |
| `GetSettings` | 获取当前前端设置（偏好格式、偏好质量） | `UFabBrowserApi` |
| `GetAuthToken` | 获取当前 Epic 认证 Token | `UFabBrowserApi` |
| `GetRefreshToken` | 获取认证刷新 Token | `UFabBrowserApi` |
| `CopyToClipboard` | 复制内容到系统剪贴板 | `UFabBrowserApi` |
| `OpenUrlInBrowser` | 在系统浏览器中打开 URL | `UFabBrowserApi` |

### 设置面板

在编辑器菜单 **Edit → Editor Preferences → Plugins → Fab** 中可配置：

| 设置项 | 说明 |
|---|---|
| Experience Mode | Standard（离屏渲染）或 Performance（原生渲染，仅 Windows） |
| Cache Directory | 资产缓存目录路径 |
| Preferred Quality Tier | Megascans 资产默认质量（Low/Medium/High/Raw） |

## C++ 用法

Fab 插件的大部分功能是编辑器内部使用的，但其工作流系统支持通过 `IFabWorkflowFactory` 进行扩展。

### 头文件引入

```cpp
#include "FabModule.h"
#include "FabWorkflowFactoryRegistry.h"
#include "FabDownloader.h"
#include "Workflows/FabWorkflow.h"
```

### 基本用法

#### 注册自定义资产导入工厂

```cpp
// 来源: Source/Fab/Public/Workflows/FabWorkflowFactory.h
// 来源: Source/Fab/Public/FabWorkflowFactoryRegistry.h

// 1. 实现 IFabWorkflowFactory 接口
class FMyAssetWorkflowFactory : public IFabWorkflowFactory
{
public:
    virtual const TArray<FString>& GetImportAssetTypes() override
    {
        static TArray<FString> Types = { TEXT("MyAssetType") };
        return Types;
    }

    virtual TSharedPtr<IFabWorkflow> Create(
        const FFabAssetMetadata& InImportAssetMetadata,
        const FString& InDownloadUrl) override
    {
        // 返回自定义的 workflow 实例
        return MakeShared<FMyImportWorkflow>(
            InImportAssetMetadata.AssetId,
            InImportAssetMetadata.AssetName,
            InDownloadUrl);
    }
};

// 2. 注册到工厂注册表
TSharedPtr<IFabWorkflowFactory> MyFactory = MakeShared<FMyAssetWorkflowFactory>();
FFabWorkflowFactoryRegistry::RegisterFactory(MyFactory);

// 3. 检查资产类型是否已注册
bool bRegistered = FFabWorkflowFactoryRegistry::IsAssetTypeRegistered(TEXT("MyAssetType"));

// 4. 获取工厂并创建工作流
TSharedPtr<IFabWorkflowFactory>& Factory = FFabWorkflowFactoryRegistry::GetFactory(TEXT("MyAssetType"));
```

#### 使用下载系统

```cpp
// 来源: Source/Fab/Public/FabDownloader.h

// 创建下载请求
FFabDownloadRequest DownloadRequest(
    TEXT("asset-id-123"),
    TEXT("https://example.com/asset.zip"),
    TEXT("/Game/Fab/Downloads/asset-id-123"),
    EFabDownloadType::HTTP);

// 绑定进度回调
DownloadRequest.OnDownloadProgress().AddLambda(
    [](const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        UE_LOG(LogTemp, Log, TEXT("Download progress: %.1f%%"), Stats.PercentComplete * 100.0f);
    });

// 绑定完成回调
DownloadRequest.OnDownloadComplete().AddLambda(
    [](const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        if (Stats.bIsSuccess)
        {
            for (const FString& File : Stats.DownloadedFiles)
            {
                UE_LOG(LogTemp, Log, TEXT("Downloaded: %s"), *File);
            }
        }
    });

// 执行下载
DownloadRequest.ExecuteRequest();
```

### 进阶用法

#### 实现自定义导入工作流

```cpp
// 来源: Source/Fab/Public/Workflows/FabWorkflow.h
// 来源: Source/Fab/Private/Workflows/GenericImportWorkflow.h

class FMyImportWorkflow : public IFabWorkflow
{
public:
    FMyImportWorkflow(const FString& InAssetId, const FString& InAssetName, const FString& InDownloadURL)
        : IFabWorkflow(InAssetId, InAssetName, InDownloadURL)
    {}

    virtual void Execute() override
    {
        // 开始下载
        DownloadContent();
    }

protected:
    virtual void DownloadContent() override
    {
        DownloadRequest = MakeShared<FFabDownloadRequest>(
            AssetId, DownloadUrl, TEXT("/Game/Fab/") + AssetId);

        DownloadRequest->OnDownloadProgress().AddRaw(
            this, &FMyImportWorkflow::OnContentDownloadProgress);
        DownloadRequest->OnDownloadComplete().AddRaw(
            this, &FMyImportWorkflow::OnContentDownloadComplete);

        DownloadRequest->ExecuteRequest();
    }

    virtual void OnContentDownloadProgress(
        const FFabDownloadRequest* Request,
        const FFabDownloadStats& DownloadStats) override
    {
        SetDownloadNotificationProgress(DownloadStats.PercentComplete);
    }

    virtual void OnContentDownloadComplete(
        const FFabDownloadRequest* Request,
        const FFabDownloadStats& DownloadStats) override
    {
        if (DownloadStats.bIsSuccess)
        {
            ImportContent(DownloadStats.DownloadedFiles);
        }
        else
        {
            CancelWorkflow();
        }
    }

    virtual void ImportContent(const TArray<FString>& SourceFiles) override
    {
        // 使用 FFabGenericImporter 导入资产
        FFabGenericImporter::ImportAsset(
            SourceFiles,
            TEXT("/Game/Fab/Imported/") + AssetId,
            [this](const TArray<UObject*>& ImportedObjects)
            {
                ImportedObjects = ImportedObjects;
                CompleteWorkflow();
            });
    }

private:
    TSharedPtr<FFabDownloadRequest> DownloadRequest;
};
```

#### 使用资产缓存

```cpp
// 来源: Source/Fab/Public/Utilities/FabAssetsCache.h

// 检查资产是否已缓存
FString AssetId = TEXT("some-asset-id");
int64 ExpectedSize = 1024 * 1024; // 1MB
if (FFabAssetsCache::IsCached(AssetId, ExpectedSize))
{
    // 使用缓存文件
    FString CachedPath = FFabAssetsCache::GetCachedFile(AssetId);
    UE_LOG(LogTemp, Log, TEXT("Found cached asset at: %s"), *CachedPath);
}

// 获取缓存大小信息
FText CacheSizeText = FFabAssetsCache::GetCacheSizeString();

// 缓存新下载的资产
FFabAssetsCache::CacheAsset(TEXT("/tmp/downloaded_asset.zip"));

// 清理缓存
FFabAssetsCache::ClearCache();
```

## Demo 示例

### 自定义 Fab 导入工作流工厂

```cpp
// MyFabFactory.h
#pragma once

#include "Workflows/FabWorkflowFactory.h"
#include "Workflows/FabWorkflow.h"

class FMyAssetWorkflowFactory : public IFabWorkflowFactory
{
public:
    virtual const TArray<FString>& GetImportAssetTypes() override
    {
        static TArray<FString> Types = { TEXT("MyCustomType") };
        return Types;
    }

    virtual TSharedPtr<IFabWorkflow> Create(
        const FFabAssetMetadata& InImportAssetMetadata,
        const FString& InDownloadUrl) override;
};
```

```cpp
// MyFabFactory.cpp
#include "MyFabFactory.h"
#include "FabWorkflowFactoryRegistry.h"
#include "FabDownloader.h"
#include "Utilities/AssetUtils.h"
#include "Utilities/FabAssetsCache.h"

// 简单的自定义导入工作流
class FMyCustomWorkflow : public IFabWorkflow
{
public:
    FMyCustomWorkflow(const FString& InAssetId, const FString& InAssetName, const FString& InDownloadURL)
        : IFabWorkflow(InAssetId, InAssetName, InDownloadURL) {}

    virtual void Execute() override { DownloadContent(); }

protected:
    virtual void DownloadContent() override
    {
        // 先检查缓存
        if (FFabAssetsCache::IsCached(AssetId, 0))
        {
            FString CachedFile = FFabAssetsCache::GetCachedFile(AssetId);
            ImportedObjects.Empty();
            FAssetUtils::ScanForAssets(CachedFile);
            CompleteWorkflow();
            return;
        }

        DownloadRequest = MakeShared<FFabDownloadRequest>(
            AssetId, DownloadUrl, FPaths::ProjectContentDir() / TEXT("Fab") / AssetId);

        DownloadRequest->OnDownloadComplete().AddLambda(
            [this](const FFabDownloadRequest* Req, const FFabDownloadStats& Stats)
            {
                if (Stats.bIsSuccess && Stats.DownloadedFiles.Num() > 0)
                {
                    FFabAssetsCache::CacheAsset(Stats.DownloadedFiles[0]);
                    FAssetUtils::ScanForAssets(
                        FPaths::ProjectContentDir() / TEXT("Fab") / AssetId);
                    CompleteWorkflow();
                }
                else
                {
                    CancelWorkflow();
                }
            });

        DownloadRequest->ExecuteRequest();
    }

    virtual void OnContentDownloadProgress(const FFabDownloadRequest*, const FFabDownloadStats& Stats) override
    {
        UE_LOG(LogTemp, Log, TEXT("Downloading %s: %.0f%%"), *AssetName, Stats.PercentComplete * 100);
    }

    virtual void OnContentDownloadComplete(const FFabDownloadRequest*, const FFabDownloadStats&) override {}

private:
    TSharedPtr<FFabDownloadRequest> DownloadRequest;
};

TSharedPtr<IFabWorkflow> FMyAssetWorkflowFactory::Create(
    const FFabAssetMetadata& InImportAssetMetadata, const FString& InDownloadUrl)
{
    return MakeShared<FMyCustomWorkflow>(
        InImportAssetMetadata.AssetId,
        InImportAssetMetadata.AssetName,
        InDownloadUrl);
}

// 模块启动时注册
class FMyModule : public IModuleInterface
{
    virtual void StartupModule() override
    {
        Factory = MakeShared<FMyAssetWorkflowFactory>();
        FFabWorkflowFactoryRegistry::RegisterFactory(Factory);
    }

    virtual void ShutdownModule() override
    {
        FFabWorkflowFactoryRegistry::UnregisterFactory(Factory);
    }

    TSharedPtr<FMyAssetWorkflowFactory> Factory;
};
```

## 模块依赖

Fab 插件的源码中使用了大量 Unreal 引擎模块，以下列出其**独特**依赖：

| 模块 | 用途 |
|---|---|
| `WebBrowserWidget` | 内嵌 Web 浏览器面板，渲染 Fab 商城前端 |
| `InterchangeFramework` | 资产导入管线框架，处理 GLTF/JSON 解析 |
| `InterchangePipelines` | 通用 Interchange 导入管线（Mesh、Material、Texture 等） |
| `InterchangeNodes` | Interchange 节点系统 |
| `InterchangeFactoryNodes` | Interchange 工厂节点（StaticMesh、MaterialInstance、Texture） |
| `InterchangeImport` | Interchange 导入核心模块 |
| `BuildPatchServices` | Marketplace 资产和插件的差分下载/安装 |
| `EOSSDK` / `EOSShared` | Epic Online Services SDK，用于用户认证 |
| `AssetTools` | 资产导入/注册工具 |
| `ContentBrowser` | 内容浏览器集成（右键菜单、文件夹同步） |
| `AssetRegistry` | 资产注册表查询 |
| `Foliage` | 植被实例化类型管理 |
| `LevelEditor` | 关卡编辑器集成 |
| `ToolMenus` | 编辑器菜单/工具栏扩展 |
| `Settings` | `UDeveloperSettings` 框架 |
| `DataStorage` | 编辑器数据存储（TEDS 集成） |
| `Json` | JSON 解析 |
| `HTTP` | HTTP 下载请求 |
| `Slate` / `SlateCore` / `Widgets` | UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78f0e8f0` | [Fab] Fix Fab plugin multi-instance issues on Mac | 修复 Mac 上 Fab 插件多实例问题 |
| 2026-04-24 | `2a923e9d` | [Fab] Fix intermittent null-deref crash in FabBrowser tab teardown | 修复关闭浏览器标签时偶发空指针崩溃 |
| 2026-04-24 | `8f2e0960` | [Fab] Only intercept Fab URLs in browser navigation | 仅拦截 Fab URL，避免影响其他浏览器导航 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/抑制 PVS 静态分析警告 |
| 2026-04-22 | `1139c501` | [Fab] Skip Fab module init/shutdown when Emporium plugin is enabled | 当 Emporium 插件启用时跳过 Fab 模块初始化 |

### 维护评价

**积极维护中** ✅

- **创建时间**：2023 年 6 月，约 3 年历史
- **活跃程度**：2026 年 5 月仍有功能性更新和 Bug 修复，维护频率约每月数次
- **维护质量**：近期提交集中在平台兼容性修复（Mac）、崩溃修复和插件冲突处理，说明该插件在生产环境中被广泛使用
- **注意事项**：
  - 该插件是 **Editor-only**（Type: Editor），不会影响打包后的游戏
  - `EnabledByDefault=true`，UE5 项目默认启用
  - 最新提交提到了 `Emporium` 插件互斥逻辑，说明 Epic 可能在重构或替换该插件
  - 仅支持 Linux/Win64/Mac 平台
- **推荐使用**：✅ 推荐。这是 Epic 官方维护的 Fab 商城集成，是获取 Megascans 和其他 Fab 资产的标准方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Fab)
- [Fab 商城](https://www.fab.com/)