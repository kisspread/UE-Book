# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、仪表板视图） |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights) | |

## 用途

Audio Insights 是一个深度集成 Unreal Insights 分析工具的音频调试与性能分析插件。它解决了音频系统在大型项目中“黑盒”运行、难以监控和优化的问题。该插件通过提供专用的音频分析追踪通道（Trace Channel）和编辑器内的可视化仪表板，让开发者能够实时查看音频事件、设备状态、资源加载和性能数据，从而进行有效的音频调试、性能瓶颈定位和资源优化。

## 使用场景

- **音频性能分析**：当你的游戏出现音频卡顿或CPU占用过高时，使用 Audio Insights 的频谱分析仪、响度计和事件日志来定位是哪个音频资产或处理逻辑导致了性能问题。
- **音频事件调试**：在复杂的音频交互逻辑中，通过事件日志（Event Log）追踪音频事件的触发顺序、参数和状态，快速定位播放逻辑错误。
- **音频资源监控**：监控音频资产的加载、卸载和内存占用，优化音频流送（Streaming）和内存管理策略。
- **多客户端音频调试**：在多人游戏开发中，使用世界过滤器（World Filter）功能，将分析视图聚焦于特定的PIE（Play In Editor）客户端，独立分析每个玩家的音频状态。

## 蓝图用法

该插件主要提供编辑器工具和分析功能，运行时蓝图API较少。其核心功能通过编辑器内的仪表板和Unreal Insights工具访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDeviceId` | 获取当前音频设备的ID，用于在分析中标识设备。 | `IAudioInsightsEditorModule` |
| `CreateDashboardTabWidget` | 创建音频分析仪表板的停靠标签页控件。 | `IAudioInsightsEditorModule` |

### 使用示例（蓝图描述）

由于该插件主要面向编辑器扩展，其核心使用流程是在编辑器中操作：
1.  在编辑器菜单栏或窗口菜单中找到并打开“Audio Insights”仪表板。
2.  仪表板内包含多个可停靠的分析窗口，如频谱分析仪、响度计、事件日志等。
3.  在PIE模式下运行游戏，仪表板会实时显示来自游戏进程的音频分析数据。
4.  通过工具栏选择“监控”或“录制”模式，以实时查看或录制音频追踪数据供后续分析。

## C++ 用法

### 头文件引入

```cpp
#include "IAudioInsightsEditorModule.h"
```

### 基本用法

获取模块实例并注册一个自定义的仪表板视图工厂。这是扩展 Audio Insights 仪表板的主要方式。

```cpp
// 来自 IAudioInsightsEditorModule.h 的接口定义
// 假设你有一个自定义的视图工厂类 FMyAudioViewFactory
#include "IAudioInsightsEditorModule.h"
#include "DashboardViewFactory.h" // 假设的基类头文件

void RegisterMyViewFactory()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& EditorModule = IAudioInsightsEditorModule::GetChecked();
        TSharedRef<UE::Audio::Insights::IDashboardViewFactory> MyFactory = MakeShared<FMyAudioViewFactory>();
        EditorModule.RegisterDashboardViewFactory(MyFactory);
    }
}
```

### 进阶用法

结合 `UAudioInsightsEditorSettings` 进行配置，并处理模块的生命周期。

```cpp
#include "AudioInsightsEditorSettings.h"
#include "IAudioInsightsEditorModule.h"

void ConfigureAudioInsights()
{
    // 获取或修改插件设置
    UAudioInsightsEditorSettings* Settings = GetMutableDefault<UAudioInsightsEditorSettings>();
    if (Settings)
    {
        // 例如，设置频谱分析仪的参数
        Settings->SpectrumAnalyzerSettings.FFTSize = 2048;
        Settings->SpectrumAnalyzerSettings.WindowType = EFFTWindowType::Blackman;
        Settings->SaveConfig();
    }

    // 确保在模块卸载前反注册你的工厂
    // 通常在模块的 ShutdownModule 中处理
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& EditorModule = IAudioInsightsEditorModule::GetChecked();
        EditorModule.UnregisterDashboardViewFactory(FName("MyAudioView"));
    }
}
```

## Demo 示例

以下示例展示如何创建一个简单的自定义仪表板视图工厂并注册到 Audio Insights 中。

**MyAudioInsightsViewFactory.h**
```cpp
#pragma once

#include "DashboardViewFactory.h"
#include "Templates/SharedPointer.h"

class FMyAudioInsightsViewFactory : public UE::Audio::Insights::IDashboardViewFactory
{
public:
    FMyAudioInsightsViewFactory();
    virtual ~FMyAudioInsightsViewFactory() override;

    // IDashboardViewFactory 接口
    virtual FName GetName() const override;
    virtual FText GetDisplayName() const override;
    virtual TSharedRef<SWidget> CreateWidget() override;
    virtual void OnBeginTraceAnalysis() override;
    virtual void OnEndTraceAnalysis() override;
};
```

**MyAudioInsightsViewFactory.cpp**
```cpp
#include "MyAudioInsightsViewFactory.h"
#include "Widgets/Text/STextBlock.h"

FMyAudioInsightsViewFactory::FMyAudioInsightsViewFactory()
{
}

FMyAudioInsightsViewFactory::~FMyAudioInsightsViewFactory()
{
}

FName FMyAudioInsightsViewFactory::GetName() const
{
    return FName("MyCustomAudioView");
}

FText FMyAudioInsightsViewFactory::GetDisplayName() const
{
    return NSLOCTEXT("AudioInsights", "MyViewDisplayName", "My Custom Audio View");
}

TSharedRef<SWidget> FMyAudioInsightsViewFactory::CreateWidget()
{
    // 创建一个简单的文本块作为占位符
    return SNew(STextBlock)
        .Text(NSLOCTEXT("AudioInsights", "MyViewPlaceholder", "This is a custom Audio Insights view."));
}

void FMyAudioInsightsViewFactory::OnBeginTraceAnalysis()
{
    // 当开始追踪分析时调用，可在此初始化数据源
}

void FMyAudioInsightsViewFactory::OnEndTraceAnalysis()
{
    // 当结束追踪分析时调用，可在此清理资源
}
```

**在你的编辑器模块中注册：**
```cpp
#include "IAudioInsightsEditorModule.h"
#include "MyAudioInsightsViewFactory.h"

void FMyEditorModule::StartupModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& EditorModule = IAudioInsightsEditorModule::GetChecked();
        TSharedRef<UE::Audio::Insights::IDashboardViewFactory> MyFactory = MakeShared<FMyAudioInsightsViewFactory>();
        EditorModule.RegisterDashboardViewFactory(MyFactory);
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (IAudioInsightsEditorModule::IsModuleLoaded())
    {
        IAudioInsightsEditorModule& EditorModule = IAudioInsightsEditorModule::GetChecked();
        EditorModule.UnregisterDashboardViewFactory(FName("MyCustomAudioView"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioInsights` | 核心运行时模块，提供音频追踪通道和基础数据结构。 |
| `AudioWidgets` | 提供音频分析所需的UI控件，如频谱图、波形显示等。 |
| `TraceAnalysis` | Unreal Insights 的核心分析框架，用于处理追踪数据。 |
| `TraceServices` | 提供追踪数据的存储和查询服务。 |

## 维护状态

### 近期更新

```
- a1498af103ea [Audio Insights] AudioInsightsEditorDashboardFactory: track when layout is getting reset so we don't stop/start a trace analysis again
- a5594eab60c4 [Audio Insights] FEditorDashboardFactory::CreateTraceBookmark: use SubText var instead of SaveBookmarkNotificationLiveTraceSubText
- f21d0a8fa339 [Audio Insights] Toolbar revamp + option to select between trace monitoring or recording (see JIRA for more details)
```

- `a1498af103ea`: 修复了仪表板布局重置时错误地停止/启动追踪分析的问题。
- `a5594eab60c4`: 修正了创建追踪书签时使用的文本变量。
- `f21d0a8fa339`: 对工具栏进行了重大改进，增加了在“监控”和“录制”模式间切换的选项。

### 维护评价

**活跃维护**。该插件创建于2023年底，是一个相对较新的工具。从最近的提交记录看，开发团队正在积极修复bug并添加新功能（如工具栏改进）。作为Epic官方提供的音频分析工具，它与Unreal Insights深度集成，是UE5音频开发工作流的重要组成部分。尽管仍处于Beta阶段，但其核心功能稳定，推荐在需要进行音频性能分析和调试的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights)
- [官方文档]() (暂无)
- [测试用例]() (暂无)