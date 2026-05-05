# Animation Insights

> Allows debugging of animation systems via Unreal Insights（照抄，不翻译）

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

`GameplayInsights` 插件是一个强大的运行时调试与分析工具集，其核心是 **Rewind Debugger（回溯调试器）**。它解决了在复杂游戏场景中，特别是涉及动画、状态机和游戏逻辑时，难以复现和诊断问题的痛点。

该插件的主要功能是**录制游戏运行时的状态数据**（如动画状态、变量值、事件等），并允许开发者在录制结束后**像播放视频一样回放和检查这些状态**。它与 Unreal Insights 深度集成，将录制的数据以时间线、图表等可视化形式呈现，使得分析动画混合、状态机转换、动画通知触发等过程变得直观高效。它不仅仅是一个动画调试器，更是一个通用的游戏状态回溯分析框架。

## 使用场景

-   你在调试一个复杂的动画状态机，角色在特定条件下动画表现异常，但问题难以实时复现。→ 使用 `GameplayInsights` 录制游戏过程，然后在回放中逐帧检查动画蓝图节点、混合权重和状态转换。
-   你需要分析动画通知（Anim Notify）的触发时机是否正确，或者检查动画曲线（Curve）的值变化。→ 录制游戏，然后在 Insights 时间线上精确查看通知触发点和曲线数据。
-   你的游戏逻辑与动画深度耦合，需要同时观察游戏变量和动画状态的变化关系。→ 录制包含游戏逻辑和动画数据的完整会话，在统一的时间线上进行关联分析。
-   你需要向团队成员或自己展示一个动画 Bug 的发生过程。→ 录制问题场景，生成可共享的回放数据，用于问题复现和讨论。

## 蓝图用法

该插件的核心功能主要通过 C++ API 和 Unreal Insights 界面提供，**没有直接暴露用于蓝图的 `BlueprintCallable` 函数**。其工作流程通常是：
1.  在编辑器或开发版本中启动录制。
2.  进行游戏操作。
3.  停止录制。
4.  打开 Unreal Insights 工具查看和分析录制的数据。

蓝图资产（如动画蓝图）中的状态和变量会被自动捕获和记录，无需额外蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "RewindDebuggerRuntime/RewindDebuggerRuntime.h"
```

### 基本用法

核心类是 `RewindDebugger::FRewindDebuggerRuntime`，它是一个单例，负责管理录制的生命周期。

```cpp
// 获取运行时实例
RewindDebugger::FRewindDebuggerRuntime* RewindRuntime = RewindDebugger::FRewindDebuggerRuntime::Instance();
if (RewindRuntime)
{
    // 检查是否正在录制
    if (!RewindRuntime->IsRecording())
    {
        // 开始录制
        RewindRuntime->StartRecording();
        // 或者使用带参数的版本，指定 Trace 类型和目标
        // TArray<FString> Args = { TEXT("-server=127.0.0.1") };
        // RewindRuntime->StartRecordingWithArgs(Args);
    }
}

// ... 进行游戏操作 ...

// 停止录制
if (RewindRuntime && RewindRuntime->IsRecording())
{
    RewindRuntime->StopRecording();
}
```

### 进阶用法

你可以绑定委托来响应录制状态的变化，这对于集成到自定义编辑器工具或自动化测试中非常有用。

```cpp
// 绑定录制开始的委托
RewindRuntime->RecordingStarted.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Rewind Debugger 录制已开始。"));
});

// 绑定录制停止的委托
RewindRuntime->RecordingStopped.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Rewind Debugger 录制已停止，数据已保存。"));
    // 在这里可以触发自动打开 Insights 或执行其他分析逻辑
});

// 绑定清除录制数据的委托
RewindRuntime->ClearRecording.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Rewind Debugger 录制数据已清除。"));
});
```

## Demo 示例

以下是一个在自定义游戏模块中集成 `RewindDebuggerRuntime` 的最小示例。

**MyGameDebugHelper.h**
```cpp
// MyGameDebugHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyGameDebugHelper
{
public:
    static void StartRewindRecording();
    static void StopRewindRecording();
    static bool IsRewindRecording();
};
```

**MyGameDebugHelper.cpp**
```cpp
// MyGameDebugHelper.cpp
#include "MyGameDebugHelper.h"
#include "RewindDebuggerRuntime/RewindDebuggerRuntime.h"

void FMyGameDebugHelper::StartRewindRecording()
{
    if (RewindDebugger::FRewindDebuggerRuntime* Runtime = RewindDebugger::FRewindDebuggerRuntime::Instance())
    {
        if (!Runtime->IsRecording())
        {
            Runtime->StartRecording();
        }
    }
}

void FMyGameDebugHelper::StopRewindRecording()
{
    if (RewindDebugger::FRewindDebuggerRuntime* Runtime = RewindDebugger::FRewindDebuggerRuntime::Instance())
    {
        if (Runtime->IsRecording())
        {
            Runtime->StopRecording();
        }
    }
}

bool FMyGameDebugHelper::IsRewindRecording()
{
    if (RewindDebugger::FRewindDebuggerRuntime* Runtime = RewindDebugger::FRewindDebuggerRuntime::Instance())
    {
        return Runtime->IsRecording();
    }
    return false;
}
```

## 模块依赖

从 `RewindDebuggerRuntime` 模块的 `Build.cs` 分析，其主要依赖如下。使用此插件的模块需要添加对 `RewindDebuggerRuntime` 的依赖。

| 模块 | 用途 |
|---|---|
| `TraceServices` | 提供底层的 Trace 数据读写和分析服务，是 Insights 功能的基础。 |
| `InsightsCore` | Unreal Insights 工具的核心框架。 |
| `RewindDebuggerInterface` | 定义回溯调试器的公共接口，用于模块间解耦。 |

## 维护状态

### 近期更新

```
- 4b75188cc61e Fix for anim next variable details not showing up #rb Jack.Potter
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 2ce96ff83b54 Fix ensure conditions in RewindDebuggerRuntime.cpp
```

*   `4b75188cc61e`: 修复了动画蓝图中“下一个变量”详情不显示的问题，属于功能修复。
*   `93a13080d9ef`: 构建系统调整，将方法/静态变量的导出符号从类型改为模块，属于底层维护。
*   `2ce96ff83b54`: 修复了 `RewindDebuggerRuntime.cpp` 中的断言条件，属于稳定性修复。

### 维护评价

`GameplayInsights` 插件自 2019 年创建以来，一直是 Epic 官方动画和游戏调试工具链的重要组成部分。从近期提交记录看，它仍在被积极维护和修复，以适配新的引擎版本（如 Lyra 示例项目的构建目标）和修复已知问题。

**优点**：
-   官方维护，与引擎深度集成，稳定可靠。
-   功能强大，是分析复杂动画和游戏逻辑问题的利器。
-   与 Unreal Insights 生态无缝结合，数据可视化程度高。

**注意**：
-   默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。
-   主要面向开发者和调试场景，不直接面向最终玩家。
-   学习曲线相对较高，需要熟悉 Unreal Insights 工具。

**推荐使用**：对于任何涉及复杂动画系统或需要深度游戏状态分析的项目，强烈推荐启用和使用此插件。它是提升开发调试效率的官方标准工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
-   [官方文档](https://docs.unrealengine.com/) (无特定文档链接，但可参考 Unreal Insights 相关文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Tests) (如果存在)