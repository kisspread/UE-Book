# Data Registry Toolset

> Toolset for querying and inspecting Data Registries

| 属性 | 值 |
|---|---|
| 中文名 | 数据注册表工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistryToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataRegistryToolset) | |

## 用途

Data Registry Toolset 是一个编辑器专用工具插件，它为 Unreal Engine 的 `Data Registry` 系统提供了一套查询和检查工具。它通过暴露一系列静态函数，解决了 Data Registry 在运行时信息不透明、难以调试的问题。

开发者和数据策划可以使用此工具集来：
- **发现与列举**：枚举项目中存在哪些 Data Registry 资产。
- **深度检查**：查看单个注册表的详细信息，如其描述、数据结构（Item Struct）、ID格式和数据源。
- **数据验证**：获取注册表的 Schema（JSON格式），验证数据结构是否符合预期。
- **内容查看**：列出注册表中的所有数据项，并获取缓存中的实际数据，用于检查内容是否正确加载和配置。
- **调试数据源**：区分“编辑器定义”的数据源和“运行时”展开的数据源（特别是当使用了 Meta Source 时），便于理解数据流。

简而言之，它是 `Data Registry` 生态系统中的一个调试和管理助手。

## 使用场景

- 你正在使用 Data Registry 管理大量的游戏数据（如物品表、技能数据、任务配置），需要在编辑器中快速验证这些数据是否被正确识别和缓存。
- 你需要检查某个特定 Data Registry 的数据源配置，了解其数据是从哪些资产或运行时源加载的。
- 你的 Data Registry 使用了 `Meta Source`，需要调试最终生效的运行时源列表。
- 你希望以编程方式（通过蓝图或 C++）查询项目中的数据注册表信息，集成到自定义的编辑器工具或报告功能中。
- **请注意**：这是一个 `EditorOnly` 插件，其功能仅在 Unreal Editor 中可用，不会被打包到最终游戏包中。

## 蓝图用法

该插件的功能通过 `UDataRegistryTools` 类暴露。所有函数都是静态的，标记为 `BlueprintCallable`，可以在任何蓝图中直接调用。

### 核心节点

以下节点按功能分组：

#### 查询注册表

| 节点 | 说明 | 所在类 |
|---|---|---|
| `List Registries` | 获取所有已注册的 Data Registry 名称。可选的 `StructFilter` 参数用于过滤出使用特定物品结构的注册表。 | `UDataRegistryTools` |
| `Get Registry Info` | 获取指定注册表的详细信息，包括名称、描述、物品结构、ID格式等，返回 `FDataRegistryInfo` 结构体。 | `UDataRegistryTools` |
| `Get Schema` | 获取指定注册表的物品结构定义，并以 JSON 字符串形式返回，便于查看字段和类型。 | `UDataRegistryTools` |

#### 检查数据与源

| 节点 | 说明 | 所在类 |
|---|---|---|
| `List Items` | 列出指定注册表中定义的所有数据项（Item）的名称。 | `UDataRegistryTools` |
| `List Data Sources` | 获取指定注册表在编辑器中配置的（定义时的）数据源列表，返回 `FDataRegistrySourceSummary` 结构体数组。 | `UDataRegistryTools` |
| `List Runtime Sources` | 获取指定注册表在运行时最终展开的数据源列表，包含了由 `Meta Source` 等机制生成的瞬态子源。 | `UDataRegistryTools` |
| `Get Items` | 根据一组数据项名称，从注册表的缓存中获取其对应的结构体数据（`FInstancedStruct`）。仅返回缓存中已存在的项。 | `UDataRegistryTools` |

### 使用示例（蓝图描述）

1.  **列出所有注册表**：
    创建一个 `List Registries` 节点，直接连接到 `Print String` 节点，即可在输出日志中看到所有注册表的名称。
2.  **查看特定注册表的详细信息**：
    - 将 `List Registries` 的输出连接到 `For Each Loop`。
    - 在循环体内，将当前循环的字符串（注册表名称）连接到 `Get Registry Info` 节点。
    - 将返回的 `FDataRegistryInfo` 结构体连接到 `Break` 节点，即可访问其 `RegistryName`、`Description`、`ItemCount` 等字段进行显示或逻辑判断。
3.  **获取并显示一个注册表的缓存数据**：
    - 使用 `List Items` 获取某个注册表（如 “MyItemRegistry”）的所有数据项名称数组。
    - 将数组传递给 `Get Items` 节点。
    - `Get Items` 的输出是一个 `TMap<FString, FInstancedStruct>`。你可以使用 `Map Keys` 节点获取所有键（数据项名称），然后用 `Find` 节点根据键查找对应的值（`FInstancedStruct`），进一步通过 `Break` 或 `Make` 节点处理结构体数据。

## C++ 用法

插件的功能通过 `UDataRegistryTools` 的静态成员函数提供。由于插件模块类型是 `Editor`，这些函数主要用于编辑器工具和开发流程，**不应在运行时游戏逻辑中调用**。

### 头文件引入

```cpp
#include "DataRegistryTools.h"
```

### 基本用法

以下示例展示了如何在编辑器工具或自定义命令中调用核心查询函数。

```cpp
// 1. 列举所有注册表
TArray<FString> AllRegistries = UDataRegistryTools::ListRegistries();
UE_LOG(LogTemp, Log, TEXT("Found %d data registries."), AllRegistries.Num());

// 2. 获取特定注册表的信息
const FString RegName = TEXT("WeaponData");
FDataRegistryInfo RegInfo = UDataRegistryTools::GetRegistryInfo(RegName);
UE_LOG(LogTemp, Log, TEXT("Registry '%s': %d items, Struct: %s"),
    *RegInfo.RegistryName,
    RegInfo.ItemCount,
    RegInfo.ItemStruct ? *RegInfo.ItemStruct->GetName() : TEXT("None"));

// 3. 列出注册表的所有数据项
TArray<FString> ItemNames = UDataRegistryTools::ListItems(RegName);
UE_LOG(LogTemp, Log, TEXT("Items in '%s': %s"), *RegName, *FString::Join(ItemNames, TEXT(", ")));
```
*来源: 基于 `DataRegistryTools.h` 中的函数定义。*

### 进阶用法

结合多个函数进行深度检查，例如检查一个使用了 Meta Source 的注册表的定义源和运行时源的差异。

```cpp
const FString MetaRegName = TEXT("DynamicItemTable");

// 获取编辑器中定义的源（可能包含 Meta Source 类型）
TArray<FDataRegistrySourceSummary> DefSources = UDataRegistryTools::ListDataSources(MetaRegName);
UE_LOG(LogTemp, Log, TEXT("Registry '%s' has %d defined sources."), *MetaRegName, DefSources.Num());

// 获取运行时展开的源（应包含由 Meta Source 实例化出的具体子源）
TArray<FDataRegistrySourceSummary> RuntimeSources = UDataRegistryTools::ListRuntimeSources(MetaRegName);
UE_LOG(LogTemp, Log, TEXT("Registry '%s' has %d runtime sources."), *MetaRegName, RuntimeSources.Num());

// 比较并打印运行时源的详细信息
for (const FDataRegistrySourceSummary& Source : RuntimeSources)
{
    UE_LOG(LogTemp, Log, TEXT("  Runtime Source: %s, Class: %s, Asset: %s, Transient: %s"),
        *Source.DebugString,
        Source.SourceClass ? *Source.SourceClass->GetName() : TEXT("Null"),
        *Source.SourceAssetPath.ToString(),
        Source.bIsTransient ? TEXT("Yes") : TEXT("No"));
}
```
*来源: 基于 `FDataRegistrySourceSummary` 结构体和相关函数定义。*

## Demo 示例

以下是一个编辑器内功能（例如，一个编辑器Utility Widget或自定义命令）的最小C++示例，用于打印某个注册表的概要信息。

**DataRegistryDemo.cpp**
```cpp
#include "DataRegistryDemo.h"
#include "DataRegistryTools.h" // 引入插件头文件
#include "Modules/ModuleManager.h"

void UDataRegistryDemo::PrintRegistrySummary(const FString& RegistryName)
{
    // 1. 检查注册表是否存在
    FDataRegistryInfo Info = UDataRegistryTools::GetRegistryInfo(RegistryName);
    if (Info.RegistryName.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("DataRegistry '%s' not found."), *RegistryName);
        return;
    }

    // 2. 打印基本信息
    UE_LOG(LogTemp, Display, TEXT("--- Data Registry Summary: %s ---"), *Info.RegistryName);
    UE_LOG(LogTemp, Display, TEXT("  Description: %s"), *Info.Description);
    UE_LOG(LogTemp, Display, TEXT("  Item Count: %d"), Info.ItemCount);
    UE_LOG(LogTemp, Display, TEXT("  Item Struct: %s"), Info.ItemStruct ? *Info.ItemStruct->GetName() : TEXT("N/A"));
    UE_LOG(LogTemp, Display, TEXT("  ID Format: %s"), *Info.IdFormat);

    // 3. 打印数据源数量
    TArray<FDataRegistrySourceSummary> DefSources = UDataRegistryTools::ListDataSources(RegistryName);
    TArray<FDataRegistrySourceSummary> RuntimeSources = UDataRegistryTools::ListRuntimeSources(RegistryName);
    UE_LOG(LogTemp, Display, TEXT("  Defined Sources: %d"), DefSources.Num());
    UE_LOG(LogTemp, Display, TEXT("  Runtime Sources: %d (Difference indicates Meta Source usage)"), RuntimeSources.Num());
}
```

**DataRegistryDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "DataRegistryDemo.generated.h"

UCLASS()
class UDataRegistryDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "DataRegistryDemo", meta=(CallInEditor="true"))
    static void PrintRegistrySummary(const FString& RegistryName);
};
```

## 模块依赖

从插件的 `.uplugin` 文件可以得知，它依赖以下两个插件（它们需要在你的项目中启用）：

| 模块/插件 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供工具集定义（`UToolsetDefinition`）的基础框架，本插件中的 `UDataRegistryTools` 继承自它。 |
| `DataRegistry` | **核心依赖**。本插件的功能完全围绕 `Data Registry` 系统构建，用于查询和检查其内容和状态。 |

在 `Build.cs` 中，你需要添加这两个插件的模块依赖。通常，你需要添加类似以下代码：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "DataRegistry" });
// “ToolsetRegistry” 的模块名可能是 “Toolset” 或 “ToolsetRegistryCore”，需根据实际模块名调整。
// 由于 .uplugin 指定了插件依赖，引擎会自动处理插件加载，但模块依赖仍需在 Build.cs 中声明。
```

## 维护状态

### 近期更新

根据提供的 Git 历史记录，此插件仅有一条提交记录。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `ffe59a83` | Added toolsets for data registries. Current implemented commands include: Listing registries, Getting registry properties, data and runtime sources, Getting all the runtime data populated in the registry | **首次提交**。添加了用于数据注册表的工具集。实现了查询注册表列表、获取属性/数据/运行时源以及获取所有运行时数据的命令。 |

### 维护评价

- **状态**：这是一个**全新的、实验性**的插件。
- **分析**：
    1.  **创建时间**：文档标记为2026年4月28日创建，这看起来是一个未来的日期，可能是一个占位符或错误。基于当前信息，它应被视为一个新插件。
    2.  **更新频率**：仅有一条初始提交，尚无法评估长期维护趋势。
    3.  **活跃度**：自首次提交后无后续更新记录，但鉴于其“实验性”（`IsExperimentalVersion: true`）和“默认不启用”（`EnabledByDefault: false`）的状态，这可能是正常的初始发布。
    4.  **已知限制**：作为实验性功能，其API可能会在未来版本中更改或移除。它仅限于编辑器环境，不适用于运行时逻辑。
- **推荐**：如果你在项目中深度使用 `Data Registry` 并急需调试和检查工具，可以**谨慎启用和使用**此实验性插件。建议将其用于开发和调试目的，并做好在未来API变更时更新代码的准备。对于新项目或对稳定性要求高的项目，建议观望或评估其必要性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataRegistryToolset)
- (官方文档链接未提供)