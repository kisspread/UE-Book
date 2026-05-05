# Plugin Utilities

> Helpers to create and edit plugins. Used by Plugin Browser.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | PluginUtils (Editor) |
| 创建时间 | 2020-04-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PluginUtils) | |

## 用途

PluginUtils 是 UE5 编辑器内部使用的 Plugin 管理工具库，为 **Plugin Browser**（插件浏览器）提供底层能力。它解决了以下问题：

- **运行时创建 Plugin**：从模板文件夹自动生成新的 Plugin，包括复制模板文件、替换 `PLUGIN_NAME` 占位符、编译代码模块、注册到 Plugin Manager 等完整流程
- **动态加载/卸载 Plugin**：在编辑器运行时加载已有 Plugin（挂载 Content、加载 Module），以及安全卸载 Content-only Plugin
- **路径与名称工具**：统一处理 Plugin 的文件夹结构（Content、Resources、.uplugin 路径等）
- **名称验证**：确保新 Plugin 名称合法且不与已有 Plugin 冲突

这个 Plugin 本身不面向最终用户，而是面向 **需要在 C++ 中程序化管理 Plugin 的编辑器扩展开发者**。

## 使用场景

- 你在做一个编辑器工具，需要在运行时动态创建新 Plugin（例如自动生成 Gameplay Feature Plugin）→ 用 `FPluginUtils::CreateAndLoadNewPlugin`
- 你需要在编辑器中按需加载/卸载外部 Plugin（例如 Mod 系统）→ 用 `FPluginUtils::LoadPlugin` / `UnloadPlugin`
- 你需要验证用户输入的 Plugin 名称是否合法 → 用 `FPluginUtils::IsValidPluginName`
- 你需要从 `.uplugin` 文件路径反查 Plugin 的各个子目录 → 用 `GetPluginFolder` / `GetPluginContentFolder` 等

## 蓝图用法

PluginUtils 没有暴露任何 `BlueprintCallable` 接口。它是一个纯 C++ 编辑器工具库，仅通过 C++ API 使用。

## C++ 用法

### 头文件引入

```cpp
#include "PluginUtils.h"
```

### 基本用法 — 验证 Plugin 名称

```cpp
// 验证 Plugin 名称是否合法（仅字母、数字、下划线、连字符）
FText FailReason;
bool bValid = FPluginUtils::IsValidPluginName(TEXT("MyAwesomePlugin"), &FailReason);
if (!bValid)
{
    UE_LOG(LogTemp, Warning, TEXT("Invalid plugin name: %s"), *FailReason.ToString());
}
```

### 基本用法 — 获取 Plugin 路径

```cpp
// 根据 Plugin 位置和名称获取各种路径
FString EnginePluginsDir = FPaths::EnginePluginsDir();
FString PluginFolder = FPluginUtils::GetPluginFolder(EnginePluginsDir, TEXT("MyPlugin"));
// => ".../Engine/Plugins/MyPlugin"

FString UpluginPath = FPluginUtils::GetPluginFilePath(EnginePluginsDir, TEXT("MyPlugin"));
// => ".../Engine/Plugins/MyPlugin/MyPlugin.uplugin"

FString ContentFolder = FPluginUtils::GetPluginContentFolder(EnginePluginsDir, TEXT("MyPlugin"));
// => ".../Engine/Plugins/MyPlugin/Content"

FString ResourcesFolder = FPluginUtils::GetPluginResourcesFolder(EnginePluginsDir, TEXT("MyPlugin"));
// => ".../Engine/Plugins/MyPlugin/Resources"
```

### 进阶用法 — 创建并加载新 Plugin

```cpp
// 从模板创建一个新的 Content+Code Plugin
FPluginUtils::FNewPluginParams CreateParams;
CreateParams.FriendlyName = TEXT("My Game Feature");
CreateParams.Description = TEXT("A custom gameplay feature plugin");
CreateParams.CreatedBy = TEXT("My Studio");
CreateParams.bHasModules = true;                        // 包含 C++ 代码模块
CreateParams.bCanContainContent = true;                  // 包含 Content 目录
CreateParams.ModuleDescriptorType = EHostType::Runtime;  // Runtime 模块
CreateParams.TemplateFolders.Add(TEXT("/Path/To/TemplateFolder")); // 模板文件目录

FPluginUtils::FLoadPluginParams LoadParams;
LoadParams.bEnablePluginInProject = true;          // 自动在项目中启用
LoadParams.bSelectInContentBrowser = true;          // 创建后在 Content Browser 中选中
LoadParams.bSynchronousAssetsScan = true;           // 同步扫描资产
LoadParams.bUpdateProjectPluginSearchPath = true;   // 更新项目的 Plugin 搜索路径

TSharedPtr<IPlugin> NewPlugin = FPluginUtils::CreateAndLoadNewPlugin(
    TEXT("MyGameFeature"),
    FPaths::ProjectPluginsDir(),  // Plugin 位置
    CreateParams,
    LoadParams
);

if (NewPlugin.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Plugin created: %s"), *NewPlugin->GetName());
}
```

> **模板替换机制**：模板文件夹中文件名和内容中的 `PLUGIN_NAME` 文本会被自动替换为实际的 Plugin 名称。支持 `.cs`、`.cpp`、`.h`、`.vcxproj`、`.uplugin` 文件的内容替换，以及 `.uasset`、`.umap` 的路径重定向。

### 进阶用法 — 使用 FNewPluginParamsWithDescriptor（UE 5.6+）

```cpp
// 直接使用 FPluginDescriptor 进行更精细的控制
FPluginUtils::FNewPluginParamsWithDescriptor ExParams;
ExParams.Descriptor.FriendlyName = TEXT("Verse Plugin");
ExParams.Descriptor.Version = 1;
ExParams.Descriptor.VersionName = TEXT("1.0");
ExParams.Descriptor.Category = TEXT("Gameplay");
ExParams.Descriptor.bCanContainContent = true;
ExParams.Descriptor.bCanContainVerse = true;           // 支持 Verse
ExParams.Descriptor.bExplicitlyLoaded = true;           // 显式加载
ExParams.Descriptor.VersePath = TEXT("/MyPlugin/Game");
ExParams.NameToReplace = TEXT("TEMPLATE_NAME");         // 自定义模板替换名
ExParams.TemplateFolders.Add(TEXT("/Path/To/Template"));

FPluginUtils::FLoadPluginParams LoadParams;
LoadParams.bUpdateProjectPluginSearchPath = true;

TSharedPtr<IPlugin> Plugin = FPluginUtils::CreateAndLoadNewPlugin(
    TEXT("MyVersePlugin"),
    FPaths::ProjectPluginsDir(),
    ExParams,
    LoadParams
);
```

### 进阶用法 — 动态加载已有 Plugin

```cpp
// 加载一个已存在但未加载的 Plugin
FPluginUtils::FLoadPluginParams LoadParams;
LoadParams.bEnablePluginInProject = true;
LoadParams.bSelectInContentBrowser = true;
LoadParams.bSynchronousAssetsScan = true;

TSharedPtr<IPlugin> Plugin = FPluginUtils::LoadPlugin(
    TEXT("ExternalPlugin"),
    TEXT("/Some/External/Path/Plugins"),
    LoadParams
);

if (!Plugin.IsValid())
{
    // LoadParams.OutFailReason 可能包含失败原因
}
```

### 进阶用法 — 卸载 Plugin

```cpp
// 卸载单个 Plugin（仅 Content-only Plugin 可安全卸载）
FText FailReason;
bool bSuccess = FPluginUtils::UnloadPlugin(TEXT("MyPlugin"), &FailReason);
if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to unload: %s"), *FailReason.ToString());
}

// 批量卸载
TArray<FString> PluginNames = { TEXT("PluginA"), TEXT("PluginB") };
FPluginUtils::UnloadPlugins(PluginNames);

// 仅卸载资产但不卸载 Plugin 本身
FPluginUtils::UnloadPluginAssets(TEXT("MyPlugin"));
```

### 进阶用法 — 查找 Plugin

```cpp
// 从 .uplugin 文件路径查找已加载的 Plugin
TSharedPtr<IPlugin> Plugin = FPluginUtils::FindLoadedPlugin(
    TEXT("/path/to/MyPlugin.uplugin")
);

// 从 Package 路径查找所属 Plugin
TSharedPtr<IPlugin> OwnerPlugin = FPluginUtils::FindPluginFromPackagePath(
    FName(TEXT("/Script/MyModule"))
);
// 也支持 Content 包路径
TSharedPtr<IPlugin> ContentPlugin = FPluginUtils::FindPluginFromPackagePath(
    TEXT("/MyPlugin/Content/Assets/MyAsset")
);
```

## Demo 示例

### 完整示例：创建 Plugin 的编辑器工具按钮

```cpp
// MyPluginCreator.h
#pragma once

#include "CoreMinimal.h"

class FMyPluginCreator
{
public:
    static void CreateGameFeaturePlugin(const FString& PluginName, const FString& TemplatePath);
};
```

```cpp
// MyPluginCreator.cpp
#include "MyPluginCreator.h"
#include "PluginUtils.h"

void FMyPluginCreator::CreateGameFeaturePlugin(const FString& PluginName, const FString& TemplatePath)
{
    // 1. 验证名称
    FText NameError;
    if (!FPluginUtils::IsValidPluginName(PluginName, &NameError))
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid name: %s"), *NameError.ToString());
        return;
    }

    // 2. 验证名称不冲突
    if (!FPluginUtils::ValidateNewPluginNameAndLocation(PluginName, FPaths::ProjectPluginsDir(), &NameError))
    {
        UE_LOG(LogTemp, Error, TEXT("Name conflict: %s"), *NameError.ToString());
        return;
    }

    // 3. 配置创建参数
    FPluginUtils::FNewPluginParams CreateParams;
    CreateParams.FriendlyName = PluginName;
    CreateParams.Description = TEXT("Auto-generated game feature plugin");
    CreateParams.bHasModules = true;
    CreateParams.bCanContainContent = true;
    CreateParams.TemplateFolders.Add(TemplatePath);

    // 4. 配置加载参数
    FPluginUtils::FLoadPluginParams LoadParams;
    LoadParams.bEnablePluginInProject = true;
    LoadParams.bSelectInContentBrowser = true;
    LoadParams.bSynchronousAssetsScan = true;

    // 5. 创建并加载
    TSharedPtr<IPlugin> NewPlugin = FPluginUtils::CreateAndLoadNewPlugin(
        PluginName,
        FPaths::ProjectPluginsDir(),
        CreateParams,
        LoadParams
    );

    if (NewPlugin.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created plugin: %s"), *NewPlugin->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create plugin"));
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "PluginUtils",
    "Projects"
});
```

## 模块依赖

### PluginUtils 自身依赖

| 模块 | 依赖类型 | 用途 |
|---|---|---|
| `Projects` | Public | Plugin/Project 管理接口 |
| `Core` | Public | 基础核心库 |
| `AssetRegistry` | Private | 资产扫描与注册 |
| `AssetTools` | Private | 资产重命名操作 |
| `CoreUObject` | Private | UObject 系统 |
| `DesktopPlatform` | Private | UBT 调用、项目文件生成 |
| `EditorScriptingUtilities` | Private | 编辑器脚本工具 |
| `Engine` | Private | 引擎核心 |
| `GameProjectGeneration` | Private | 项目配置更新 |
| `GameplayTags` | Private | GameplayTag 修复 |
| `SourceControl` | Private | 源码管理集成 |
| `SubobjectDataInterface` | Private | 子对象数据（蓝图修复） |
| `UnrealEd` | Private | 编辑器核心 |

### 使用者需要依赖

| 模块 | 用途 |
|---|---|
| `PluginUtils` | Plugin 管理工具类 |
| `Projects` | `IPlugin`、`IPluginManager` 等接口 |

### Plugin 级别依赖

| Plugin | 说明 |
|---|---|
| `EditorScriptingUtilities` | 提供 `UEditorAssetLibrary` 等编辑器脚本功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-07-30 | `a5d34bd3866c` | **Add gameplaytag fixup to plugin creation from template** — 从模板创建 Plugin 时自动修复 GameplayTag 引用，避免模板中的 Tag 路径在新 Plugin 中失效 |
| 2025-07-28 | `41846f8b1f9d` | **Exclude unmounted plugins from UnloadPluginAssets** — 修复了 `UnloadPluginAssets` 尝试卸载未挂载 Plugin 资产的问题；将 `IsEnabled` 检查改为 `IsMounted`，正确处理 ExplicitlyLoaded Plugin |
| 2025-05-30 | `8396b185774c` | **Updated headers using UnrealCodeFixup** — 确保 `dllstorage` 标注在方法/静态变量上而非类型上（DLL 导出规范化） |

### 维护评价

- **创建时间**：2020-04-24，已有 6+ 年历史
- **最近更新**：2025-07-30，近期有实质性功能更新（GameplayTag 修复）
- **活跃程度**：**活跃维护** — 最近 6 个月内有功能性更新
- **内部重要性**：Plugin Browser 的底层依赖，Epic 自家编辑器工具链的核心组件
- **API 稳定性**：旧 API（`CreateAndMountNewPlugin`、`MountPlugin`、`FMountPluginParams`）已在 UE 5.0 标记为 `UE_DEPRECATED`，新代码应使用 `Load` 系列 API
- **UE 5.6 变更**：带 `NameToReplace` 参数的 `CreateAndLoadNewPlugin` 重载在 5.6 标记为废弃，应改用 `FNewPluginParamsWithDescriptor.NameToReplace`
- **推荐使用**：✅ 如果你需要在 C++ 中程序化创建/管理 Plugin，这是官方推荐的工具库。注意它仅在编辑器环境（`WITH_EDITOR`）下可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PluginUtils)
- 官方文档：无（未提供 DocsURL）
- 测试用例：未找到独立测试文件（该 Plugin 的测试可能集成在 Plugin Browser 的测试中）
