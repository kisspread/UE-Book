# Blueprint Stats

> Blueprint Stats

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图统计 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintStats` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats) | |

## 用途

这是一个用于收集和分析蓝图（Blueprint）资产复杂度与结构统计数据的编辑器工具插件。它并非面向最终玩家的运行时功能，而是为开发人员（尤其是技术美术、设计师或需要优化蓝图性能的程序员）提供的诊断和分析工具。

其核心功能是解析一个 `UBlueprint` 资产，并统计其中包含的各类节点（Node）、函数（Function）、宏（Macro）、纯/非纯节点等数量，并能将这些统计信息汇总。通过它，开发团队可以：
1.  **量化蓝图复杂度**：识别过于庞大、难以维护的“巨型蓝图”。
2.  **辅助性能分析**：评估蓝图中非纯（有副作用）函数和节点的密度，这些节点可能对运行时性能有更大影响。
3.  **项目健康度检查**：统计数据蓝图（Data-Only Blueprint）和用户自定义函数的数量，帮助理解资产结构。

## 使用场景

- 你在开发一个大型项目，美术或设计师创建了逻辑复杂、节点数量众多的蓝图，你需要快速了解其复杂度并决定是否需要进行重构。
- 你正在优化游戏性能，需要找出蓝图中可能导致性能瓶颈的大量非纯函数调用或特定类型的节点。
- 你需要生成一份项目蓝图资产的报告，用于团队审查或版本管理记录。

## 蓝图用法

该插件主要提供 C++ 接口和数据结构，用于编辑器工具扩展。经过分析，**该插件未暴露任何蓝图可调用的节点（`UFUNCTION(BlueprintCallable)`）**。它的使用方式是通过 C++ 代码访问其模块接口，创建和操作 `FBlueprintStatRecord` 对象来收集统计数据。

## C++ 用法

### 头文件引入

```cpp
// 访问插件模块接口
#include "IBlueprintStatsModule.h"

// 使用统计数据记录
#include "BlueprintStats.h"
```

### 基本用法

获取插件模块并为一个蓝图创建统计记录。

```cpp
// 检查模块是否可用
if (IBlueprintStatsModule::IsAvailable())
{
    // 获取模块实例（通常不需要直接操作模块本身，更多是使用其提供的类型）
    IBlueprintStatsModule& StatsModule = IBlueprintStatsModule::Get();

    // 假设你有一个指向 UBlueprint 对象的指针（例如从资产编辑器或内容浏览器获取）
    UBlueprint* MyBlueprint = /* ... */;

    // 为该蓝图创建一个统计记录，构造函数会自动解析蓝图并读取统计数据
    FBlueprintStatRecord StatRecord(MyBlueprint);

    // 获取一些基本统计信息
    UE_LOG(LogTemp, Log, TEXT("Blueprint '%s' has %d nodes."), *MyBlueprint->GetName(), StatRecord.NumNodes);
    UE_LOG(LogTemp, Log, TEXT("User Functions: %d"), StatRecord.NumUserFunctions);
    UE_LOG(LogTemp, Log, TEXT("Pure Functions: %d"), StatRecord.NumUserPureFunctions);
}
```

### 进阶用法

将多个蓝图的统计记录合并，生成一个汇总报告。

```cpp
// 创建一个用于汇总的“元记录”，其 SourceBlueprint 为 nullptr
FBlueprintStatRecord SummaryRecord;

// 假设有一个蓝图资产数组
TArray<UBlueprint*> AllBlueprints = /* ... */;

for (UBlueprint* Bp : AllBlueprints)
{
    if (Bp)
    {
        // 为每个蓝图创建记录
        FBlueprintStatRecord SingleRecord(Bp);
        // 将单个记录合并到汇总记录中
        SummaryRecord.MergeAnotherRecordIn(SingleRecord);
    }
}

// 使用汇总记录的 ToString 导出为可读的字符串（可进一步写入文件）
FString StatsText = SummaryRecord.ToString(true); // true 表示包含表头
UE_LOG(LogTemp, Log, TEXT("Project Summary:\n%s"), *StatsText);
```

## Demo 示例

一个控制台命令（或编辑器工具菜单项），用于对当前编辑器中选中的蓝图资产进行统计。

**BlueprintStatsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FBlueprintStatsDemo
{
public:
    /** 在控制台中运行蓝图统计命令 */
    static void RunBlueprintStats();
};
```

**BlueprintStatsDemo.cpp**
```cpp
#include "BlueprintStatsDemo.h"
#include "IBlueprintStatsModule.h"
#include "BlueprintStats.h"
#include "Engine/Blueprint.h"
#include "Editor.h" // 用于获取编辑器选择

void FBlueprintStatsDemo::RunBlueprintStats()
{
    if (!IBlueprintStatsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("BlueprintStats module is not available."));
        return;
    }

    // 获取编辑器中当前选中的资产
    USelection* SelectedAssets = GEditor->GetSelectedAssets();

    if (!SelectedAssets || SelectedAssets->Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets selected."));
        return;
    }

    // 创建汇总记录
    FBlueprintStatRecord SummaryRecord;

    // 遍历所有选中的资产
    for (FSelectionIterator It(*SelectedAssets); It; ++It)
    {
        UObject* Asset = *It;
        UBlueprint* BlueprintAsset = Cast<UBlueprint>(Asset);
        if (BlueprintAsset)
        {
            UE_LOG(LogTemp, Log, TEXT("Analyzing blueprint: %s"), *BlueprintAsset->GetName());
            FBlueprintStatRecord Record(BlueprintAsset);
            SummaryRecord.MergeAnotherRecordIn(Record);
        }
    }

    // 输出结果
    if (SummaryRecord.NumBlueprints > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("\n=== Selected Blueprints Stats ===\n%s"), *SummaryRecord.ToString(true));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("No blueprints were found in the selection."));
    }
}
```

## 模块依赖

从 `Build.cs` 分析，该插件依赖于一些标准模块，但有一个独特的依赖：

| 模块 | 用途 |
|---|---|
| `Kismet` | 访问蓝图图表（`UEdGraph`）相关类，这是进行节点和连接分析的核心依赖。 |

其他依赖（如 `Core`, `CoreUObject`, `Engine` 等）属于基础依赖，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2024-01-12 | `56a32fea` | Silence false V621, V654, and V1078 warnings mostly caused by TStaticArray, placement new, or popula... | 静默静态代码分析工具产生的假阳性警告（主要与模板、内存操作相关）。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 未明确说明的插件范围更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内置的供应商链接为 HTTPS 安全协议。 |
| 2020-08-14 | `48113fc7` | Adding EditorFramework to build.cs files | 将 EditorFramework 模块添加到构建文件中。 |

### 维护评价

**维护状态：可能已废弃**

-   **年龄**：该插件创建于 **2014 年**，已经超过 12 年。
-   **活动频率**：从 git 历史看，最近几年的提交几乎全部是“维护性”更新，如**迁移日志宏、修复编译警告、更新链接**等，没有涉及功能新增、API 改进或重要的 Bug 修复。
-   **实验性状态**：插件路径位于 `Experimental` 文件夹，且 `EnabledByDefault` 为 `false`，表明 Epic 官方从未将其提升为正式支持的生产功能。
-   **代码规模**：源文件极少（4个），功能非常基础和集中。

**结论**：这是一个非常古老的、实验性的、且长期缺乏实质性功能更新的插件。虽然其核心的 `FBlueprintStatRecord` 类在当前引擎版本中可能仍能编译并工作，但它很可能**不再被 Epic 主动维护**，也未见于官方的生产管线中。对于新项目，**不推荐依赖此插件**。如果需要蓝图分析功能，建议查看更现代的引擎内置功能或第三方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats)