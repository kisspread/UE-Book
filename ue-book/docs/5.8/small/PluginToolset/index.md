# PluginToolset

> Toolset for listing, inspecting, and creating Plugins via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 插件工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PluginToolset) | |

## 用途

该插件是一个面向 AI 工具集注册表的专用工具集，它将 UE 编辑器中管理插件的功能（如浏览、创建、启用/禁用、编辑描述符）封装为一组标准化的、可通过 AI 代理调用的接口。它的存在是为了让 AI 工具能够自主地或通过脚本与引擎的插件管理系统进行交互，实现插件的自动化管理、查询和批量操作，而无需手动通过编辑器的图形界面进行。

## 使用场景

- **自动化工作流**：在 CI/CD 或自动化测试流水线中，需要根据条件动态创建、启用或禁用项目插件。
- **AI 辅助开发**：AI 开发助手需要了解项目中已有的插件信息，或根据开发任务（如“需要一个网络模块”）自动搜索、创建并配置合适的插件。
- **批量管理**：需要同时查询或修改多个插件的属性或依赖关系。
- **脚本化插件模板**：通过代码驱动的方式，基于预定义模板快速生成新的插件骨架项目。

## 蓝图用法

此插件的所有功能均标记为 `meta=(AICallable)`，意为主要为 AI 工具集设计，但在蓝图中亦可调用。

### 核心节点

#### 查询类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListEnabledPlugins` | 返回所有已启用插件的名称列表（字母排序） | `UPluginToolset` |
| `ListDiscoveredPlugins` | 返回所有已发现（包括禁用）插件的名称列表（字母排序） | `UPluginToolset` |
| `GetPluginInfo` | 获取指定插件的元数据，包括版本、基础目录等 | `UPluginToolset` |
| `IsEnabled` | 检查指定插件是否已启用 | `UPluginToolset` |
| `GetPluginDependencies` | 获取指定插件在其 .uplugin 文件中声明的依赖项列表 | `UPluginToolset` |
| `GetPluginDependents` | 获取所有依赖于指定插件的其他插件名称列表 | `UPluginToolset` |
| `GetPluginForAsset` | 根据资产路径或挂载点路径，返回拥有该资产的插件名称 | `UPluginToolset` |
| `GetPluginTemplateDescriptions` | 获取所有可用的插件模板描述 | `UPluginToolset` |

#### 创建与校验类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsPluginCreationAllowed` | 检查编辑器设置是否允许从插件浏览器创建插件 | `UPluginToolset` |
| `ValidateNewPluginNameAndLocation` | 验证新插件的名称和相对位置是否有效 | `UPluginToolset` |
| `CreatePlugin` | 从指定模板创建一个新插件并加载到编辑器中，成功时返回描述符文件名 | `UPluginToolset` |

#### 编辑与管理类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsPluginModificationAllowed` | 检查编辑器设置是否允许修改插件 | `UPluginToolset` |
| `SetPluginEnabled` | 在项目配置中启用或禁用插件（需重启编辑器生效） | `UPluginToolset` |
| `GetPluginDescriptor` | 获取指定插件的可编辑描述符字段 | `UPluginToolset` |
| `UpdatePluginDescriptor` | 更新指定插件的描述符字段并写入 .uplugin 文件 | `UPluginToolset` |
| `AddPluginDependency` | 为指定插件添加一个依赖项 | `UPluginToolset` |
| `RemovePluginDependency` | 从指定插件移除一个依赖项 | `UPluginToolset` |

### 使用示例（蓝图描述）

1.  **查询插件列表**：调用 `ListDiscoveredPlugins` 获取所有插件名称，然后可以遍历此列表，调用 `GetPluginInfo` 或 `IsEnabled` 获取详细信息。
2.  **创建新插件**：首先调用 `GetPluginTemplateDescriptions` 获取可用模板列表。选择其中一个模板（如 `FPluginTemplateDescriptionToolsetInfo`）。然后调用 `ValidateNewPluginNameAndLocation` 验证插件名和位置。如果验证通过，调用 `CreatePlugin` 传入插件名、相对路径、模板信息等参数来创建插件。
3.  **修改插件依赖**：先用 `GetPluginDependencies` 查看当前依赖，然后用 `AddPluginDependency` 或 `RemovePluginDependency` 进行增删。

## C++ 用法

### 头文件引入

```cpp
#include "PluginToolset/PluginToolset.h"
```

### 基本用法

```cpp
// 列出所有已启用的插件
TArray<FString> EnabledPlugins = UPluginToolset::ListEnabledPlugins();
for (const FString& PluginName : EnabledPlugins)
{
    UE_LOG(LogTemp, Log, TEXT("Enabled Plugin: %s"), *PluginName);
}

// 获取特定插件的详细信息
FPluginToolsetInfo MyPluginInfo = UPluginToolset::GetPluginInfo(TEXT("MyPlugin"));
UE_LOG(LogTemp, Log, TEXT("Plugin Base Directory: %s"), *MyPluginInfo.BaseDir);
```

### 进阶用法

```cpp
// 创建一个新插件的完整工作流
const FString NewPluginName = TEXT("MyNewFeature");

// 1. 获取模板列表
TArray<FPluginTemplateDescriptionToolsetInfo> Templates = UPluginToolset::GetPluginTemplateDescriptions();
if (Templates.Num() > 0)
{
    // 2. 选择一个模板（这里选择第一个）
    const FPluginTemplateDescriptionToolsetInfo& SelectedTemplate = Templates[0];

    // 3. 验证名称和位置
    FString RelativeLocation; // 可选，指定子目录
    bool bPlaceInEngine = false; // 通常放在游戏插件目录
    if (UPluginToolset::ValidateNewPluginNameAndLocation(NewPluginName, RelativeLocation, bPlaceInEngine, SelectedTemplate))
    {
        // 4. 创建插件
        FString CreatedDescriptor = UPluginToolset::CreatePlugin(
            NewPluginName,
            RelativeLocation,
            bPlaceInEngine,
            SelectedTemplate,
            TEXT("A plugin for my new feature.")
        );

        if (!CreatedDescriptor.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully created plugin. Descriptor: %s"), *CreatedDescriptor);

            // 5. (可选) 为新插件添加依赖
            UPluginToolset::AddPluginDependency(NewPluginName, TEXT("SomeOtherPlugin"), false, true);
        }
    }
}
```

## Demo 示例

**MyPluginManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "PluginToolset/PluginToolset.h"
#include "MyPluginManager.generated.h"

UCLASS()
class UMyPluginManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 蓝图可调用：检查并报告某个插件的状态
    UFUNCTION(BlueprintCallable, Category = "PluginManager")
    bool CheckAndReportPluginStatus(const FString& PluginName);

private:
    void LogPluginInfo(const FPluginToolsetInfo& Info);
};
```

**MyPluginManager.cpp**
```cpp
#include "MyPluginManager.h"

bool UMyPluginManager::CheckAndReportPluginStatus(const FString& PluginName)
{
    // 检查插件是否存在
    TArray<FString> AllPlugins = UPluginToolset::ListDiscoveredPlugins();
    if (!AllPlugins.Contains(PluginName))
    {
        UE_LOG(LogTemp, Warning, TEXT("Plugin '%s' not found."), *PluginName);
        return false;
    }

    // 获取信息并检查状态
    bool bEnabled = UPluginToolset::IsEnabled(PluginName);
    FPluginToolsetInfo Info = UPluginToolset::GetPluginInfo(PluginName);

    UE_LOG(LogTemp, Log, TEXT("Plugin: %s, Enabled: %s"), *PluginName, bEnabled ? TEXT("Yes") : TEXT("No"));
    LogPluginInfo(Info);

    // 如果禁用，则启用它
    if (!bEnabled)
    {
        UPluginToolset::SetPluginEnabled(PluginName, true);
        UE_LOG(LogTemp, Log, TEXT("Plugin '%s' has been enabled."), *PluginName);
    }

    return true;
}

void UMyPluginManager::LogPluginInfo(const FPluginToolsetInfo& Info)
{
    UE_LOG(LogTemp, Log, TEXT("  Version: %s (%d)"), *Info.VersionName, Info.Version);
    UE_LOG(LogTemp, Log, TEXT("  Description: %s"), *Info.Description);
    UE_LOG(LogTemp, Log, TEXT("  Base Dir: %s"), *Info.BaseDir);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 AI 工具集注册表的核心框架，本插件通过它注册自身 |
| `PluginUtils` | 提供底层的插件管理实用工具函数，如创建、修改 .uplugin 文件等 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `24cd8c64` | Update to PluginToolset description. | 更新了插件的描述信息。 |
| 2026-05-12 | `71d2c0c9` | Add plugin descriptor editing tools to UPluginToolset | 为工具集添加了插件描述符编辑功能。 |
| 2026-05-12 | `770b7544` | PluginToolset.SetPluginEnabled: raise error for nonexistent plugin | 修复了 `SetPluginEnabled` 函数，当插件不存在时会抛出错误。 |
| 2026-05-12 | `8d6d15aa` | Update Plugin Toolset's CreatePlugin to use a relative PluginLocation name. Also update the FPluginT... | 更新了 `CreatePlugin` 接口，使其使用相对路径，并调整了模板相关结构。 |
| 2026-05-12 | `8af5936e` | [Backout] - CL53534904 | 回滚了先前的一个更改（CL53534904）。 |

### 维护评价

这是一个**全新的实验性插件**，创建于 2026 年 5 月。根据提交记录，其初始功能开发在创建当天（2026-05-12）非常密集，随后进行了描述更新和一个小修复。目前处于早期积极开发阶段。

**需要注意**：
1.  **实验性**：插件标记为 `IsExperimentalVersion=true` 且默认未启用 (`EnabledByDefault=false`)，意味着它可能在未来发生破坏性更改或被废弃。
2.  **API 稳定性**：作为 AI 工具集，其核心接口 (`UFUNCTION(meta=(AICallable))`) 可能为了配合 AI 代理的需求而调整。
3.  **依赖项**：依赖于同样位于 `Experimental` 目录下的 `ToolsetRegistry` 和 `PluginUtils` 插件。

**推荐程度**：如果你正在开发 AI 工具集或需要通过代码高度自动化地管理 UE 插件，可以尝试使用此插件。但对于常规的游戏开发项目，建议等待其 API 更加稳定并从 `Experimental` 目录移出后再考虑集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PluginToolset)
- 官方文档：无
- 测试用例：无 (在提供的源码信息中未发现)