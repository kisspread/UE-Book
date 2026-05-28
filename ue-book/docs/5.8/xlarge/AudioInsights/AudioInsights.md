# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频洞察工具 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（SVG 图标、UI 资产） |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (EditorNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights) | |

## 用途

Audio Insights 是 UE5 的**音频调试与性能分析工具套件**，基于 Unreal Insights 追踪系统构建。它解决的核心问题是：在复杂项目中，音频系统内部的信号流、音量变化、总线连接、子混音处理等运行时行为难以直观观察和诊断。

该插件通过 Unreal Insights 的 Trace 通道实时采集音频引擎内部事件，然后在专用的 Dashboard 面板中以**图表、节点图、事件日志**等形式可视化呈现。主要功能包括：

- **Sound Dashboard**：实时监控所有活跃音源的状态（振幅、音量、音高、滤波器频率、优先级、距离衰减等），支持 Mute/Solo/Pin 操作
- **Signal Flow Graph**：以节点图形式可视化音频信号从声源到总线、子混音的完整流向，支持连线动画
- **Event Log**：记录音频事件（播放、停止、虚拟化等）的时间线日志
- **Audio Bus / Submix 监控**：实时查看音频总线和子混音的包络电平
- **Output Metering**：输出响度计（LKFS、True Peak）
- **Cache 系统**：带时间轴控制的事件缓存，支持回放、暂停、快照导出

## 使用场景

- 你需要诊断某个 MetaSound 或 SoundCue 的音量为什么异常 → 打开 **Sound Dashboard** 实时查看参数变化
- 你需要确认音频信号是否正确路由到目标总线或子混音 → 使用 **Signal Flow** 节点图查看连接关系
- 你需要排查音频性能问题，找出哪些声音消耗最多 CPU → 在 **Sound Dashboard** 中查看 Relative Render Cost 列
- 你需要记录和回放音频事件用于 bug 复现 → 使用 **Event Log** 的缓存和时间线回放功能
- 你需要在 Unreal Insights 独立程序中分析离线 .utrace 文件 → AudioInsights 模块支持在 Insights 程序中加载

## 蓝图用法

Audio Insights 主要是一个**编辑器/Insights 面板工具**，不直接暴露蓝图节点。音频调试事件通过引擎内部的 Trace 系统发送，用户在 Insights 面板中查看结果。

### 可配置设置

| 设置项 | 说明 | 所在类 |
|---|---|---|
| `AmplitudeDisplayMode` | 振幅显示单位（dB / Linear） | `FSoundDashboardSettings` |
| `TreeViewMode` | 声音列表视图模式（树形 / 活跃声音 / 扁平列表） | `FSoundDashboardSettings` |
| `AutoExpandMode` | 新声音进入时的自动展开行为 | `FSoundDashboardSettings` |
| `CacheSizeMB` | 事件缓存大小（8-512 MB） | `FCacheSettings` |
| `GraphJustification` | Signal Flow 节点对齐方式（边缘 / 中心） | `FSignalFlowSettings` |
| `StopCacheWhenPausedBehaviour` | 暂停时缓存行为 | `FCacheSettings` |

## C++ 用法

### 头文件引入

```cpp
#include "IAudioInsightsModule.h"
```

### 基本用法：注册自定义 Dashboard View

Audio Insights 支持通过模块接口注册自定义的 Dashboard 面板：

```cpp
// 获取 Audio Insights 模块
IAudioInsightsModule& AudioInsightsModule = IAudioInsightsModule::GetChecked();

// 注册自定义 Dashboard View 工厂
AudioInsightsModule.RegisterDashboardViewFactory(MyDashboardFactory);
```

### 进阶用法：注册自定义事件日志类型

外部插件可以向 Event Log 注册自定义事件类别和事件名：

```cpp
// 在你的插件 StartupModule 中注册
IAudioInsightsModule& AudioInsightsModule = IAudioInsightsModule::GetChecked();

// 注册事件类别和事件名
TMap<FString, TSet<FString>> CategoriesToEvents;
CategoriesToEvents.Add(TEXT("MyPlugin"), { TEXT("MyCustomEvent"), TEXT("AnotherEvent") });
AudioInsightsModule.RegisterEventLogCategories(CategoriesToEvents);

// 注册本地化显示名称
TMap<FString, FText> DisplayNames;
DisplayNames.Add(TEXT("MyPlugin"), NSLOCTEXT("MyPlugin", "CategoryName", "我的插件"));
DisplayNames.Add(TEXT("MyCustomEvent"), NSLOCTEXT("MyPlugin", "EventName", "自定义事件"));
AudioInsightsModule.RegisterEventLogDisplayNames(DisplayNames);
```

### 进阶用法：自定义 Trace Provider

继承 `FTraceProviderBase` 或 `TDeviceDataMapTraceProvider` 来创建自定义的音频追踪数据提供者：

```cpp
// 继承 TDeviceDataMapTraceProvider 管理设备级数据
class FMyCustomTraceProvider 
    : public TDeviceDataMapTraceProvider<uint32, TSharedPtr<FMyEntry>>
{
public:
    FMyCustomTraceProvider() : TDeviceDataMapTraceProvider(TEXT("MyCustomProvider")) {}
    
    static FName GetName_Static() { return TEXT("MyCustomProvider"); }
    
    virtual UE::Trace::IAnalyzer* ConstructAnalyzer(
        TraceServices::IAnalysisSession& InSession) override;
};
```

## Demo 示例

```cpp
// MyAudioInsightsExtension.h
#pragma once

#include "IAudioInsightsModule.h"

class FMyAudioInsightsExtension
{
public:
    void Startup()
    {
        if (IAudioInsightsModule::IsModuleLoaded())
        {
            IAudioInsightsModule& Module = IAudioInsightsModule::GetChecked();
            
            // 注册自定义事件日志
            TMap<FString, TSet<FString>> Events;
            Events.Add(TEXT("Gameplay"), { TEXT("SFX_Played"), TEXT("Music_Crossfade") });
            Module.RegisterEventLogCategories(Events);
        }
    }
    
    void Shutdown()
    {
        // 清理资源
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioWidgets` | 音频 UI 控件（电平表、响度计等） |
| `TraceServices` | Unreal Insights 追踪分析框架 |
| `Insights` | Unreal Insights 核心时序视图扩展 |
| `AssetRegistry` | 资产注册表（用于 Sound Dashboard 中的资产浏览） |
| `AudioMixer` | 音频混合器（设备管理委托） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `28c5c884` | [Audio Insights] Plugin template readme file to assist users when expanding Audio Insights with cust | 添加插件模板 README，帮助用户扩展自定义功能 |
| 2026-05-19 | `a9b19eba` | [Audio Insights] Stop Event Log from automatically setting new items in the details panel when scrub | 修复 Event Log 在拖动时间轴时自动设置详情面板的问题 |
| 2026-05-14 | `d492400a` | [Audio Insights] Fix localization for event log filter menu strings | 修复事件日志过滤菜单的本地化字符串 |
| 2026-05-14 | `64ecb7b0` | [Audio Insights] Setting Audio Insights and Audio Insights Runtime plugins to be Production | 将插件状态标记为生产就绪 |
| 2026-05-14 | `62b99116` | [Audio Insights] Add user-adjustable node padding multipliers to signal flow graph settings menu. Tw | 在 Signal Flow 设置中添加可调节的节点间距参数 |

### 维护评价

**积极维护中**。该插件创建于 2023 年 12 月，虽然相对较新，但近期（2026 年 5 月）仍有密集的功能更新和 bug 修复。从 commit 记录看：

- 已从实验性状态正式升级为**生产就绪**（Production）
- 持续增加新功能（自定义事件注册、节点间距调节、插件扩展模板）
- 积极修复 UI 和本地化问题
- 代码规模较大（172 个源文件），架构成熟

**推荐使用**。作为 Epic 官方维护的音频调试工具，它与 Unreal Insights 深度集成，是 UE5 音频开发的重要生产力工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights)
- [AudioWidgets 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets)（依赖项）