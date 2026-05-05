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

GameplayInsights 插件（又称 Animation Insights）是一个强大的动画系统调试工具，它深度集成了 Unreal Insights 分析框架。其核心功能是**时间回溯调试**：它能够记录游戏运行时（PIE 或独立进程）的动画状态、骨骼网格体姿态、动画蓝图变量、状态机状态等关键数据，并将这些数据与 Unreal Insights 的时间线同步。开发者可以在 Insights 中像播放录像一样，前后拖动时间轴，精确查看任意时刻的动画状态，从而诊断动画卡顿、状态机转换错误、动画蓝图逻辑问题等复杂问题。它解决了传统动画调试中无法“暂停”和“回放”游戏运行时状态的痛点。

## 使用场景

- **动画状态机调试**：你的角色动画在特定条件下表现异常（如卡在某个状态、转换不正确），但难以在实时运行中定位问题。使用 Animation Insights，你可以记录运行过程，然后在 Insights 时间线上逐帧检查状态机的激活状态和转换条件。
- **动画蓝图逻辑分析**：动画蓝图中的变量（如速度、是否在空中）驱动了动画选择。当动画表现不符合预期时，你可以在 Insights 中同时查看这些变量的实时值和对应的动画姿态，快速定位逻辑错误。
- **动画性能优化**：动画系统出现卡顿或掉帧。通过 Insights 的时间线，你可以精确看到是哪个动画节点、哪个骨骼网格体的更新在特定时间点消耗了过多时间。
- **网络同步动画调试**：在多人游戏中，动画状态需要同步。此工具可以帮助可视化客户端和服务端动画状态的差异。

## 蓝图用法

该插件主要作为编辑器和分析工具使用，其核心功能通过 Unreal Insights 界面和 C++ API 暴露，直接的蓝图可调用节点较少。主要的蓝图交互可能集中在触发数据记录或配置调试通道上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` / `StopRecording` | 控制动画调试数据的录制（通常通过 Insights 界面或控制台命令触发） | `URewindDebugger` |
| `AddDebugChannel` | 为自定义数据添加一个调试通道，以便在 Insights 中显示 | `URewindDebugger` |

### 使用示例（蓝图描述）

1.  **启用插件**：在编辑器中，前往 `编辑 -> 插件`，搜索 “Animation Insights” 并启用它。重启编辑器。
2.  **启动分析**：运行游戏（PIE），然后打开 `工具 -> Unreal Insights`。
3.  **配置录制**：在 Insights 的 “Trace” 面板中，确保勾选了 `Animation` 和 `Gameplay` 相关的通道。
4.  **开始录制**：在游戏运行时，点击 Insights 的录制按钮，或使用控制台命令 `Trace.Start`。
5.  **停止与回放**：停止录制后，在 Insights 的时间线上，你可以拖动指针，左侧的 “Animation” 面板会同步显示对应时刻的骨骼姿态、动画状态等信息。

## C++ 用法

### 头文件引入

```cpp
#include "RewindDebugger.h"
#include "IRewindDebuggerExtension.h"
```

### 基本用法

以下示例展示了如何创建一个简单的自定义调试通道，用于记录和显示自定义数据。

```cpp
// 来源：基于插件架构推断的典型用法
// MyGameplayInsightsExtension.h
#pragma once

#include "IRewindDebuggerExtension.h"

class FMyGameplayInsightsExtension : public IRewindDebuggerExtension
{
public:
    // 当时间轴上的时间点改变时被调用
    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override;

    // 用于在 Insights 面板中绘制自定义数据
    virtual void DrawDetails(IRewindDebugger* RewindDebugger) override;
};
```

```cpp
// MyGameplayInsightsExtension.cpp
#include "MyGameplayInsightsExtension.h"
#include "RewindDebugger.h"

void FMyGameplayInsightsExtension::Update(float DeltaTime, IRewindDebugger* RewindDebugger)
{
    // 在这里，你可以根据 RewindDebugger 提供的当前时间，查询你的游戏系统状态
    // 例如，获取某个角色在特定时间点的自定义数据
    // float CurrentTime = RewindDebugger->GetCurrentTime();
    // FMyCustomData Data = GetCustomDataAtTime(CurrentTime);
    // 将数据缓存起来，供 DrawDetails 使用
}

void FMyGameplayInsightsExtension::DrawDetails(IRewindDebugger* RewindDebugger)
{
    // 使用 ImGui 或 Slate 在 Insights 的详情面板中绘制你的自定义数据
    // ImGui::Text("My Custom Value: %f", CachedCustomData.Value);
}
```

### 进阶用法

注册你的扩展，使其被 RewindDebugger 加载和调用。

```cpp
// 在你的模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    // 获取 RewindDebugger 模块并注册扩展
    IRewindDebugger* RewindDebugger = FModuleManager::GetModulePtr<IRewindDebuggerModule>("RewindDebugger")->GetRewindDebugger();
    if (RewindDebugger)
    {
        MyExtension = MakeShared<FMyGameplayInsightsExtension>();
        RewindDebugger->RegisterExtension(MyExtension);
    }
}

void FMyModule::ShutdownModule()
{
    if (IRewindDebugger* RewindDebugger = ...)
    {
        RewindDebugger->UnregisterExtension(MyExtension);
    }
}
```

## Demo 示例

一个最小的自定义调试通道扩展，用于记录和显示一个简单的计数器。

```cpp
// SimpleCounterInsightsExtension.h
#pragma once

#include "IRewindDebuggerExtension.h"

class FSimpleCounterInsightsExtension : public IRewindDebuggerExtension
{
public:
    virtual void Update(float DeltaTime, IRewindDebugger* RewindDebugger) override;
    virtual void DrawDetails(IRewindDebugger* RewindDebugger) override;

private:
    int32 Counter = 0;
};
```

```cpp
// SimpleCounterInsightsExtension.cpp
#include "SimpleCounterInsightsExtension.h"
#include "RewindDebugger.h"
#include "ImGuiModule.h" // 假设使用 ImGui 绘制

void FSimpleCounterInsightsExtension::Update(float DeltaTime, IRewindDebugger* RewindDebugger)
{
    // 模拟：每帧增加计数器
    Counter++;
}

void FSimpleCounterInsightsExtension::DrawDetails(IRewindDebugger* RewindDebugger)
{
    if (ImGui::Begin("Simple Counter"))
    {
        ImGui::Text("Frame Counter: %d", Counter);
        ImGui::End();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Animation` | 核心动画系统，提供动画数据结构和接口 |
| `GameplayInsights` | 本插件的核心运行时模块，提供动画数据收集和通道 |
| `RewindDebugger` | 时间回溯调试器的核心框架，提供录制、回放和扩展接口 |
| `Insights` | Unreal Insights 分析框架，提供数据可视化和时间线界面 |

## 维护状态

### 近期更新

```
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- f31df6b1039a Fix crash in Anim Insights pose scrubbing #rb samuele.rigamonti #jira UE-210748
- da92084a122a Optimized out more private modules includes and dependencies.
```

*   `2057280165b3`：代码规范更新，确保 DLL 导出符号正确。这是维护性提交。
*   `f31df6b1039a`：修复了在 Insights 中拖动时间轴查看动画姿态时发生的崩溃。这是一个重要的稳定性修复。
*   `da92084a122a`：优化了头文件包含和模块依赖，减少了编译时间和耦合度。

### 维护评价

**维护中**。该插件创建于 2019 年，已有约 6 年历史，属于“老古董”级别。然而，从近期的 git 提交记录来看，它仍在被积极维护和修复（如最近的崩溃修复）。作为 Unreal Insights 生态的一部分，它随着引擎版本更新而持续迭代。尽管默认未启用，但对于需要深度动画调试的项目（尤其是使用复杂动画蓝图或状态机的项目）来说，它是一个**强烈推荐**的专业工具。其“时间回溯”功能是传统调试方法无法比拟的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中发现标准测试文件)