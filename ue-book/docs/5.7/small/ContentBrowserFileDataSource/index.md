# Content Browser - File Data Source

> Data Source plugin providing loose file support for the Content Browser

| 属性 | 值 |
|---|---|
| 分类 | Content Browser |
| 默认启用 | ❌ No |
| 包含内容 | ❌ No |
| 模块 | ContentBrowserFileDataSource (EditorAndProgram) |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董 (5.9 年) |
| 支持程序 | LiveLinkHub |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserFileDataSource) | |

## 用途

ContentBrowserFileDataSource 是 UE5 Content Browser 的**数据源扩展插件**，它让 Content Browser 能够浏览和管理磁盘上的**非资产文件**（loose files）。

默认情况下，Content Browser 只能浏览 `.uasset` / `.umap` 等 Unreal 资产包。本插件通过实现 `UContentBrowserDataSource` 接口，将任意磁盘目录"挂载"（mount）到 Content Browser 的虚拟路径树中，使用户能像操作普通资产一样浏览、创建、重命名、复制、移动、删除磁盘上的散列文件。

核心机制：
1. **File Mount**：将磁盘路径映射到虚拟路径（如 `D:/Game/Scripts` → `/Scripts`）
2. **后台发现**：使用独立线程递归扫描挂载目录，异步构建文件树
3. **文件变更监听**：通过 `IDirectoryWatcher` 实时感知磁盘文件变化并自动更新
4. **可配置文件类型**：通过 `FFileConfigData` 注册支持的文件扩展名及对应的操作（创建、编辑、预览、复制等）

## 使用场景

- **LiveLinkHub**：作为 `SupportedPrograms` 中唯一列出的程序，LiveLinkHub 使用此插件在 Content Browser 中展示和管理非资产文件
- **自定义编辑器工具**：需要在 Content Browser 中浏览脚本文件（.lua、.py）、配置文件（.json、.xml）或其他自定义格式文件
- **外部文件集成**：将项目外部的资源目录（如共享素材库、第三方工具输出目录）挂载到 Content Browser 中统一管理
- **源码控制集成**：插件内置了 SCC（Source Control）右键菜单，支持对挂载文件执行版本控制操作

## 蓝图用法

此插件**没有暴露 BlueprintCallable 接口**。它是纯 C++ 编辑器扩展，通过 `UContentBrowserDataSource` 基类的虚函数与 Content Browser 系统交互。所有操作都在 C++ 层面进行。

## C++ 用法

### 头文件引入

```cpp
#include "ContentBrowserFileDataSource.h"
#include "ContentBrowserFileDataPayload.h"  // FFileConfigData, FFileActions, FDirectoryActions
```

### 核心概念

#### File Mount（文件挂载）

将一个磁盘目录映射到 Content Browser 的虚拟路径树中：

```cpp
// 创建数据源实例
UContentBrowserFileDataSource* DataSource = NewObject<UContentBrowserFileDataSource>();

// 配置支持的文件类型
ContentBrowserFileData::FFileConfigData Config;

// 设置目录操作（可选）
ContentBrowserFileData::FDirectoryActions DirActions;
DirActions.CanCreate.BindLambda([](const FName InPath, const FString& InDiskPath, FText* OutError) {
    return true; // 允许创建子目录
});
Config.SetDirectoryActions(DirActions);

// 注册文件类型
ContentBrowserFileData::FFileActions FileActions;
FileActions.TypeExtension = TEXT("lua");
FileActions.TypeName = FTopLevelAssetPath(TEXT("/Script/MyModule"), TEXT("LuaScript"));
FileActions.TypeDisplayName = FText::FromString(TEXT("Lua Script"));
FileActions.TypeShortDescription = FText::FromString(TEXT("Lua"));
FileActions.TypeFullDescription = FText::FromString(TEXT("Lua Script File"));
FileActions.TypeColor = FLinearColor(0.2f, 0.4f, 0.8f);
FileActions.DefaultNewFileName = TEXT("NewScript.lua");
Config.RegisterFileActions(FileActions);

// 初始化数据源（AutoRegister=true 会自动注册到 ContentBrowserDataSubsystem）
DataSource->Initialize(Config, true);

// 挂载磁盘目录到虚拟路径
DataSource->AddFileMount(FName("/MyScripts"), TEXT("D:/Game/Scripts"));
```

#### 文件类型操作委托

`FFileActions` 支持以下可绑定的委托：

| 委托 | 说明 |
|---|---|
| `CanCreate` | 是否允许在指定目录创建此类型文件 |
| `ConfigureCreation` | 创建前弹出对话框让用户配置（返回文件名建议和创建配置） |
| `Create` | 实际执行文件创建 |
| `CanEdit` / `Edit` | 编辑操作（如用外部编辑器打开） |
| `CanPreview` / `Preview` | 预览操作 |
| `CanDuplicate` | 是否允许复制 |
| `CanDelete` | 是否允许删除 |
| `CanRename` | 是否允许重命名 |
| `CanCopy` / `CanMove` | 是否允许复制/移动到目标路径 |
| `GetAttribute` / `GetAttributes` | 获取文件的自定义属性（用于 Content Browser 列显示） |
| `PassesFilter` | 自定义过滤逻辑 |

#### 运行时管理挂载

```cpp
// 检查挂载是否存在
bool bExists = DataSource->HasFileMount(FName("/MyScripts"));

// 移除挂载（会自动停止目录监听和清理发现的文件）
DataSource->RemoveFileMount(FName("/MyScripts"));
```

### 进阶用法

#### 后台文件发现

插件使用 `FContentBrowserFileDataDiscovery`（继承 `FRunnable`）在独立线程中递归扫描目录。扫描结果通过 `Tick()` 回调合并到主数据结构中：

```
AddFileMount() → BackgroundDiscovery->AddPathToSearch()
                     ↓ (后台线程)
              IFileManager::IterateDirectory() → DiscoveredItems[]
                     ↓ (主线程 Tick)
              AddDiscoveredItem() → QueueItemDataUpdate()
```

- 子目录会被优先插入队列头部，利用磁盘局部性
- 可通过 `PrioritizeSearchPath()` 让指定路径的扫描优先处理
- `IsDiscoveringItems()` 查询是否仍在扫描中

#### 目录实时监听

`AddFileMount()` 会自动注册 `IDirectoryWatcher` 回调。当磁盘文件变化时：
- **文件添加/修改**：自动发现并添加到虚拟路径树
- **文件删除**：自动从虚拟路径树移除
- **目录创建**：自动开始扫描新目录
- **目录删除**：递归清理所有子项

#### 源码控制菜单

模块启动时（`StartupModule`）自动为 Content Browser 的文件右键菜单和文件夹右键菜单添加 SCC 操作项，通过 `FFileSourceControlContextMenu` 实现。支持 Perforce、Git 等已注册的源码控制系统。

## Demo 示例

### 最小完整示例：注册一个自定义文件类型

```cpp
// MyFileDataSourceSubsystem.h
#pragma once

#include "ContentBrowserFileDataSource.h"
#include "ContentBrowserFileDataPayload.h"
#include "Subsystems/EngineSubsystem.h"
#include "MyFileDataSourceSubsystem.generated.h"

UCLASS()
class UMyFileDataSourceSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    UPROPERTY()
    TObjectPtr<UContentBrowserFileDataSource> DataSource;
};
```

```cpp
// MyFileDataSourceSubsystem.cpp
#include "MyFileDataSourceSubsystem.h"

void UMyFileDataSourceSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 配置文件类型
    ContentBrowserFileData::FFileConfigData Config;

    // 注册 JSON 文件
    {
        ContentBrowserFileData::FFileActions Actions;
        Actions.TypeExtension = TEXT("json");
        Actions.TypeName = FTopLevelAssetPath(TEXT("/Script/MyPlugin"), TEXT("JsonFile"));
        Actions.TypeDisplayName = FText::FromString(TEXT("JSON File"));
        Actions.TypeShortDescription = FText::FromString(TEXT("JSON"));
        Actions.TypeFullDescription = FText::FromString(TEXT("JavaScript Object Notation file"));
        Actions.TypeColor = FLinearColor(0.8f, 0.6f, 0.0f);
        Actions.DefaultNewFileName = TEXT("NewFile.json");

        // 允许用系统默认编辑器打开
        Actions.DefaultEditVerb = ELaunchVerb::Edit;

        Config.RegisterFileActions(Actions);
    }

    // 创建并初始化数据源
    DataSource = NewObject<UContentBrowserFileDataSource>();
    DataSource->Initialize(Config, true);

    // 挂载项目目录下的 Config 文件夹
    const FString ConfigDir = FPaths::ProjectDir() / TEXT("Config");
    DataSource->AddFileMount(FName("/ProjectConfig"), ConfigDir);
}

void UMyFileDataSourceSubsystem::Deinitialize()
{
    if (DataSource)
    {
        DataSource->Shutdown();
        DataSource = nullptr;
    }
    Super::Deinitialize();
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "ContentBrowserData",
    "ContentBrowserFileDataSource",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、文件系统、线程 |
| `CoreUObject` | UObject 系统、反射 |
| `ContentBrowserData` | Content Browser 数据源基类 `UContentBrowserDataSource` |
| `AssetTools` | 注册资产类型操作（AssetTypeActions） |
| `Slate` / `SlateCore` | UI 框架（右键菜单） |
| `SourceControl` | 源码控制抽象层 |
| `SourceControlWindows` | 源码控制 UI |
| `ToolMenus` | 工具菜单扩展系统 |
| `UnrealEd` | 编辑器核心 |
| `UncontrolledChangelists` | 未管控变更列表 |
| `DirectoryWatcher` | 目录变更监听（动态加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-28 | `8e28d46b` | Fixed typo in `EnumerateItemsAtUserProvidedPath` | Bug 修复：路径枚举函数中的拼写错误 |
| 2025-07-28 | `f9181087` | Fixed content browser navigation to various user provided paths | 重要修复：解决了虚拟路径、权限过滤器、类路径、别名路径的导航问题；新增导航栏路径建议 |
| 2025-07-17 | `004d9d7a` | Fixed unsafe SCC state query from non-game thread | 线程安全修复：避免从非游戏线程调用 `ISourceControlProvider::GetState` |

### 维护评价

- **创建时间**：2020 年 6 月，随 UE5 早期开发引入
- **活跃度**：2025 年 7 月仍有实质性更新（非编译修复），属于**活跃维护**
- **定位**：作为 Content Browser 数据源扩展框架的一部分，是 UE5 模块化 Content Browser 架构的关键组件
- **特殊说明**：`EnabledByDefault=false`，且 `SupportedPrograms` 仅列出 `LiveLinkHub`，表明这是一个面向特定程序的插件，普通 UE 项目默认不会启用
- **推荐度**：如果你在开发需要在 Content Browser 中展示非资产文件的编辑器工具或自定义程序，这是一个官方提供的成熟方案
- **已知限制**：
  - 不支持集合（Collection）过滤（源码中有 TODO 注释）
  - 需要多线程支持（不支持单线程环境）
  - 目录移除时存在竞态条件（源码中有 TODO 注释）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ContentBrowser/ContentBrowserFileDataSource)
- [官方文档]()（无）
- [测试用例]()（未找到独立测试文件）
