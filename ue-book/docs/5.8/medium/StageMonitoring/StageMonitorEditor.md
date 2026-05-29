# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation

| 属性 | 值 |
|---|---|
| 中文名 | 舞台监控器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageDataProvider` (Runtime), `StageMonitor` (UncookedOnly), `StageMonitorCommon` (Runtime), `StageMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

`StageMonitoring` 是一个专为虚拟制片（Virtual Production）环境设计的**监控与诊断工具**。在虚拟制片流程中，通常涉及摄像机追踪、渲染服务器、媒体服务器、LED 墙控制器等多台计算机协同工作。本插件的核心功能是**聚合、展示和分析来自这些不同机器（数据提供者）的性能指标、状态数据和事件活动**，以便技术人员能够实时监控整个制作阶段的健康状态，快速定位性能瓶颈或故障节点。

它解决的**核心问题**是：在复杂的多机分布式环境中，缺乏一个集中、统一的视图来观察所有设备的运行状况。通过本插件，用户可以在 Unreal Editor 中获得一个专属的监控面板，实时查看 CPU/GPU 负载、内存使用、线程耗时、平均帧率等关键指标，以及来自各设备的事件日志（Activities）和关键状态（Critical States）。

## 使用场景

- 你正在运行一个包含多台机器的虚拟制片现场（如 LED Volume 拍摄），需要集中监控所有追踪服务器、渲染集群和媒体服务器的性能。
- 你需要为整个虚拟制片阶段建立一个基线性能视图，并在出现卡顿或延迟时快速定位到具体是哪台机器、哪个线程出了问题。
- 你需要记录和回顾拍摄期间各设备的状态变化和事件，用于后期分析或报告生成。
- 你希望设置过滤器，只关注特定设备（提供者）、特定类型的消息或特定时间范围内的活动，以便专注于诊断特定问题。

## 蓝图用法

该插件主要提供**编辑器面板和底层监控会话接口**，其核心逻辑（数据采集、状态管理）主要面向 C++ 开发。通过搜索源码，未发现直接暴露的 `BlueprintCallable` 或 `BlueprintReadWrite` API。其功能主要通过编辑器UI（`SStageMonitorPanel`）和 C++ 接口（`IStageMonitorSession`）进行交互。

### 核心节点

此插件无公开的蓝图节点。其交互完全通过编辑器内建的 `Stage Monitor` 面板完成。

## C++ 用法

### 头文件引入

```cpp
// 使用监控会话接口
#include "IStageMonitorSession.h"
```

### 基本用法

该插件的核心是 `IStageMonitorSession` 接口，用于管理监控会话。通常，你不需要直接实例化它，而是通过 `SStageMonitorPanel` 获得对当前活动会话的引用。

```cpp
// （概念性示例）在某个编辑器工具或上下文中，获取并监听监控会话的变化
#include "IStageMonitorSession.h"

void FMyTool::SetupStageMonitoring()
{
    // 假设有一个方法能获取到当前活跃的监控会话
    TSharedPtr<IStageMonitorSession> ActiveSession = GetActiveStageMonitorSession();
    if (ActiveSession.IsValid())
    {
        // 绑定新活动（如性能数据、事件）到来的回调
        ActiveSession->OnNewStageActivity().AddLambda([this](const FDataProviderActivityPtr& NewActivity)
        {
            // 处理新收到的舞台活动数据
            UE_LOG(LogTemp, Log, TEXT("New Activity from %s: %s"), *NewActivity->GetSourceName().ToString(), *NewActivity->GetDescription().ToString());
        });

        // 绑定关键状态变化的回调
        ActiveSession->OnCriticalStateChanged().AddLambda([this](const FName& SourceName, bool bIsCritical)
        {
            if (bIsCritical)
            {
                UE_LOG(LogTemp, Warning, TEXT("Critical state triggered by: %s"), *SourceName.ToString());
            }
        });
    }
}
```

### 进阶用法：自定义数据过滤器

插件提供了 `FDataProviderActivityFilter` 类，允许你以编程方式定义复杂的过滤逻辑。

```cpp
#include "SDataProviderActivityFilter.h" // 需包含相应的头文件，路径可能为Private/Widgets/...，需确保模块依赖

void FMyAnalyzer::AnalyzeSpecificProviderData(TSharedPtr<IStageMonitorSession> Session)
{
    if (!Session.IsValid()) return;

    // 创建一个过滤器
    FDataProviderActivityFilter MyFilter(Session);
    
    // 配置过滤器：只关注名为“RenderServer01”的提供者
    MyFilter.FilterSettings.RestrictedProviders.Add(FName(TEXT("RenderServer01")));
    // 只关注时间码年龄小于5分钟的数据
    MyFilter.FilterSettings.MaxMessageAgeInMinutes = 5;
    MyFilter.FilterSettings.bEnableTimeFilter = true;

    // 获取所有未过滤的活动
    TArray<FDataProviderActivityPtr> AllActivities;
    Session->GetAllActivities(AllActivities);

    // 应用过滤器
    TArray<FDataProviderActivityPtr> FilteredActivities;
    MyFilter.FilterActivities(AllActivities, FilteredActivities);

    // 处理过滤后的数据
    for (const auto& Activity : FilteredActivities)
    {
        // ... 进行你的分析
    }
}
```

## Demo 示例

以下示例展示了如何在编辑器工具中嵌入一个简化的舞台监控数据查看器。

### MyStageMonitorWidget.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class IStageMonitorSession;
class SDataProviderListView;

class SMyStageMonitorWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyStageMonitorWidget) {}
    SLATE_ARGUMENT(TWeakPtr<IStageMonitorSession>, InMonitorSession)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SDataProviderListView> DataProviderList;
    TWeakPtr<IStageMonitorSession> CurrentSession;
};
```

### MyStageMonitorWidget.cpp

```cpp
#include "MyStageMonitorWidget.h"
#include "Widgets/SDataProviderListView.h" // 需包含插件提供的列表视图
#include "IStageMonitorSession.h"

void SMyStageMonitorWidget::Construct(const FArguments& InArgs)
{
    CurrentSession = InArgs._InMonitorSession;

    ChildSlot
    [
        SNew(SVerticalBox)
        // 标题
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Stage Performance Monitor")))
            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
        ]
        // 数据提供者列表
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        .Padding(0.f, 5.f)
        [
            SAssignNew(DataProviderList, SDataProviderListView, CurrentSession)
        ]
    ];
}
```

## 模块依赖

使用 `StageMonitoring` 插件功能（尤其是 `StageMonitorCommon` 和 `StageDataProvider` 模块）时，你的模块可能需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `StageMonitorCommon` | 提供核心数据结构（如 `FStageDataEntry`）和会话接口 `IStageMonitorSession` |
| `VirtualProductionUtilities` | 提供虚拟制片相关的通用工具和类型 |
| `Takes` | 可能与录制（Take）数据或元数据管理相关 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以支持共享字符串，优化内存。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至UE_LOGF，属于代码维护。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 修复BUG，移除JSON对象中的重复字符串以释放内存。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前错误的查找替换操作后的重新提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚之前的某个提交。 |

### 维护评价

`StageMonitoring` 插件创建于 2020 年，距今已超过 **5 年**，属于 `👴 老古董`。尽管创建较早，但从近期（2026年）的提交记录看，它**仍在被积极维护和更新**。近期的更新主要集中在**性能优化、内存管理和代码现代化**（如日志宏迁移）上，表明 Epic 仍在投入资源维护此插件以适应最新的引擎版本。

该插件标记为 `IsBetaVersion: true`，意味着它仍处于实验或测试阶段，其 API 和功能在未来版本中可能发生变更。**建议在生产环境中谨慎使用**，并密切关注后续更新。总体而言，它是一个**功能成熟但仍在演进的、专用于虚拟制片监控的工具**，对于相关领域的工作流价值很高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)
- [官方文档](https://docs.unrealengine.com) (未提供特定文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring/Source/StageMonitor/Tests) (需检查具体路径)