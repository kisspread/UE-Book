# Content Browser - Alias Data Source

> Data Source plugin providing allowing Content Browser items to appear in other directories other than their original location

| 属性 | 值 |
|---|---|
| 中文名 | 内容浏览器别名数据源 |
| 分类 | Content Browser |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ContentBrowserAliasDataSource` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-05-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAliasDataSource) | |

## 用途

本插件是 `ContentBrowserAssetDataSource` 的配套扩展，旨在为虚幻引擎的内容浏览器提供一种灵活的资产组织与展示机制。其核心功能是允许资产在内容浏览器中以**别名（Alias）** 的形式出现在其原始目录之外的其他虚拟路径下。

这意味着，一个实际位于 `/Game/Characters/Hero/` 的资产，可以通过创建别名，在内容浏览器中同时出现在 `/Game/ByProject/ProjectA/`、`/Game/ByCategory/Meshes/` 等自定义的虚拟目录中。别名尽可能地模拟原始资产的行为，支持编辑、保存、缩略图查看等操作，但通常会限制移动或删除等可能破坏资产源文件的操作。

插件主要服务于需要更灵活资产组织和视图管理的场景，特别是在大型项目或需要多维度展示同一资产集时。

## 使用场景

-   **大型项目资产管理**：当一个大型项目包含多个子项目或模块时，你可以为共享的资产创建逻辑分组别名，让不同团队的成员能快速找到自己需要的资产，而无需在复杂的物理目录结构中导航。
-   **创建自定义资产库视图**：美术总监或技术负责人希望为团队提供一套按功能（如“所有角色模型”、“所有粒子效果”）或按重要性（如“核心资产”）组织的虚拟资产目录，这些视图是动态生成的，不改变资产的实际存放位置。
-   **支持Verse编程语言资产**：源码注释和最近的提交表明，该插件被用于处理Verse相关资产的虚拟目录显示，允许Verse类等资产以逻辑方式组织在内容浏览器中，而不必遵循严格的包路径规则。

## 蓝图用法

本插件主要提供一个编辑器模块（`Editor`类型），其核心功能通过C++ API暴露。蓝图中直接使用的节点较少，更多是供其他编辑器系统调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAlias` | 为一个资产添加一个别名路径。 | `UContentBrowserAliasDataSource` |
| `RemoveAlias` | 从数据源中移除一个指定的别名。 | `UContentBrowserAliasDataSource` |
| `ReconcileAliasesForAsset` | 根据新的别名列表，自动调用AddAlias或RemoveAlias以使当前存储的数据与新列表保持一致。 | `UContentBrowserAliasDataSource` |

### 使用示例（蓝图描述）

由于是编辑器专用模块，通常在C++编辑器工具或编写自定义资产操作逻辑时调用。以下是在蓝图编辑器工具中可能的使用逻辑：

1.  **获取数据源实例**：在编辑器工具蓝图中，首先需要获取 `UContentBrowserAliasDataSource` 的单例。通常通过 `FContentBrowserAliasDataSourceModule` 的 `TryGetAliasDataSource()` 函数获取。
2.  **添加别名**：获取到数据源实例后，调用 `AddAlias` 节点。输入需要添加别名的 `FAssetData` 和一个表示别名路径的 `FName`（例如 `/Game/Aliases/MyHero`）。
3.  **同步更改**：如果资产的别名信息发生变化（例如从元数据中读取到了新的别名列表），调用 `ReconcileAliasesForAsset` 来同步。

## C++ 用法

### 头文件引入

```cpp
#include "ContentBrowserAliasDataSource.h"
#include "ContentBrowserAliasDataSourceModule.h"
```

### 基本用法

```cpp
// 基本用法：获取别名数据源并添加/删除别名。
// 来源：基于 UContentBrowserAliasDataSource 类公共接口推断。
#include "ContentBrowserAliasDataSourceModule.h"
#include "ContentBrowserAliasDataSource.h"

// 1. 获取模块和数据源单例
FContentBrowserAliasDataSourceModule& AliasModule = FModuleManager::LoadModuleChecked<FContentBrowserAliasDataSourceModule>(TEXT("ContentBrowserAliasDataSource"));
UContentBrowserAliasDataSource* AliasDataSource = AliasModule.TryGetAliasDataSource();

if (AliasDataSource)
{
    // 2. 准备一个资产的数据
    FAssetData MyAssetData; // 假设你已经通过资产注册表等途径获得了某个资产的FAssetData

    // 3. 为该资产添加一个别名
    FName AliasPath = FName(TEXT("/Game/Aliases/MyAsset_Alias"));
    AliasDataSource->AddAlias(MyAssetData, AliasPath);

    // 4. （可选）稍后移除该别名
    // AliasDataSource->RemoveAlias(MyAssetData.GetSoftObjectPath(), AliasPath);
}
```

### 进阶用法

```cpp
// 进阶用法：使用元数据标签自动管理别名，并提供本地化显示名称。
// 来源：基于 UContentBrowserAliasDataSource 类注释与 FContentBrowserLocalizedAlias 结构体推断。
#include "ContentBrowserAliasDataSource.h"
#include "AssetRegistry/AssetRegistryModule.h"

UContentBrowserAliasDataSource* AliasDataSource = /* ... 获取方式同上 ... */;
IAssetRegistry& AssetRegistry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();

// 1. 监听资产更新，以同步基于元数据的别名
AssetRegistry.OnAssetUpdated().AddLambda([AliasDataSource](const FAssetData& InAssetData)
{
    if (AliasDataSource)
    {
        // 自动处理资产上定义的 `AliasTagName` 元数据标签
        AliasDataSource->ReconcileAliasesFromMetaData(InAssetData);
    }
});

// 2. 为别名文件夹设置一个本地化显示名称
AliasDataSource->AddAliasFolderDisplayName(FName("/Game/Aliases"), NSLOCTEXT("MyProject", "AliasFolder", "My Project Aliases"));

// 3. 手动添加带有本地化显示名称的别名
TArray<FContentBrowserLocalizedAlias> LocalizedAliases;
FContentBrowserLocalizedAlias& Alias = LocalizedAliases.AddDefaulted_GetRef();
Alias.Alias = FName(TEXT("/Game/Aliases/LocalizedMesh"));
Alias.DisplayName = NSLOCTEXT("MyProject", "MeshAlias", "Core Meshes");
AliasDataSource->AddAliases(MyAssetData, LocalizedAliases);
```

## Demo 示例

一个最小的编辑器模块，演示如何在编辑器启动时为一个现有资产添加别名。

```cpp
// MyAliasSetupModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyAliasSetupModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyAliasSetupModule.cpp
#include "MyAliasSetupModule.h"
#include "ContentBrowserAliasDataSourceModule.h"
#include "ContentBrowserAliasDataSource.h"
#include "AssetRegistry/AssetData.h"
#include "AssetRegistry/AssetRegistryModule.h"

#define LOCTEXT_NAMESPACE "MyAliasSetup"

void FMyAliasSetupModule::StartupModule()
{
    // 延迟到编辑器完全启动后执行
    FCoreDelegates::OnAllModuleLoadingPhasesComplete.AddLambda([]()
    {
        // 获取别名数据源
        FContentBrowserAliasDataSourceModule& AliasModule = FModuleManager::LoadModuleChecked<FContentBrowserAliasDataSourceModule>(TEXT("ContentBrowserAliasDataSource"));
        UContentBrowserAliasDataSource* AliasDataSource = AliasModule.TryGetAliasDataSource();

        if (AliasDataSource && GIsEditor)
        {
            // 找到一个特定的资产（例如 StarterContent 中的一个材质）
            IAssetRegistry& AssetRegistry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();
            TArray<FAssetData> AssetDataList;
            AssetRegistry.GetAssetsByPackageName(FName("/Game/StarterContent/Materials/M_Basic_Floor"), AssetDataList);

            if (AssetDataList.Num() > 0)
            {
                const FAssetData& FloorMaterialAsset = AssetDataList[0];

                // 为它创建一个别名到自定义的别名目录下
                AliasDataSource->AddAlias(FloorMaterialAsset, FName("/Game/Aliases/CoreMaterials/FloorMaterial"));

                // 也可以添加一个本地化版本
                FContentBrowserLocalizedAlias LocalizedAlias;
                LocalizedAlias.Alias = FName("/Game/Aliases/CoreMaterials/LocalizedFloor");
                LocalizedAlias.DisplayName = LOCTEXT("FloorAlias", "The Main Floor");
                AliasDataSource->AddAlias(FloorMaterialAsset, LocalizedAlias);
            }
        }
    });
}

void FMyAliasSetupModule::ShutdownModule()
{
    // 清理工作（如果需要）
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyAliasSetupModule, MyAliasSetup)
```

**模块依赖**：要在你的编辑器插件中使用此功能，你的模块需要在 `.Build.cs` 中依赖 `ContentBrowserAliasDataSource` 模块。

## 模块依赖

从插件的模块依赖关系看，它本身依赖于 `ContentBrowserAssetDataSource`。当你的模块要使用 `ContentBrowserAliasDataSource` 提供的功能时，需要在你的模块的 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ContentBrowserAliasDataSource` | 提供别名数据源核心类 `UContentBrowserAliasDataSource` 和模块类 `FContentBrowserAliasDataSourceModule`。 |
| `ContentBrowserAssetDataSource` | 作为 `ContentBrowserAliasDataSource` 的基础，依赖它以获得完整的资产数据源功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏UE_LOG迁移到新的UE_LOGF。 |
| 2026-02-03 | `dcd1cc44` | [Backout] - CL50425790 | 回退了编号为CL50425790的更改。 |
| 2026-02-02 | `d969643d` | Fixes the Content Browser to not show the `_Verse` folders and `_Verse` items coming from cooked plu | 修复了内容浏览器显示来自已打包插件的`_Verse`文件夹和项的问题。 |
| 2026-02-02 | `ad37203d` | [Backout] - CL50266363 | 回退了编号为CL50266363的更改。 |
| 2026-01-28 | `4c512dd3` | Fixes the Content Browser to not show the `_Verse` folders and `_Verse` items coming from cooked plu | 修复了内容浏览器显示来自已打包插件的`_Verse`文件夹和项的问题。 |

### 维护评价

该插件是一个**相对较新且仍在活跃开发中**的**实验性**模块。

-   **创建时间**：约 2 年前（2024年5月），相较于许多引擎核心插件非常年轻。
-   **近期活跃度**：在2026年仍有持续的维护活动，包括代码质量改进（日志迁移）和重要的功能修复（Verse相关资产的显示问题）。这表明 Epic 内部正在积极使用和维护此插件，特别是为了支持新的 Verse 编程语言。
-   **状态与风险**：插件被标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明它仍处于**实验阶段**，API 和行为可能在未来版本中发生变化。在生产项目中依赖此功能需谨慎，并做好未来适配的准备。
-   **推荐使用**：如果你的项目有明确的资产别名化组织需求，特别是与 Verse 开发相关，可以尝试使用此插件来提升工作流。但对于核心生产管线，建议密切关注其更新，并理解其实验性质。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserAliasDataSource)