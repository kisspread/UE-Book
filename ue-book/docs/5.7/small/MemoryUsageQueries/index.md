# MemoryUsageQueries

> Memory Usage Queries, original contribution from The Coalition (Microsoft) https://thecoalitionstudio.com

| 属性 | 值 |
|---|---|
| 分类 | MemoryUsageQueries |
| 默认启用 | ❌ 否 |
| 包含内容 | 否 |
| 模块 | MemoryUsageQueries (Runtime) |
| 创建时间 | 2023-01-06 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/MemoryUsageQueries) | |

## 用途

MemoryUsageQueries 是一个基于 **Low Level Memory Tracker (LLM)** 的资产内存分析工具。它解决了 UE5 中一个核心痛点：**如何精确知道每个资产（Asset）及其依赖链占用了多少内存？**

这个 plugin 由 The Coalition（微软旗下，开发《战争机器》的工作室）贡献给 Epic，说明它在大型项目的内存优化中经过了实战验证。

核心能力：
- 查询单个或多个资产的内存占用（独占 / 包含依赖的总内存）
- 分析多个资产之间的依赖关系，区分**共享依赖**和**独占依赖**
- 通过 GC 可达性分析判断哪些依赖是**可释放的**（removable），哪些是**不可释放的**
- 按 LLM Group / Class / Category 筛选和汇总资产内存
- 支持通过 ini 配置定义资产集合（Collection），方便团队统一管理内存预算

> ⚠️ **前提条件**：必须以 `-LLM` 命令行参数启动引擎，否则所有查询将失败并报错 `"Provider is not available. Please run with -LLM"`。

## 使用场景

- 你在做大型开放世界游戏，需要知道一个关卡加载时实际占用多少内存 → 用 `MemQuery.CombinedUsage`
- 你发现内存超标，想知道某个角色蓝图的依赖链中哪个资产最占内存 → 用 `MemQuery.Dependencies`
- 你想判断卸载一组资产能释放多少内存（考虑其他地方还在引用的情况）→ 用 `MemQuery.UniqueUsage`
- 你想按路径模式（如 `*/Character*/*`）批量查看一类资产的内存占用 → 用 `MemQuery.Collection`
- 你想分析某个类的所有蓝图子类中哪些可以删除以节省内存 → 用 `MemQuery.Savings`

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。它完全通过控制台命令和 C++ API 使用。

## 控制台命令

所有命令都以 `MemQuery.` 开头，在运行时控制台中输入。所有命令都支持以下通用参数：

| 参数 | 说明 |
|---|---|
| `Log=<文件名>` | 将输出写入文件（保存到 Profiling/MemQuery/ 目录） |
| `csv` | 以 CSV 格式输出 |
| `notrunc` | 不截断结果列表 |
| `Limit=<n>` | 限制显示条数（默认 15） |

### 内存用量查询

| 命令 | 参数 | 说明 |
|---|---|---|
| `MemQuery.Usage` | `Name=<资产名>` | 查询单个资产的 Exclusive（独占）和 Inclusive（含依赖）内存 |
| `MemQuery.CombinedUsage` | `Names="<资产1> <资产2> ..."` | 查询多个资产合并后的总内存（含所有依赖的并集） |
| `MemQuery.SharedUsage` | `Names="<资产1> <资产2> ..."` | 查询多个资产的**共享**依赖内存 |
| `MemQuery.UniqueUsage` | `Names="<资产1> <资产2> ..."` | 查询多个资产的**独占**依赖内存（GC 可释放的部分） |
| `MemQuery.CommonUsage` | `Names="<资产1> <资产2> ..."` | 查询多个资产的**公共**依赖内存（不可被 GC 释放的部分） |

### 依赖分析

| 命令 | 参数 | 说明 |
|---|---|---|
| `MemQuery.Dependencies` | `Name=<资产名> Limit=<n>` | 列出单个资产的所有依赖，按大小排序 |
| `MemQuery.CombinedDependencies` | `Names="..." Limit=<n>` | 列出多个资产的合并依赖 |
| `MemQuery.SharedDependencies` | `Names="..." Limit=<n>` | 仅列出多个资产**共有**的依赖 |
| `MemQuery.UniqueDependencies` | `Names="..." Limit=<n>` | 仅列出多个资产**独占**的依赖 |
| `MemQuery.CommonDependencies` | `Names="..." Limit=<n>` | 仅列出**不可释放**的依赖 |

### LLM 筛选（需启用 LLM）

| 命令 | 参数 | 说明 |
|---|---|---|
| `MemQuery.ListAssets` | `Asset=<子串> Group=<组名> Class=<类名>` | 列出按大小排序的资产内存占用 |
| `MemQuery.ListAssetsCategorized` | 同上 + `Category=<Assets/AssetClasses>` | 按分类列出资产内存 |
| `MemQuery.ListClasses` | `Group=<组名> Asset=<资产名>` | 列出按大小排序的资产类内存占用 |
| `MemQuery.ListGroups` | `Asset=<资产名> Class=<类名>` | 列出按大小排序的 LLM 组内存占用 |

### 集合与预算

| 命令 | 参数 | 说明 |
|---|---|---|
| `MemQuery.Collection` | `<集合名> -showdeps` | 显示 ini 中配置的资产集合的内存使用情况，`-showdeps` 可显示依赖明细 |
| `MemQuery.Savings` | `<预设名> Limit=<n>` | 分析某个类的蓝图子类中，删除哪些可以节省内存 |

### 使用示例

查看单个资产内存：
```
MemQuery.Usage Name=/Game/Characters/Hero
```

查看两个资产的独占内存（卸载后可释放的部分）：
```
MemQuery.UniqueUsage Names="/Game/Maps/Level1 /Game/Maps/Level2"
```

列出最大的 20 个角色资产：
```
MemQuery.ListAssets Asset=/Game/Characters/ Limit=20
```

将结果输出为 CSV 文件：
```
MemQuery.ListAssets csv Log=AssetSizes
```

## C++ 用法

### 头文件引入

```cpp
#include "MemoryUsageQueries.h"            // 核心查询函数
#include "MemoryUsageInfoProvider.h"       // IMemoryUsageInfoProvider 接口
#include "MemoryUsageQueriesConfig.h"      // Collection/Savings 配置
```

### 前置条件

所有查询都需要一个 `IMemoryUsageInfoProvider`，通过以下方式获取：

```cpp
const IMemoryUsageInfoProvider* Provider = MemoryUsageQueries::GetCurrentMemoryUsageInfoProvider();
if (!Provider || !Provider->IsProviderAvailable())
{
    // LLM 未启用，无法查询
    return;
}
```

### 查询单个资产内存

```cpp
FName PackageName(TEXT("/Game/Characters/Hero"));
uint64 ExclusiveSize = 0;
uint64 InclusiveSize = 0;

// Exclusive: 仅该资产自身占用
// Inclusive: 该资产 + 所有传递依赖的总占用
MemoryUsageQueries::GetMemoryUsage(Provider, PackageName, ExclusiveSize, InclusiveSize);
```

### 查询多个资产的合并内存

```cpp
TArray<FName> PackageNames = {
    FName(TEXT("/Game/Maps/Level1")),
    FName(TEXT("/Game/Maps/Level2"))
};

uint64 CombinedSize = 0;   // 所有依赖的并集
uint64 SharedSize = 0;     // 共有依赖
uint64 UniqueSize = 0;     // 独占依赖（可释放）
uint64 CommonSize = 0;     // 不可释放的依赖

MemoryUsageQueries::GetMemoryUsageCombined(Provider, PackageNames, CombinedSize);
MemoryUsageQueries::GetMemoryUsageShared(Provider, PackageNames, SharedSize);
MemoryUsageQueries::GetMemoryUsageUnique(Provider, PackageNames, UniqueSize);
MemoryUsageQueries::GetMemoryUsageCommon(Provider, PackageNames, CommonSize);
```

### 获取依赖详情（带大小）

```cpp
FName PackageName(TEXT("/Game/Characters/Hero"));
TMap<FName, uint64> DependenciesWithSize;

// 返回该资产所有依赖，按大小降序排列
MemoryUsageQueries::GetDependenciesWithSize(Provider, PackageName, DependenciesWithSize);

for (const auto& [DepName, Size] : DependenciesWithSize)
{
    UE_LOG(LogTemp, Log, TEXT("  %s: %.2f MB"), *DepName.ToString(), Size / (1024.0f * 1024.0f));
}
```

### 收集可释放 / 不可释放依赖

```cpp
TArray<FName> PackageNames = { FName(TEXT("/Game/Maps/Level1")) };
TMap<FName, uint64> InternalDeps;  // 可释放（removable）
TMap<FName, uint64> ExternalDeps;  // 不可释放（non-removable）

MemoryUsageQueries::GatherDependenciesForPackages(
    Provider, PackageNames, InternalDeps, ExternalDeps,
    MemoryUsageQueries::EDependencyType::EDep_All
);
```

`EDependencyType` 枚举值：
- `EDep_All` — 同时返回可释放和不可释放依赖
- `EDep_Removable` — 仅返回可释放依赖
- `EDep_NonRemovable` — 仅返回不可释放依赖

### LLM 筛选查询

```cpp
#if ENABLE_LOW_LEVEL_MEM_TRACKER
TMap<FName, uint64> AssetsWithSize;

// 按 Group、Class、Asset 名称筛选
MemoryUsageQueries::GetFilteredPackagesWithSize(
    AssetsWithSize,
    FName(TEXT("Meshes")),           // Group 过滤（可选）
    TEXT("/Game/Characters/Hero"),   // Asset 名称子串过滤（可选）
    FName(TEXT("SkeletalMesh"))      // Class 过滤（可选）
);

TMap<FName, uint64> ClassesWithSize;
MemoryUsageQueries::GetFilteredClassesWithSize(ClassesWithSize);

TMap<FName, uint64> GroupsWithSize;
MemoryUsageQueries::GetFilteredGroupsWithSize(GroupsWithSize);
#endif
```

## 配置：Collection 与 Savings Preset

在项目的 `Config/DefaultMemoryUsageQueries.ini` 中配置。

### Collection（资产集合）

按路径模式定义一组资产，支持通配符：

```ini
[/Script/MemoryUsageQueries.MemoryUsageQueriesConfig]
; 收集所有 Character 和 Pawn 路径下的资产，排除 Item 路径
+Collections = (Name="Pawns", Includes=("/Character/", "/Pawn/"), Excludes=("/Item*/"))

; 带内存预算（单位 MB）
+Collections = (Name="Weapons", Includes=("/Weapons/"), BudgetMB=50.0)
```

然后通过控制台查询：
```
MemQuery.Collection Pawns
MemQuery.Collection Pawns -showdeps
```

### Savings Preset（节省分析预设）

定义一个基类，分析其所有叶子蓝图子类的内存占用：

```ini
[/Script/MemoryUsageQueries.MemoryUsageQueriesConfig]
+SavingsPresets = (Key="Pawns", Value="/Script/OurProject.OurCharacter")
```

然后通过控制台查询：
```
MemQuery.Savings Pawns
```

## Demo 示例

### 最小示例：查询资产内存

```cpp
// MyMemoryAnalyzer.h
#pragma once
#include "CoreMinimal.h"

class FMyMemoryAnalyzer
{
public:
    static void AnalyzeAsset(const FString& AssetPath);
    static void CompareAssets(const TArray<FString>& AssetPaths);
};
```

```cpp
// MyMemoryAnalyzer.cpp
#include "MyMemoryAnalyzer.h"
#include "MemoryUsageQueries.h"
#include "MemoryUsageInfoProvider.h"

void FMyMemoryAnalyzer::AnalyzeAsset(const FString& AssetPath)
{
    const IMemoryUsageInfoProvider* Provider = MemoryUsageQueries::GetCurrentMemoryUsageInfoProvider();
    if (!Provider || !Provider->IsProviderAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("LLM not enabled. Launch with -LLM flag."));
        return;
    }

    FName PackageName(*AssetPath);
    uint64 Exclusive = 0, Inclusive = 0;
    MemoryUsageQueries::GetMemoryUsage(Provider, PackageName, Exclusive, Inclusive);

    UE_LOG(LogTemp, Log, TEXT("%s: Exclusive=%.2f MB, Inclusive=%.2f MB"),
        *AssetPath,
        Exclusive / (1024.0f * 1024.0f),
        Inclusive / (1024.0f * 1024.0f));
}

void FMyMemoryAnalyzer::CompareAssets(const TArray<FString>& AssetPaths)
{
    const IMemoryUsageInfoProvider* Provider = MemoryUsageQueries::GetCurrentMemoryUsageInfoProvider();
    if (!Provider || !Provider->IsProviderAvailable())
    {
        return;
    }

    TArray<FName> PackageNames;
    for (const FString& Path : AssetPaths)
    {
        PackageNames.Add(FName(*Path));
    }

    uint64 Combined = 0, Shared = 0, Unique = 0;
    MemoryUsageQueries::GetMemoryUsageCombined(Provider, PackageNames, Combined);
    MemoryUsageQueries::GetMemoryUsageShared(Provider, PackageNames, Shared);
    MemoryUsageQueries::GetMemoryUsageUnique(Provider, PackageNames, Unique);

    UE_LOG(LogTemp, Log, TEXT("Combined=%.2f MB, Shared=%.2f MB, Unique=%.2f MB"),
        Combined / (1024.0f * 1024.0f),
        Shared / (1024.0f * 1024.0f),
        Unique / (1024.0f * 1024.0f));
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "MemoryUsageQueries"
});
```

> 注意：运行时需要以 `-LLM` 参数启动引擎才能获取数据。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统、GC、包管理 |
| `AssetRegistry` | 资产注册表查询（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `EngineSettings` | 引擎设置（私有依赖） |
| `PakFile` | Pak 文件和 IoStore 包存储查询（私有依赖） |

如果你的模块要使用 MemoryUsageQueries 的 C++ API，只需依赖 `MemoryUsageQueries` 模块即可（它已公开依赖 `Core` 和 `CoreUObject`）。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-27 | `bd4ed85` | 移除模块中不必要的 `bAllowConfidentialPlatformDefines`（构建配置清理，非功能变更） |
| 2025-05-30 | `711eddb` | 补充缺失的 `Greater.h` include（修复编译） |
| 2025-05-29 | `8cfef61` | 预先添加 `Greater.h` include 以适配即将到来的头文件变更 |

### 维护评价

- **创建时间**：2023 年 1 月，约 3 年历史，属于较新的 plugin
- **活跃度**：最近一次实质性功能更新在 2023 年初（初始提交），2025 年的更新均为编译修复，无新功能
- **稳定性**：API 在 5.6 中经历了一次清理（大量 `FString` 参数版本标记为 `UE_DEPRECATED`，推荐使用 `FName` 版本），说明 Epic 在积极维护接口质量
- **风险**：plugin 本身功能稳定且依赖 LLM 基础设施（这是引擎核心组件），短期内不太可能被废弃
- **推荐**：✅ 推荐使用。对于任何需要运行时内存分析的项目来说，这是 UE5 内置的最佳工具。唯一的门槛是需要启用 LLM（`-LLM` 标志），这会带来少量性能开销。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MemoryUsageQueries)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [The Coalition 工作室](https://thecoalitionstudio.com) — 原始贡献者
