# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageMonitorCommon` (Runtime), `StageDataProvider` (Runtime), `StageMonitor` (UncookedOnly), `StageMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

Stage Monitoring 是一个面向虚拟制片（Virtual Production）的多机监控系统。在 LED Volume 拍摄场景中，通常有多台机器协同工作——nDisplay 渲染节点、媒体服务器、追踪系统等——每台机器运行独立的 Unreal Engine 实例。Stage Monitoring 解决的核心问题是：**如何实时掌握所有机器的运行状态，在录制（Take）等关键时刻及时发现性能问题或系统故障**。

该插件采用 Provider/Monitor 架构：
- **StageDataProvider**（运行在每台被监控的机器上）：收集本机的帧性能、Genlock 同步、Timecode 等状态数据，通过 MessageBus 广播
- **StageMonitor**（运行在监控端）：发现并连接所有 Provider，收集数据，管理会话（Session），在编辑器面板中展示

关键特性：
- **自动发现**：Monitor 定期发送 Discovery 消息，Provider 自动响应并注册
- **会话 ID 过滤**：通过 `StageSessionId` 区分不同虚拟制片阶段的数据，避免多个舞台互相干扰
- **关键状态追踪**：当 Take Recorder 开始录制时，系统进入"关键状态"（Critical State），标记该时段的所有数据以便事后分析
- **Genlock 监控**：检测同步信号丢失（Missed Sync），这是 LED Volume 渲染中最严重的问题之一
- **Timecode Provider 监控**：监控时间码提供者的同步状态变化
- **帧性能报告**：定期发送 GameThread/RenderThread/GPU 时间、内存使用、平均 FPS 等数据
- **Hitch 检测**：可选的卡顿检测功能，当帧时间超过阈值时发送告警
- **会话持久化**：支持将监控会话保存到文件，事后加载分析

## 使用场景

- 你在做 LED Volume 虚拟制片，有多台 nDisplay 渲染节点 → 用 Stage Monitoring 实时监控所有节点的帧率和 Genlock 状态
- 你需要在 Take 录制期间监控所有机器是否有性能下降 → 开启 Critical State 追踪，录制期间的异常会被标记
- 你想在录制后回溯分析各机器的表现 → 使用 Session 保存/加载功能
- 你有多台机器通过 Timecode 同步 → 用 Timecode Provider Watchdog 监控同步状态

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 函数。它是一个纯 C++ 插件，通过编辑器面板（Stage Monitor Panel）和控制台命令进行交互。

编辑器中的操作：
1. 通过 **Window → Stage Monitor** 打开监控面板
2. 面板顶部有 Monitor 开关，可启动/停止监控
3. 支持 Live 模式（实时数据）和 Loaded 模式（加载历史会话）
4. 可通过工具栏保存/加载会话文件

## C++ 用法

### 头文件引入

```cpp
#include "IStageMonitorModule.h"
#include "IStageMonitor.h"
#include "IStageMonitorSession.h"
#include "IStageMonitorSessionManager.h"
#include "IStageDataProviderModule.h"
#include "StageMonitoringSettings.h"
#include "StageMonitorUtils.h"
```

### 基本用法 — 获取 Monitor 实例

```cpp
// 检查模块是否可用
if (IStageMonitorModule::IsAvailable())
{
    // 获取模块和 Monitor 实例
    IStageMonitorModule& MonitorModule = IStageMonitorModule::Get();
    IStageMonitor& Monitor = MonitorModule.GetStageMonitor();

    // 检查 Monitor 是否正在监听
    if (Monitor.IsActive())
    {
        // 获取当前活跃会话
        IStageMonitorSessionManager& SessionManager = MonitorModule.GetStageMonitorSessionManager();
        TSharedPtr<IStageMonitorSession> ActiveSession = SessionManager.GetActiveSession();

        if (ActiveSession.IsValid())
        {
            // 获取所有已连接的 Provider
            TConstArrayView<FStageSessionProviderEntry> Providers = ActiveSession->GetProviders();
            for (const FStageSessionProviderEntry& Provider : Providers)
            {
                // Provider.Descriptor 包含机器名、进程ID等信息
                // Provider.State 可以是 Active / Inactive / Closed
            }
        }
    }

    // 启用/禁用 Monitor
    MonitorModule.EnableMonitor(true);
}
```

来源: `IStageMonitorModule.h`, `IStageMonitor.h`

### 查询 Provider 最新数据

```cpp
// 获取某个 Provider 的最新帧性能数据
TSharedPtr<IStageMonitorSession> Session = SessionManager.GetActiveSession();
FGuid ProviderIdentifier = /* ... */;

TSharedPtr<FStageDataEntry> LatestEntry = Session->GetLatest(
    ProviderIdentifier, FFramePerformanceProviderMessage::StaticStruct());

if (LatestEntry.IsValid() && LatestEntry->Data.IsValid())
{
    FFramePerformanceProviderMessage* PerfData =
        LatestEntry->Data->GetPtr<FFramePerformanceProviderMessage>();
    if (PerfData)
    {
        float FPS = PerfData->AverageFPS;
        float GPUTime = PerfData->GPU_MS;
        uint64 CPUMem = PerfData->CPU_MEM;
        // ...
    }
}
```

来源: `IStageMonitorSession.h`, `StageMonitorUtils.h`

### 监听关键状态（Critical State）

```cpp
// 检查当前是否处于关键状态（如正在录制）
if (Session->IsStageInCriticalState())
{
    FName Source = Session->GetCurrentCriticalStateSource(); // e.g. "TakeRecorder"
}

// 查询某个时间点是否在关键状态范围内
double SomeTimestamp = /* ... */;
if (Session->IsTimePartOfCriticalState(SomeTimestamp))
{
    TArray<FName> Sources = Session->GetCriticalStateSources(SomeTimestamp);
}

// 获取历史关键状态来源
TArray<FName> HistorySources = Session->GetCriticalStateHistorySources();
```

来源: `IStageMonitorSession.h`

### 会话保存与加载

```cpp
IStageMonitorSessionManager& SessionManager = MonitorModule.GetStageMonitorSessionManager();

// 保存当前会话
SessionManager.SaveSession(TEXT("/path/to/session.json"));

// 监听保存完成
SessionManager.OnStageMonitorSessionSaved().AddLambda([]()
{
    // 保存完成
});

// 加载历史会话
SessionManager.LoadSession(TEXT("/path/to/session.json"));

// 监听加载完成
SessionManager.OnStageMonitorSessionLoaded().AddLambda([]()
{
    TSharedPtr<IStageMonitorSession> LoadedSession = SessionManager.GetLoadedSession();
    // 分析历史数据...
});
```

来源: `IStageMonitorSessionManager.h`

### 委托回调

```cpp
// 监听新数据到达
Session->OnStageSessionNewDataReceived().AddLambda(
    [](TSharedPtr<FStageDataEntry> NewData)
    {
        // 处理新数据
    });

// 监听 Provider 状态变化
Session->OnStageDataProviderStateChanged().AddLambda(
    [](const FGuid& Identifier, EStageDataProviderState NewState)
    {
        if (NewState == EStageDataProviderState::Inactive)
        {
            // Provider 超时，可能有网络问题
        }
    });

// 监听 Provider 列表变化
Session->OnStageDataProviderListChanged().AddLambda([]()
{
    // 有新的 Provider 连接或断开
});
```

来源: `IStageMonitorSession.h`

### 控制台命令

```cpp
// 非 Shipping/Test 构建下可用的控制台命令：
StageMonitor.Monitor.Start   // 启动监控
StageMonitor.Monitor.Stop    // 停止监控
```

来源: `StageMonitorModule.cpp`

## Demo 示例

以下展示如何在自己的模块中查询 Stage Monitor 数据。注意：通常不需要自己创建 Provider 或 Monitor——插件会自动管理。

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "StageMonitor",
    "StageMonitorCommon",
    "StageDataCore",
});
```

### 自定义监控逻辑

```cpp
// MyStageWatcher.h
#pragma once

#include "CoreMinimal.h"

class IStageMonitorSession;

class FMyStageWatcher
{
public:
    void Initialize();
    void CheckFramePerformance();

private:
    TSharedPtr<IStageMonitorSession> ActiveSession;
};

// MyStageWatcher.cpp
#include "MyStageWatcher.h"
#include "IStageMonitorModule.h"
#include "IStageMonitorSession.h"
#include "StageMonitorUtils.h" // FFramePerformanceProviderMessage

void FMyStageWatcher::Initialize()
{
    if (!IStageMonitorModule::IsAvailable())
    {
        return;
    }

    IStageMonitorModule& Module = IStageMonitorModule::Get();
    ActiveSession = Module.GetStageMonitorSessionManager().GetActiveSession();

    if (ActiveSession.IsValid())
    {
        // 注册回调，在新数据到达时检查性能
        ActiveSession->OnStageSessionNewDataReceived().AddRaw(
            this, &FMyStageWatcher::OnNewData);
    }
}

void FMyStageWatcher::CheckFramePerformance()
{
    if (!ActiveSession.IsValid())
    {
        return;
    }

    for (const FStageSessionProviderEntry& Provider : ActiveSession->GetProviders())
    {
        if (Provider.State != EStageDataProviderState::Active)
        {
            UE_LOG(LogTemp, Warning, TEXT("Provider %s is not active!"),
                *Provider.Descriptor.FriendlyName.ToString());
            continue;
        }

        auto Latest = ActiveSession->GetLatest(
            Provider.Identifier, FFramePerformanceProviderMessage::StaticStruct());

        if (Latest.IsValid() && Latest->Data.IsValid())
        {
            auto* Perf = Latest->Data->GetPtr<FFramePerformanceProviderMessage>();
            if (Perf && Perf->AverageFPS < 24.0f)
            {
                UE_LOG(LogTemp, Warning,
                    TEXT("Low FPS on %s: %.1f (GPU: %.1fms)"),
                    *Provider.Descriptor.FriendlyName.ToString(),
                    Perf->AverageFPS, Perf->GPU_MS);
            }
        }
    }
}
```

## 模块依赖

### 使用 StageMonitor 模块时需要依赖：

| 模块 | 用途 |
|---|---|
| `StageDataCore` | Stage 消息基础类型（`FStageProviderMessage`、`FStageDataBaseMessage` 等） |
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `GameplayTags` | VP Role 过滤用的 GameplayTag 系统 |
| `VPRoles` | 虚拟制片角色管理 |
| `VPUtilities` | 虚拟制片工具函数 |

### 使用 StageMonitorCommon 模块时需要依赖：

| 模块 | 用途 |
|---|---|
| `StageDataCore` | Stage 消息基础类型 |
| `DeveloperSettings` | 项目设置（`UDeveloperSettings`） |
| `GameplayTags` | VP Role 配置 |

### 使用 StageDataProvider 模块时需要依赖：

| 模块 | 用途 |
|---|---|
| `StageDataCore` | Stage 消息基础类型 |
| `StageMonitorCommon` | 共享设置 |
| `RHI` | GPU 时间获取 |
| `RenderCore` | 渲染线程数据 |
| `TimeManagement` | Genlock / Timecode 相关 |
| `TakeRecorder` | （仅 Editor）录制状态感知 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-12 | `ce6ff392` | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 警告 — 编译兼容性修复 |
| 2025-05-02 | `52f52bc0` | Timecode: 新增 Cvar 控制 subframe 的 ToString 显示 |
| 2025-04-23 | `b6f496e4` | 移除基于时间戳的动态分辨率启发式方法 — 属于引擎范围清理 |

### 维护评价

- **创建时间**：2020 年 9 月，已有约 6 年历史
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，至今未正式转正
- **最近更新**：2025 年 9 月有编译修复，但最近几次更新都是引擎范围的附带修改（Timecode Cvar、动态分辨率清理），并非 Stage Monitoring 自身的功能更新
- **实质性功能更新**：近 3 次 commit 均无功能性变更，该插件处于维护模式
- **无测试用例**：插件目录内未发现自动化测试文件
- **建议**：该插件对虚拟制片场景仍有价值，但作为 Beta 产品使用时需注意可能存在的边界问题。如果你的 VP 工作流需要多机监控，这是目前 UE5 唯一的内置方案，推荐使用但不要过度依赖其 API 稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StageMonitoring)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 依赖插件：[Takes](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes), [VirtualProductionUtilities](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualProductionUtilities)
