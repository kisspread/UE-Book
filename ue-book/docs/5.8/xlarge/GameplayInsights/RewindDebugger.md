# Animation Insights

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | 动画洞察调试器 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

这是一个基于 Unreal Insights 基础设施构建的**时间回溯调试器（Rewind Debugger）**。它不仅仅是动画调试工具，而是一套完整的"时间旅行"调试系统：

1. **录制游戏数据**：在 PIE 或独立进程中录制动画姿态、对象状态、事件等 Trace 数据
2. **时间回放与拖拽**：在时间轴上自由拖拽，查看任意时刻的游戏状态快照
3. **多对象追踪**：同时追踪多个游戏对象及其子对象的生命周期和状态变化
4. **动画姿态重放**：将录制的骨骼网格体姿态重新应用到编辑器中的预览组件上
5. **相机回放**：回放录制的相机数据，或让相机跟随调试目标
6. **远程会话分析**：支持连接远程进程的 Trace 会话，也可打开 .utrace 文件进行离线分析

插件默认禁用（`EnabledByDefault: false`），需要在插件管理器中手动启用。`SupportedPrograms` 设为 `UnrealInsights`，表明它作为 Unreal Insights 的扩展插件运行。

## 使用场景

- 你在开发角色动画系统，需要回看某个动画姿态在某一帧的具体状态 → 用 Rewind Debugger 的动画回放功能
- 你在调试多角色战斗，需要对比不同对象在同一时刻的行为 → 用多对象时间轴追踪
- 你在调试网络同步问题，需要连接远程服务器的 Trace 会话 → 用远程会话连接功能
- 你有一份之前录制的 .utrace 文件，需要离线分析动画表现 → 用 Open Trace 功能
- 你需要为自定义的游戏系统添加调试时间轴（如 AI 决策、技能系统）→ 实现 `IRewindDebuggerTrackCreator` 扩展

## 蓝图用法

本插件是编辑器级调试工具，不暴露蓝图节点。所有交互通过编辑器 UI（Rewind Debugger 面板）或 C++ 接口完成。

### 设置属性（配置类）

虽然不可在运行时蓝图中使用，但以下设置可在"项目设置 → Rewind Debugger"中配置：

| 设置 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `CameraMode` | `ERewindDebuggerCameraMode` | 回放时相机模式：录制回放/跟随目标/禁用 | `URewindDebuggerSettings` |
| `ObjectTrackSortMode` | `ERewindDebuggerObjectSortMode` | 对象轨道排序方式：按时间/按名称 | `URewindDebuggerSettings` |
| `bShouldAutoEject` | `bool` | PIE 暂停时自动断开玩家控制 | `URewindDebuggerSettings` |
| `bShouldAutoRecordOnPIE` | `bool` | PIE 启动时自动开始录制 | `URewindDebuggerSettings` |
| `PlaybackRate` | `float` | 播放速度倍率 | `URewindDebuggerSettings` |
| `bShowEmptyObjectTracks` | `bool` | 是否在时间轴上显示空轨道 | `URewindDebuggerSettings` |
| `HiddenTrackTypes` | `TArray<FName>` | 隐藏的轨道类型列表 | `URewindDebuggerSettings` |
| `SelectorAllowedTypes` | `TArray<FSoftClassPath>` | 目标选择器允许的类类型 | `URewindDebuggerProjectSettings` |

### 快捷键命令

| 命令 | 快捷键 | 说明 |
|---|---|---|
| 暂停/播放 | `Space` | 切换录制播放状态 |
| 开始录制 | `Ctrl+Shift+R` | 开始录制游戏数据 |
| 停止录制 | `Ctrl+Shift+S` | 停止录制 |
| 第一帧 | `Up` | 跳转到第一帧 |
| 上一帧 | `Left` | 后退一帧 |
| 反向播放 | `Ctrl+Shift+Space` | 反向回放 |
| 播放 | `Down` | 正向播放 |
| 下一帧 | `Right` | 前进一帧 |
| 最后一帧 | `Ctrl+Up` | 跳转到最后一帧 |

## C++ 用法

### 核心接口

本插件的公共 API 基于一组接口，允许扩展和集成：

| 接口 | 用途 |
|---|---|
| `IRewindDebugger` | 调试器核心接口，提供回放控制、对象查询、时间管理 |
| `IRewindDebuggerModule` | 模块接口，提供 Tab 注册和 Widget 生成 |
| `IRewindDebuggerExtension` | 调试器扩展接口，可注入自定义更新逻辑（如动画回放、相机跟随） |
| `IRewindDebuggerTrackCreator` | 轨道创建器接口，为自定义系统创建调试轨道 |
| `IRewindDebuggerViewCreator` | 视图创建器接口，创建自定义详情视图 |
| `IRewindDebuggerDoubleClickHandler` | 双击处理器接口，处理轨道双击事件 |

### 头文件引入

```cpp
#include "IRewindDebugger.h"
#include "IRewindDebuggerModule.h"
#include "RewindDebuggerSettings.h"
```

### 基本用法 - 获取调试器实例并控制回放

```cpp
// 获取 Rewind Debugger 单例
FRewindDebugger* Debugger = FRewindDebugger::Instance();
if (!Debugger) return;

// 查询当前状态
bool bRecording = Debugger->IsRecording();
bool bSimulating = Debugger->IsPIESimulating();
double Duration = Debugger->GetRecordingDuration();
double CurrentTime = Debugger->GetScrubTime();

// 回放控制
Debugger->Play();           // 正向播放
Debugger->Pause();          // 暂停
Debugger->PlayReverse();    // 反向播放
Debugger->ScrubToStart();   // 跳到开头
Debugger->ScrubToEnd();     // 跳到结尾
Debugger->StepForward();    // 前进一帧
Debugger->StepBackward();   // 后退一帧

// 拖拽到指定时间
Debugger->ScrubToTime(5.0, /*bIsScrubbing=*/false);

// 录制控制
if (Debugger->CanStartRecording())
{
    Debugger->StartRecording();
}

// 获取当前分析会话
const TraceServices::IAnalysisSession* Session = Debugger->GetAnalysisSession();
```

### 基本用法 - 创建自定义调试扩展

```cpp
// 来源: Private/RewindDebuggerAnimation.h, Private/RewindDebuggerCamera.h

// 实现 IRewindDebuggerExtension 来为自定义系统添加调试支持
class FMyGameExtension : public IRewindDebuggerExtension
{
public:
    virtual FString GetName() override
    {
        return TEXT("MyGameExtension");
    }

    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override
    {
        // 获取当前回放时间和调试对象
        double ScrubTime = RewindDebugger->GetScrubTime();
        uint64 RootObjectId = RewindDebugger->GetRootObjectId();
        const TraceServices::IAnalysisSession* Session = RewindDebugger->GetAnalysisSession();

        // 在此处根据 ScrubTime 更新自定义系统状态
        // 例如：读取 Trace 数据中的自定义事件，更新 UI 预览等
    }

    virtual void Clear(IRewindDebugger* RewindDebugger) override
    {
        // 清理所有临时生成的预览资源
    }
};
```

### 进阶用法 - 连接远程会话

```cpp
// 需要 UE_WITH_TRACE_BASED_DEBUGGERS_ANALYSIS 宏
#if UE_WITH_TRACE_BASED_DEBUGGERS_ANALYSIS

FRewindDebugger* Debugger = FRewindDebugger::Instance();

// 连接到远程 Trace 会话（直连模式）
FGuid RemoteSessionID = /* 从会话列表获取 */;
bool bConnected = Debugger->ConnectToLiveSession_Direct(RemoteSessionID);

// 或通过 Relay 连接
bool bRelayConnected = Debugger->ConnectToLiveSession_Relay(RemoteSessionID);

// 分析会话管理
const UE::TraceBasedDebuggers::FTraceSessionDescriptor& Descriptor =
    Debugger->GetCurrentSessionDescriptor();

// 清理分析会话
Debugger->ClearAnalysisSessionLinkedToRemoteSessionID(RemoteSessionID);

#endif
```

### 进阶用法 - 查询调试对象和轨道

```cpp
FRewindDebugger* Debugger = FRewindDebugger::Instance();

// 获取所有正在调试的对象
TArray<TSharedPtr<FDebugObjectInfo>>& Objects = Debugger->GetDebuggedObjects();
for (auto& Obj : Objects)
{
    // 每个 FDebugObjectInfo 包含对象 ID、名称、类型等信息
}

// 检查特定对象是否正在调试
uint64 ObjectId = /* 某个对象的 ID */;
bool bDebugging = Debugger->IsObjectCurrentlyDebugged(ObjectId);

// 获取当前选中的对象和轨道
TSharedPtr<FDebugObjectInfo> SelectedObj = Debugger->GetSelectedObject();
TSharedPtr<RewindDebugger::FRewindDebuggerTrack> SelectedTrack = Debugger->GetSelectedTrack();

// 获取所有轨道
TArray<TSharedPtr<RewindDebugger::FRewindDebuggerTrack>>& Tracks = Debugger->GetTracks();

// 获取轨道类型（用于 UI 渲染）
TArrayView<RewindDebugger::FRewindDebuggerTrackType> TrackTypes = Debugger->GetTrackTypes();

// 选择特定轨道
Debugger->SelectTrack(ObjectId);

// 刷新轨道列表（当调试目标变化时调用）
Debugger->RefreshDebugTracks();
```

## Demo 示例

以下示例展示如何创建一个自定义的 Rewind Debugger 扩展，为自定义游戏系统添加时间轴调试支持：

### MyRewindExtension.h

```cpp
#pragma once

#include "IRewindDebugger.h"

// 自定义扩展：在 Rewind Debugger 中显示自定义的游戏事件轨道
class FMyRewindExtension : public RewindDebugger::IRewindDebuggerExtension
{
public:
    FMyRewindExtension();
    virtual ~FMyRewindExtension();

    void Initialize();
    void Shutdown();

    // IRewindDebuggerExtension interface
    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override;
    virtual void Clear(IRewindDebugger* RewindDebugger) override;
    virtual FString GetName() override { return TEXT("MyRewindExtension"); }

    static FMyRewindExtension* GetInstance() { return Instance; }

private:
    // 存储从 Trace 数据中提取的自定义事件
    struct FMyEventData
    {
        double Time;
        FString EventName;
        int32 Value;
    };

    TArray<FMyEventData> CachedEvents;
    double LastScrubTime = -1.0;
    bool bDataDirty = true;

    static FMyRewindExtension* Instance;
};
```

### MyRewindExtension.cpp

```cpp
#include "MyRewindExtension.h"
#include "TraceServices/AnalysisSession.h"

FMyRewindExtension* FMyRewindExtension::Instance = nullptr;

FMyRewindExtension::FMyRewindExtension()
{
    Instance = this;
}

FMyRewindExtension::~FMyRewindExtension()
{
    Instance = nullptr;
}

void FMyRewindExtension::Initialize()
{
    // 初始化扩展，注册事件监听等
}

void FMyRewindExtension::Shutdown()
{
    Clear(nullptr);
}

void FMyRewindExtension::Update(float DeltaTime, IRewindDebugger* RewindDebugger)
{
    if (!RewindDebugger)
    {
        return;
    }

    const TraceServices::IAnalysisSession* Session = RewindDebugger->GetAnalysisSession();
    if (!Session)
    {
        return;
    }

    double CurrentTime = RewindDebugger->GetScrubTime();

    // 仅在时间变化时更新缓存数据
    if (!FMath::IsNearlyEqual(CurrentTime, LastScrubTime) || bDataDirty)
    {
        LastScrubTime = CurrentTime;
        bDataDirty = false;

        // 在此读取 Trace 数据中的自定义通道
        // 例如：遍历当前帧范围内所有事件，更新 CachedEvents
        CachedEvents.Reset();

        // 模拟：从 Trace 数据中提取事件
        // 实际实现需要通过 IGameplayProvider 或自定义 Provider 查询
    }

    // 根据 CachedEvents 更新预览组件或 UI
}

void FMyRewindExtension::Clear(IRewindDebugger* RewindDebugger)
{
    CachedEvents.Reset();
    LastScrubTime = -1.0;
    bDataDirty = true;
}
```

## 模块依赖

本插件的模块依赖较多，因为需要集成 Unreal Insights 分析框架和编辑器调试 UI。以下列出非标准依赖：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 分析服务，提供 Trace 会话和数据查询 |
| `TraceAnalysis` | Trace 数据分析框架 |
| `TraceLog` | Trace 日志基础设施 |
| `ToolWidgets` | 编辑器工具控件（状态栏、会话选择器等） |
| `ToolMenus` | 编辑器菜单系统扩展 |
| `AnimationBlueprintLibrary` | 动画蓝图调试支持 |
| `SkeletalMeshDescription` | 骨骼网格体描述，用于姿态预览 |
| `Persona` | 动画编辑器模块 |
| `AnimationEditor` | 动画编辑器 UI |

> **注意**：具体的 Build.cs 依赖因模块而异。上述列表基于头文件分析推断，实际使用时请参考各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复吸管工具在重新附加玩家控制时未正确取消的问题 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger` | 在 IRewindDebugger 接口上添加可编程的拖拽和视图居中功能 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass | 对 Rewind Debugger 工具栏进行 UX 优化 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | Rewind Debugger 相关更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

**活跃维护**。从近期提交记录看，该插件在 2026 年 4-5 月仍有密集的功能性更新和 UX 优化，包括接口扩展（可编程拖拽）、UI 改进（工具栏 UX）和 bug 修复。

- **创建时间**：2019 年 10 月，已维护约 7 年
- **更新频率**：近期每月 2-3 次提交，内容涵盖功能扩展、UX 优化和代码质量改进
- **维护状态**：作为 Epic 官方维护的 Insights 扩展，持续活跃
- **注意事项**：插件默认禁用（`EnabledByDefault: false`），需手动启用；仅在支持 Unreal Insights 的环境中可用
- **推荐使用**：✅ 强烈推荐。这是 UE5 中最强大的时间回溯调试工具，对于动画系统开发和游戏行为分析极为有用。支持扩展，可为自定义系统添加时间轴调试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
- 官方文档（无）