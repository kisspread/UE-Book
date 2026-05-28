# Rewind Debugger Runtime

> Runtime component for RewindDebugger, handling recording control and trace channel management.

| 属性 | 值 |
|---|---|
| 中文名 | 回放调试器运行时 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RewindDebuggerRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

`RewindDebuggerRuntime` 模块是 GameplayInsights 插件的核心运行时组件。它解决的核心问题是：**如何在运行时程序（尤其是游戏）中精确控制动画和游戏状态数据的捕获、记录，并使其能够被 Unreal Insights 的前端工具进行“倒带”式回放和分析**。

它主要做两件事：
1.  **启动/停止记录**：管理基于 Unreal Insights 的追踪（Trace）会话，控制记录的开始和结束。
2.  **启用动画追踪通道**：确保在录制期间，动画系统相关的 Trace 通道（例如 `Animation`）被正确启用，以捕获姿态、节点状态等关键数据。

它存在的意义在于，它为动画师和程序员提供了一种无需侵入游戏代码、基于会话的动画性能与状态调试方法，使得在游戏运行时出现的动画问题可以被录制下来，事后进行帧级别分析。

## 使用场景

-   **调试动画延迟或卡顿**：当游戏运行时出现动画“抽搐”或“不跟手”的问题，你可以启动 Rewind Debugger 记录，然后在 Unreal Insights 中逐帧回放，查看具体是哪个动画节点或资产导致了延迟。
-   **复现罕见动画 Bug**：对于只在特定操作序列下才出现的动画穿模或状态错误，可以录制该序列，然后反复在 Insights 中倒带回放，分析状态机切换和姿态计算过程。
-   **性能剖析**：分析动画蓝图、动画图节点的执行耗时，找出性能瓶颈。
-   **支持远程调试**：该模块内置了对远程会话（Remote Sessions）的支持，允许从一台设备（如移动设备）录制，然后在另一台装有 Unreal Insights 的电脑上进行分析。

## 蓝图用法

此模块为运行时逻辑模块，**未暴露任何蓝图可调用节点**。其控制主要通过 Unreal Insights 前端界面或 C++ API 完成。

## C++ 用法

### 头文件引入

```cpp
#include "RewindDebuggerRuntime/RewindDebuggerRuntime.h"
```

### 基本用法

核心功能是通过单例 `FRewindDebuggerRuntime` 来控制录制。

```cpp
// 获取 RewindDebuggerRuntime 单例
RewindDebugger::FRewindDebuggerRuntime* Runtime = RewindDebugger::FRewindDebuggerRuntime::Instance();

if (Runtime)
{
    // 开始录制（这会启动一个 Unreal Insights 会话）
    Runtime->StartRecording();
    
    // ... 运行游戏，执行你想要录制的操作 ...
    
    // 停止录制
    // 注意：停止录制的控制通常由 RewindDebugger 的高层模块或 Insights UI 触发，
    // 但你可以通过广播停止录制的委托来实现。
    // Runtime->StopRecording(); // 具体方法需查阅完整头文件，此处为示意。
}
```

### 进阶用法

你可以监听录制状态的变化，以便在录制开始或失败时执行自定义逻辑。

```cpp
// 订阅录制状态变化委托
RewindDebugger::FRewindDebuggerRuntime* Runtime = RewindDebugger::FRewindDebuggerRuntime::Instance();
if (Runtime)
{
    Runtime->RecordingStarted.AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Rewind Debugger 录制已开始。"));
        // 在这里启用你自定义的、需要额外记录的调试数据
    });
    
    Runtime->RecordingStartFailed.AddLambda([](const FText& FailureReason)
    {
        UE_LOG(LogTemp, Warning, TEXT("Rewind Debugger 录制启动失败: %s"), *FailureReason.ToString());
    });
    
    Runtime->RecordingStopped.AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Rewind Debugger 录制已停止。"));
    });
}
```

`FRewindDebuggerEngineEditorBridge` 类负责处理编辑器/引擎与运行时之间的桥接逻辑（例如在PIE期间显示录制状态消息），通常不直接由游戏代码调用。

## Demo 示例

一个最小的自定义扩展，用于在录制时追踪自己的数据。

```cpp
// MyAnimDebugRuntime.h
#pragma once
#include "RewindDebuggerRuntime/RewindDebuggerRuntime.h"

// 实现 IRewindDebuggerRuntimeExtension 接口，在录制开始/停止时管理自定义数据
class FMyAnimDebugRuntimeExtension : public RewindDebugger::IRewindDebuggerRuntimeExtension
{
public:
    virtual void RecordingStarted() override
    {
        // 启用你自定义的 Trace 通道，例如 “MyAnim”
        UE::Trace::ToggleChannel(TEXT("MyAnim"), true);
    }

    virtual void RecordingStopped() override
    {
        UE::Trace::ToggleChannel(TEXT("MyAnim"), false);
    }

    virtual void Clear() override
    {
        // 清理你的调试数据
    }
};

// MyAnimDebugRuntime.cpp
#include "MyAnimDebugRuntime.h"
// 实例化扩展。通常在模块启动时注册。
static FMyAnimDebugRuntimeExtension MyAnimDebugRuntimeExtensionInstance;
```

## 模块依赖

`RewindDebuggerRuntime` 模块的 Build.cs 文件声明了以下依赖（已省略常见依赖如 Core, Engine）：

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | GameplayInsights 核心运行时模块 |
| `GameplayInsightsEditor` | GameplayInsights 编辑器模块（用于 Editor 桥接） |
| `RewindDebugger` | RewindDebugger 的公共接口和抽象层 |
| `Trace` / `TraceAnalysis` / `TraceInsights` | Unreal Insights 追踪和分析核心功能 |
| `MessageEndpoint` | 用于支持远程会话通信 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复了 Rewind Debugger 吸管工具在玩家控制器重新连接时未正确取消的问题 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 在 IRewindDebugger 接口上增加了可编程的拖拽擦洗和视图居中功能 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对 Rewind Debugger 工具栏进行了用户体验优化 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | （提交信息不完整） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式 |

### 维护评价

**维护状态：活跃维护中** ✅

该插件创建于 2019 年，但最近在 2026 年 5 月仍有**功能性更新和用户体验改进**，表明它是一个被 Epic 持续维护和优化的官方工具，绝非已废弃。作为 Unreal Insights 动画调试工作流的关键运行时部分，它随着引擎动画系统和 Insights 工具的演进持续更新。

*   **优点**：官方维护，稳定可靠，深度集成 Unreal Insights，是专业动画调试的标准工具。
*   **注意**：默认未启用 (`EnabledByDefault: false`)，需要在项目设置或 Insights 启动参数中手动开启。它主要用于深度调试和性能剖析，对于简单的动画问题可能过于重量级。
*   **推荐**：**强烈推荐**给所有使用 Unreal 动画系统并遇到复杂问题或需要进行性能优化的团队。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
-   官方文档：（暂无专门文档链接，请参考 Unreal Insights 官方文档中关于动画调试的章节）
-   测试用例：（`RewindDebuggerRuntime` 模块自身的测试用例路径未在给定信息中提供，通常可能在 `Engine/Tests/` 目录下）