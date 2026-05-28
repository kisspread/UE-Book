# Insights Data Source Filters

> Source data filtering for Unreal Insights.

| 属性 | 值 |
|---|---|
| 中文名 | 数据源过滤 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（预设资产、测试资源） |
| 模块 | `SourceFilteringCore` (Runtime), `SourceFilteringEditor` (Editor), `SourceFilteringTrace` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering) | |

## 用途

该插件是 Unreal Insights 性能分析工具的一个**运行时源数据过滤框架**。它提供了一套可扩展的机制，允许开发者在运行时动态地过滤、选择哪些 Actor 和数据应该被包含在 Unreal Insights 的跟踪输出中，从而聚焦于特定的性能分析场景。插件通过定义过滤器（Filter）和过滤器集合（Filter Set）来控制哪些 Actor 会被跟踪，并可利用异步任务和优化策略提升过滤效率。

**解决的问题：**
1.  **数据过载**：在大型复杂项目中，Insights 跟踪的数据量巨大，难以快速定位到需要分析的特定对象。
2.  **动态控制**：需要在不重启游戏或编辑器的情况下，灵活地切换跟踪范围（如只跟踪特定角色、特定类型的世界）。
3.  **性能优化**：避免过滤逻辑本身成为性能瓶颈，因此插件内部集成了异步评估和缓存机制。

**为什么存在：** 作为 Unreal Insights 生态的核心组成部分，此插件为其提供了强大的数据过滤和管理能力，是专业性能分析工作流中不可或缺的一环。

## 使用场景

-   你在进行大型开放世界游戏的性能分析 → 使用此插件过滤，只跟踪玩家角色和关键的游戏逻辑 Actor，忽略成百上千的装饰性静态物体。
-   你需要分析特定网络模式（如 Dedicated Server）下的性能 → 通过插件按 `ENetMode` 过滤掉 Client 端的世界和数据。
-   你正在调试某个导致卡顿的 Actor → 创建一个自定义过滤器，在特定条件下（如 Actor 位于屏幕内）才将其纳入跟踪范围。
-   你需要一套可复用的过滤规则 → 创建过滤器预设资产（Preset），在不同项目或不同分析阶段快速加载。

## 蓝图用法

插件的核心是创建和管理数据源过滤器。你可以在蓝图中创建自定义过滤器，并将其组合成过滤器集合。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Does Actor Pass Filter` | （事件）检查一个 Actor 是否通过此过滤器。你需要实现此函数来定义过滤逻辑。 | `UDataSourceFilter` |
| `Add Filter` | 向当前活跃的过滤器集合中添加一个过滤器实例。 | `USourceFilterCollection` |
| `Remove Filter` | 从过滤器集合中移除一个过滤器。 | `USourceFilterCollection` |
| `Make Filter Set` | 将两个过滤器组合成一个过滤器集合（AND/OR 关系）。 | `USourceFilterCollection` |
| `Set Filter State` | 启用或禁用一个特定的过滤器。 | `USourceFilterCollection` |

### 使用示例（蓝图描述）

1.  **创建自定义过滤器**：
    -   在内容浏览器中，右键创建新的 **蓝图类**，父类选择 `DataSourceFilter`。
    -   打开该蓝图，在事件图表中重写 `Does Actor Pass Filter` 事件。
    -   例如，添加逻辑：`返回 Actor 是否具有特定 Tag`，或者 `Actor 与玩家的距离是否小于 5000`。
    -   保存并编译该蓝图过滤器。

2.  **应用过滤器**：
    -   你需要通过 `FTraceSourceFiltering` 管理器（通常在 Insights 面板中操作）或通过控制台命令来激活和管理过滤器集合。
    -   蓝图中，可以通过 `Get Trace Source Filtering` 节点获取管理器实例，进而操作 `FilterCollection`。
    -   使用 `Add Filter` 节点，将上一步创建的过滤器蓝图类添加到集合中。过滤器会立即生效。

## C++ 用法

在 C++ 中，你可以创建原生过滤器（性能更高）、管理过滤逻辑，以及进行自动化测试。

### 头文件引入

```cpp
// 核心数据源过滤接口
#include "DataSourceFilter.h"
// 过滤器集合资产
#include "SourceFilterCollection.h"
// 跟踪和过滤管理
#include "TraceSourceFiltering.h"
#include "TraceWorldFiltering.h"
```

### 基本用法

**1. 创建原生过滤器**
继承 `UDataSourceFilter` 并实现 `DoesActorPassFilter_Implementation` 函数。
（参考 `Public/DataSourceFilter.h`）

```cpp
// MyNativeFilter.h
#pragma once
#include "DataSourceFilter.h"
#include "MyNativeFilter.generated.h"

UCLASS(Blueprintable)
class UMyNativeFilter : public UDataSourceFilter
{
    GENERATED_BODY()
public:
    // 实现原生过滤逻辑
    virtual bool DoesActorPassFilter_Implementation(const AActor* InActor) const override;
};

// MyNativeFilter.cpp
#include "MyNativeFilter.h"

bool UMyNativeFilter::DoesActorPassFilter_Implementation(const AActor* InActor) const
{
    if (!InActor) return false;
    // 例如：只允许静态网格体 Actor 通过
    return InActor->FindComponentByClass<UStaticMeshComponent>() != nullptr;
}
```

**2. 编程式管理过滤器集合**
（参考 `Public/SourceFilterCollection.h`）

```cpp
#include "TraceSourceFiltering.h"
#include "SourceFilterCollection.h"

// 获取过滤器管理器单例
FTraceSourceFiltering& FilterManager = FTraceSourceFiltering::Get();
USourceFilterCollection* FilterCollection = FilterManager.GetFilterCollection();

// 添加一个过滤器类
UDataSourceFilter* NewFilter = FilterCollection->AddFilterOfClass(UMyNativeFilter::StaticClass());

// 创建一个过滤器集合 (AND 模式)
UDataSourceFilter* FilterA = ...; // 已有的过滤器实例
UDataSourceFilter* FilterB = ...; // 已有的过滤器实例
UDataSourceFilterSet* FilterSet = FilterCollection->MakeFilterSet(FilterA, FilterB, EFilterSetMode::And);

// 移动一个过滤器到某个集合下
FilterCollection->MoveFilter(NewFilter, FilterSet);
```

### 进阶用法

**编写自动化测试**（参考 `Public/TraceSourceFilteringTestBase.h`）
插件提供了一个测试基类，方便编写过滤逻辑的自动化测试。

```cpp
// MyFilterTest.cpp
#include "TraceSourceFilteringTestBase.h"
#include "MyNativeFilter.h"

class FMyFilterTest : public FTraceSourceFilteringTestBase
{
public:
    FMyFilterTest() : FTraceSourceFilteringTestBase(TEXT("MyFilterTest"), false) {}
protected:
    virtual void SetupTest(const FString& Parameters) override
    {
        // 1. 添加测试 Actor
        AStaticMeshActor* MeshActor = AddActor<AStaticMeshActor>(true); // 期望通过
        ACharacter* Character = AddActor<ACharacter>(false); // 期望不通过

        // 2. 添加我们自定义的原生过滤器
        auto& NativeFilter = AddFilter<UMyNativeFilter>();

        // 3. （可选）添加到过滤器集合
        // AddFilterSet(EFilterSetMode::And).InsertFilter(NativeFilter);
    }
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyFilterTest, "MyProject.Insights.FilterTest", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)
```

## Demo 示例

一个最小的自定义原生过滤器示例，用于过滤出所有带有 `“Traceable”` 标签的 Actor。

```cpp
// TraceableTagFilter.h
#pragma once
#include "DataSourceFilter.h"
#include "TraceableTagFilter.generated.h"

UCLASS(Blueprintable, Category = "Insights")
class UTraceableTagFilter : public UDataSourceFilter
{
    GENERATED_BODY()
public:
    UTraceableTagFilter();

    // 可以在蓝图或编辑器中设置的配置属性
    UPROPERTY(EditAnywhere, Category = "Config")
    FName RequiredTag = FName("Traceable");

protected:
    virtual bool DoesActorPassFilter_Implementation(const AActor* InActor) const override;
    virtual void GetDisplayText_Internal(FText& OutDisplayText) const override;
};

// TraceableTagFilter.cpp
#include "TraceableTagFilter.h"

UTraceableTagFilter::UTraceableTagFilter()
{
    // 配置：这是一个原生实现、可以异步执行、且是“出生时过滤”（减少计算次数）
    Configuration.bNative = true;
    Configuration.bCanRunAsynchronously = true;
    Configuration.bOnSpawnOnly = true;
}

bool UTraceableTagFilter::DoesActorPassFilter_Implementation(const AActor* InActor) const
{
    if (!InActor)
    {
        return false;
    }
    // 检查 Actor 是否拥有指定的 Tag
    return InActor->ActorHasTag(RequiredTag);
}

void UTraceableTagFilter::GetDisplayText_Internal(FText& OutDisplayText) const
{
    OutDisplayText = FText::Format(NSLOCTEXT("TraceableTagFilter", "Display", "Has Tag: {0}"), FText::FromName(RequiredTag));
}
```

**如何使用这个示例过滤器：**
1.  编译以上代码。
2.  启动编辑器或游戏。
3.  打开 Unreal Insights 并连接到当前会话。
4.  在 Insights 的 Trace Filtering 面板（如果可用）或通过控制台命令（如 `Trace.Filter.AddClass MyGame.TraceableTagFilter`）加载此过滤器。
5.  之后，只有被标记为 `“Traceable”` 的 Actor 的相关性能数据才会出现在 Insights 的跟踪输出中。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 核心依赖。提供了 Insights 框架、Trace Channel 基础以及编辑器面板。 |
| `StructUtils` | 用于 `FObjectKey` 等结构体工具，确保过滤器实例的稳定标识。 |
| `PropertyEditor` | （`SourceFilteringEditor` 模块）用于在编辑器细节面板中自定义过滤器属性的显示。 |
| `TraceAnalysis` | 提供底层的 Trace 分析通道（`TraceSourceFiltersChannel`），用于输出过滤状态。 |

*注意：该插件默认禁用（`EnabledByDefault: false`），你需要在项目设置或通过控制台命令显式启用。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha... | 修复了上次UE_LOG迁移导致的多行格式字符串换行符丢失问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件代码中的 UE_LOG 迁移为新的 UE_LOGF 宏。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 执行了代码规范化，将析构函数体改为 = default。 |

### 维护评价

-   **创建时间**：历史非常悠久（约12年），表明它是 Unreal Insights 基础架构的成熟组成部分。
-   **更新频率**：近一年的提交（截至2026年5月）主要是**维护性更新**，如代码规范修复、编译器警告修复、日志宏迁移，**没有显著的功能增强或架构变更**。
-   **活跃度**：**维护不活跃**。最后的实质性功能更新时间远早于近期提交。插件功能已趋于稳定，可能仅由 Epic 核心团队进行最低限度的维护。
-   **已知限制**：这是一个默认禁用的**开发者工具**插件，不适用于最终打包的游戏（`TargetConfigurationDenyList: Shipping`）。
-   **推荐使用**：如果你需要深度定制 Unreal Insights 的跟踪数据，这是一个**强大且必要**的工具。但由于其复杂的内部实现和较低的维护活跃度，建议仅在有明确性能分析需求时启用和使用，并准备好查阅源码以解决潜在问题。对于简单的过滤需求，可能优先使用引擎内置的过滤选项。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering)
-   [官方文档](https://docs.unrealengine.com/) (无特定文档链接，请参考 `Trace` 相关章节)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringTrace/Tests) (位于 `SourceFilteringTrace/Tests` 目录下)