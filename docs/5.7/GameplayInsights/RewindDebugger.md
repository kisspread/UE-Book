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

GameplayInsights 是一个**运行时游戏调试工具集**，核心功能是将动画系统和游戏逻辑的状态数据接入 Unreal Insights 性能分析框架，并提供 **Rewind Debugger（回溯调试器）** 让开发者在编辑器中像"倒带"一样回放和检查游戏运行时的每一帧状态。

这个插件解决的核心问题是：**动画和游戏逻辑的调试往往是瞬时的、难以复现的**。传统的断点和日志只能看到当前帧，而 RewindDebugger 会持续录制运行时数据流，允许你在时间轴上前后拖动，查看任意时刻的动画图状态、混合权重、骨骼变换、状态机转换等信息。

插件通过 `SupportedPrograms: ["UnrealInsights"]` 声明与 Unreal Insights 工具集成，录制的数据可以在 Insights 独立工具或编辑器内面板中查看。

## 使用场景

- 你在调试动画蓝图中的状态机转换逻辑，需要查看某一帧的混合权重和状态路径 → 用 RewindDebugger 回溯到那一帧
- 你需要分析动画系统的性能瓶颈（Tick 耗时、骨骼求值开销）→ 用 GameplayInsights 在 Insights 中查看动画通道的时间线
- 你在调试 Gameplay Ability System 或 StateTree，需要查看执行流程 → 用 RewindDebugger 的 track 系统可视化执行过程
- 你需要录制一段游戏过程并反复检查某个动画 bug → 开启录制后用时间轴回放

## 模块架构

本插件由 6 个模块组成，按职责分为三层：

```
┌─────────────────────────────────────────────────┐
│              编辑器 / UI 层                       │
│  GameplayInsightsEditor  RewindDebugger          │
│  (Insights 面板 UI)      (回溯调试器 UI/框架)     │
├─────────────────────────────────────────────────┤
│              运行时录制层                         │
│  GameplayInsights        RewindDebuggerRuntime   │
│  (动画数据录制)           (通用回溯数据录制)       │
│  RewindDebuggerVLog      RewindDebuggerVLogRuntime│
│  (VLog 集成 UI)          (VLog 运行时录制)        │
└─────────────────────────────────────────────────┘
```

| 模块 | 类型 | 职责 |
|---|---|---|
| `GameplayInsights` | Runtime | 动画系统数据的 Insights 通道录制（动画图状态、骨骼数据等） |
| `GameplayInsightsEditor` | Runtime | Insights 工具中的动画调试面板 UI |
| `RewindDebugger` | Runtime | 回溯调试器核心框架：时间轴 UI、Track 管理、录制/回放控制 |
| `RewindDebuggerRuntime` | Runtime | 回溯调试器的运行时数据录制基础设施 |
| `RewindDebuggerVLog` | Runtime | 将 Visual Logger 数据集成到回溯调试器的 UI 层 |
| `RewindDebuggerVLogRuntime` | Runtime | Visual Logger 数据的运行时录制桥接 |

## 蓝图用法

本插件主要面向**编辑器工具和运行时调试**，不提供面向游戏逻辑的蓝图 API。交互方式为：

1. 在编辑器中打开 **Window → Developer Tools → Rewind Debugger** 面板
2. 运行 PIE（Play In Editor），Rewind Debugger 自动开始录制
3. 使用时间轴控件回溯查看各帧状态

> ⚠️ 插件默认未启用（`EnabledByDefault: false`），需要在 Edit → Plugins 中手动启用，或通过项目配置文件启用。

## C++ 用法

### 扩展 RewindDebugger Track

RewindDebugger 采用可扩展的 Track 架构，你可以注册自定义 Track 来可视化自己的系统数据：

```cpp
// 头文件引入
#include "RewindDebugger.h"
#include "IRewindDebuggerExtension.h"

// 实现自定义 Track（参考 RewindDebuggerVLog 模块的实现模式）
class FMyCustomTrack : public IRewindDebuggerTrack
{
public:
    virtual bool UpdateCamera() override { return false; }
    virtual void IterateSubTracks(TFunction<void(IRewindDebuggerTrack&)> Callback) override {}
    virtual bool HasProcessors() const override { return false; }
    // ... 其他接口实现
};

// 注册到 RewindDebugger
// 参考源码: RewindDebugger 模块中的 FRewindDebugger::RegisterTrack()
```

### 集成动画数据录制

```cpp
// 头文件引入
#include "GameplayInsightsModule.h"

// GameplayInsights 模块通过 Insights 的 Trace 系统录制动画数据
// 数据通道定义在 GameplayInsights 模块中
// 参考源码: Engine/Plugins/Animation/GameplayInsights/Source/GameplayInsights/
```

### 头文件引入

```cpp
// 回溯调试器核心
#include "RewindDebugger.h"

// 运行时录制
#include "RewindDebuggerRuntime.h"

// 动画 Insights
#include "GameplayInsightsModule.h"
```

## 模块依赖

由于插件包含 6 个模块且依赖关系较复杂，以下列出各模块的**关键独特依赖**：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 的数据服务层，用于注册和查询 Trace 通道 |
| `TraceAnalysis` | Insights 的 Trace 数据分析框架 |
| `RewindDebugger` | 回溯调试器核心框架（其他模块依赖此模块） |
| `RewindDebuggerRuntime` | 运行时录制基础设施 |
| `GameplayInsights` | 动画数据录制和 Insights 通道定义 |
| `AnimationCore` | 动画核心数据类型（骨骼、变换等） |
| `AnimGraphRuntime` | 动画图运行时，用于录制动画图状态 |
| `VisualLogger` | Visual Logger 系统（VLog 模块依赖） |

## 维护状态

### 近期更新

```
- 1c99e02fa85a [StateTreeDebugger] Prevent StateTreeDebugger from auto-recording on PIE start when not using the legacy mode. Users should rely on the RewindDebugger option. #jira UE-347105
- 1f3a6a06c1b0 [RewindDebugger] fixed primary track not assigned immediately on track creation
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
```

- 最近的更新涉及 StateTree 调试器集成和 RewindDebugger 的 track 创建 bug 修复，表明插件仍在积极维护中。
- StateTree 集成说明该插件正在扩展支持更多游戏框架的调试能力。

### 维护评价

- **创建时间**：2019 年，已有约 6 年历史
- **维护状态**：**活跃维护中**。近期 commit 包含功能改进（StateTree 集成）和 bug 修复，说明 Epic 持续投入开发
- **重要性**：这是 Unreal Engine 官方动画调试的核心工具，被 StateTree Debugger 等新系统依赖
- **注意事项**：
  - 插件默认未启用，需要手动开启
  - 仅在 UnrealInsights 程序中可用（`SupportedPrograms`）
  - 6 个模块的架构可能对初学者有一定学习门槛
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。如果你在做任何动画相关的开发工作，这是不可或缺的调试工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [GameplayInsights 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/GameplayInsights)
- [GameplayInsightsEditor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/GameplayInsightsEditor)
- [RewindDebugger 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebugger)
- [RewindDebuggerRuntime 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerRuntime)
- [RewindDebuggerVLog 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLog)
- [RewindDebuggerVLogRuntime 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLogRuntime)