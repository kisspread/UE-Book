# Motion Design Scene State Integration

> A plugin that integrates UE5's Scene State framework with Motion Design (Avalanche), providing tasks for sequence playback, Remote Control controller manipulation, and ticker actor spawning within a state-machine-driven workflow.

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction (原 Experimental) |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器图标） |
| 模块 | `AvalancheSceneState` (Runtime), `AvalancheSceneStateBlueprint` (UncookedOnly), `AvalancheSceneStateEditor` (Editor) |
| 实验性 | ⚠️ 是 (IsBetaVersion=true) |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheSceneState) | |

---

## 用途

AvalancheSceneState 是 Motion Design（Avalanche）生态系统与 UE5 Scene State 框架之间的桥接插件。

**它解决的核心问题**：Motion Design 工作流需要一个状态机来管理场景中各元素的状态切换（如切换画面布局、播放动画序列、修改远程控制参数等），而 Scene State 正是 UE5 提供的状态机框架。本插件将两者对接，使 Motion Design 用户可以在 Scene State 蓝图中直接使用 Motion Design 特有的 Task（序列播放、RC 控制器、Ticker 生成等）。

**插件依赖关系**：

```
Avalanche (Motion Design 核心)
    ↓
AvalancheSceneState (本插件，桥接层)
    ↓
SceneState / SceneStateBinding / SceneStateTasks / SceneStateGameplay (UE5 状态机框架)
```

---

## 架构概览

插件围绕以下几个核心类构建：

```
AAvaSceneStateActor          ← 每个 Motion Design 场景只有一个，管理嵌入式 Scene State Blueprint
  └─ UAvaSceneStateComponent ← 继承 USceneStateComponent，使用自定义 Player
       └─ UAvaSceneStatePlayer ← 继承 USceneStateComponentPlayer，禁止编辑器内编辑状态类
```

**Task 体系**（均继承自 `FSceneStateTask`）：

| Task | 显示名称 | 功能 |
|---|---|---|
| `FAvaSceneStatePlaySequenceTask` | Play Sequence | 按名称或标签播放 Motion Design 序列 |
| `FAvaSceneStateRCTask` | Set RC Controller Values | 将 PropertyBag 中的值写入 Remote Control 控制器 |
| `FAvaSceneStateSpawnerTickerTask` | Spawn Actor to Ticker | 生成 Actor 并将其排队到 Ticker 组件 |

**Remote Control 集成**：

| 类 | 功能 |
|---|---|
| `UAvaSceneStateRCEventBehavior` | RC Behavior 子类，配合 BehaviorNode 使用 |
| `UAvaSceneStateRCEventBehaviorNode` | 在 RC 行为通过时广播 Scene State 事件 |

---

## 使用场景

- **你在做 Motion Design 项目，需要在不同画面状态之间切换** → 使用本插件在 Scene State 蓝图中定义状态和切换逻辑
- **你需要在状态切换时自动播放/停止 Motion Design 序列** → 使用 `Play Sequence` Task
- **你需要通过状态机控制 Remote Control Preset 中的控制器值** → 使用 `Set RC Controller Values` Task
- **你需要在状态切换时生成 Actor 并加入 Ticker 系统** → 使用 `Spawn Actor to Ticker` Task
- **你需要在 Remote Control 行为触发时广播事件给 Scene State** → 使用 `Broadcast Event` Behavior Node

---

## 核心类详解

### AAvaSceneStateActor

继承自 `ASceneStateActor`，是 Motion Design 场景中的 Scene State 容器。

**编辑器特性**：
- 每个 World 最多存在一个实例（`FindOrSpawnSceneStateActor` 语义）
- 内嵌 `USceneStateBlueprint`（非独立资产，作为 Actor 的子对象存在）
- Blueprint 编译时自动更新 Scene State Generated Class
- World 清理时自动清理嵌入的 Blueprint 资源
- 不在场景大纲中显示为用户管理的 Actor（`IsUserManaged() = false`）

### FAvaSceneStatePlaySequenceTask

在状态机进入某状态时播放 Motion Design 序列。

**关键配置**：
- `SequenceQueryType`：按名称（`Name`）或按标签（`Tag`）查找序列
- `SequenceName` / `SequenceTag`：具体的查找条件
- `PlaySettings`：播放参数（`FAvaSequencePlayParams`）
- `WaitType`：等待类型 — `WaitUntilStop`（等待序列播放完毕）或 `NoWait`（立即完成 Task）

**执行流程**：
1. 查找场景的 `IAvaSceneInterface` → 获取 `IAvaSequencePlaybackObject`
2. 根据 `SequenceQueryType` 调用 `PlaySequencesByLabel` 或 `PlaySequencesByTag`
3. 如果有等待需求，监听 `OnSequenceFinished` 事件；所有序列播放完毕后标记 Task 完成

### FAvaSceneStateRCTask

将 PropertyBag 中存储的值批量写入 Remote Control Preset 的控制器。

**关键概念**：
- `ControllerMappings`：控制器映射数组，每条映射包含目标控制器 ID（`TargetController`）和源属性 ID（`SourcePropertyId`）
- `ControllerValues`：`FInstancedPropertyBag`，存储要写入的值
- 支持**类型提升**（Promotion Copy）：如 `bool → int`、`float → double` 等兼容类型自动转换

**执行流程**：
1. 通过 `FindSceneInterface` 获取场景接口 → 获取 `URemoteControlPreset`
2. 遍历 PropertyBag 中的每个属性，找到对应的 Controller Mapping
3. 根据类型兼容性（Compatible / Promotable）复制值到控制器
4. 调用 `OnModifyPropertyValue()` 通知修改，广播 `OnControllerModified`

### FAvaSceneStateSpawnerTickerTask

继承自 `FSceneStateSpawnActorTask`，在生成 Actor 后将其加入 Ticker 组件队列。

**关键配置**：
- `Ticker`：目标 Ticker Actor（必须包含 `UAvaTickerComponent`）
- 继承父类的 Actor 类、生成位置等配置

**执行流程**：
1. `ShouldSpawnActor` 验证 Ticker Actor 有效且包含 `UAvaTickerComponent`
2. 父类生成 Actor
3. `OnActorSpawned` 调用 `TickerComponent->QueueActor(InActorChecked)` 将其加入队列

### UAvaSceneStateRCEventBehaviorNode

Remote Control 行为节点，在行为通过时广播 Scene State 事件。

**配置**：
- `Event`（`FSceneStateEventTemplate`）：要广播的事件模板

**适用条件**：Behavior 必须是 `UAvaSceneStateRCEventBehavior` 类型，且能获取到有效的 World 上下文。

---

## 蓝图用法

本插件主要通过 Scene State Blueprint 编辑器使用，不直接暴露 BlueprintCallable 函数。工作流如下：

### 编辑器工作流

1. 在 Motion Design 编辑器工具栏点击 **Scene State** 按钮（自动创建或打开 Scene State Actor 和 Blueprint）
2. Scene State Blueprint 编辑器中，添加 State 并配置 Transition
3. 在 State 的 Task 列表中添加：
   - **Play Sequence** — 配置序列名称/标签和播放参数
   - **Set RC Controller Values** — 添加控制器映射，设置目标控制器和值
   - **Spawn Actor to Ticker** — 配置 Actor 类和目标 Ticker Actor
4. 使用工具栏下拉菜单中的 **Delete Scene State** 选项删除场景状态

### RC 控制器值编辑器界面

`Set RC Controller Values` Task 有专门的自定义 Details 面板：
- **Controller Mappings** 数组：每行显示目标控制器选择器
- **Controller Values** 属性袋：每行显示值编辑器 + 类型选择器（Pin Type Selector）
- 映射和值通过 PropertyBag 的 ID 一一对应，自动同步

---

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "AvaSceneStateActor.h"
#include "AvaSceneStateComponent.h"
#include "AvaSceneStatePlayer.h"

// Remote Control Task
#include "RemoteControl/AvaSceneStateRCTask.h"

// Sequence Task
#include "Sequence/AvaSceneStatePlaySequenceTask.h"

// Ticker Task
#include "Ticker/AvaSceneStateSpawnerTickerTask.h"
```

### 查找场景接口

场景接口是连接 Scene State 执行上下文与 Motion Design 场景的桥梁。所有 Task 内部都通过它获取场景资源（RC Preset、Sequence Player 等）。

来源：`AvaSceneStateUtils.cpp`

```cpp
#include "AvaSceneStateUtils.h"  // Private, 内部使用
#include "AvaSceneSubsystem.h"
#include "SceneStateExecutionContext.h"

// 在 Task 执行上下文中查找 Motion Design 场景接口
IAvaSceneInterface* SceneInterface = UE::AvaSceneState::FindSceneInterface(InContext);
if (SceneInterface)
{
    // 获取 Remote Control Preset
    URemoteControlPreset* Preset = SceneInterface->GetRemoteControlPreset();
    
    // 获取序列播放对象
    IAvaSequencePlaybackObject* PlaybackObject = SceneInterface->GetPlaybackObject();
}
```

### RC Task 值写入与类型提升

来源：`AvaSceneStateRCTask.cpp`

```cpp
// 支持的类型提升路径：
// Bool  → Byte, Int32, UInt32, Int64, Float, Double
// Byte  → Int32, UInt32, Int64, Float, Double
// Int32 → Int64, Float, Double
// Float → Int32, Int64, Double

// 实际写入逻辑（简化）：
switch (Compatibility)
{
case EPropertyCompatibility::Compatible:
    // 直接复制
    TargetProperty->CopyCompleteValue(TargetMemory, SourceMemory);
    break;

case EPropertyCompatibility::Promotable:
    // 类型提升后复制（如 float → double）
    UE::AvaSceneState::Private::PromoteCopy({
        .SourceProperty = SourcePropertyDesc.CachedProperty,
        .SourceMemory = SourceMemory,
        .TargetProperty = TargetProperty,
        .TargetMemory = TargetMemory
    });
    break;
}
```

### 播放序列并等待完成

来源：`AvaSceneStatePlaySequenceTask.cpp`

```cpp
// 监听序列完成事件
Instance.OnSequenceFinishedHandle = UAvaSequencePlayer::OnSequenceFinished()
    .AddStatic(&FAvaSceneStatePlaySequenceTask::OnSequenceStopped, TaskContext);

// 按名称播放
Instance.SequencePlayers = PlaybackObject->PlaySequencesByLabel(
    Instance.SequenceName, Instance.PlaySettings);

// 或按标签播放
Instance.SequencePlayers = PlaybackObject->PlaySequencesByTag(
    Instance.SequenceTag, /*bExactMatch*/ true, Instance.PlaySettings);

// 如果没有等待需求或无序列被播放，立即完成
if (Instance.SequencePlayers.IsEmpty() || WaitType == NoWait)
{
    Finish(InContext, InTaskInstance);
}
```

---

## 模块依赖

### AvalancheSceneState (Runtime) — 依赖

| 模块 | 用途 |
|---|---|
| `AvalancheRemoteControl` | Motion Design 远程控制集成 |
| `AvalancheSequence` | Motion Design 序列系统 |
| `AvalancheTag` | Motion Design 标签系统 |
| `SceneState` | UE5 Scene State 核心框架 |
| `SceneStateBinding` | Scene State 属性绑定系统 |
| `SceneStateTasks` | Scene State Task 基础设施 |
| `SceneStateGameplay` | Scene State Gameplay 集成 |
| `RemoteControl` | Remote Control Preset 系统 |
| `RemoteControlLogic` | Remote Control 逻辑/行为系统 |
| `SceneStateEvent` | Scene State 事件系统 |
| `PropertyBindingUtils` | 属性绑定工具（类型兼容性检查） |

### AvalancheSceneStateBlueprint (UncookedOnly) — 依赖

| 模块 | 用途 |
|---|---|
| `SceneStateBlueprint` | Scene State Blueprint 资产类 |
| `PropertyBindingUtils` | 属性绑定工具 |

### AvalancheSceneStateEditor (Editor) — 依赖

| 模块 | 用途 |
|---|---|
| `AvalancheEditorCore` | Motion Design 编辑器核心（FAvaEditorBuilder） |
| `SceneStateBlueprintEditor` | Scene State Blueprint 编辑器 |
| `PropertyEditor` | UE 属性自定义面板 |
| `StructUtilsEditor` | StructUtils 编辑器支持 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-09-12 | `f89d77efed22` | Additional non-unity fixes from removing GCObject.h from StrongObjectPtr.h | 编译修复，非功能性更新 |
| 2025-08-27 | `f25e96ca6e25` | Motion Design: set the scene state and data link plugins to beta | 将插件标记为 Beta（`IsBetaVersion=true`） |
| 2025-08-27 | `94f961385e8e` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 从 Experimental 迁移到 VirtualProduction 目录 |
| 2025-08-20 | `a02df074ac86` | Motion Design: fixed crash when deleting scene state actor while selected | Bug 修复：删除选中的 Scene State Actor 时崩溃 |
| 2025-08-18 | `436fff18a989` | Added spawner ticker task | 新增 `Spawn Actor to Ticker` Task |

### 维护评价

- **创建时间**：2025-04-22，约 1 年历史
- **活跃度**：2025 年 8-9 月有密集更新（迁移到正式目录、新增功能、Bug 修复），之后无更新
- **状态**：Beta 阶段（`IsBetaVersion=true`），刚从 Experimental 升级
- **趋势**：作为 Motion Design 生态的核心组件（Scene State 集成），预计将随 Motion Design 一起继续维护
- **注意**：此插件依赖 Scene State 框架（同样是实验性/Beta 状态），两者可能同步演进
- **建议**：可用于 Motion Design 项目的原型开发，但生产环境需关注后续 API 稳定性

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/AvalancheSceneState)
- [Scene State 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SceneState)（基础框架）
- [Avalanche (Motion Design)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)（父级生态）
