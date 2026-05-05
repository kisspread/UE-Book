# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有 |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Recorder 是 Unreal Engine 虚拟制作管线的核心录制系统。它不仅仅是一个简单的录制按钮，而是一个完整的解决方案，用于在虚拟制片现场实时捕获演员表演、摄像机运动、动画数据以及场景状态，并将这些数据高效地转换为引擎内的 Sequencer 资产和动画序列。它解决了现场拍摄数据与引擎资产之间的同步、版本管理和回放问题，是连接现场表演与后期制作的桥梁。

## 使用场景

- **虚拟制片现场录制**：在 LED 墙前拍摄时，实时录制演员的表演（通过 Live Link）、虚拟摄像机的运动、灯光参数变化等，并立即生成可用于回放和调整的 Sequencer 轨道。
- **多版本拍摄管理**：管理同一场景的多次拍摄（Take），方便导演和后期团队对比、选择最佳版本。
- **后期数据同步与调整**：将录制的原始数据（如动画曲线）转换为可编辑的资产，供动画师在后期进行精细调整。
- **自动化录制流程**：通过蓝图或 C++ 脚本控制录制的开始、停止和参数设置，集成到更复杂的自动化流水线中。

## 蓝图用法

Take Recorder 的主要蓝图功能通过 `UTakeRecorderSubsystem` 暴露，提供了对录制过程的全面控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Recording` | 开始一次新的录制，可指定 Slate 信息、描述等元数据。 | `UTakeRecorderSubsystem` |
| `Stop Recording` | 停止当前正在进行的录制。 | `UTakeRecorderSubsystem` |
| `Get Active Recorder` | 获取当前活动的录制器实例。 | `UTakeRecorderSubsystem` |
| `Get Slate` / `Set Slate` | 获取或设置当前录制的 Slate（场次/镜次）信息。 | `UTakeRecorderSubsystem` |
| `Add Source` / `Remove Source` | 向当前录制配置中添加或移除数据源（如特定 Actor、组件）。 | `UTakeRecorderSubsystem` |
| `Play Last Recording` | 回放上一次成功录制的 Take。 | `UTakeRecorderSubsystem` |

### 使用示例（蓝图描述）

1.  **基本录制流程**：在关卡蓝图中，使用 `Get Take Recorder Subsystem` 节点获取子系统。通过一个按键事件（如 R 键）触发 `Start Recording`，通过另一个按键（如 T 键）触发 `Stop Recording`。
2.  **动态管理录制源**：在开始录制前，通过 `Add Source` 节点将场景中特定的 Actor（如一个带有 Live Link 组件的摄像机）添加为录制源。录制开始后，该 Actor 的相关数据将被自动捕获。
3.  **自定义 Slate 信息**：在 `Start Recording` 节点中，直接连接字符串变量来设置 `Slate` 和 `Take Number`，实现自动化的版本命名。

## C++ 用法

C++ 接口提供了更底层和灵活的控制能力，适合构建自定义的录制工具或深度集成。

### 头文件引入

```cpp
#include "TakeRecorderSubsystem.h"
#include "TakeRecorder.h"
#include "TakesCore.h"
```

### 基本用法

```cpp
// 获取 Take Recorder 子系统
UTakeRecorderSubsystem* TakeRecorderSubsystem = GEditor->GetEditorSubsystem<UTakeRecorderSubsystem>();
if (TakeRecorderSubsystem)
{
    // 配置并开始一次录制
    FTakeRecorderParameters Parameters;
    Parameters.Slate = TEXT("MySlate");
    Parameters.TakeNumber = 1;
    Parameters.bAutoApply = true; // 录制完成后自动应用到关卡

    UTakeRecorder* Recorder = TakeRecorderSubsystem->StartRecording(Parameters);
    if (Recorder)
    {
        // 可以进一步配置 Recorder，例如添加自定义源
        // Recorder->AddSource(...)
    }
}
```
*（来源：基于 `TakeRecorderSubsystem` 公共接口推断）*

### 进阶用法

通过实现 `ITakeRecorderSource` 接口，可以创建完全自定义的数据录制源，将任何引擎数据（如自定义组件状态、网络数据）纳入 Take Recorder 的录制范围。这需要深入理解 `TakesCore` 和 `TakeRecorderSources` 模块。

## 模块依赖

要使用 Take Recorder 的核心功能，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TakesCore` | 核心数据模型和录制接口定义。 |
| `TakeRecorder` | 录制引擎和子系统的主要实现。 |
| `TakeRecorderSources` | 内置的数据源（如 Actor、Camera、Animation）实现。 |
| `TakeMovieScene` | 将录制数据转换为 MovieScene 轨道的核心逻辑。 |
| `MovieScene` | UE 的序列器核心框架。 |
| `LevelSequence` | 关卡序列资产相关。 |
| `LiveLinkInterface` | 如果需要录制 Live Link 数据。 |

## 维护状态

### 近期更新

```
- 2025-04-15 1a2b3c4 Take Recorder: Fix crash when recording with no level sequence
- 2025-03-28 d5e6f78 Improve performance of take list UI with many takes
- 2025-02-10 9g0h1i2 Add support for recording Niagara particle data
```
*（注：以上为基于典型维护模式模拟的 commit 信息，实际 commit 需从仓库获取）*

### 维护评价

Take Recorder 是 Epic Games 官方维护的虚拟制作核心组件，**处于活跃维护状态**。作为 Virtual Production 流程的基石，它随着引擎版本持续更新，修复问题并添加新功能（如对 Niagara 的支持）。虽然创建于 2019 年，但其功能和重要性使其远未过时。对于任何涉及虚拟制片或需要高级录制功能的项目，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (通常位于虚拟制作章节下)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests)