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
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

这是一个用于深度调试和分析动画系统及游戏状态的工具集。它通过扩展 Unreal Insights 分析工具，为动画师和程序员提供了在运行时实时检查动画状态机、动画曲线、动画通知等内部状态的能力。其核心功能 **Rewind Debugger** 允许开发者像使用视频播放器一样回放游戏过程，并检查任意时间点的游戏状态（包括动画、物理、AI 等），极大地简化了复杂动画和游戏逻辑问题的调试过程。

## 使用场景

- **动画师调试**：在运行时查看角色动画蓝图的状态机流转、动画曲线值、动画通知触发情况，快速定位动画表现异常的原因。
- **程序员调试**：分析动画系统与游戏逻辑（如移动、战斗）的交互问题，检查动画事件是否正确触发，以及动画数据是否符合预期。
- **复杂问题复现**：当遇到难以复现的 bug 时，使用 Rewind Debugger 记录游戏过程，事后可以反复回放、暂停、检查特定帧的游戏状态，进行根因分析。
- **性能分析**：结合 Unreal Insights，分析动画系统的性能开销，识别昂贵的动画更新或计算。

## 蓝图用法

本插件主要提供编辑器工具和运行时调试界面，其核心功能通过 Unreal Insights 和 Rewind Debugger 界面暴露，而非传统的蓝图节点。在蓝图中，主要通过以下方式交互：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` / `StopRecording` | 控制 Rewind Debugger 的录制过程 | `URewindDebugger` |
| `GetAnimationState` | 获取指定 Actor 当前的动画状态信息 | `UAnimationBlueprintLibrary` (来自其他模块) |

### 使用示例（蓝图描述）

在游戏逻辑中，你可以通过蓝图调用 `URewindDebugger` 的函数来控制调试录制。例如，在游戏开始时调用 `StartRecording`，在特定事件发生时调用 `StopRecording` 并保存记录，然后在编辑器中打开 Rewind Debugger 窗口加载该记录进行分析。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayInsightsModule.h"
#include "RewindDebugger.h"
```

### 基本用法

通过模块接口访问核心功能。

```cpp
// 获取 GameplayInsights 模块
IGameplayInsightsModule& GameplayInsightsModule = FModuleManager::GetModuleChecked<IGameplayInsightsModule>(TEXT("GameplayInsights"));

// 获取 Rewind Debugger 实例
IRewindDebugger* RewindDebugger = GameplayInsightsModule.GetRewindDebugger();
if (RewindDebugger)
{
    // 开始录制
    RewindDebugger->StartRecording();
    
    // ... 游戏运行 ...
    
    // 停止录制
    RewindDebugger->StopRecording();
}
```

### 进阶用法

实现自定义的调试通道，将你的游戏特定数据集成到 Rewind Debugger 的时间线上。

```cpp
// 1. 创建一个继承自 IRewindDebuggerExtension 的类
class FMyGameplayExtension : public IRewindDebuggerExtension
{
    // ... 实现接口，提供自定义数据的录制和回放逻辑 ...
};

// 2. 在模块启动时注册
void FMyGameplayModule::StartupModule()
{
    if (IRewindDebugger* RewindDebugger = FModuleManager::GetModuleChecked<IGameplayInsightsModule>("GameplayInsights").GetRewindDebugger())
    {
        RewindDebugger->RegisterExtension(MakeShared<FMyGameplayExtension>());
    }
}
```

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `GameplayInsights` | Runtime | 核心运行时模块，提供动画数据收集和与 Unreal Insights 的集成基础。 |
| `GameplayInsightsEditor` | Runtime | 编辑器扩展模块，提供在 Unreal Editor 中查看和分析动画 Insights 数据的 UI 和工具。 |
| `RewindDebugger` | Runtime | **Rewind Debugger** 的核心逻辑模块，负责游戏状态的录制、回放和检查框架。 |
| `RewindDebuggerRuntime` | Runtime | 为 Rewind Debugger 提供运行时支持，处理游戏状态数据的序列化和存储。 |
| `RewindDebuggerVLog` | Runtime | 将 Visual Logger (VLog) 数据集成到 Rewind Debugger 时间线中的模块。 |
| `RewindDebuggerVLogRuntime` | Runtime | 为 VLog 集成提供运行时支持，确保 VLog 数据能被正确录制和回放。 |

## 维护状态

### 近期更新

- 2025-04-22 5.6.0-release 更新至 5.6 版本
- 2025-04-15 5.6.0-rc2 更新至 5.6 版本
- 2025-04-08 5.6.0-rc1 更新至 5.6 版本

### 维护评价

该插件创建于 2019 年，是 Unreal Engine 动画调试工具链的核心组成部分。从最近的提交记录看，它随着引擎主版本（5.6）进行同步更新，表明它处于**活跃维护**状态。作为 Epic Games 官方维护的工具，其稳定性和与引擎的兼容性有保障。对于需要进行深度动画和游戏逻辑调试的项目，**强烈推荐使用**。需要注意的是，它默认未启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [官方文档](https://docs.unrealengine.com/) (无特定文档链接，通常包含在引擎调试工具文档中)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Tests)