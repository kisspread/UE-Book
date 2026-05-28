# Rewind Debugger VLog Runtime

> Runtime extension for the Rewind Debugger to record and debug Visual Logger (VLog) log category verbosity details during Unreal Insights sessions.

| 属性 | 值 |
|---|---|
| 中文名 | 动画洞察 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLogRuntime) | |

## 用途

`RewindDebuggerVLogRuntime` 模块是 `GameplayInsights` 插件的一个运行时扩展，其核心功能是在 Unreal Insights 的录制和回放（Rewind Debugger）流程中，对 Visual Logger (`UE_LOG`) 的**日志类别（Log Category）详细级别（Verbosity）** 进行细粒度的录制和查询。

这个模块解决了在复杂的动画系统调试中，开发者不仅需要录制动画状态，还需要动态控制和查询特定日志类别在历史时间点的状态的问题。它通过注册为 `IRewindDebuggerRuntimeExtension`，在录制开始时捕获当前的日志类别状态，并通过消息端点（Message Endpoint）机制，允许远程（如编辑器）会话在回放时查询和修改这些状态。

## 使用场景

-   **动画系统深度调试**：当你在调试角色动画蓝图或复杂的动画图时，需要追踪特定日志类别（如 `LogAnimation`、`LogAnimNode`）的输出，并希望在回放时（Rewind Debugger）能够按时间线查看这些日志，同时能够动态启用或禁用某些日志以聚焦于关键信息。
-   **远程设备日志控制**：在为 Xbox、PlayStation 等设备进行性能分析和调试时，可以通过消息端点远程控制目标设备上运行的游戏实例的日志详细级别，无需重新编译或重启。
-   **历史会话状态分析**：通过 `FVLogExtensionSessionData`，你可以查询在录制期间哪些日志类别处于活动状态，以及是否使用了详细级别过滤，这对于重现和分析特定问题至关重要。

## 蓝图用法

此模块主要是运行时扩展和底层数据交换，**未暴露直接的蓝图节点（BlueprintCallable）**。其功能通常通过 `RewindDebugger` 和 `GameplayInsights` 上层插件提供的 UI 和工作流间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "RewindDebuggerVLogRuntimeTypes.h" // 用于访问消息和数据结构
#include "RewindDebuggerRuntimeInterface/IRewindDebuggerRuntimeExtension.h" // 用于实现扩展
```

### 基本用法：实现一个 VLog 运行时扩展

该模块本身就是一个 `IRewindDebuggerRuntimeExtension` 的实现。如果你需要为其他类型的日志创建类似的扩展，可以参考其模式。

```cpp
// MyCustomVLogRuntime.h
#pragma once

#include "RewindDebuggerRuntimeInterface/IRewindDebuggerRuntimeExtension.h"

#if UE_DEBUG_RECORDING_ENABLED
class FMyCustomVLogRuntime : public IRewindDebuggerRuntimeExtension
{
public:
    virtual void RecordingStarted() override;
    virtual void RecordingStopped() override;
    virtual void RegisterMessageHandlers(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpointBuilder& EndpointBuilder) override;
    virtual void RegisterMessageTypes(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpoint& Endpoint) override;
};
#endif
```

**来源**：基于 `Private/RewindDebuggerVLogRuntime.h` 中的 `FRewindDebuggerVLogRuntime` 类。

### 进阶用法：查询和响应日志状态

在录制期间，可以通过会话数据查询日志类别状态。在 `RecordingStarted` 中，通常会初始化或保存当前状态。

```cpp
// 在某个可以访问会话数据的地方
#include "TraceBasedDebuggers/SessionInfo.h"
#include "RewindDebuggerVLogRuntimeTypes.h"

void QueryAndPrintVLogStatus()
{
    if (auto* SessionInfo = TraceBasedDebuggers::FSessionInfo::Get())
    {
        // 获取此扩展存储在会话中的数据
        if (auto* VLogData = SessionInfo->GetDebuggerData<UE::RewindDebugger::FVLogExtensionSessionData>())
        {
            // 查询是否在录制时使用了详细级别过滤
            bool bFiltering = VLogData->bUsingVerbosityFilterWhenRecording;
            UE_LOG(LogTemp, Log, TEXT("Using verbosity filter: %s"), bFiltering ? TEXT("Yes") : TEXT("No"));

            // 遍历所有记录的日志类别状态
            for (const auto& Pair : VLogData->LogCategoriesStatesByName)
            {
                const FName& CategoryName = Pair.Key;
                const FLogCategoryVerbosity& State = Pair.Value;
                UE_LOG(LogTemp, Log, TEXT("Category '%s' Verbosity: %d (%s)"), 
                    *CategoryName.ToString(), 
                    State.Verbosity, 
                    LexToString(State.GetVerbosity()));
            }
        }
    }
}
```

**来源**：基于 `Public/RewindDebuggerVLogRuntimeTypes.h` 中的 `FVLogExtensionSessionData` 结构体。

### 发送消息命令（概念性）

`RewindDebuggerVLogRuntime` 内部实现了通过消息端点接收 `FLogCategoryStatusQueryMessage` 等消息。在实际的远程调试场景中，编辑器端的 `RewindDebuggerVLog` 模块会发送这些消息。以下是如何构建和发送一个日志类别状态查询命令的示例：

```cpp
// 假设你已经有一个 FMessageEndpoint 指针 Endpoint 和一个目标实例 ID TargetInstanceID
void SendVerbosityQueryCommand(FMessageEndpointPtr Endpoint, const FGuid& TargetInstanceID)
{
    // 发送一个查询命令，请求目标实例返回所有日志类别的当前状态
    auto QueryMessage = MakeShared<FLogCategoryStatusQueryMessage>();
    // 在实际消息协议中，Endpoint 会处理目标路由
    Endpoint->Send(QueryMessage, ...); // 省略目标地址参数
}
```

**来源**：基于 `Public/RewindDebuggerVLogRuntimeTypes.h` 中定义的多个消息结构体，如 `FLogCategoryStatusQueryMessage`。

## Demo 示例

一个最小化的运行时扩展示例，展示如何继承接口。

**MyMinimalVLogExtension.h**
```cpp
#pragma once

#include "RewindDebuggerRuntimeInterface/IRewindDebuggerRuntimeExtension.h"

#if UE_DEBUG_RECORDING_ENABLED
class FMyMinimalVLogExtension : public IRewindDebuggerRuntimeExtension
{
public:
    virtual void RecordingStarted() override
    {
        UE_LOG(LogTemp, Display, TEXT("My VLog Extension: Recording Started. Logging current state..."));
        // 在此处记录初始日志状态
    }

    virtual void RecordingStopped() override
    {
        UE_LOG(LogTemp, Display, TEXT("My VLog Extension: Recording Stopped."));
    }

    // 以下两个函数需要在 .cpp 中实现以注册消息
    virtual void RegisterMessageHandlers(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpointBuilder& EndpointBuilder) override;
    virtual void RegisterMessageTypes(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpoint& Endpoint) override;
};
#endif
```

**MyMinimalVLogExtension.cpp**
```cpp
#include "MyMinimalVLogExtension.h"

#if UE_DEBUG_RECORDING_ENABLED
#include "RewindDebuggerVLogRuntimeTypes.h"

void FMyMinimalVLogExtension::RegisterMessageHandlers(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpointBuilder& EndpointBuilder)
{
    // 注册处理来自远程会话的消息
    EndpointBuilder.Handler<FLogCategoryStatusQueryMessage>(... // 处理函数
    );
}

void FMyMinimalVLogExtension::RegisterMessageTypes(const TSharedPtr<TraceBasedDebuggers::FRemoteSessionsManager>& RemoteSessionManager, FMessageEndpoint& Endpoint)
{
    // 在远程会话管理器中注册此扩展使用的消息类型
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RewindDebuggerRuntimeInterface` | 提供 `IRewindDebuggerRuntimeExtension` 接口定义。 |
| `TraceBasedDebuggers` | 提供 `FRemoteSessionsManager`, `FMessageEndpoint`, `FSessionInfo` 等核心消息和会话管理基础设施。 |
| `VisualLogger` | 与 `UE_LOG` 系统交互的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复回放调试器取色器在重新连接玩家控制器时未正确取消的问题 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 为回放调试器接口添加可编程的进度条擦洗和视图居中表面功能 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对回放调试器的工具栏进行用户体验优化。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | （回放调试器）常规更新或维护 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至新的 UE_LOGF 格式。 |

### 维护评价

-   **活跃维护**：尽管创建于 2019 年，但该模块（及其所属的 `GameplayInsights` / `RewindDebugger` 系列）在近期（2026年4-5月）仍有频繁的功能性更新和缺陷修复，表明其处于**活跃维护**状态。
-   **实验性标志**：`.uplugin` 中 `EnabledByDefault: false`，表明它是一个需要用户手动启用的功能。这通常意味着它可能针对特定工作流或仍处于完善中。
-   **推荐使用**：**强烈推荐**用于需要深度动画系统调试和远程日志控制的专业开发场景。它是 UE5 内置的高级动画调试工具链的核心组成部分之一。请确保在项目设置中手动启用该插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLogRuntime)