# Motion Design Scene State

> （Description 字段为空，基于源码分析）为虚拟制片（Motion Design）场景提供状态机驱动的场景状态管理系统，支持状态切换、事件触发、数据绑定和任务执行。

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是一个面向虚拟制片（Motion Design）场景的状态管理系统。它解决的核心问题是：**在复杂的虚拟制片场景中，如何以可视化、可编程的方式管理场景中各元素的状态流转**。

该插件提供了一套完整的状态机框架，包括：

- **状态机（State Machine）**：定义场景中对象的状态及状态之间的转换规则
- **事件系统（Event）**：状态转换的触发机制，支持自定义事件定义和事件图表
- **数据绑定（Binding）**：将状态数据与场景中的实际对象属性进行绑定
- **任务系统（Tasks）**：状态激活时执行的具体逻辑（如动画播放、材质切换等）
- **蓝图集成**：通过蓝图图表编辑器可视化编辑状态机逻辑

该插件从 Experimental 迁移到 VirtualProduction 目录，表明 Epic 将其定位为 Motion Design 工具链的核心组件。

## 使用场景

- 你在做虚拟制片的 Motion Design 场景 → 需要管理场景中多个元素的联动状态切换
- 你需要一个可视化的状态机编辑器来定义场景流程 → 用 SceneState 的图表编辑器
- 你需要在状态切换时触发特定的场景效果（灯光变化、动画播放等） → 用 SceneStateTasks
- 你需要将状态数据绑定到场景对象的属性上 → 用 SceneStateBinding
- 你需要自定义事件来驱动状态转换 → 用 SceneStateEvent

## 模块架构

本插件由 14 个模块组成，按功能分为以下几层：

### 核心层

| 模块 | 类型 | 说明 |
|---|---|---|
| `SceneState` | Runtime | 核心状态机运行时，定义状态、转换、上下文等基础类型 |
| `SceneStateBinding` | Runtime | 数据绑定系统，将状态数据映射到场景对象属性 |
| `SceneStateEvent` | Runtime | 事件系统，定义事件类型和事件触发机制 |
| `SceneStateTasks` | Runtime | 任务系统，定义状态激活时执行的具体操作 |

### 蓝图层

| 模块 | 类型 | 说明 |
|---|---|---|
| `SceneStateBlueprint` | Runtime | 蓝图集成，提供蓝图可用的状态机类型 |
| `SceneStateGameplay` | Runtime | Gameplay 集成，将状态机与游戏逻辑关联 |

### 编辑器层

| 模块 | 类型 | 说明 |
|---|---|---|
| `SceneStateEditor` | Runtime | 状态机编辑器核心 UI |
| `SceneStateBlueprintEditor` | Runtime | 蓝图编辑器扩展 |
| `SceneStateEventEditor` | Runtime | 事件编辑器 |
| `SceneStateEventGraph` | Runtime | 事件图表编辑器（可视化编辑事件逻辑） |
| `SceneStateGameplayEditor` | Runtime | Gameplay 编辑器扩展 |
| `SceneStateMachineEditor` | Runtime | 状态机编辑器（可视化编辑状态和转换） |
| `SceneStateMachineGraph` | Runtime | 状态机图表（节点和连线的图表表示） |
| `SceneStateTransitionGraph` | Runtime | 转换图表（可视化编辑状态转换条件） |

## 蓝图用法

> ⚠️ 本插件为实验性功能，API 可能在后续版本中发生变化。

### 核心节点

由于本插件主要通过编辑器图表（而非蓝图节点）进行交互，运行时蓝图 API 较少。核心交互通过状态机资产完成。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 状态机资产编辑 | 在编辑器中创建和编辑状态机资产 | `USceneStateMachine` |
| 事件触发 | 通过事件驱动状态转换 | `USceneStateEvent` |
| 数据绑定配置 | 将状态输出绑定到场景对象 | `USceneStateBinding` |

### 使用示例（编辑器工作流）

1. **创建状态机资产**：在 Content Browser 中右键 → Virtual Production → Scene State → 创建状态机资产
2. **编辑状态**：双击打开状态机编辑器，添加状态节点
3. **定义转换**：在状态之间创建转换连线，设置转换条件
4. **配置任务**：为每个状态配置要执行的任务（如播放动画、切换材质等）
5. **设置绑定**：将任务参数绑定到场景中的实际对象属性
6. **触发事件**：在运行时通过事件触发状态转换

## C++ 用法

### 头文件引入

```cpp
#include "SceneState.h"
#include "SceneStateBinding.h"
#include "SceneStateEvent.h"
#include "SceneStateTasks.h"
```

### 基本用法

本插件的核心逻辑通过编辑器资产驱动，C++ 扩展主要集中在自定义任务和事件类型。

```cpp
// 自定义状态任务示例
// 来源: SceneStateTasks 模块结构
#include "SceneStateTask.h"

UCLASS()
class UMyCustomTask : public USceneStateTask
{
    GENERATED_BODY()

public:
    // 任务激活时调用
    virtual void Activate(const FSceneStateExecutionContext& Context) override;

    // 任务结束时调用
    virtual void Deactivate(const FSceneStateExecutionContext& Context) override;
};
```

### 进阶用法

```cpp
// 自定义事件类型
#include "SceneStateEvent.h"

UCLASS()
class UMyCustomEvent : public USceneStateEvent
{
    GENERATED_BODY()

public:
    // 定义事件携带的数据
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Intensity;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLinearColor Color;
};

// 自定义数据绑定
#include "SceneStateBinding.h"

// 通过绑定系统将状态数据映射到场景对象
// 绑定在编辑器中配置，运行时自动解析
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MotionDesignCore` | Motion Design 核心框架（推测，基于 VirtualProduction 上下文） |
| `DataLink` | 数据链接系统，与 SceneState 配合实现数据绑定 |

> 注：具体依赖需查看各模块 Build.cs 确认。本插件位于 VirtualProduction 目录下，与 Motion Design 工具链紧密集成。

## 维护状态

### 近期更新

```
- 2e995baebf56 Fix `suppress` misspellings in Engine/Plugins.
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

### 维护评价

- **创建时间**：2025-04-22，非常新的插件
- **迁移状态**：刚从 Experimental 迁移到 VirtualProduction，表明 Epic 正在积极整合
- **Beta 状态**：IsBetaVersion=true，API 可能不稳定
- **模块规模**：14 个模块、701 个源文件，架构完整但复杂
- **推荐程度**：⚠️ **谨慎使用** — 作为实验性/Beta 插件，适合在 Motion Design 工作流中尝试，但不建议在生产环境中作为核心依赖。关注后续版本的 API 稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]()（暂无）