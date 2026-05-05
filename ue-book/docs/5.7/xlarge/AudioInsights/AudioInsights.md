# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Slate 样式资源） |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights) | |

## 用途

Audio Insights 是一套集成在 **Unreal Insights** 分析框架中的音频性能分析与调试工具集。它解决了以下核心问题：

1. **实时音频监控**：在运行时（PIE 或独立程序）实时查看所有活跃声音的振幅、音量、距离、优先级等参数，无需打断游戏流程
2. **音频事件追踪**：记录并过滤所有音频事件（播放、停止、虚拟化等），支持按 MetaSound、SoundCue、SoundWave 等类别筛选
3. **Submix / Audio Bus 可视化**：监控 Submix 和 Audio Bus 的包络跟随器数据，实时显示电平表
4. **虚拟循环调试**：追踪 Virtual Loop 的虚拟化/反虚拟化状态、播放时间、空间位置等
5. **音频参数时序绘图**：将音频参数（振幅、音量、频率等）绘制为时间序列曲线，支持时间轴回溯
6. **音频日志过滤**：从引擎日志中提取音频相关的日志输出，独立显示

该插件通过 Unreal Trace 系统捕获音频数据，经由 `FTraceProviderBase` 子类处理后，展示在多个专用仪表板视图中。它同时支持 **编辑器 PIE 模式** 和 **UnrealInsights 独立程序模式**。

## 使用场景

- 你在调试一个大型开放世界游戏的音频性能问题 → 用 **Sound Dashboard** 查看所有活跃声音的资源消耗
- 你需要确认某个 MetaSound 是否正确触发 → 用 **Audio Event Log** 过滤 MetaSound 类别事件
- 你在调优混音，需要实时观察各 Submix 的电平 → 用 **Submix Dashboard** 配合音频电平表
- 你需要分析某个声音参数（如音量衰减）随时间的变化 → 用 **Sound Plots** 绘制时序曲线
- 你在排查 Virtual Loop 的虚拟化逻辑 → 用 **Virtual Loop Dashboard** 查看虚拟化状态和空间位置
- 你需要在 Unreal Insights 独立程序中分析离线 trace 文件 → 该插件完全支持 UnrealInsights 程序

## 架构概览

本插件采用 **Provider → Cache → Dashboard** 三层架构：

```
┌─────────────────────────────────────────────────────┐
│                  Unreal Insights                     │
│  ┌───────────────────────────────────────────────┐  │
│  │            Dashboard Views (UI)                │  │
│  │  Sound | EventLog | Submix | AudioBus | ...    │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ IDashboardViewFactory          │
│  ┌──────────────────▼────────────────────────────┐  │
│  │           Cache Manager (Editor)               │  │
│  │  FAudioInsightsCacheManager                    │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │  │
│  │  │ Chunk 0 │ │ Chunk 1 │ │ Chunk N │  ...     │  │
│  │  └─────────┘ └─────────┘ └─────────┘         │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ IAudioCachedMessage            │
│  ┌──────────────────▼────────────────────────────┐  │
│  │         Trace Providers (数据源)               │  │
│  │  Sound | Submix | AudioBus | VirtualLoop | ... │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │ Trace::IAnalyzer               │
│  ┌──────────────────▼────────────────────────────┐  │
│  │           FTraceModule (Trace 管理)            │  │
│  │  启动/停止 trace、管理 trace channels          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 核心类

| 类 | 职责 |
|---|---|
| `IAudioInsightsModule` | 插件模块接口，管理 Dashboard 工厂注册和 Trace 模块 |
| `FTraceModule` | Trace 分析模块，管理 trace channels 和分析会话 |
| `FDashboardFactory` | 创建主 Dashboard Tab Widget，管理所有视图工厂 |
| `FTraceProviderBase` | Trace 数据提供者基类，处理 trace 事件并生成数据条目 |
| `FAudioInsightsCacheManager` | 编辑器模式下的消息缓存管理器，支持时间轴回溯 |
| `IDashboardViewFactory` | 仪表板视图工厂接口，定义如何创建 UI |

## 仪表板视图详解

### Sound Dashboard（声音仪表板）

**类**：`FSoundDashboardViewFactory`（继承 `FTraceTreeDashboardViewFactory`）

树形视图，展示所有活跃声音实例。支持三种查看模式：
- **Tree View**：按类别（MetaSound、SoundCue 等）分组的树形结构
- **Active Sounds**：仅显示当前活跃的声音
- **Flat List**：扁平列表，每个声音波形独立显示

**功能**：
- 静音（Mute）/ 独奏（Solo）单个声音
- 实时显示振幅、音量、距离、优先级、LPF/HPF 频率等参数
- 支持 Pin（固定）声音条目到顶部
- 内置 Sound Plots 时序绘图
- 按声音类型过滤（MetaSound、SoundCue、SoundWave 等）
- 可配置列的显示/隐藏

### Audio Event Log（音频事件日志）

**类**：`FAudioEventLogDashboardViewFactory`

时间线视图，记录所有音频事件。支持：
- 按事件类型过滤（MetaSound、SoundCue、ProceduralSource 等）
- 自定义事件类别和事件名称
- 时间戳、播放顺序、资产路径、Actor 等列
- 缓存状态显示（编辑器模式）
- 右键菜单操作

### Submix Dashboard（Submix 仪表板）

**类**：`FSubmixDashboardViewFactory`

表格视图，监控所有 Submix 实例。支持：
- 包络跟随器（Envelope Follower）数据可视化
- 音频电平表集成
- Submix 加载/卸载状态追踪

### Audio Bus Dashboard（音频总线仪表板）

**类**：`FAudioBusDashboardViewFactory`

表格视图，监控所有 Audio Bus。支持：
- 按类型过滤（Asset-based / Code-generated）
- 包络跟随器数据
- 音频电平表集成

### Virtual Loop Dashboard（虚拟循环仪表板）

**类**：`FVirtualLoopDashboardViewFactory`

表格视图，监控 Virtual Loop 的虚拟化状态。支持：
- 虚拟化/反虚拟化事件追踪
- 播放时间、更新间隔
- 空间位置和旋转信息
- 编辑器模式下的 Debug Draw

### Audio Meters Panel（音频电平面板）

**类**：`FAudioMetersPanelDashboardViewFactory`

可滚动的音频电平表集合，实时显示各音频源的电平。

### Sound Plots（声音绘图）

**类**：`FSoundPlotsDashboardViewFactory`

时序曲线图，绘制音频参数随时间的变化。支持：
- 多条曲线叠加显示
- 自定义 Y 轴范围
- 时间轴缩放和平移
- 时间标记（Time Marker）同步

### Audio Log（音频日志）

**类**：`FLogDashboardViewFactory`

过滤后的音频日志输出，从引擎日志中提取 `LogAudioInsights` 类别的输出。

## 蓝图用法

本插件主要面向 C++ 和编辑器工具开发，**不暴露 BlueprintCallable API**。

以下设置类型可在编辑器偏好设置中配置：

### 可配置枚举

| 枚举 | 说明 | 所在文件 |
|---|---|---|
| `EAudioAmplitudeDisplayMode` | 振幅显示单位（dB / Linear） | `SoundDashboardSettings.h` |
| `ESoundDashboardTreeViewingOptions` | 声音仪表板查看模式 | `SoundDashboardSettings.h` |
| `ESoundDashboardAutoExpandOptions` | 自动展开选项 | `SoundDashboardSettings.h` |

### 编辑器偏好设置

通过 **Edit → Editor Preferences → Plugins → Audio Insights** 访问：

- **Sound Dashboard**：配置列可见性、振幅显示模式、树形查看选项、自动展开行为
- **Audio Event Log**：配置列可见性、自定义事件类别、事件过滤器

## C++ 用法

### 头文件引入

```cpp
#include "IAudioInsightsModule.h"
#include "Views/DashboardViewFactory.h"
#include "AudioInsightsTraceProviderBase.h"
```

### 访问模块

```cpp
// 获取 Audio Insights 模块实例
IAudioInsightsModule& AudioInsightsModule = IAudioInsightsModule::GetChecked();

// 获取关联的音频设备 ID
::Audio::FDeviceId DeviceId = AudioInsightsModule.GetDeviceId();

// 获取 Trace 模块
IAudioInsightsTraceModule& TraceModule = AudioInsightsModule.GetTraceModule();

// 编辑器模式下获取缓存管理器
#if WITH_EDITOR
UE::Audio::Insights::FAudioInsightsCacheManager& CacheManager = AudioInsightsModule.GetCacheManager();
#endif
```

### 注册自定义 Dashboard 视图工厂

```cpp
// 创建自定义视图工厂
TSharedRef<UE::Audio::Insights::IDashboardViewFactory> MyFactory = 
    MakeShared<FMyCustomDashboardViewFactory>();

// 注册到 Audio Insights
IAudioInsightsModule& Module = IAudioInsightsModule::GetChecked();
Module.RegisterDashboardViewFactory(MyFactory);

// 注销
Module.UnregisterDashboardViewFactory(MyFactory->GetName());
```

### 创建自定义 Trace Provider

```cpp
// 继承 FTraceProviderBase
class FMyCustomTraceProvider : public UE::Audio::Insights::FTraceProviderBase
{
public:
    FMyCustomTraceProvider() : FTraceProviderBase(FName("MyCustomProvider"))
    {
    }

    static FName GetName_Static() { return FName("MyCustomProvider"); }

    virtual Trace::IAnalyzer* ConstructAnalyzer(
        TraceServices::IAnalysisSession& InSession) override
    {
        // 返回自定义的 Trace Analyzer
        return new FMyCustomAnalyzer(SharedThis(this));
    }

    virtual bool ProcessMessages() override
    {
        // 处理接收到的消息
        // ...
        return FTraceProviderBase::ProcessMessages();
    }

private:
    class FMyCustomAnalyzer : public FTraceAnalyzerBase
    {
    public:
        FMyCustomAnalyzer(TSharedRef<FMyCustomTraceProvider> InProvider)
            : FTraceAnalyzerBase(InProvider)
        {
        }

        virtual void OnAnalysisBegin(const FOnAnalysisContext& Context) override
        {
            FTraceAnalyzerBase::OnAnalysisBegin(Context);
            // 注册要监听的 trace events
        }

        virtual void OnEvent(uint16 RouteId, const FOnEventContext& Context) override
        {
            // 处理 trace event
        }
    };
};
```

### 创建可缓存消息

```cpp
// 消息必须继承 IAudioCachedMessage 并接受 FOnEventContext 构造参数
struct FMyCustomMessage : public UE::Audio::Insights::IAudioCachedMessage
{
    FMyCustomMessage() = default;
    FMyCustomMessage(const Trace::IAnalyzer::FOnEventContext& InContext)
    {
        // 从 trace event context 解析数据
        const auto& EventData = Context.EventData;
        MyValue = EventData.GetValue<float>("MyValue");
        Timestamp = Context.EventTime.AsSeconds();
    }

    virtual uint32 GetSizeOf() const override { return sizeof(FMyCustomMessage); }
    virtual uint64 GetID() const override { return MyId; }
    virtual const FName GetMessageName() const override { return FName("MyCustom"); }

    uint64 MyId = 0;
    float MyValue = 0.0f;
};
```

### 使用缓存管理器查询历史数据

```cpp
#if WITH_EDITOR
UE::Audio::Insights::FAudioInsightsCacheManager& CacheManager = 
    IAudioInsightsModule::GetChecked().GetCacheManager();

// 查找最接近某个时间戳的消息
const FSubmixLoadedMessage* Msg = CacheManager.FindClosestMessage<FSubmixLoadedMessage>(
    SubmixMessageNames::Loaded,  // 消息名称
    CurrentTimestamp,             // 目标时间戳
    SubmixId                     // 可选：按 ID 过滤
);

// 遍历时间范围内的消息
CacheManager.IterateOverRange<FSubmixEnvelopeValuesMessage>(
    SubmixMessageNames::EnvelopeValues,
    StartTime,
    EndTime,
    [](const FSubmixEnvelopeValuesMessage& Message)
    {
        // 处理每条消息
    },
    SubmixId  // 可选：按 ID 过滤
);

// 获取缓存信息
float Duration = CacheManager.GetCacheDuration();
uint32 UsedSize = CacheManager.GetUsedCacheSize();
uint32 MaxSize = CacheManager.GetMaxCacheSize();
#endif
```

### 使用消息队列

```cpp
// 创建线程安全的消息队列
UE::Audio::Insights::TAnalyzerMessageQueue<FMyCustomMessage> MessageQueue(5.0); // 5秒历史

// 生产者线程：入队
MessageQueue.Enqueue(FMyCustomMessage(EventContext));

// 消费者线程：出队所有消息
TArray<FMyCustomMessage> Messages = MessageQueue.DequeueAll();
for (const FMyCustomMessage& Msg : Messages)
{
    // 处理消息
}
```

## Demo 示例

### 自定义 Dashboard 视图工厂

```cpp
// MyCustomDashboardViewFactory.h
#pragma once

#include "Views/DashboardViewFactory.h"

class FMyCustomDashboardViewFactory : public UE::Audio::Insights::IDashboardViewFactory
{
public:
    FMyCustomDashboardViewFactory() = default;
    virtual ~FMyCustomDashboardViewFactory() = default;

    virtual FName GetName() const override
    {
        return FName("MyCustomDashboard");
    }

    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("My Custom Dashboard"));
    }

    virtual UE::Audio::Insights::EDefaultDashboardTabStack GetDefaultTabStack() const override
    {
        return UE::Audio::Insights::EDefaultDashboardTabStack::Analysis;
    }

    virtual FSlateIcon GetIcon() const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports");
    }

    virtual TSharedRef<SWidget> MakeWidget(
        TSharedRef<SDockTab> OwnerTab, 
        const FSpawnTabArgs& SpawnTabArgs) override
    {
        // 创建自定义仪表板 UI
        return SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("My Custom Audio Dashboard")))
            ]
            + SVerticalBox::Slot()
            .FillHeight(1.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("Custom content goes here...")))
            ];
    }
};
```

```cpp
// MyCustomDashboardViewFactory.cpp
#include "MyCustomDashboardViewFactory.h"

// 注册（通常在模块 StartupModule 中）
void RegisterMyDashboard()
{
    IAudioInsightsModule& Module = IAudioInsightsModule::GetChecked();
    Module.RegisterDashboardViewFactory(
        MakeShared<FMyCustomDashboardViewFactory>());
}
```

### 使用可见列设置系统

```cpp
// MyDashboardSettings.h
#pragma once

#include "Settings/VisibleColumnsSettings.h"
#include "MyDashboardSettings.generated.h"

USTRUCT()
struct FMyDashboardVisibleColumns : public UE::Audio::Insights::FVisibleColumnsSettings
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, config)
    bool bName = true;

    UPROPERTY(EditAnywhere, config)
    bool bValue = true;

    UPROPERTY(EditAnywhere, config)
    bool bTimestamp = false;

    virtual const FProperty* FindProperty(const FName& PropertyName) const override
    {
        return StaticStruct()->FindPropertyByName(PropertyName);
    }
};
```

```cpp
// 在 Dashboard 视图中使用列设置菜单
void FMyDashboardViewFactory::AddColumnSettingsMenu(FMenuBuilder& MenuBuilder)
{
    auto SettingsMenu = MakeShared<UE::Audio::Insights::FVisibleColumnsSettingsMenu<FMyDashboardVisibleColumns>>(
        HeaderRowWidget, 
        MyVisibleColumnSettings);

    SettingsMenu->BuildVisibleColumnsMenuContent(MenuBuilder);

    // 监听列可见性变化
    SettingsMenu->OnVisibleColumnsSettingsUpdated.AddLambda([this]()
    {
        RefreshColumnVisibility();
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights Trace 分析服务（会话管理、Provider 注册） |
| `Trace` | Unreal Insights Trace 底层系统（Analyzer、Event Context） |
| `AudioWidgets` | 音频 UI 控件（插件依赖，提供 SAudioMeterWidget 等） |
| `DSP` | 数字信号处理工具（分贝转换等） |
| `AudioMixer` | 音频混音器设备接口 |
| `AssetRegistry` | 资产注册表（追踪音频资产的添加/移除） |
| `RewindDebugger` | 回溯调试器集成（IRewindDebuggerRuntimeExtension） |

## 维护状态

### 近期更新

```
- 3f2e5071f0dd [Audio Insights] Submix dashboard: Separate alive ping message from loaded message to avoid requesting sending cvar to activate audio meter every second.
- 763496ee2fe3 [Audio Insights] Fix for enable plot button color not matching curve after inspecting a timestamp, and plots not immediately appearing when enabling plots while processing is paused.
- 9778e926bedf [Audio Insights] BugHawk fixes for CLs 46514818 and 46514823
```

- 第一条：优化 Submix 仪表板的消息分离，避免每秒重复发送 CVar 激活音频电平表
- 第二条：修复绘图按钮颜色不匹配曲线的问题，以及处理暂停时启用绘图不立即显示的问题
- 第三条：BugHawk 自动化测试修复

### 维护评价

**活跃维护中** ✅

- **创建时间**：2023-12-01，约 2 年历史，属于较新的插件
- **维护状态**：持续活跃开发，近期有功能优化和 Bug 修复
- **Beta 状态**：标记为 `IsBetaVersion=true`，API 和功能可能随版本变化
- **Epic 官方维护**：由 Epic Games 开发和维护，质量有保障
- **架构成熟度**：代码架构清晰（Provider → Cache → Dashboard），扩展性好

**注意事项**：
- 作为 Beta 插件，部分 API 可能在未来版本中发生变化
- `SupportedPrograms` 限制为 `UnrealInsights`，意味着 AudioInsights 模块仅在编辑器和 UnrealInsights 程序中加载
- 依赖 AudioWidgets 插件，需确保该插件已启用

**推荐使用**：适合需要深度音频调试和性能分析的项目。作为 Epic 官方工具，与 Unreal Insights 集成度高，是音频性能分析的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights)
- [AudioInsights 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights/Source/AudioInsights)
- [AudioInsightsEditor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights/Source/AudioInsightsEditor)