# Animation Insights

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

GameplayInsights 是一个**运行时动画调试与分析系统**，它将游戏运行时的动画数据（骨骼姿态、动画节点状态、混合权重、曲线值等）通过 Unreal Insights 的 Trace 系统记录下来，并提供**时间回溯调试器（Rewind Debugger）**，允许开发者在编辑器中回放和检查历史动画状态。

这个插件解决的核心问题是：**动画系统是高度时序化的，传统的断点调试无法有效分析动画状态变化**。通过录制完整的动画 Trace 数据，开发者可以：
- 回溯到任意时间点查看骨骼姿态
- 检查动画蓝图中每个节点的输入/输出
- 分析混合空间的权重变化
- 查看动画曲线随时间的变化
- 调试 Pose Watch（姿态监视点）

插件由 6 个模块组成，分为三层：
1. **Runtime 层**：`RewindDebuggerRuntime`、`RewindDebuggerVLogRuntime` — 在游戏运行时收集 Trace 数据
2. **分析层**：`GameplayInsights`、`RewindDebugger`、`RewindDebuggerVLog` — 解析 Trace 数据并提供 Provider 接口
3. **UI 层**：`GameplayInsightsEditor` — 编辑器中的可视化界面和时间线控件

## 使用场景

- 你在调试动画蓝图中的混合逻辑，需要查看某个 AnimNode 在不同时间点的 BlendWeight → 用 Rewind Debugger 回溯检查
- 你需要分析角色在一段时间内的骨骼姿态变化，定位穿模或抖动问题 → 用 Insights 录制骨骼 Pose 数据
- 你在开发自定义动画节点，需要验证节点的输入曲线和输出姿态 → 用 CurveTimelineView 和 PoseWatch
- 你需要在运行时检查 Gameplay Object 的属性变化轨迹 → 用 GameplayProvider 的属性追踪功能
- 你在做性能优化，需要查看动画 Tick 的时序和频率 → 用 TickRecord 数据分析

## 模块架构

```
GameplayInsights/
├── Source/
│   ├── GameplayInsights/          ← 核心分析模块（Provider 接口、UI 控件）
│   ├── GameplayInsightsEditor/    ← 编辑器集成（Insights 面板、菜单）
│   ├── RewindDebugger/            ← 回溯调试器框架（Track 系统、时间控制）
│   ├── RewindDebuggerRuntime/     ← 运行时 Trace 数据收集
│   ├── RewindDebuggerVLog/        ← Visual Logger 集成分析
│   └── RewindDebuggerVLogRuntime/ ← Visual Logger 运行时收集
```

### 模块职责

| 模块 | 职责 |
|---|---|
| `GameplayInsights` | 核心 Provider 接口（`IGameplayProvider`、`IAnimationProvider`）、时间线 UI 控件、对象属性序列化 |
| `GameplayInsightsEditor` | Insights 工具面板集成、动画调试 UI、菜单扩展 |
| `RewindDebugger` | 回溯调试器核心框架、Track 抽象基类、时间轴控制器 |
| `RewindDebuggerRuntime` | 运行时 Trace Channel 注册、动画数据写入 |
| `RewindDebuggerVLog` | Visual Logger 数据的分析和展示 |
| `RewindDebuggerVLogRuntime` | Visual Logger 数据的运行时 Trace 收集 |

## 蓝图用法

本插件主要面向**编辑器工具开发**和**C++ 扩展**，不提供常规的 BlueprintCallable 节点。其核心接口通过 C++ 模块接口和 Provider 模式暴露。

### 编辑器操作

1. **启用插件**：在 Edit → Plugins 中搜索 "Animation Insights"，启用后重启编辑器
2. **启动 Trace**：通过 Unreal Insights 工具或编辑器菜单启动动画数据录制
3. **打开 Rewind Debugger**：Window → Developer Tools → Rewind Debugger
4. **回溯调试**：在 Rewind Debugger 时间轴上点击任意时间点查看动画状态

## C++ 用法

### 核心接口

#### IGameplayInsightsModule

模块主接口，用于控制对象属性追踪和 Trace 录制。

```cpp
#include "IGameplayInsightsModule.h"

// 获取模块接口
IGameplayInsightsModule& Module = FModuleManager::Get().LoadModuleChecked<IGameplayInsightsModule>("GameplayInsights");

#if WITH_EDITOR
// 启用某个 UObject 的属性追踪
Module.EnableObjectPropertyTrace(MyActor, true);

// 检查是否已启用追踪
bool bTracing = Module.IsObjectPropertyTraceEnabled(MyActor);

// 启动全局 Trace 录制
Module.StartTrace();
#endif
```

#### IGameplayProvider

提供对 Trace 数据中 Gameplay 对象信息的访问。

```cpp
#include "IGameplayProvider.h"

// 通过 AnalysisSession 获取 Provider
const IGameplayProvider* GameplayProvider = Session.ReadProvider<IGameplayProvider>("GameplayProvider");

// 获取对象信息
const FObjectInfo* ObjectInfo = GameplayProvider->GetObjectInfo(ObjectId);
if (ObjectInfo)
{
    UE_LOG(LogTemp, Log, TEXT("Object: %s, Class: %llu"), ObjectInfo->Name, ObjectInfo->ClassId);
}

// 获取类信息
const FClassInfo* ClassInfo = GameplayProvider->GetClassInfo(ObjectInfo->ClassId);
```

#### IAnimationProvider

提供对动画 Trace 数据的访问，包括骨骼姿态、动画节点、曲线等。

```cpp
#include "IAnimationProvider.h"

const IAnimationProvider* AnimationProvider = Session.ReadProvider<IAnimationProvider>("AnimationProvider");

// 遍历骨骼网格体姿态数据
AnimationProvider->ReadSkeletalMeshPoseMessages(ComponentId, 
    [&](const FSkeletalMeshPoseMessage& PoseMessage)
    {
        // 访问骨骼变换
        // PoseMessage.TransformStartIndex 指向变换数据数组
        // PoseMessage.NumTransforms 是骨骼数量
        // PoseMessage.CurveStartIndex 指向曲线数据
    });

// 遍历动画 Tick 记录
AnimationProvider->ReadTickRecordMessages(ComponentId,
    [&](const FTickRecordMessage& TickRecord)
    {
        // TickRecord.BlendWeight - 混合权重
        // TickRecord.PlaybackTime - 播放时间
        // TickRecord.PlayRate - 播放速率
        // TickRecord.bLooping - 是否循环
    });
```

### 扩展 Rewind Debugger Track

通过继承 `FRewindDebuggerTrack` 来创建自定义的调试轨道。

```cpp
#include "RewindDebuggerTrack.h"
#include "RewindDebuggerPlaceholderTrack.h"

// 占位轨道（用于快速创建简单轨道）
class FMyCustomTrack : public FRewindDebuggerPlaceholderTrack
{
public:
    FMyCustomTrack(const FName& InObjectName, const FText& InDisplayName)
        : FRewindDebuggerPlaceholderTrack(InObjectName, InDisplayName)
    {
    }
};
```

### 对象属性序列化

使用 `FObjectAsTraceIdProxyArchiveReader` 从 Trace 数据中反序列化对象引用。

```cpp
#include "ObjectAsTraceIdProxyArchiveReader.h"

// 创建 Reader，将 Trace ID 解析为 UObject 引用
FObjectAsTraceIdProxyArchiveReader ArchiveReader(InnerArchive, GameplayProvider);

// 序列化对象引用（会自动从 Trace 数据中解析）
UObject* ResolvedObject = nullptr;
ArchiveReader << ResolvedObject;
```

### 时间线 UI 控件

#### SEventTimelineView

在 Slate UI 中显示事件时间线。

```cpp
#include "SEventTimelineView.h"

// 创建事件数据
auto EventData = MakeShared<SEventTimelineView::FTimelineEventData>();

// 添加时间点事件
SEventTimelineView::FTimelineEventData::EventPoint Point;
Point.Time = 1.5;
Point.Type = FText::FromString(TEXT("AnimNotify"));
Point.Description = FText::FromString(TEXT("FootStep"));
Point.Color = FLinearColor::Green;
EventData->Points.Add(Point);

// 添加时间窗口事件
SEventTimelineView::FTimelineEventData::EventWindow Window;
Window.TimeStart = 2.0;
Window.TimeEnd = 3.5;
Window.Type = FText::FromString(TEXT("Montage"));
Window.Description = FText::FromString(TEXT("AttackCombo"));
Window.Color = FLinearColor::Red;
EventData->Windows.Add(Window);

// 创建 Slate 控件
SNew(SEventTimelineView)
    .ViewRange_Lambda([this]() { return TRange<double>(0.0, 10.0); })
    .EventData(EventData)
    .DesiredSize(FVector2D(800.f, 40.f));
```

#### SCurveTimelineView

在 Slate UI 中显示曲线数据。

```cpp
#include "SCurveTimelineView.h"

// 创建曲线数据
auto CurveData = MakeShared<SCurveTimelineView::FTimelineCurveData>();

SCurveTimelineView::FTimelineCurveData::CurvePoint CurvePoint;
CurvePoint.Time = 1.0;
CurvePoint.Value = 0.75f;
CurveData->Points.Add(CurvePoint);

// 创建曲线控件
SNew(SCurveTimelineView)
    .ViewRange_Lambda([this]() { return TRange<double>(0.0, 10.0); })
    .CurveData(CurveData)
    .CurveColor(FLinearColor::Yellow)
    .FillColor(FLinearColor(1.0f, 1.0f, 0.0f, 0.2f))
    .RenderFill(true)
    .TrackName(FText::FromString(TEXT("BlendWeight")))
    .DesiredSize(FVector2D(800.f, 60.f));
```

## Demo 示例

### 自定义 Rewind Debugger Track

```cpp
// MyAnimationDebugTrack.h
#pragma once

#include "CoreMinimal.h"
#include "RewindDebuggerTrack.h"

class FMyAnimationDebugTrack : public RewindDebugger::FRewindDebuggerTrack
{
public:
    FMyAnimationDebugTrack(uint64 InObjectId);
    
    // FRewindDebuggerTrack 接口
    virtual bool UpdateInternal() override;
    virtual void IterateSubTracksInternal(TFunction<void(RewindDebugger::FRewindDebuggerTrack&)> IterFunction) override;
    
private:
    virtual FName GetNameInternal() const override;
    virtual FText GetDisplayNameInternal() const override;
    virtual uint64 GetObjectIdInternal() const override;
    
    uint64 ObjectId;
    TArray<TSharedPtr<RewindDebugger::FRewindDebuggerTrack>> Children;
};
```

```cpp
// MyAnimationDebugTrack.cpp
#include "MyAnimationDebugTrack.h"

FMyAnimationDebugTrack::FMyAnimationDebugTrack(uint64 InObjectId)
    : ObjectId(InObjectId)
{
}

FName FMyAnimationDebugTrack::GetNameInternal() const
{
    return FName(TEXT("MyAnimationDebug"));
}

FText FMyAnimationDebugTrack::GetDisplayNameInternal() const
{
    return FText::FromString(TEXT("My Animation Debug"));
}

uint64 FMyAnimationDebugTrack::GetObjectIDInternal() const
{
    return ObjectId;
}

bool FMyAnimationDebugTrack::UpdateInternal()
{
    // 从 Trace Session 中获取数据更新轨道状态
    // 返回 true 表示数据有变化需要刷新 UI
    return false;
}

void FMyAnimationDebugTrack::IterateSubTracksInternal(
    TFunction<void(RewindDebugger::FRewindDebuggerTrack&)> IterFunction)
{
    for (auto& Child : Children)
    {
        IterFunction(*Child);
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，本插件的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 的 Trace 数据分析框架，提供 AnalysisSession 和 Timeline 容器 |
| `TraceAnalysis` | Trace 数据分析引擎 |
| `RewindDebugger` | 回溯调试器核心框架（被 GameplayInsights 和 GameplayInsightsEditor 依赖） |
| `RewindDebuggerRuntime` | 运行时 Trace 数据收集（被 RewindDebugger 依赖） |
| `GameplayInsights` | 核心 Provider 接口（被 GameplayInsightsEditor 依赖） |
| `ToolWidgets` | 编辑器工具控件 |
| `Insights` | Unreal Insights 面板集成 |

## 维护状态

### 近期更新

```
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
- c5a00763e456 Add flags to gamplay tracing system in FObjectInfo. Use flags to differentiate between UAF graph assets, and transient UAF graphs, in order to avoid crashing on double click
- 72d075624de4 [RewindDebugger] deprecated IterateSubTracksInternal and replaced it by GetChildrenInternal that can be use to iterate subtracks and to visit all tracks recursively
```

- `ce6ff392ddca` — 编译警告修复，处理 `nodiscard` 属性的返回值
- `c5a00763e456` — 功能更新：为 `FObjectInfo` 添加标志位，区分 UAF 图资产和瞬态 UAF 图，修复双击崩溃问题
- `72d075624de4` — API 重构：废弃 `IterateSubTracksInternal`，替换为支持递归遍历的 `GetChildrenInternal`

### 维护评价

**活跃维护**。该插件虽然创建于 2019 年（约 6 年前），但近期仍有实质性功能更新和 API 改进。最近的 commit 包含：
- 新功能（ObjectInfo 标志位系统）
- API 现代化（废弃旧接口，引入新接口）
- 编译兼容性修复

作为 Epic Games 官方维护的动画调试工具链核心组件，它与 Unreal Insights 系统深度集成，是 UE5 动画开发调试的重要基础设施。**推荐使用**，特别是当你需要深入调试动画蓝图、分析动画性能或开发自定义动画调试工具时。

**注意事项**：
- 默认未启用（`EnabledByDefault: false`），需要手动在插件设置中启用
- 仅支持 `UnrealInsights` 程序（`SupportedPrograms`）
- 6 个模块全部标记为 Runtime 类型，但实际功能需要编辑器环境才能完整使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [官方文档]()（无）