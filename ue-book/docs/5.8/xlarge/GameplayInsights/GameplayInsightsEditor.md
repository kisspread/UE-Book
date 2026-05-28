# Animation Insights

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | 动画洞察 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

GameplayInsights 插件为 **Unreal Insights** 工具提供扩展功能，专注于**游戏运行时数据（尤其是动画系统）的调试与性能分析**。它解决了在复杂场景中难以追踪和理解动画蓝图执行流程、性能瓶颈以及对象状态变化的问题。该插件通过集成到 Unreal Insights 的时间线视图中，允许开发者回溯（Rewind）游戏状态，并可视化地检查动画姿态、骨骼网格体数据、动画节点执行顺序等关键信息。

其核心价值在于将游戏逻辑（Gameplay）与底层性能分析（Insights）工具无缝结合，为动画程序员和游戏逻辑开发者提供了一个强大的、时间线维度的调试工具。

## 使用场景

- **动画性能分析**：当你需要定位动画蓝图中的性能瓶颈，例如哪个 AnimNode 或 PoseLink 消耗了过多 CPU 时间时，可以使用 Animation Insights 在 Unreal Insights 的时间线上查看对应的耗时块。
- **动画状态回溯调试**：当角色动画出现意外行为（如穿模、姿态错误）时，可以利用 **Rewind Debugger** 功能，回退到问题发生的时刻，逐步检查当时的动画姿态、骨骼变换以及相关的动画事件。
- **理解复杂动画图逻辑**：对于大型或复杂的动画蓝图，可以通过该插件追踪动画求值节点的执行顺序和数据流向，帮助理解其内部工作原理。
- **与虚拟日志 (VLog) 结合**：`RewindDebuggerVLog` 模块可能支持在时间线上叠加游戏内生成的文本日志信息，实现上下文关联的调试。

## 蓝图用法

基于现有分析，该插件主要作为调试和分析工具集成到 Unreal Insights 中，其核心功能通常通过 Unreal Insights 的 UI 触发，而非传统的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPoseFromProvider` | 从动画数据提供者设置骨骼网格体组件的姿态，用于重放或显示记录的姿态数据。 | `UInsightsSkeletalMeshComponent` |

### 使用示例（蓝图描述）

此插件的主要交互发生在 Unreal Insights 的应用程序界面中。开发者通常在游戏运行时启用追踪通道（Trace Channels），然后在 Insights 中打开生成的 `.utrace` 文件。在 Insights 的 “Animation” 或 “Gameplay” 轨道上，可以：
1.  **查看动画事件和姿态**：在时间线上找到特定帧，查看该时刻的动画状态和骨骼姿态。
2.  **使用 Rewind Debugger**：在 Insights 工具栏中激活“Rewind Debugger”模式，此时可以像回放视频一样拖动时间轴，游戏世界的状态（包括动画姿态）会同步回退到对应时刻。
3.  **关联 SkeletalMeshComponent**：在 Rewind 模式下选中一个 Actor，其 `SkeletalMeshComponent` 的动画数据会通过类似 `UInsightsSkeletalMeshComponent` 的机制被重放，以可视化调试。

## C++ 用法

该插件的运行时逻辑主要服务于数据收集和与 Insights 工具的交互。开发者通常通过 C++ 在游戏模块中启用相应的追踪通道。

### 头文件引入

```cpp
#include "GameplayInsightsModule.h" // 引入插件主模块
```

### 基本用法

要启用动画和游戏逻辑的追踪，需要在项目启动时初始化相关模块。具体依赖于项目的设置。

### 进阶用法

自定义或扩展追踪数据可能需要深入 `AnimationProvider` 和相关的消息类型（如 `FSkeletalMeshPoseMessage`），这通常涉及更底层的 Trace 系统操作。

## Demo 示例

该插件为 Unreal Insights 的内置扩展，其“示例”即为使用 Unreal Insights 工具本身。标准的使用流程如下：

1.  **启动游戏并启用追踪**：通过命令行参数 `-trace=animation,gameplay` 启动游戏，或在编辑器项目设置中启用相应的追踪通道。
2.  **连接 Unreal Insights**：运行 `UnrealInsights.exe` 并连接到正在运行的游戏实例，或直接打开生成的 `.utrace` 文件。
3.  **分析数据**：在 Insights 界面中，切换到“Animation”或“Gameplay”轨道，查看时间线上的数据点。激活“Rewind Debugger”工具进行交互式调试。

## 模块依赖

从模块名称和通用实践推断，该插件内部模块之间有依赖关系。使用该插件的项目模块可能需要依赖：

| 模块 | 用途 |
|---|---|
| `TraceAnalysis` / `TraceServices` | Unreal Insights 底层数据追踪和分析服务。 |
| `AnimationCore` | 动画系统的核心数据结构与接口。 |
| `AnimationBlueprintLibrary` | 可能用于辅助动画蓝图相关的调试信息提取。 |

*注：具体依赖需查阅各子模块的 `Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it’s active | 修复了在拾色器激活时重新附着玩家控制导致的Rewind调试器状态问题 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 为Rewind调试器接口添加了可编程的时间轴拖拽和视图居中功能 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对Rewind调试器的工具栏进行了用户体验优化 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 对Rewind调试器进行了更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至新的UE_LOGF |

### 维护评价

该插件仍处于**活跃维护**状态。从近期（2026年4月-5月）的提交记录来看，开发团队正在持续改进 `RewindDebugger` 模块的功能和用户体验，例如添加新的交互方式和优化界面。这表明该插件是 Unreal Engine 调试工具链中一个重要的、持续发展的部分。

它特别适合需要深度分析和调试动画系统、游戏逻辑时序问题的项目。需要注意的是，该插件默认未启用 (`EnabledByDefault: false`)，需要开发者在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/GameplayInsights)（如果存在）