# Blueprint Stats

> Blueprint Stats

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图统计 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintStats` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-03-15 |
| 年龄标签 | 👴 老古董（约5年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BlueprintStats) | |

## 用途

`BlueprintStats` 是一个编辑器插件，用于统计和分析项目中蓝图的各种指标。它没有提供可视化 UI 或自动报告功能，而是通过静态记录类 `FBlueprintStatRecord` 在内存中收集数据，供其他工具或编辑器脚本使用。该插件的主要目标是让开发者能够以编程方式获取蓝图的节点数量、函数调用频率、宏使用情况、纯/非纯函数分布、是否仅包含数据等统计数据，从而辅助代码质量分析、性能评估或蓝图重构决策。

## 使用场景

- 你需要对项目中的所有蓝图进行批量审计，例如统计有多少蓝图是纯数据蓝图（没有自定义逻辑）、哪些函数被频繁使用。
- 你正在开发一个编辑器工具或插件，需要获取蓝图内部的节点类型和使用频率。
- 你希望了解蓝图中纯函数（Pure Function）与非纯函数的比例，以评估代码风格或优化蓝图执行效率。

## 蓝图用法

**此插件没有公开任何蓝图可调用节点或蓝图函数。** 所有功能均通过 C++ 类实现，仅供 C++ 代码直接使用。请参考下方 C++ 用法。

## C++ 用法

### 头文件引入

```cpp
#include "BlueprintStats.h"  // 核心记录类
#include "IBlueprintStatsModule.h" // 模块接口（可选）
```

### 基本用法

创建一个 `FBlueprintStatRecord` 对象并传入一个 `UBlueprint*`，它会自动解析该蓝图的统计数据。

```cpp
// BlueprintStatsTest.cpp (示例)
#include "BlueprintStats.h"
#include "Engine/Blueprint.h"

void PrintBlueprintStats(UBlueprint* BP)
{
    FBlueprintStatRecord Record(BP);
    FString Stats = Record.ToString();
    UE_LOG(LogTemp, Log, TEXT("Blueprint Stats:\n%s"), *Stats);
}
```

来源文件: `Source/BlueprintStats/Private/BlueprintStats.h`，构造函数读取蓝图统计。

### 进阶用法

合并多个蓝图的记录，生成全局统计数据。

```cpp
#include "BlueprintStats.h"
#include "Engine/Blueprint.h"
#include "UObject/UObjectIterator.h"

void AggregateAllBlueprints()
{
    FBlueprintStatRecord GlobalStats;

    for (TObjectIterator<UBlueprint> It; It; ++It)
    {
        UBlueprint* BP = *It;
        if (BP)
        {
            FBlueprintStatRecord SingleRecord(BP);
            GlobalStats.MergeAnotherRecordIn(SingleRecord);
        }
    }

    // 输出全局统计（表头）
    UE_LOG(LogTemp, Log, TEXT("%s"), *FBlueprintStatRecord::ToString(/*bHeader=*/true));
    UE_LOG(LogTemp, Log, TEXT("%s"), *GlobalStats.ToString());
}
```

`MergeAnotherRecordIn` 方法将单个记录的内容累加到合并记录中，`ToString` 方法支持生成 CSV 风格的头部与数据行。

## Demo 示例

以下是一个完整的、可编译的最小编辑器模块示例，展示如何使用 `BlueprintStats` 统计当前所有蓝图并输出到日志。

### BlueprintStatsDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FBlueprintStatsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### BlueprintStatsDemo.cpp

```cpp
#include "BlueprintStatsDemo.h"
#include "BlueprintStats.h"
#include "Engine/Blueprint.h"
#include "UObject/UObjectIterator.h"

IMPLEMENT_MODULE(FBlueprintStatsDemoModule, BlueprintStatsDemo);

void FBlueprintStatsDemoModule::StartupModule()
{
    // 收集所有蓝图并输出全局统计
    FBlueprintStatRecord GlobalStats;
    for (TObjectIterator<UBlueprint> It; It; ++It)
    {
        if (It->IsValidLowLevel())
        {
            FBlueprintStatRecord Record(*It);
            GlobalStats.MergeAnotherRecordIn(Record);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("=== Blueprint Stats Aggregated ==="));
    UE_LOG(LogTemp, Log, TEXT("%s"), *GlobalStats.ToString());
}

void FBlueprintStatsDemoModule::ShutdownModule()
{
    // 清理
}
```

### BlueprintStatsDemo.Build.cs

```csharp
using UnrealBuildTool;

public class BlueprintStatsDemo : ModuleRules
{
    public BlueprintStatsDemo(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "BlueprintStats"   // 依赖此插件
        });
    }
}
```

**注意**：此 Demo 需要将项目设置为 Editor 模块（`ModuleType = ModuleRules.ModuleType.Editor`），因为 `BlueprintStats` 本身是 Editor 插件。实际测试时，请在现有 Editor 模块中添加引用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 标准基础类型 |
| `CoreUObject` | UObject 支持 |
| `Engine` | UBlueprint、UEdGraph 等引擎类 |

除此以外无特殊依赖。

## 维护状态

### 近期更新

- 2024-01-12 `56a32fea` Silence false V621, V654, and V1078 warnings mostly caused by TStaticArray, placement new, or popular code patterns.
- 2023-01-16 `bbc37aa2` [Engine/Plugins] update.
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.
- 2020-08-14 `48113fc7` Adding EditorFramework to build.cs files.
- 2020-03-15 `b7568cc6` Fix for UE-90683: You can no longer delete conflicting variables.

### 维护评价

- **创建时间**：2020 年，至今约 5 年。
- **更新频率**：最近实质性代码变更还是 2020 年（添加记录功能），后续 commits 都是编译警告修复或链接更新。
- **活跃度**：不活跃，没有新功能开发。
- **已知问题**：无公开重大缺陷，但 API 简单，仅提供基础统计，无输出 UI 或导出功能。
- **推荐使用**：如果你需要编写 C++ 工具进行蓝图统计，此插件提供便利的基础类；但若需要更高级可视化，建议自行扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BlueprintStats)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/BlueprintStats/Source/BlueprintStats/Private/BlueprintStats.cpp) （核心实现文件）