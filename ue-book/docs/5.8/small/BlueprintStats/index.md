# Blueprint Stats

> Blueprint Stats

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图统计 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintStats` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats) | |

## 用途

BlueprintStats 是一个实验性的编辑器工具插件，用于收集和分析项目中蓝图资产的统计数据。它并非面向最终用户的功能性插件，而是供引擎开发者和资深技术美术用于评估蓝图资产复杂度、性能影响及代码结构的分析工具。通过该插件，可以量化单个蓝图的节点数量、函数调用情况、纯函数/非纯函数比例等关键指标，有助于进行蓝图的重构优化和性能瓶颈定位。

## 使用场景

- **性能优化分析**：当项目出现由蓝图引起的性能问题时，使用此工具统计大型蓝图的节点数量和复杂逻辑，找出优化目标。
- **代码审查与规范**：在团队中评估蓝图资产的“健康度”，例如检查非纯函数节点是否过多、自定义函数使用是否合理等。
- **技术调研**：引擎开发者或技术美术研究蓝图资产结构，了解其内部节点和函数的分布情况。

## 蓝图用法

该插件主要提供 C++ 接口，未在公开头文件中发现直接标记为 `BlueprintCallable` 的函数。其核心统计逻辑 `FBlueprintStatRecord::ReadStatsFromBlueprint()` 为 `protected` 成员，通常由引擎内部或通过 C++ 代码调用。统计结果更适合在编辑器日志、自定义编辑器工具或命令行报告中呈现，而非直接在蓝图图表中操作。

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IBlueprintStatsModule.h"

// 核心统计记录类（位于Private目录，如需使用请注意编译依赖）
#include "BlueprintStats.h" // 可能需要添加模块的Private路径
```

### 基本用法

`FBlueprintStatRecord` 是核心数据类，用于存储单个蓝图或聚合的统计数据。

```cpp
// 示例：为特定蓝图创建统计记录
UBlueprint* MyBlueprint = /* 获取蓝图对象 */;
FBlueprintStatRecord BlueprintRecord(MyBlueprint); // 构造时自动读取统计

// 获取统计数据
int32 NodeCount = BlueprintRecord.NumNodes;
int32 UserFunctions = BlueprintRecord.NumUserFunctions;
float ImpureRatio = (BlueprintRecord.ImpureFunctionNodes > 0) ?
    (float)BlueprintRecord.ImpureNodesWithInputsAndOutputs / BlueprintRecord.ImpureFunctionNodes : 0.0f;

// 输出到日志
UE_LOG(LogTemp, Log, TEXT("Blueprint: %s, Nodes: %d, Functions: %d"),
    *MyBlueprint->GetName(), NodeCount, UserFunctions);
BlueprintRecord.ToString(); // 可直接输出格式化字符串到日志
```

### 进阶用法

可以合并多个蓝图的统计信息，以分析整个文件夹或类别的蓝图集合。

```cpp
// 创建一个用于聚合的空记录
FBlueprintStatRecord AggregatedRecord;

// 合并多个蓝图的统计
for (UBlueprint* BP : AllBlueprintsToAnalyze)
{
    FBlueprintStatRecord SingleRecord(BP);
    AggregatedRecord.MergeAnotherRecordIn(SingleRecord);
}

// 分析聚合后的数据
UE_LOG(LogTemp, Log, TEXT("Aggregated Stats - Total Blueprints: %d, Total Nodes: %d"),
    AggregatedRecord.NumBlueprints, AggregatedRecord.NumNodes);
```

## Demo 示例

以下是一个完整的编辑器模块示例，演示如何为指定蓝图生成统计报告。

**BlueprintStatsDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FBlueprintStatsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // 为指定路径的蓝图资产生成统计报告
    void GenerateStatsForAsset(const FString& AssetPath);
};
```

**BlueprintStatsDemo.cpp**
```cpp
#include "BlueprintStatsDemo.h"
#include "IBlueprintStatsModule.h"
#include "BlueprintStats.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Engine/Blueprint.h"

#define LOCTEXT_NAMESPACE "FBlueprintStatsDemoModule"

void FBlueprintStatsDemoModule::StartupModule()
{
    // 可在此注册菜单项或控制台命令来触发统计
}

void FBlueprintStatsDemoModule::ShutdownModule()
{
}

void FBlueprintStatsDemoModule::GenerateStatsForAsset(const FString& AssetPath)
{
    if (!IBlueprintStatsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("BlueprintStats module is not available."));
        return;
    }

    // 通过资产注册表加载蓝图对象
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

    FAssetData AssetData = AssetRegistry.GetAssetByObjectPath(FSoftObjectPath(AssetPath));
    if (!AssetData.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Asset not found: %s"), *AssetPath);
        return;
    }

    UBlueprint* Blueprint = Cast<UBlueprint>(AssetData.GetAsset());
    if (!Blueprint)
    {
        UE_LOG(LogTemp, Error, TEXT("Asset is not a Blueprint: %s"), *AssetPath);
        return;
    }

    // 生成并输出统计记录
    FBlueprintStatRecord StatRecord(Blueprint);
    FString Report = StatRecord.ToString(/* bHeader = */ true);
    UE_LOG(LogTemp, Log, TEXT("Blueprint Stats Report:\n%s"), *Report);

    // 也可以直接访问成员变量进行自定义分析
    if (StatRecord.NumUserFunctions > 20)
    {
        UE_LOG(LogTemp, Warning, TEXT("Blueprint '%s' has a high number of user functions (%d). Consider refactoring."),
            *Blueprint->GetName(), StatRecord.NumUserFunctions);
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FBlueprintStatsDemoModule, BlueprintStatsDemo)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF，属于日志系统维护性更新 |
| 2024-01-12 | `56a32fea` | Silence false V621, V654, and V1078 warnings mostly caused by TStaticArray, placement new, or popula | 静默静态分析工具的误报警告，编译维护 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构批量更新，无实质功能变化 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内部链接为HTTPS，安全合规性修复 |

### 维护评价

BlueprintStats 是一个历史悠久（11年）的**实验性**插件，自创建以来一直保持 `EnabledByDefault: false` 状态。虽然其仓库记录显示最近几年仍有零星的提交，但这些更新几乎全部是**编译修复、日志迁移、静态分析警告处理等基础维护**，未见任何功能增强或改进。其核心代码结构（`FBlueprintStatRecord`）自始至终未发生改变。

综合来看，该插件处于 **“可能废弃”** 状态。它更像是一个早期开发过程中用于内部测试和研究的“原型”工具，其功能已被更强大、更集成的蓝图分析工具（如内置的蓝图分析器、性能剖析工具）所取代。**强烈不建议在新项目中依赖或启用此插件。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/BlueprintStats) (推测路径，原仓库中未明确提供)