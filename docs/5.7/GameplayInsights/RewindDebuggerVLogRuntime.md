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

Animation Insights 插件的核心是提供一套基于 Unreal Insights 框架的**动画系统调试与分析工具**。它不仅仅是记录日志，而是构建了一个**时间可回放的调试环境**。开发者可以在游戏运行时录制动画相关的数据（如状态机状态、蒙太奇播放、动画曲线、通知等），然后在 Unreal Insights 工具中像回放视频一样，前后拖动时间轴来检查任意时刻的动画状态，极大地简化了复杂动画逻辑（如状态机嵌套、动画混合、通知时序）的调试过程。

它解决了传统断点调试和日志打印在调试动画时序问题上的低效和不可回溯性问题。

## 使用场景

- 你的角色动画状态机逻辑复杂，状态切换频繁且难以复现 bug → 使用 Animation Insights 录制并回放状态机转换过程。
- 你需要调试动画蒙太奇（Montage）的播放、混合与中断逻辑 → 使用工具查看蒙太奇的精确播放进度和混合权重。
- 你在开发一个需要精确动画通知（AnimNotify）触发的游戏机制（如脚步声、攻击判定）→ 使用工具检查通知的触发时间点是否正确。
- 你需要分析动画蓝图的性能瓶颈，查看哪些动画节点消耗了最多时间 → 使用 Insights 的性能分析视图。

## 蓝图用法

本插件主要作为**开发时调试工具**集成在 Unreal Insights 应用程序中，而非直接在游戏蓝图中提供大量可调用节点。其主要的交互发生在编辑器和 Insights 工具内。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` | 开始录制动画调试数据 | `URewindDebugger` |
| `StopRecording` | 停止录制 | `URewindDebugger` |

### 使用示例（蓝图描述）

1.  在编辑器中，通过 `Window -> Developer Tools -> Animation Insights` 打开插件面板。
2.  在面板中点击“录制”按钮（对应蓝图中的 `StartRecording`）。
3.  在游戏视口中操作角色，复现需要调试的动画行为。
4.  停止录制后，打开 Unreal Insights 工具，加载录制的 `.utrace` 文件。
5.  在 Insights 的 “Animation” 通道中，使用时间轴滑块回放和检查动画状态。

## C++ 用法

### 头文件引入

```cpp
#include "RewindDebugger.h"
#include "IRewindDebuggerExtension.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码控制录制的开始与停止，这通常用于集成到自定义的编辑器工具或自动化测试中。

```cpp
// 来源: 基于 RewindDebugger 模块的公开接口推断
#include "RewindDebugger.h"

void StartAnimationDebugRecording()
{
    if (FRewindDebugger* RewindDebugger = FRewindDebugger::Instance())
    {
        RewindDebugger->StartRecording();
    }
}

void StopAnimationDebugRecording()
{
    if (FRewindDebugger* RewindDebugger = FRewindDebugger::Instance())
    {
        RewindDebugger->StopRecording();
    }
}
```

### 进阶用法

插件通过 `IRewindDebuggerExtension` 接口支持扩展。你可以创建自定义的调试通道，将你游戏特有的数据（如自定义的动画状态、技能冷却）也纳入时间回放调试系统中。

```cpp
// 来源: 基于插件架构和接口模式推断
#include "IRewindDebuggerExtension.h"

class FMyGameplayInsightsExtension : public IRewindDebuggerExtension
{
public:
    virtual void RecordingStarted() override
    {
        // 当全局录制开始时，初始化你的数据收集器
    }

    virtual void RecordingStopped() override
    {
        // 当全局录制停止时，清理资源
    }

    virtual void Update(float DeltaTime) override
    {
        // 每帧更新，收集当前帧需要记录的数据
        // 例如：记录当前技能状态、自定义动画参数等
    }
};

// 在模块启动时注册扩展
void FMyGameplayInsightsModule::StartupModule()
{
    if (FRewindDebugger* RewindDebugger = FRewindDebugger::Instance())
    {
        RewindDebugger->RegisterExtension(MakeShared<FMyGameplayInsightsExtension>());
    }
}
```

## Demo 示例

以下是一个最小化的自定义调试通道扩展示例，用于记录一个简单的自定义动画状态。

**MyAnimInsightsExtension.h**
```cpp
#pragma once
#include "IRewindDebuggerExtension.h"

class FMyAnimInsightsExtension : public IRewindDebuggerExtension
{
public:
    virtual void Update(float DeltaTime) override;
    // 其他接口函数实现...
private:
    // 用于存储录制数据的结构
    struct FFrameData
    {
        float Time;
        bool bIsJumping;
    };
    TArray<FFrameData> RecordedData;
};
```

**MyAnimInsightsExtension.cpp**
```cpp
#include "MyAnimInsightsExtension.h"
#include "RewindDebugger.h"

void FMyAnimInsightsExtension::Update(float DeltaTime)
{
    // 假设我们有一个全局或可访问的角色引用
    // AMyCharacter* MyCharacter = GetMyCharacter();
    // if (MyCharacter && FRewindDebugger::Instance()->IsRecording())
    // {
    //     FFrameData Data;
    //     Data.Time = GetWorld()->GetTimeSeconds();
    //     Data.bIsJumping = MyCharacter->GetCharacterMovement()->IsFalling();
    //     RecordedData.Add(Data);
    // }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 的底层追踪服务和数据访问接口 |
| `TraceAnalysis` | 用于分析和处理追踪数据 |
| `GameplayInsights` | 本插件的核心运行时模块，提供动画数据追踪和序列化 |
| `RewindDebugger` | 回放调试器的核心框架，管理录制、回放和扩展点 |
| `AnimationCore` | 提供动画系统的核心数学和数据结构 |
| `AnimationBlueprintLibrary` | 用于与动画蓝图交互，获取状态机等信息 |

## 维护状态

### 近期更新

```
- 736bd5e2ed27 Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 476ee06851ad Shipping compile fixes for Rewind Debugger Runtime modules [FYI] samuele.rigamonti
- 87c10d8e971e Compile fixes for RewindDebugger runtime modules [FYI] samuele.rigamonti
```

**解读**：最近的三次提交均为**维护性修复**，主要解决编译问题（如 DLL 导出符号）和针对特定构建目标（LyraGame）的适配。没有新功能或重大重构。

### 维护评价

- **创建时间**：2019年，是一个相对成熟的插件。
- **最近更新**：最近的更新集中在编译修复，表明插件已进入**稳定维护期**，核心功能不再频繁变动。
- **活跃度**：作为 Epic 官方提供的调试工具，其稳定性优先于新功能开发。它随引擎版本更新而维护，但不会有独立的功能迭代。
- **已知限制**：需要手动启用 (`EnabledByDefault: false`)，且主要服务于开发调试阶段，不包含在最终发布包中。
- **推荐使用**：**强烈推荐**用于开发阶段的动画系统调试。它是解决复杂动画时序问题的利器，能极大提升调试效率。尽管更新不频繁，但其核心价值稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [官方文档]() (无)
- [测试用例]() (可能位于 `Engine/Tests/` 目录下，需具体查找)