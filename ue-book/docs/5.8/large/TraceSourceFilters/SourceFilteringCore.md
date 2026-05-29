# Insights Data Source Filters

> Source data filtering for Unreal Insights.

| 属性 | 值 |
|---|---|
| 中文名 | 数据源过滤器 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SourceFilteringCore` (Runtime), `SourceFilteringTrace` (Runtime), `SourceFilteringEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-05-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering) | |

## 用途

这个插件为 Unreal Insights 提供数据源过滤功能。它解决的核心问题是：在复杂的游戏世界中，Unreal Insights 的追踪（Trace）系统会记录海量的 Actor 数据，导致性能分析界面充斥着大量无关信息，干扰关键性能瓶颈的定位。通过这个插件，开发者可以定义过滤规则，有选择性地只追踪特定类型的 Actor，从而在 Insights 中只看到真正关心的性能数据，提高分析效率。

## 使用场景

- **性能分析时聚焦特定对象**：当你正在分析一个拥有数百个 Actor 的开放世界场景时，你可能只关心玩家角色和 AI 敌人。使用此插件，你可以配置过滤器，让 Insights 只记录这两个类及其子类的性能数据，过滤掉静态网格体、粒子效果等无关对象。
- **网络模式调试**：在多人游戏中调试网络问题时，你可以创建一个过滤器，只追踪带有特定网络角色（如 PlayerController）的 Actor，从而在 Insights 中清晰地观察网络相关的性能开销。
- **简化异步加载分析**：在分析异步加载过程时，你可以设置过滤器，只追踪在特定关卡流中需要加载的 Actor，避免被其他关卡的干扰信息分散注意力。

## 蓝图用法

此插件主要通过定义数据源过滤器类来工作。核心蓝图功能在于自定义过滤器的显示文本和配置属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Display Text` | 返回过滤器在 Insights UI 中显示的文本。 | `IDataSourceFilterInterface` |
| `Get Tool Tip Text` | 返回过滤器在 Insights UI 中的工具提示文本。 | `IDataSourceFilterInterface` |
| `Filter Applying Tick Interval` | （属性）配置过滤器应用的帧间隔，用于控制过滤频率。 | `FDataSourceFilterConfiguration` |

### 使用示例（蓝图描述）

1.  **创建过滤器类**：在 C++ 中创建一个新类，继承自 `UDataSourceFilter`（注意：该基类在插件的其他模块中定义，此处仅为概念说明），并实现 `IDataSourceFilterInterface` 接口。
2.  **实现接口函数**：覆盖 `GetDisplayText` 和 `GetToolTipText` 函数，在蓝图中为它们提供具体的显示文本，例如“只追踪玩家角色”。
3.  **配置过滤器**：在编辑器中，你可以为这个过滤器类的实例设置 `FDataSourceFilterConfiguration` 属性，例如调整 `FilterApplyingTickInterval` 来每 2 帧应用一次过滤，以平衡精确度和性能。
4.  **应用到世界**：在游戏世界的某个设置面板（由 `SourceFilteringEditor` 模块提供）中，将你创建的过滤器添加到过滤器集合中，并设置集合的逻辑模式（AND/OR/NOT）。

## C++ 用法

使用此插件的核心是实现 `IDataSourceFilterInterface` 接口，并创建过滤器管理逻辑。

### 头文件引入

```cpp
#include "IDataSourceFilterInterface.h"
#include "DataSourceFiltering.h"
```

### 基本用法

定义一个简单的数据源过滤器类。

```cpp
// 来源: 概念性代码，基于 Public/IDataSourceFilterInterface.h
UCLASS()
class UMyActorFilter : public UObject, public IDataSourceFilterInterface
{
    GENERATED_BODY()

public:
    // IDataSourceFilterInterface 接口实现
    virtual void GetDisplayText_Implementation(FText& OutDisplayText) const override
    {
        OutDisplayText = NSLOCTEXT("MyActorFilter", "DisplayName", "仅追踪玩家角色");
    }

    virtual void GetToolTipText_Implementation(FText& OutDisplayText) const override
    {
        OutDisplayText = NSLOCTEXT("MyActorFilter", "ToolTip", "过滤掉所有非玩家角色的 Actor。");
    }

    virtual const FDataSourceFilterConfiguration& GetConfiguration() const override
    {
        return Configuration;
    }

    virtual void SetEnabled(bool bState) override
    {
        bIsEnabled = bState;
    }

    virtual bool IsEnabled() const override
    {
        return bIsEnabled;
    }

private:
    UPROPERTY()
    FDataSourceFilterConfiguration Configuration;
    
    bool bIsEnabled = true;
};
```

### 进阶用法

结合过滤器集合接口 `IDataSourceFilterSetInterface` 来管理多个过滤器的逻辑。

```cpp
// 来源: 概念性代码，基于 Public/IDataSourceFilterSetInterface.h 和 DataSourceFiltering.h
// 创建一个过滤器集合，使用 AND 模式，即 Actor 必须通过集合内所有过滤器
UCLASS()
class UMyFilterSet : public UObject, public IDataSourceFilterSetInterface
{
    GENERATED_BODY()

public:
    virtual EFilterSetMode GetFilterSetMode() const override
    {
        return FilterMode;
    }

    // 添加过滤器到集合
    void AddFilter(UDataSourceFilterInterface* Filter)
    {
        Filters.Add(Filter);
    }

    // 对一个Actor执行过滤
    bool ApplyFilters(AActor* Actor) const
    {
        if (FilterMode == EFilterSetMode::AND)
        {
            for (const auto& Filter : Filters)
            {
                if (Filter && Filter->IsEnabled() && !CheckActorAgainstFilter(Actor, Filter))
                {
                    return false; // Actor 未通过某个过滤器
                }
            }
            return true; // Actor 通过了所有过滤器
        }
        // ... 实现 OR 和 NOT 逻辑
        return true;
    }

private:
    UPROPERTY()
    EFilterSetMode FilterMode = EFilterSetMode::AND;

    UPROPERTY()
    TArray<TObjectPtr<UDataSourceFilterInterface>> Filters;

    bool CheckActorAgainstFilter(AActor* Actor, UDataSourceFilterInterface* Filter) const
    {
        // 具体的过滤逻辑，例如根据 FActorClassFilter 进行检查
        // 这里需要根据插件其他模块定义的 Filter 类型来实现
        return true;
    }
};
```

## Demo 示例

以下是一个最小可编译的过滤器示例，它实现了 `IDataSourceFilterInterface` 接口。

```cpp
// MySimpleFilter.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "IDataSourceFilterInterface.h"
#include "MySimpleFilter.generated.h"

UCLASS(Blueprintable)
class UMySimpleFilter : public UObject, public IDataSourceFilterInterface
{
    GENERATED_BODY()

public:
    UMySimpleFilter();
    
    // IDataSourceFilterInterface 接口
    virtual void GetDisplayText_Implementation(FText& OutDisplayText) const override;
    virtual void GetToolTipText_Implementation(FText& OutDisplayText) const override;
    virtual const FDataSourceFilterConfiguration& GetConfiguration() const override;
    virtual void SetEnabled(bool bState) override;
    virtual bool IsEnabled() const override;

private:
    UPROPERTY()
    FDataSourceFilterConfiguration Configuration;
    
    bool bEnabled;
};
```

```cpp
// MySimpleFilter.cpp
#include "MySimpleFilter.h"

UMySimpleFilter::UMySimpleFilter()
{
    bEnabled = true;
    Configuration.bOnlyApplyDuringActorSpawn = false;
    Configuration.bCanRunAsynchronously = true;
    Configuration.FilterApplyingTickInterval = 5;
}

void UMySimpleFilter::GetDisplayText_Implementation(FText& OutDisplayText) const
{
    OutDisplayText = NSLOCTEXT("MySimpleFilter", "DisplayName", "我的简单过滤器");
}

void UMySimpleFilter::GetToolTipText_Implementation(FText& OutDisplayText) const
{
    OutDisplayText = NSLOCTEXT("MySimpleFilter", "ToolTip", "一个用于演示的基础过滤器。");
}

const FDataSourceFilterConfiguration& UMySimpleFilter::GetConfiguration() const
{
    return Configuration;
}

void UMySimpleFilter::SetEnabled(bool bState)
{
    bEnabled = bState;
}

bool UMySimpleFilter::IsEnabled() const
{
    return bEnabled;
}
```

## 模块依赖

要使用此插件的功能，你的模块需要依赖以下插件提供的模块。由于 `SourceFilteringCore` 暴露了接口定义，这是最基础的依赖。

| 模块 | 用途 |
|---|---|
| `SourceFilteringCore` | 提供核心数据结构（如 `FDataSourceFilterConfiguration`）和接口定义（`IDataSourceFilterInterface`, `IDataSourceFilterSetInterface`）。 |
| `TraceSourceFiltering` | 提供运行时 Trace 系统集成，实现实际的过滤逻辑。 |
| `SourceFilteringEditor` | 提供编辑器 UI 和配置界面。 |

**注意**：该插件依赖 `GameplayInsights` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量到单精度浮点转换产生的编译器警告。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings that were lost. | 代码格式整理：作为日志宏迁移的后续，修复了迁移过程中多行格式字符串丢失的换行符。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将代码中的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 `printf` 风格格式化说明符的问题。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 通过 UnrealCodeFixup 工具，将引擎中所有的 `~Type() {}` 空析构函数改为 `= default`。 |

### 维护评价

- **创建时间**：该插件非常新，首次提交于 2026 年 5 月。
- **更新频率**：最近 6 个月内有多次提交，但提交内容主要集中在代码风格统一（如日志宏迁移）和编译警告修复，**没有实质性功能更新**。
- **维护状态**：插件由 Epic Games 维护，属于官方工具链的一部分，因此 **维护状态稳定**，但当前阶段更侧重于内部代码质量和工程维护。
- **推荐使用**：推荐。作为官方 Insights 工具链的扩展，它为解决特定的性能分析需求（聚焦关键 Actor）提供了可靠的方案。虽然插件较新且功能相对专一，但其设计（基于接口）清晰，易于扩展。如果你的项目需要精细化的 Trace 数据过滤，这是一个值得尝试的官方工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering)
- [官方文档]() (暂无)