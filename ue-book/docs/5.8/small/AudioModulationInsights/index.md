# AudioModulationInsights

> Audio Modulation dashboards for Audio Insights.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（仪表板视图） |
| 模块 | `AudioModulationInsights` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AudioModulationInsights) | |

## 用途

AudioModulationInsights 是一个 Unreal Insights 插件，它为 Unreal Engine 的音频调制系统（Audio Modulation System）提供了专门的仪表板视图。该插件的核心功能是**可视化和分析音频调制系统的运行时数据**，帮助开发者在 Unreal Insights 工具中监控和调试音频调制参数（如总线值、混音状态、生成器输出等）的变化。

它解决了在复杂音频场景中，开发者难以实时观察和理解音频调制参数如何影响最终声音输出的问题。通过将调制系统的 Trace 数据以结构化的表格和图表形式呈现，开发者可以快速定位调制链中的问题，验证参数变化是否符合预期。

## 使用场景

- 你正在开发一个具有复杂动态音频环境的游戏（如开放世界游戏），需要监控多个音频总线（Control Bus）和混音（Bus Mix）的实时值变化。
- 你正在调试一个音频调制生成器（Generator）或参数补丁（Parameter Patch）的行为，需要查看其输出值以及它对其他调制器的贡献。
- 你需要在 Unreal Insights 的时间轴视图中，将音频调制事件与游戏逻辑、音频播放事件进行关联分析。
- 你希望为音频设计师提供一个直观的工具，让他们无需深入代码就能理解调制系统的运行状态。

## 蓝图用法

该插件是 Unreal Insights 的扩展，不直接暴露给游戏蓝图。其功能完全集成在 Unreal Insights 应用程序中。

## C++ 用法

该插件作为 Unreal Insights 的扩展模块运行，其核心是注册自定义的仪表板视图工厂（Dashboard View Factory）和 Trace 数据提供者（Trace Provider）。游戏代码通常不直接与之交互。

### 头文件引入

```cpp
// 该插件的公共头文件主要用于 Insights 扩展开发
#include "AudioModulationInsightsModule.h"
#include "Views/AudioModulationDashboardViewFactory.h"
```

### 基本用法

该插件的核心在于其模块启动时注册视图工厂。以下是其模块实现的核心逻辑（源自 `AudioModulationInsightsModule.cpp`）：

```cpp
void FAudioModulationInsightsModule::StartupModule()
{
    // 创建并注册音频调制仪表板视图工厂
    AudioModulationDashboardViewFactory = MakeShared<AudioModulationInsights::FAudioModulationDashboardViewFactory>();
    UE::Audio::Insights::RegisterDashboardViewFactory(AudioModulationDashboardViewFactory.ToSharedRef());
}

void FAudioModulationInsightsModule::ShutdownModule()
{
    // 注销视图工厂
    if (AudioModulationDashboardViewFactory.IsValid())
    {
        UE::Audio::Insights::UnregisterDashboardViewFactory(AudioModulationDashboardViewFactory.ToSharedRef());
        AudioModulationDashboardViewFactory.Reset();
    }
}
```

### 进阶用法

插件内部通过 `FAudioModulationTraceProvider` 处理来自音频调制系统的 Trace 消息。它定义了三种消息类型来对应调制器的生命周期：
1.  `FActivateModulatorTraceMessage`: 调制器被激活时发送。
2.  `FUpdateModulatorTraceMessage`: 调制器值更新时发送。
3.  `FDeactivateModulatorTraceMessage`: 调制器被停用时发送。

这些消息被解析后，用于更新 `FAudioModulationDashboardEntry` 数据结构，该结构存储了每个调制器的当前状态（ID、类型、名称、值、旁通状态、贡献者列表等），并最终在 Insights 的仪表板表格中显示。

## Demo 示例

由于这是一个 Insights 工具插件，没有独立的运行时组件。以下示例展示了如何创建一个类似的 Insights 仪表板视图工厂（概念性代码）：

```cpp
// MyCustomInsightsViewFactory.h
#pragma once
#include "Views/TableDashboardViewFactory.h"

class FMyCustomInsightsViewFactory : public UE::Audio::Insights::FTraceObjectTableDashboardViewFactory
{
public:
    FMyCustomInsightsViewFactory();
    virtual ~FMyCustomInsightsViewFactory() = default;

    // 必须重写的接口
    virtual FName GetName() const override;
    virtual FText GetDisplayName() const override;
    virtual FSlateIcon GetIcon() const override;
    virtual void ProcessEntries(UE::Audio::Insights::FTraceTableDashboardViewFactory::EProcessReason Reason) override;
    virtual const TMap<FName, FColumnData>& GetColumns() const override;
    // ... 其他重写函数
};

// MyCustomInsightsViewFactory.cpp
#include "MyCustomInsightsViewFactory.h"

FMyCustomInsightsViewFactory::FMyCustomInsightsViewFactory()
{
    // 初始化列定义等
}

FName FMyCustomInsightsViewFactory::GetName() const
{
    return TEXT("MyCustomView");
}

FText FMyCustomInsightsViewFactory::GetDisplayName() const
{
    return NSLOCTEXT("MyInsights", "MyCustomView", "My Custom View");
}

// ... 其他函数实现

// 在某个模块的 StartupModule 中注册
void FMyInsightsModule::StartupModule()
{
    MyViewFactory = MakeShared<FMyCustomInsightsViewFactory>();
    UE::Audio::Insights::RegisterDashboardViewFactory(MyViewFactory.ToSharedRef());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioInsights` | 提供音频 Insights 的基础框架、Trace 提供者基类和仪表板视图工厂接口。 |
| `TraceAnalysis` | 用于分析 Unreal Trace 数据流，是 Insights 插件处理 Trace 事件的核心依赖。 |

## 维护状态

### 近期更新

- 2026-04-15 `4672ae6a` [Audio Insights] [AudioModulationInsights] Write a trace file based on the data contained in the Aud
- 2026-04-09 `a78fe857` [Audio Insights] Expand Details panel selection to all relevant dashboards. Implements OnSelectionCh
- 2026-03-12 `a7005c61` [Audio Insights] - Modulation: Fix Bughawk error in AudioModulationInsightsStyle.cpp

### 维护评价

该插件创建于 2026 年 2 月，是一个非常新的实验性插件。从 Git 历史看，它在创建后的两个月内有多次实质性功能更新和错误修复，表明处于**活跃开发**状态。作为 `IsExperimentalVersion: true` 的插件，其 API 和功能可能会发生变化。目前它专注于为音频调制系统提供 Insights 视图，功能明确。鉴于其新近创建和活跃的更新，**推荐在需要深度调试音频调制系统时使用**，但需注意其实验性状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AudioModulationInsights)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/AudioModulationInsights/Tests) (如果存在)