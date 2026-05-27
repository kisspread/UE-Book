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
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats) | |

## 用途

BlueprintStats 是一个轻量级的蓝图分析工具，用于收集和统计项目中蓝图资产的各项指标。它能统计蓝图中的节点数量、函数数量（纯函数/非纯函数）、宏数量、仅数据蓝图数量等信息，并以文本形式输出统计报告。

这个插件解决的核心问题是：**在大型项目中，如何快速了解蓝图资产的复杂度和健康状况**。通过统计数据，开发者可以识别过于复杂的蓝图、发现不合理的节点使用模式，辅助进行蓝图优化和项目管理。

## 使用场景

- 你需要审查项目中蓝图的整体复杂度，找出节点过多的"巨型蓝图"
- 你想统计项目中纯函数 vs 非纯函数的使用比例，评估蓝图设计质量
- 你需要识别仅数据蓝图（Data-Only Blueprint）的数量，了解资产使用情况
- 你想生成蓝图资产的统计报告，用于项目里程碑回顾或代码审查

## 蓝图用法

此插件为纯 C++ 模块，不提供蓝图可调用节点。统计功能仅在编辑器中通过 C++ API 使用。

## C++ 用法

### 头文件引入

```cpp
#include "IBlueprintStatsModule.h"
#include "BlueprintStats.h"
```

### 基本用法

对单个蓝图进行统计分析（来源：`Source/BlueprintStats/Private/BlueprintStats.h`）：

```cpp
#include "BlueprintStats.h"

// 对单个蓝图收集统计数据
UBlueprint* MyBlueprint = /* 获取你的蓝图 */;
FBlueprintStatRecord Record(MyBlueprint);

// 输出统计信息
UE_LOG(LogTemp, Log, TEXT("蓝图统计:\n%s"), *Record.ToString());
```

`FBlueprintStatRecord` 构造时传入 `UBlueprint*` 会自动调用 `ReadStatsFromBlueprint()` 采集数据。传入 `nullptr` 则创建空记录，适合后续合并多个蓝图的统计。

### 进阶用法

合并多个蓝图的统计数据，生成汇总报告：

```cpp
#include "BlueprintStats.h"

// 创建一个空的汇总记录
FBlueprintStatRecord SummaryRecord(nullptr);

// 遍历所有蓝图并合并统计
for (UBlueprint* Blueprint : AllBlueprints)
{
    FBlueprintStatRecord SingleRecord(Blueprint);
    SummaryRecord.MergeAnotherRecordIn(SingleRecord);
}

// 输出表头 + 汇总数据（适合 CSV 导出）
FString Header = SummaryRecord.ToString(true);   // bHeader=true，输出列名
FString Data = SummaryRecord.ToString(false);     // 输出数据行

UE_LOG(LogTemp, Log, TEXT("%s\n%s"), *Header, *Data);
```

## Demo 示例

```cpp
// BlueprintStatReporter.h
#pragma once

#include "CoreMinimal.h"

class FBlueprintStatReporter
{
public:
    static void ReportAllBlueprints();
};
```

```cpp
// BlueprintStatReporter.cpp
#include "BlueprintStatReporter.h"
#include "BlueprintStats.h"
#include "Engine/Blueprint.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FBlueprintStatReporter::ReportAllBlueprints()
{
    // 通过资产注册表获取所有蓝图
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

    TArray<FAssetData> BlueprintAssets;
    AssetRegistry.GetAssetsByClass(UBlueprint::StaticClass()->GetClassPathName(), BlueprintAssets);

    // 创建汇总记录
    FBlueprintStatRecord Summary(nullptr);

    for (const FAssetData& Asset : BlueprintAssets)
    {
        UBlueprint* BP = Cast<UBlueprint>(Asset.GetAsset());
        if (BP)
        {
            FBlueprintStatRecord SingleRecord(BP);
            Summary.MergeAnotherRecordIn(SingleRecord);
        }
    }

    // 输出报告
    UE_LOG(LogTemp, Display, TEXT("=== 蓝图统计报告 ==="));
    UE_LOG(LogTemp, Display, TEXT("蓝图总数: %d"), Summary.NumBlueprints);
    UE_LOG(LogTemp, Display, TEXT("仅数据蓝图: %d"), Summary.NumDataOnlyBlueprints);
    UE_LOG(LogTemp, Display, TEXT("节点总数: %d"), Summary.NumNodes);
    UE_LOG(LogTemp, Display, TEXT("用户函数数: %d"), Summary.NumUserFunctions);
    UE_LOG(LogTemp, Display, TEXT("纯函数数: %d"), Summary.NumUserPureFunctions);
    UE_LOG(LogTemp, Display, TEXT("用户宏数: %d"), Summary.NumUserMacros);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2024-01-12 | `56a32fea` | Silence false V621, V654, and V1078 warnings mostly caused by TStaticArray, placement new, or popula | 静默静态分析器的误报警告 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量改动 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新供应商链接为安全协议 |
| 2020-08-14 | `48113fc7` | Adding EditorFramework to build.cs files | 在 Build.cs 中添加 EditorFramework 依赖 |

### 维护评价

⚠️ **此插件已长期无人维护，不推荐在新项目中使用。**

- 创建于 2014 年，至今已有约 12 年历史，属于"文物"级别插件
- 至少 6 年来没有任何功能性更新，最近的改动全部是编译兼容性和静态分析警告修复
- 作为 Experimental 插件且 `EnabledByDefault=false`，Epic 从未将其提升为正式功能
- 功能非常简陋（仅 4 个源文件），缺少现代蓝图分析工具（如 Unreal Insights）的深度
- 如果你需要蓝图统计功能，建议考虑 Unreal Insights 或自建分析工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BlueprintStats)（未发现独立测试文件）