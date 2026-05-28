# Memory Usage Queries

> Memory Usage Queries, original contribution from The Coalition (Microsoft) https://thecoalitionstudio.com

| 属性 | 值 |
|---|---|
| 中文名 | 内存使用查询 |
| 分类 | Engine |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MemoryUsageQueries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-01-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MemoryUsageQueries) | |

## 用途

该插件提供了一套运行时内存查询工具，用于精确分析和报告已加载资产（Assets）及其相关类（Classes）的内存占用情况。其核心是通过 `IMemoryUsageInfoProvider` 接口（默认实现基于低级内存追踪器 LLM）查询内存数据，支持按资产、类、分组（LLM Groups）进行过滤、聚合（如独占、共享、公共大小）以及依赖关系分析。它解决了在复杂项目中定位内存热点、分析资源内存占用结构以及评估卸载特定资源对内存影响的问题，是性能和内存优化的利器。

## 使用场景

- 你的游戏在运行时出现内存压力，需要找出哪些资产（纹理、模型、音频等）占用内存最多。
- 你需要分析一组关联资产（如一个角色的所有资源）的总内存占用，并区分其中哪些内存是独占的，哪些是与其他资产共享的。
- 你正在规划资源包（Chunk）或流式加载策略，需要了解卸载某个资产后，其依赖的哪些其他资产可以被安全回收。
- 你需要按资产类别（UClass）或 LLM 定义的内存分组来汇总内存使用，以评估不同类型资产的内存开销。
- 你需要在运行时或编辑器工具中提供详细的内存使用报告。

## 蓝图用法

该插件主要提供 C++ API，未发现标记为 `BlueprintCallable` 的函数。其功能主要通过 C++ 代码在运行时工具、分析命令或自定义编辑器面板中集成使用。

## C++ 用法

### 头文件引入

```cpp
#include "MemoryUsageQueries.h"
#include "MemoryUsageInfoProvider.h"
```

### 基本用法

查询单个或多个资产的内存占用信息。`IMemoryUsageInfoProvider` 的默认实现通常在启动时已创建。

```cpp
// 假设已获取 IMemoryUsageInfoProvider* Provider
// 例如：const IMemoryUsageInfoProvider* Provider = MemoryUsageQueries::GetCurrentMemoryUsageInfoProvider();

if (Provider && Provider->IsProviderAvailable())
{
    // 查询单个资产的内存使用（独占和共享）
    const FName AssetName = TEXT("/Game/Characters/Hero/Textures/T_Hero_D");
    uint64 ExclusiveSize = 0;
    uint64 InclusiveSize = 0;
    MemoryUsageQueries::GetMemoryUsage(Provider, AssetName, ExclusiveSize, InclusiveSize);
    UE_LOG(LogTemp, Log, TEXT("Asset %s: Exclusive=%llu, Inclusive=%llu"), *AssetName.ToString(), ExclusiveSize, InclusiveSize);

    // 查询多个资产的组合内存使用
    TArray<FName> AssetNames = {
        TEXT("/Game/Characters/Hero/SK_Hero"),
        TEXT("/Game/Characters/Hero/Textures/T_Hero_N")
    };
    uint64 TotalCombinedSize = 0;
    MemoryUsageQueries::GetMemoryUsageCombined(Provider, AssetNames, TotalCombinedSize);
    UE_LOG(LogTemp, Log, TEXT("Combined size of assets: %llu"), TotalCombinedSize);
}
```

### 进阶用法

分析资产依赖关系及其内存开销，或利用 LLM 过滤查询。

```cpp
// 分析一个资产的依赖项及其内存大小
TMap<FName, uint64> DependenciesWithSize;
MemoryUsageQueries::GetDependenciesWithSize(Provider, AssetName, DependenciesWithSize);

for (const auto& Pair : DependenciesWithSize)
{
    UE_LOG(LogTemp, Log, TEXT("Dependency: %s, Size: %llu"), *Pair.Key.ToString(), Pair.Value);
}

#if ENABLE_LOW_LEVEL_MEM_TRACKER
// 使用 LLM 数据按组名和资产名模式过滤内存包
TMap<FName, uint64> FilteredPackages;
FName GroupName = TEXT("Textures"); // LLM 分组名
FString AssetSubstring = TEXT("T_Hero_");
if (MemoryUsageQueries::GetFilteredPackagesWithSize(FilteredPackages, GroupName, AssetSubstring))
{
    // 处理过滤后的结果
}
#endif
```

## Demo 示例

一个查询并打印特定资产内存使用信息的最小示例。

```cpp
// MyMemoryAnalyzer.h
#pragma once

#include "CoreMinimal.h"

class FMyMemoryAnalyzer
{
public:
    static void AnalyzeAndPrintMemory();
};
```

```cpp
// MyMemoryAnalyzer.cpp
#include "MyMemoryAnalyzer.h"
#include "MemoryUsageQueries.h"
#include "MemoryUsageInfoProvider.h"

void FMyMemoryAnalyzer::AnalyzeAndPrintMemory()
{
    const IMemoryUsageInfoProvider* Provider = MemoryUsageQueries::GetCurrentMemoryUsageInfoProvider();
    if (!Provider || !Provider->IsProviderAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Memory usage info provider is not available."));
        return;
    }

    const FName AssetToAnalyze = TEXT("/Game/Maps/PrototypeMap");
    uint64 ExclusiveSize = 0;
    uint64 InclusiveSize = 0;
    MemoryUsageQueries::GetMemoryUsage(Provider, AssetToAnalyze, ExclusiveSize, InclusiveSize);

    UE_LOG(LogTemp, Display, TEXT("=== Memory Analysis for %s ==="), *AssetToAnalyze.ToString());
    UE_LOG(LogTemp, Display, TEXT("Exclusive Memory: %llu bytes (%.2f MB)"), ExclusiveSize, ExclusiveSize / (1024.0 * 1024.0));
    UE_LOG(LogTemp, Display, TEXT("Inclusive Memory: %llu bytes (%.2f MB)"), InclusiveSize, InclusiveSize / (1024.0 * 1024.0));
    UE_LOG(LogTemp, Display, TEXT("Shared Memory (with deps): %llu bytes"), InclusiveSize - ExclusiveSize);

    // 分析依赖
    TMap<FName, uint64> Dependencies;
    MemoryUsageQueries::GetDependenciesWithSize(Provider, AssetToAnalyze, Dependencies);
    UE_LOG(LogTemp, Display, TEXT("Dependencies (%d):"), Dependencies.Num());
    for (const auto& Dep : Dependencies)
    {
        UE_LOG(LogTemp, Display, TEXT("  - %s: %llu bytes"), *Dep.Key.ToString(), Dep.Value);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件依赖引擎内置的低级内存追踪器（LLM）功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-27 | `7a525ad7` | Fixed occurrences of using LLM_SCOPE instead of LLM_SCOPE_BYNAME. This fixes unnecessary constructio | 修复了使用错误的LLM作用域宏，避免了不必要的构造开销。 |
| 2025-07-27 | `bd4ed858` | * Removed bAllowConfidentialPlatformDefines from modules because they don’t need it (android and ios | 移除了模块中不必要的 `bAllowConfidentialPlatformDefines` 配置。 |
| 2025-05-30 | `711eddbe` | Added missing Greater.h include. | 添加了缺失的 `Greater.h` 头文件包含。 |
| 2025-05-29 | `8cfef610` | Added Greater.h include to files which use TGreater, which will break with an upcoming change to rem | 为使用 `TGreater` 的文件添加头文件包含，以适配即将到来的引擎变更。 |
| 2025-05-20 | `c1d4eecb` | Replaced bool arguments with EFindObjectFlags. | 使用枚举标志替换了布尔函数参数，接口更清晰。 |

### 维护评价

该插件创建于 2023 年初，最近一次更新（2026年1月）是代码健壮性修复。虽然更新频率不高，但最近一年内仍有维护活动，主要涉及编译兼容性和代码清理，表明插件仍在维护中，以适应引擎的演进。该插件提供了一套稳定且功能明确的内存查询API，对于需要精细内存分析的项目（尤其是主机或移动端优化）非常有用。考虑到其基础功能稳定且更新及时，**推荐在需要运行时内存分析时使用此插件**。需要手动在 `.uproject` 或编辑器中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MemoryUsageQueries)
- [官方文档]() (无)
- [测试用例]() (未在插件目录内发现公开测试用例)