# Fab

> Fab Plugin

| 属性 | 值 |
|---|---|
| 中文名 | Fab 市场集成 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、Pipline配置） |
| 模块 | `Fab` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Fab) | |

## 用途

Fab 插件将 **Epic Games 的 Fab 数字内容市场** 直接集成到 Unreal Editor 中。它通过内嵌的 Web 浏览器界面，让用户无需离开编辑器即可浏览、搜索、购买和导入来自 Fab 市场（以及 Quixel Megascans）的数字资产（Model、Material、Surface、Decal、Plant 等）。

本插件是传统 **Quixel Bridge** 的现代化替代品，旨在提供一个统一的内容导入入口，支持资产下载、缓存管理、拖拽放置、自动解压、并利用 Engine 的 Interchange 框架自动导入高品质资产。

## 使用场景

- 你是一名关卡设计师，正在搭建场景，需要快速从 Fab 市场拖入一个 3D 模型或植物 → 直接用插件内嵌浏览器完成拖拽导入
- 你是材质美术，想使用 Quixel Megascans 的 Surface 或 Decal → 通过插件直接导入并自动应用可调整的材质实例
- 你的团队使用同一套高质量资产库，需要本地缓存以避免重复下载 → 插件提供智能缓存机制
- 你正在搭建一个植被丰富的场景 → 插件支持自动生成植被实例系统

## 蓝图用法

本插件的主要交互是通过编辑器 UI 和 C++ API 进行，公开的蓝图节点较少，但提供了关键的 **浏览器通信** 蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add To Project` | 将指定 URL 的 Fab 资产下载/导入到当前项目 | `UFabBrowserApi` |
| `Drag Start` | 发起一次拖拽事件，告知 JS 端准备拖入资产 | `UFabBrowserApi` |
| `Login` | 触发 Fab 用户登录流程 | `UFabBrowserApi` |
| `Logout` | 登出当前 Fab 用户 | `UFabBrowserApi` |
| `Get Auth Token` | 获取当前登录用户的认证 Token | `UFabBrowserApi` |

### 使用示例（蓝图描述）

1. **从浏览器拖入 Mesh**：当用户在浏览器中点击“拖入”时，JS 会调用蓝图的 `Drag Start` 节点，该节点发起 C++ 下载流程 → 下载完成后通过 `Generic Drag Drop Workflow` 自动执行网格导入。
2. **点击“添加到项目”按钮**：浏览器按钮触发 `Add To Project` 事件，传入 `DownloadUrl` 和 `AssetMetadata`。插件内部创建 `IFabWorkflow`，执行 `Download->Import->Sync Content Browser` 的完整链路。

## C++ 用法

### 头文件引入

```cpp
#include "FabModule.h"
#include "FabDownloader.h"
#include "Workflows/FabWorkflow.h"
#include "Workflows/FabWorkflowFactoryRegistry.h"
```

### 基本用法

```cpp
// 1. 获取 Fab 模块接口
IFabModule& FabModule = IFabModule::Get();

// 2. 创建下载请求（HTTP 方式）
TSharedPtr<FFabDownloadRequest> DownloadRequest = MakeShareable(
    new FFabDownloadRequest(
        TEXT("asset_12345"),
        TEXT("https://cdn.fab.com/download/..."),
        TEXT("/Game/FabDownloads"),
        EFabDownloadType::HTTP
    )
);

// 3. 绑定进度和完成回调
DownloadRequest->OnDownloadProgress().AddLambda(
    [](const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        UE_LOG(LogFab, Display, TEXT("Download progress: %f%%"), Stats.PercentComplete);
    }
);

DownloadRequest->OnDownloadComplete().AddLambda(
    [](const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        if (Stats.bIsSuccess)
        {
            UE_LOG(LogFab, Display, TEXT("Download completed, %d files"), Stats.DownloadedFiles.Num());
            // 触发 Interchange 导入
            FAssetUtils::ScanForAssets(FPaths::GetPath(Request->GetDownloadStats().DownloadedFiles[0]));
        }
    }
);

// 4. 执行下载
DownloadRequest->ExecuteRequest();
```

来源：`Source/Fab/Public/FabDownloader.h` & `Source/Fab/Private/FabDownloader.cpp`

```cpp
// 注册自定义工作流工厂（高级用法）
class FMyCustomWorkflowFactory : public IFabWorkflowFactory
{
public:
    virtual const TArray<FString>& GetImportAssetTypes() override
    {
        static TArray<FString> Types = { TEXT("CustomType") };
        return Types;
    }

    virtual TSharedPtr<IFabWorkflow> Create(
        const FFabAssetMetadata& InImportAssetMetadata,
        const FString& InDownloadUrl) override
    {
        return MakeShareable(new FMyCustomWorkflow(InImportAssetMetadata.AssetId,
                                                    InImportAssetMetadata.AssetName,
                                                    InDownloadUrl));
    }
};

void RegisterCustomFactory()
{
    TSharedPtr<FMyCustomWorkflowFactory> Factory = MakeShareable(new FMyCustomWorkflowFactory);
    FFabWorkflowFactoryRegistry::RegisterFactory(Factory);
}
```

来源：`Source/Fab/Public/Workflows/FabWorkflowFactoryRegistry.h`

### 进阶用法

```cpp
// 使用缓存系统
FFabAssetsCache::ClearCache();   // 清空本地缓存
int64 CacheSize = FFabAssetsCache::GetCacheSize(); // 获取缓存大小（字节）
bool bCached = FFabAssetsCache::IsCached(TEXT("asset_megascan_001"), 1024 * 1024 * 50); // 检查是否已缓存

// 资产本地化映射管理
UFabLocalAssets::AddLocalAsset(TEXT("/Game/MyFabs/Surface_Grass_01"), TEXT("4598e2d1-..."));
const FString* Path = UFabLocalAssets::FindPath(TEXT("4598e2d1-...")); // 返回 "/Game/MyFabs/Surface_Grass_01"
```

来源：`Source/Fab/Public/Utilities/FabAssetsCache.h` & `Source/Fab/Private/Utilities/FabLocalAssets.h`

```cpp
// 使用 Quixel GLTF 导入器 - 针对 Megascans
FQuixelGltfImporter::ImportGltf3DAsset(
    TEXT("/tmp/megascan_export/MyAsset.gltf"),
    TEXT("/Game/FabImports/MyAsset"),
    [](const TArray<UObject*>& ImportedObjects)
    {
        for (UObject* Obj : ImportedObjects)
        {
            UE_LOG(LogFab, Display, TEXT("Imported: %s"), *Obj->GetName());
        }
    }
);
```

来源：`Source/Fab/Private/Importers/QuixelGLTFImporter.h`

## Demo 示例

以下是一个完整的 C++ 示例，演示如何创建一个下载请求、监听事件并执行导入：

**MyFabImporter.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "FabDownloader.h"
#include "Workflows/FabWorkflow.h"
#include "Containers/Ticker.h"

class FMyFabImporter
{
public:
    void StartImport(const FString& AssetId, const FString& DownloadUrl)
    {
        DownloadRequest = MakeShareable(new FFabDownloadRequest(
            AssetId,
            DownloadUrl,
            FPaths::ProjectSavedDir() / TEXT("FabTemp"),
            EFabDownloadType::HTTP
        ));

        DownloadRequest->OnDownloadProgress().AddRaw(this, &FMyFabImporter::OnProgress);
        DownloadRequest->OnDownloadComplete().AddRaw(this, &FMyFabImporter::OnComplete);

        DownloadRequest->ExecuteRequest();
    }

    void OnProgress(const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        UE_LOG(LogTemp, Display, TEXT("Fab Importer: %f%% - %s/s"),
               Stats.PercentComplete,
               *FText::AsMemory(Stats.DownloadSpeed).ToString());
    }

    void OnComplete(const FFabDownloadRequest* Request, const FFabDownloadStats& Stats)
    {
        if (Stats.bIsSuccess)
        {
            UE_LOG(LogTemp, Display, TEXT("Download completed successfully. Importing..."));

            // 扫描下载文件夹中的新资源
            FAssetUtils::ScanForAssets(FPaths::GetPath(Stats.DownloadedFiles[0]));
            FAssetUtils::SyncContentBrowserToFolder(TEXT("/Game/FabImports"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Download failed."));
        }
    }

private:
    TSharedPtr<FFabDownloadRequest> DownloadRequest;
};
```

**用法**：

```cpp
FMyFabImporter* Importer = new FMyFabImporter();
Importer->StartImport(TEXT("fab_asset_001"), TEXT("https://cdn.fab.com/download/..."));
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Interchange` | 资产导入管线（static mesh, texture, material instance） |
| `EditorDataStorageFeatures` | TEDS 集成（My Library / 内容源） |
| `EditorWidgets` | Content Browser 右键菜单扩展、图标生成 |
| `WebBrowser` + `WebBrowserTexture` | 内嵌浏览器标签页 |
| `EOSSDK` | EOS（Epic Online Services）认证登录 |
| `Json`, `JsonUtilities` | Quixel 元数据解析、API 响应解析 |
| `HTTP` | HTTP 资产下载 |
| `BuildPatchServices` | 大型 Marketplace 资产的分块下载（BuildPatchRequest） |

## 维护状态

### 近期更新

- 2025-10-02 a51ef85 — [Fab] Bump plugin version for UE 5.7
- 2025-09-29 e50c7c4 — [Fab] Lower case uproperties for macOS WebKit compatibility - fixes MH issue
- 2025-09-29 2f93c71 — Disable slate drag and drops from conflicting with each other
- 2025-09-25 d5d2a37 — Fixing Shown vs Hidden Tab Visibility bug with macOS WebKit and the Fab and Quixel plugins
- 2025-09-12 ce6ff39 — Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue

### 维护评价

- **创建时间**：2025-09-12（非常新）
- **更新频率**：截至 2025-10 已有多处功能性及兼容性修复，更新活跃
- **活跃维护**：✅ 是。最近 1 个月内有多次 commit，包含 bug 修复（WebKit 兼容、拖拽冲突、Tab 可见性）和版本更新
- **已知限制**：macOS WebKit 有属性大小写兼容问题，插件已通过小写 UPROPERTY 修复；仍可能存在浏览器指纹 / 认证方面的边界问题
- **推荐使用**：✅ 强烈推荐。作为 Quixel Bridge 的后继者，官方直接集成，在新版本（5.5+）中即将替代老旧的 Bridge 插件，且支持 Interchange 最新管线。如果你的项目需要高质量 Megascans / Fab 资产，这是首选。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Fab)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Fab/Source/Fab/Private)（内联测试在 Private 目录中）