# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频洞察 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（仪表盘模板、UI组件） |
| 模块 | `AudioInsights` (Runtime), `AudioInsightsEditor` (EditorNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights) | |

## 用途

AudioInsights 是一个**音频性能分析和调试框架**，旨在为 Unreal Engine 的音频系统提供专业的监控和诊断工具。

**核心问题**：传统的音频调试依赖日志和断点，缺乏实时的可视化分析。该插件将音频事件（如音源创建、销毁、音量变化）转化为结构化数据，并集成到 Unreal Insights 的 Timing 和 Dashboard 视图中。

**解决方案**：
1. **实时性能监控**：追踪音频线程活动、内存分配和资源状态。
2. **可视化仪表盘**：将音频数据以表格和图表形式呈现，支持按对象、设备或时间过滤。
3. **时间轴回放**：在 Timing 视图中查看音频事件在时间线上的分布，辅助定位延迟问题。
4. **模板化扩展**：提供插件模板，开发者可快速创建自定义音频分析仪表盘。

## 使用场景

- **性能优化**：当游戏出现音频卡顿或延迟时，使用 AudioInsights 分析音频线程的负载和阻塞点。
- **资源管理**：监控音频内存使用，识别未释放的音源或资源泄漏。
- **调试音频逻辑**：在蓝图或 C++ 中触发音频事件后，通过仪表盘实时查看事件是否正确触发。
- **创建自定义分析工具**：基于提供的模板，为特定音频子系统（如音效混合、空间音频）开发专属监控面板。

## 蓝图用法

AudioInsights 主要面向**编辑器工具**和**Unreal Insights 程序**，不直接提供运行时蓝图节点。其功能通过 Unreal Insights 的 UI 和自定义仪表盘访问。

### 核心节点（无）

> 该插件无 BlueprintCallable 函数，所有功能通过 Unreal Insights 的界面操作。

## C++ 用法

### 头文件引入

```cpp
#include "AudioInsights.h"
#include "AudioInsightsEditor.h"
```

### 基本用法（创建自定义仪表盘）

该插件的核心用法是扩展 `FTraceObjectTableDashboardViewFactory` 来创建自定义分析面板。模板代码位于 `Templates/Basic/`。

**1. 定义消息结构体** (ObjectTraceMessages.h):
```cpp
// 定义你的音频事件消息
struct FMyAudioEventMessage : public UE::Audio::Insights::IAudioCachedMessage
{
    virtual uint64 GetID() const override { return ID; }
    virtual const FName GetMessageName() const override { return MyMessageNames::EventName; }
    
    uint32 ID;
    float Volume;
    // ... 其他音频属性
};
```

**2. 创建追踪提供者** (ObjectTraceProvider.h):
```cpp
class FMyAudioTraceProvider : public UE::Audio::Insights::TDeviceDataMapTraceProvider<uint32, TSharedPtr<FMyDashboardEntry>>
{
public:
    // 构造分析器来处理 Unreal Trace 事件
    virtual UE::Trace::IAnalyzer* ConstructAnalyzer(TraceServices::IAnalysisSession& InSession) override;
    
private:
    // 在游戏线程上处理消息队列，更新仪表盘条目
    virtual bool ProcessMessages() override;
    
    // 响应时间轴拖拽，重建特定时间点的状态
    virtual void OnTimingViewTimeMarkerChanged(double TimeMarker) override;
};
```

**3. 定义视图工厂** (ObjectDashboardViewFactory.h):
```cpp
class FMyDashboardViewFactory : public UE::Audio::Insights::FTraceObjectTableDashboardViewFactory
{
public:
    virtual FName GetName() const override;
    virtual FText GetDisplayName() const override;
    
private:
    // 定义表格列（ID、音量、状态等）
    virtual const TMap<FName, FColumnData>& GetColumns() const override;
    
    // 过滤和排序条目
    virtual void ProcessEntries(EProcessReason Reason) override;
    virtual void SortTable() override;
};
```

### 进阶用法（注册自定义图标和样式）

```cpp
// PLUGIN_NAMEStyle.cpp
FStyle::FStyle() : FSlateStyleSet("MyAudioInsightsStyle")
{
    // 注册自定义图标
    Set("MyAudioIcon", new FSlateImageBrush("MyIcon.png", FVector2D(16, 16)));
    
    // 注册彩色状态指示器
    Set("StatusActive", new FSlateColorBrush(FLinearColor::Green));
    Set("StatusInactive", new FSlateColorBrush(FLinearColor::Red));
}

// 在仪表盘中使用
FSlateIcon FMyDashboardViewFactory::GetIcon() const
{
    return FSlateIcon(FStyle::GetStyleName(), "MyAudioIcon");
}
```

**来源文件**: `Templates/Basic/Source/PLUGIN_NAME/Private/PLUGIN_NAMEStyle.cpp`

## Demo 示例

以下是一个最小的自定义音频对象仪表盘实现，用于监控音源的音量变化：

### MyAudioMonitor.h
```cpp
#pragma once
#include "AudioInsights.h"

namespace MyAudioMonitor
{
    struct FVolumeMessage : public UE::Audio::Insights::IAudioCachedMessage
    {
        virtual uint64 GetID() const override { return ObjectID; }
        virtual const FName GetMessageName() const override { return "VolumeUpdate"; }
        
        uint32 ObjectID;
        float Volume = 0.0f;
        double Timestamp = 0.0;
    };
    
    class FVolumeTraceProvider : public UE::Audio::Insights::TDeviceDataMapTraceProvider<uint32, TSharedPtr<FVolumeEntry>>
    {
    public:
        FVolumeTraceProvider();
        virtual UE::Trace::IAnalyzer* ConstructAnalyzer(TraceServices::IAnalysisSession& InSession) override;
        
    private:
        virtual bool ProcessMessages() override;
        virtual void OnTimingViewTimeMarkerChanged(double TimeMarker) override;
        
        UE::Audio::Insights::TAnalyzerMessageQueue<FVolumeMessage> VolumeMessages;
    };
    
    class FVolumeDashboardFactory : public UE::Audio::Insights::FTraceObjectTableDashboardViewFactory
    {
    public:
        FVolumeDashboardFactory();
        
        virtual FName GetName() const override { return "MyVolumeMonitor"; }
        virtual FText GetDisplayName() const override { return FText::FromString("音量监控器"); }
        
    private:
        virtual const TMap<FName, FColumnData>& GetColumns() const override;
    };
}
```

### MyAudioMonitor.cpp
```cpp
#include "MyAudioMonitor.h"

namespace MyAudioMonitor
{
    // 构造分析器（在追踪分析线程运行）
    UE::Trace::IAnalyzer* FVolumeTraceProvider::ConstructAnalyzer(TraceServices::IAnalysisSession& InSession)
    {
        class FVolumeAnalyzer : public UE::Trace::IAnalyzer
        {
        public:
            FVolumeAnalyzer(UE::Audio::Insights::TAnalyzerMessageQueue<FVolumeMessage>& InQueue)
                : MessageQueue(InQueue) {}
                
            virtual void OnAnalysisBegin(const FOnAnalysisContext& Context) override
            {
                FEventRouteBuilder<1> RouteBuilder(Context);
                // 注册音频音量事件的路由
                RouteBuilder.AddRoute("Audio.VolumeChanged");
            }
            
            virtual void OnEvent(uint16 RouteId, const FOnEventContext& Context) override
            {
                // 解析事件数据并加入队列
                FVolumeMessage Message;
                Message.ObjectID = Context.EventData.GetValue<uint32>("ObjectID");
                Message.Volume = Context.EventData.GetValue<float>("Volume");
                Message.Timestamp = Context.EventTime.AsSeconds(InSession.GetTraceTime());
                
                MessageQueue.Enqueue(Message);
            }
            
        private:
            UE::Audio::Insights::TAnalyzerMessageQueue<FVolumeMessage>& MessageQueue;
        };
        
        return new FVolumeAnalyzer(VolumeMessages);
    }
    
    // 在游戏线程上处理消息
    bool FVolumeTraceProvider::ProcessMessages()
    {
        auto ProcessLambda = [this](const FVolumeMessage& Msg)
        {
            TSharedPtr<FVolumeEntry>* Entry = DeviceDataMap.Find(Msg.ObjectID);
            if (!Entry)
            {
                Entry = &DeviceDataMap.Add(Msg.ObjectID, MakeShared<FVolumeEntry>());
            }
            
            (*Entry)->Volume = Msg.Volume;
            (*Entry)->LastUpdate = Msg.Timestamp;
            return true;
        };
        
        VolumeMessages.ProcessMessages(ProcessLambda);
        return true;
    }
    
    // 定义表格列
    const TMap<FName, FColumnData>& FVolumeDashboardFactory::GetColumns() const
    {
        static TMap<FName, FColumnData> Columns;
        if (Columns.Num() == 0)
        {
            Columns.Add("ID", {FText::FromString("对象ID"), 80, EColumnSortMode::None});
            Columns.Add("Volume", {FText::FromString("当前音量"), 120, EColumnSortMode::Ascending});
            Columns.Add("LastUpdate", {FText::FromString("最后更新时间"), 150, EColumnSortMode::Descending});
        }
        return Columns;
    }
    
    // 构造函数：注册到 Audio Insights 系统
    FVolumeDashboardFactory::FVolumeDashboardFactory()
    {
        // 创建并注册追踪提供者
        auto Provider = MakeShared<FVolumeTraceProvider>();
        Provider->Initialize("VolumeProvider");
        
        // 将仪表盘工厂注册到 Audio Insights 系统
        UE::Audio::Insights::FTraceDashboardManager::Get().RegisterFactory(this);
    }
}
```

## 模块依赖

从 Build.cs 的依赖分析得出：

| 模块 | 用途 |
|---|---|
| `AudioWidgets` | 提供音频相关的 UI 控件和可视化组件 |
| `TraceServices` | 解析 Unreal Trace 事件流 |
| `TraceAnalysis` | 分析追踪数据的核心框架 |

**注意**：该插件还依赖于 Unreal Insights 程序的上下文，部分模块仅在 Unreal Insights 程序中加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `28c5c884` | [Audio Insights] Plugin template readme file to assist users when expanding Audio Insights with cust | 添加插件模板的说明文档，帮助用户自定义扩展 |
| 2026-05-19 | `a9b19eba` | [Audio Insights] Stop Event Log from automatically setting new items in the details panel when scrub | 修复时间轴拖拽时事件日志自动跳转的问题 |
| 2026-05-14 | `d492400a` | [Audio Insights] Fix localization for event log filter menu strings | 修复事件日志过滤器的本地化问题 |
| 2026-05-14 | `64ecb7b0` | [Audio Insights] Setting Audio Insights and Audio Insights Runtime plugins to be Production | 将插件标记为生产就绪状态 |
| 2026-05-14 | `62b99116` | [Audio Insights] Add user-adjustable node padding multipliers to signal flow graph settings menu. Tw | 添加信号流图的节点间距设置 |

### 维护评价

**综合评价：活跃维护且功能稳定**

- **创建时间**：2023年12月创建，相对年轻但已稳定运行2年。
- **活跃程度**：近期有持续的功能改进和错误修复，2026年5月有多次更新，表明仍处于活跃开发中。
- **生产状态**：已在2026年5月标记为生产就绪（Production），说明 Epic 认为其足够稳定。
- **功能完整性**：提供了完整的模板系统和工具链，支持开发者扩展自定义分析仪表盘。
- **已知限制**：依赖于 Unreal Insights 程序上下文，独立使用场景有限。
- **推荐使用**：✅ **强烈推荐**用于音频系统的性能分析和调试。特别适合需要深入分析音频性能瓶颈的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights)
- [插件模板](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights/Templates/Basic)