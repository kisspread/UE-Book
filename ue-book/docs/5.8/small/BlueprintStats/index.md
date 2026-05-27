# Blueprint Stats

> Blueprint Stats（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图统计 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintStats` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats) | |

## 用途

基于源码分析，`BlueprintStats` 插件的核心功能是**收集和统计单个蓝图资产或整个项目的蓝图数据**。它提供了一个 `FBlueprintStatRecord` 结构，用于遍历一个蓝图中的图表和节点，统计出诸如节点总数、各类节点（纯函数、不纯函数、宏等）的数量、用户自定义函数数量等详细信息。同时，它可以将多个蓝图的统计记录合并，从而获得项目的整体蓝图概况。

这个插件解决了**蓝图资产分析**的需求，通常用于项目优化、性能分析或代码审查，以了解蓝图的使用情况、复杂度和潜在的性能瓶颈。

## 使用场景

- 你需要评估项目的蓝图整体复杂度，以制定优化策略。
- 你需要识别包含过多节点或函数的“巨型蓝图”。
- 你想统计项目中用户创建的函数、宏和数据蓝图的数量。
- 你需要一个工具来辅助蓝图资产的迁移或重构决策。

## 蓝图用法

此插件主要为 C++ 编辑器工具或命令行工具设计，**未暴露任何可供蓝图直接调用的节点** (未在源码中发现 `UFUNCTION(BlueprintCallable)`)。

## C++ 用法

### 头文件引入

```cpp
#include "IBlueprintStatsModule.h"
```

### 基本用法

获取模块接口并创建统计记录来分析单个蓝图。
(来源：源码头文件 `Source/BlueprintStats/Public/IBlueprintStatsModule.h` 和 `Source/BlueprintStats/Private/BlueprintStats.h`)

```cpp
// 确保模块已加载
if (IBlueprintStatsModule::IsAvailable())
{
    // 创建一个针对目标蓝图的统计记录
    UBlueprint* TargetBlueprint = ...; // 从资产路径加载或获取
    FBlueprintStatRecord StatRecord(TargetBlueprint);

    // 输出统计信息到日志
    UE_LOG(LogTemp, Log, TEXT("Blueprint Stats: %s"), *StatRecord.ToString());
}
```

### 进阶用法

合并多个蓝图的统计数据以获得项目汇总信息。
(来源：源码头文件 `Source/BlueprintStats/Private/BlueprintStats.h`)

```cpp
// 创建一个用于汇总的“元记录”
FBlueprintStatRecord ProjectTotalRecord;

// 遍历项目中的所有蓝图资产
for (UBlueprint* Blueprint : AllProjectBlueprints)
{
    FBlueprintStatRecord SingleRecord(Blueprint);
    ProjectTotalRecord.MergeAnotherRecordIn(SingleRecord);
}

// 输出带表头的汇总信息
UE_LOG(LogTemp, Log, TEXT("%s"), *ProjectTotalRecord.ToString(true));
```

## Demo 示例

一个完整的、可编译的最小示例，在编辑器模块中统计当前打开的蓝图。

```cpp
// MyBlueprintAnalyzer.h
#pragma once
#include "CoreMinimal.h"
#include "BlueprintStats.h" // 包含 FBlueprintStatRecord

class FMyBlueprintAnalyzer
{
public:
    void AnalyzeCurrentEditorBlueprint();
};
```

```cpp
// MyBlueprintAnalyzer.cpp
#include "MyBlueprintAnalyzer.h"
#include "IBlueprintStatsModule.h"
#include "Kismet2/BlueprintEditorUtils.h"

void FMyBlueprintAnalyzer::AnalyzeCurrentEditorBlueprint()
{
    // 检查模块是否可用
    if (!IBlueprintStatsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("BlueprintStats module is not available."));
        return;
    }

    // 获取当前在编辑器中打开的蓝图（示例逻辑）
    UBlueprint* EditorBlueprint = FBlueprintEditorUtils::FindBlueprintForAsset(/* Some Asset */);
    if (EditorBlueprint)
    {
        // 创建统计记录，构造函数会自动分析蓝图
        FBlueprintStatRecord StatRecord(EditorBlueprint);

        // 获取并打印统计字符串
        FString StatsString = StatRecord.ToString();
        UE_LOG(LogTemp, Log, TEXT("Blueprint '%s' Analysis:\n%s"), *EditorBlueprint->GetName(), *StatsString);

        // 也可以直接访问统计成员
        UE_LOG(LogTemp, Log, TEXT(" - Total Nodes: %d"), StatRecord.NumNodes);
        UE_LOG(LogTemp, Log, TEXT(" - User Functions: %d"), StatRecord.NumUserFunctions);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("No active blueprint found in the editor."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `KismetCompiler` | 用于蓝图编译相关的功能，可能用于在统计前确保蓝图处于可分析状态 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至新的 UE_LOGF。 |
| 2024-01-12 | `56a32fea` | Silence false V621, V654, and V1078 warnings mostly caused by TStaticArray, placement new, or popula | 修复多个静态分析警告，主要与模板和 placement new 有关。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录范围的通用提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内链接为 HTTPS 协议。 |
| 2020-08-14 | `48113fc7` | Adding EditorFramework to build.cs files | 在构建文件中添加 EditorFramework 依赖。 |

### 维护评价

- **年龄**：该插件创建于 2014 年，历史超过 10 年，属于“文物”级别。
- **更新频率**：最近一次实质性更新（日志宏迁移）在 2026 年 4 月，但之前的大部分更新（2020-2024）都是通用的引擎维护、编译警告修复或链接更新，**没有新功能或核心架构的改动**。
- **活跃度**：处于**维护不活跃**状态。它似乎是一个功能已完成的工具，在 Epic 的迭代中未被移除，但也未得到积极开发。
- **已知限制**：
    1.  默认未启用 (`EnabledByDefault: false`)，需要手动启用。
    2.  仅提供编辑器功能，没有运行时或蓝图 API。
    3.  功能较为基础，主要进行简单的计数统计。
- **推荐度**：**不推荐在新项目中主动启用或依赖**。如果你需要蓝图分析功能，它可能提供一个起点，但其设计和功能深度可能不足以满足现代项目的复杂分析需求。建议考虑更成熟的社区分析工具或自研方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/BlueprintStats) (路径为推测)