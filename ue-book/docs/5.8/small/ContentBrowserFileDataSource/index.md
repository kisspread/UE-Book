# Content Browser - File Data Source

> Data Source plugin providing loose file support for the Content Browser

| 属性 | 值 |
|---|---|
| 中文名 | 文件数据源 |
| 分类 | Content Browser |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ContentBrowserFileDataSource` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserFileDataSource) | |

## 用途

此插件是虚幻编辑器**内容浏览器**的一个**数据源**。它解决了编辑器默认只能浏览和管理被 UAsset 系统管理的资产（如.uasset, .umap）的问题。通过此插件，开发者可以让内容浏览器直接展示、交互和操作文件系统上的“松散文件”（Loose Files），例如文本文件（.txt, .json）、图片（.png）、视频（.mp4）、数据文件等，而无需将它们先导入为 UAsset。

**核心价值**：为编辑器工具和自定义工作流提供一种无缝集成的方式，让非资产文件也能在内容浏览器中像标准资产一样被发现、预览、编辑、移动和删除。

## 使用场景

-   你正在开发一个需要读取和编辑外部配置文件（如 JSON, XML）的工具或插件。
-   你的工作流涉及大量美术原始素材（如 PSD, FBX, PNG），你希望能在内容浏览器中直接管理它们，而不仅仅是通过外部文件浏览器。
-   你需要创建一个自定义的资产类型（例如 `.myformat`），并为其提供完整的编辑器内生命周期管理，包括在内容浏览器中的显示和交互。

## 蓝图用法

此插件主要通过 C++ 接口提供功能，未提供 BlueprintCallable 的蓝图节点。

## C++ 用法

### 头文件引入

```cpp
// 核心数据源和配置
#include "ContentBrowserFileDataSource.h"
#include "ContentBrowserFileDataPayload.h"

// 用于创建项目和枚举的工具函数
#include "ContentBrowserFileDataCore.h"
```

### 基本用法

此插件通常作为其他数据源或编辑器模块的基础设施使用。以下是如何初始化并注册一个自定义文件类型的基本流程。

```cpp
// 引自 `ContentBrowserFileDataSource.h` 和 `ContentBrowserFileDataPayload.h`
// 假设我们有一个自定义的 .myconfig 文件类型需要支持

// 1. 定义我们的文件操作（需要继承 FFileActions 或实现相关委托）
struct FMyConfigFileActions : public ContentBrowserFileData::FFileActions
{
    FMyConfigFileActions()
    {
        // 配置文件类型的基本信息
        TypeExtension = TEXT(".myconfig");
        TypeName = FTopLevelAssetPath(TEXT("/Script/MyEditor"), TEXT("MyConfigAsset"));
        TypeDisplayName = NSLOCTEXT("MyConfig", "DisplayName", "My Config File");
        TypeShortDescription = NSLOCTEXT("MyConfig", "ShortDesc", "A custom config file");
        TypeFullDescription = NSLOCTEXT("MyConfig", "FullDesc", "A full description of the custom config file format.");
        TypeColor = FLinearColor::Blue;
        DefaultNewFileName = TEXT("NewConfig");
        DefaultEditVerb = ELaunchVerb::Edit;

        // 绑定操作委托
        CanCreate.BindLambda([](const FName, const FString&, FText*) -> bool { return true; });
        Create.BindLambda([](const FName InFilePath, const FString& InFilename, const FStructOnScope&) -> bool {
            // 这里实现实际的文件创建逻辑
            const FString FullPath = FPaths::Combine(InFilePath.ToString(), InFilename);
            return FFileHelper::SaveStringToFile(TEXT("{}"), *FullPath);
        });
        CanEdit.BindLambda([](const FName, const FString&, FText*) -> bool { return true; });
        Edit.BindLambda([](const FName InFilePath, const FString& InFilename) -> bool {
            const FString FullPath = FPaths::Combine(InFilePath.ToString(), InFilename);
            FPlatformProcess::LaunchFileInDefaultExternalApplication(*FullPath);
            return true;
        });
        PassesFilter.BindStatic([](const FName, const FString& InFilename, const FContentBrowserDataFilter&) -> bool {
            return InFilename.EndsWith(TEXT(".myconfig"));
        });
    }
};

// 2. 在某个编辑器模块的 StartupModule 中初始化数据源
void FMyEditorModule::StartupModule()
{
    // 获取或创建数据源实例
    UContentBrowserFileDataSource* FileDataSource = NewObject<UContentBrowserFileDataSource>();
    // 注册我们的自定义文件类型
    ContentBrowserFileData::FFileConfigData Config;
    Config.RegisterFileActions(MakeShared<FMyConfigFileActions>());
    // 初始化数据源，但不自动注册（我们可能希望手动控制时机）
    FileDataSource->Initialize(Config, false);
    // 手动添加一个文件挂载点，例如指向项目的 /Config 目录
    FileDataSource->AddFileMount(FName(TEXT("/MyProject/Config")), FPaths::ProjectConfigDir());
    // 现在，内容浏览器将能够浏览 /MyProject/Config 路径下的 .myconfig 文件
}

void FMyEditorModule::ShutdownModule()
{
    if (FileDataSource)
    {
        FileDataSource->Shutdown();
    }
}
```

**来源**：基于 `UContentBrowserFileDataSource::Initialize` 和 `FFileConfigData::RegisterFileActions` 的实现逻辑。

### 进阶用法

**管理文件夹操作**：

```cpp
// 可以单独定义文件夹的行为
ContentBrowserFileData::FDirectoryActions DirActions;
DirActions.CanCreate.BindLambda([](const FName, const FString&, FText*) -> bool { return true; });
DirActions.Create.BindLambda([](const FName InPath, const FString& InFolderName, const FStructOnScope&) -> bool {
    const FString FullPath = FPaths::Combine(InPath.ToString(), InFolderName);
    return IFileManager::Get().MakeDirectory(*FullPath, true);
});
DirActions.CanDelete.BindLambda([](const FName, const FString&, FText*) -> bool { return true; });
// ... 绑定其他委托

Config.SetDirectoryActions(DirActions);
```

**获取项的属性**：

```cpp
// 从 FContentBrowserItemData 获取文件系统路径
FString DiskPath;
if (ContentBrowserFileData::GetItemPhysicalPath(DataSource, ItemData, DiskPath))
{
    UE_LOG(LogTemp, Log, TEXT("物理路径: %s"), *DiskPath);
}

// 获取文件大小等属性
ContentBrowserFileData::FContentBrowserItemDataAttributeValue SizeAttr;
if (ContentBrowserFileData::GetFileItemAttribute(FilePayload, false, FName("FileSize"), SizeAttr))
{
    if (const int64* FileSize = SizeAttr.Get<int64>())
    {
        UE_LOG(LogTemp, Log, TEXT("文件大小: %lld bytes"), *FileSize);
    }
}
```

## Demo 示例

以下是一个最小的、可工作的编辑器模块，它将“项目日志”目录挂载到内容浏览器中。

**MyFileDataSourceModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class UContentBrowserFileDataSource;

class FMyFileDataSourceModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    UContentBrowserFileDataSource* FileDataSource = nullptr;
};
```

**MyFileDataSourceModule.cpp**
```cpp
#include "MyFileDataSourceModule.h"
#include "ContentBrowserFileDataSource.h"
#include "ContentBrowserFileDataPayload.h"
#include "ContentBrowserFileDataCore.h"

#define LOCTEXT_NAMESPACE "FMyFileDataSourceModule"

void FMyFileDataSourceModule::StartupModule()
{
    // 定义通用的目录操作
    ContentBrowserFileData::FDirectoryActions DirActions;
    DirActions.CanCreate.BindLambda([](const FName, const FString&, FText*) { return true; });
    DirActions.Create.BindLambda([](const FName InPath, const FString& InFolderName, const FStructOnScope&) -> bool {
        const FString FullPath = FPaths::Combine(InPath.ToString(), InFolderName);
        return IFileManager::Get().MakeDirectory(*FullPath, true);
    });

    // 定义对日志文件的操作
    ContentBrowserFileData::FFileActions LogFileActions;
    LogFileActions.TypeExtension = TEXT(".log");
    LogFileActions.TypeDisplayName = LOCTEXT("LogFile", "Log File");
    LogFileActions.TypeColor = FLinearColor::Green;
    LogFileActions.DefaultNewFileName = TEXT("NewLog");
    LogFileActions.CanEdit.BindLambda([](const FName, const FString&, FText*) { return true; });
    LogFileActions.Edit.BindLambda([](const FName InPath, const FString& InFilename) -> bool {
        const FString FullPath = FPaths::Combine(InPath.ToString(), InFilename);
        FPlatformProcess::LaunchFileInDefaultExternalApplication(*FullPath, nullptr, FLaunchVerb::Open);
        return true;
    });
    LogFileActions.PassesFilter.BindStatic([](const FName, const FString& InFilename, const FContentBrowserDataFilter&) -> bool {
        return InFilename.EndsWith(TEXT(".log"));
    });

    // 配置并初始化数据源
    ContentBrowserFileData::FFileConfigData Config;
    Config.SetDirectoryActions(DirActions);
    Config.RegisterFileActions(MakeShared<ContentBrowserFileData::FFileActions>(LogFileActions));

    FileDataSource = NewObject<UContentBrowserFileDataSource>();
    FileDataSource->Initialize(Config);
    // 挂载项目的 Saved/Logs 目录
    FileDataSource->AddFileMount(FName(TEXT("/ProjectLogs")), FPaths::ProjectLogDir());
}

void FMyFileDataSourceModule::ShutdownModule()
{
    if (FileDataSource)
    {
        FileDataSource->Shutdown();
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

要使用此插件，你的模块（Build.cs）需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ContentBrowser` | 核心内容浏览器接口，提供 `UContentBrowserDataSource` 基类 |
| `AssetDefinition` | 用于定义资产类型和交互，与内容浏览器项目系统集成 |
| `SourceControl` | 用于文件操作时的源码控制状态检查（可选，但通常需要） |
| `DirectoryWatcher` | 用于监视文件系统变化，实时更新内容浏览器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数产生的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的 `UE_LOG` 宏迁移到使用 `UE_LOGF` 新日志宏系统。 |
| 2025-07-28 | `8e28d46b` | Fixed type in UContentBrowserFileDataSource::EnumerateItemsAtUserProvidedPath. | 修复了 `EnumerateItemsAtUserProvidedPath` 函数中的一个类型错误。 |
| 2025-07-28 | `f9181087` | Fixed the content browser not navigating to various user provided paths from the navigation bar. | 修复了从导航栏输入用户自定义路径时，内容浏览器无法正确跳转的问题。 |
| 2025-07-17 | `004d9d7a` | ContextMenu: Fixed unsafe call to ISourceControlProvider::GetState from a non game thread. | 修复了从非游戏线程（如编辑器线程）不安全地调用源码控制接口的严重问题。 |

### 维护评价

该插件自 2020 年创建以来持续维护。虽然作为**编辑器核心功能**的插件，其日常功能性更新不多，但最近在 2025-2026 年仍有**关键的错误修复和兼容性改进**（如线程安全、导航修复）。这表明它仍处于**活跃维护**状态，是编辑器内容浏览器基础设施的一个稳定且受支持的组成部分。

**推荐使用**：如果你的编辑器工具需要浏览非资产文件系统，此插件是官方提供的、经过验证的解决方案。由于它默认未启用 (`EnabledByDefault: false`)，你需要在项目或插件中手动启用它。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserFileDataSource)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/ContentBrowser) (注：相关测试位于引擎的 ContentBrowser 测试目录下)