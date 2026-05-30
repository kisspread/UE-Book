# Motion Design Scene State

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态机 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是一套面向**虚拟制作 / Motion Design** 的可视化状态机系统。它解决了在虚拟制作场景中，如何以图形化方式编排、驱动和管理"场景状态"的问题。

核心能力：
- **场景状态机**：以节点图方式定义场景中的状态和状态间的转换逻辑
- **事件驱动**：通过事件系统（Event）触发状态转换和任务执行
- **数据绑定（Binding）**：将状态机中的数据与外部对象属性进行绑定，实现双向驱动
- **任务系统（Tasks）**：每个状态可挂载一系列任务（Task），在进入/退出状态时执行
- **游戏运行时集成**：通过组件（Component）和 Actor 方式嵌入关卡，支持运行时播放状态机

该插件从 Experimental 分类迁移到 VirtualProduction，说明 Epic 正在将其作为 Motion Design 工作流的核心基础设施来推进。

## 使用场景

- 你在做**虚拟制作**项目，需要在关卡中编排灯光、材质、动画等元素的切换流程 → 用 SceneState 定义状态和转换
- 你需要在 Motion Design 中用**事件驱动**场景元素的变化 → 用 SceneStateEvent 定义事件并绑定到状态转换
- 你想让设计师通过**可视化图表**而非代码来配置场景逻辑 → 用 SceneStateMachineGraph / SceneStateTransitionGraph 编辑器
- 你需要将状态机运行时嵌入 Actor 并通过蓝图控制 → 用 SceneStateComponent / SceneStateActor

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSceneState` | 获取当前正在运行的场景状态对象 | `USceneStateComponent` |
| `GetSceneState` | 从 Actor 获取场景状态对象 | `ASceneStateActor` |
| `GetSceneStateClass` | 获取当前关联的场景状态类 | `USceneStateComponent` |
| `SetSceneStateClass` | 设置要运行的场景状态类 | `USceneStateComponent` |
| `GetSceneStateComponent` | 获取 Actor 上的场景状态组件 | `ASceneStateActor` |

### 使用示例

**方式一：使用 SceneStateComponent（推荐）**

1. 在任意 Actor 上添加 `SceneStateComponent`
2. 在组件的 Details 面板中指定 `SceneStateClass`（即你要播放的状态机资产）
3. 运行时组件会自动初始化并播放状态机
4. 通过蓝图调用 `GetSceneState` 获取状态对象进行进一步操作

**方式二：使用 SceneStateActor（快速放置）**

1. 在场景中直接放置 `SceneStateActor`
2. 在 Details 面板中配置 `SceneStateClass`
3. Actor 内部已自带 `SceneStateComponent`，无需额外配置

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateComponent.h"
#include "SceneStateActor.h"
#include "SceneStateComponentPlayer.h"
#include "SceneStateGameplaySchema.h"
```

### 基本用法

**获取组件上的场景状态对象**

```cpp
// 假设已有一个 USceneStateComponent*
USceneStateComponent* StateComponent = MyActor->FindComponentByClass<USceneStateComponent>();
if (StateComponent)
{
    // 获取当前运行的场景状态对象
    USceneStateObject* StateObject = StateComponent->GetSceneState();
    
    // 获取/设置场景状态类
    TSubclassOf<USceneStateObject> StateClass = StateComponent->GetSceneStateClass();
    StateComponent->SetSceneStateClass(NewStateClass);
}
```

**通过 SceneStateActor 访问**

```cpp
// ASceneStateActor 封装了 SceneStateComponent
ASceneStateActor* StateActor = /* 获取或 Spawn */;
USceneStateComponent* Component = StateActor->GetSceneStateComponent();
USceneStateObject* StateObject = StateActor->GetSceneState();
```

### 进阶用法

**自定义场景状态 Schema**

```cpp
// 继承 USceneStateGameplaySchema 来定义自定义的允许任务和上下文
UCLASS()
class UMyCustomSchema : public USceneStateGameplaySchema
{
    GENERATED_BODY()

protected:
#if WITH_EDITOR
    virtual bool OnIsTaskStructAllowed(TSubScriptStructOf<FSceneStateTask> InTaskStruct) const override
    {
        // 过滤允许的任务类型
        return true;
    }
#endif

    virtual TSubclassOf<UObject> OnGetContextObjectClass() const override
    {
        // 返回上下文对象类，状态机运行时用它作为执行上下文
        return AActor::StaticClass();
    }
};
```

**组件实例数据缓存（用于关卡流送和编辑器场景重建）**

```cpp
// SceneStateComponent 自动支持实例数据缓存
// 当关卡流送或 Detail 面板触发重建时，状态机状态会被保留
TStructOnScope<FActorComponentInstanceData> InstanceData = StateComponent->GetComponentInstanceData();
// FSceneStateComponentInstanceData 会保存 SceneStatePlayer 的引用
```

## Demo 示例

**最小示例：在自定义 Actor 中使用 SceneStateComponent**

```cpp
// MySceneStateActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySceneStateActor.generated.h"

class USceneStateComponent;

UCLASS()
class AMySceneStateActor : public AActor
{
    GENERATED_BODY()

public:
    AMySceneStateActor();

    UFUNCTION(BlueprintCallable)
    void SwitchSceneState(TSubclassOf<USceneStateObject> NewStateClass);

    UFUNCTION(BlueprintCallable)
    USceneStateObject* GetCurrentSceneState() const;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Scene State", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<USceneStateComponent> SceneStateComponent;
};
```

```cpp
// MySceneStateActor.cpp
#include "MySceneStateActor.h"
#include "SceneStateComponent.h"
#include "SceneStateObject.h"

AMySceneStateActor::AMySceneStateActor()
{
    SceneStateComponent = CreateDefaultSubobject<USceneStateComponent>(TEXT("SceneState"));
    RootComponent = CreateDefaultSubobject<USceneSceneComponent>(TEXT("Root"));
}

void AMySceneStateActor::SwitchSceneState(TSubclassOf<USceneStateObject> NewStateClass)
{
    if (SceneStateComponent && NewStateClass)
    {
        SceneStateComponent->SetSceneStateClass(NewStateClass);
    }
}

USceneStateObject* AMySceneStateActor::GetCurrentSceneState() const
{
    if (SceneStateComponent)
    {
        return SceneStateComponent->GetSceneState();
    }
    return nullptr;
}
```

## 模块架构

本插件包含 14 个模块，按职责可分为以下几层：

| 层级 | 模块 | 职责 |
|---|---|---|
| **核心运行时** | `SceneState` | 状态机核心逻辑（状态定义、执行引擎） |
| | `SceneStateBinding` | 数据绑定层，连接状态机与外部对象属性 |
| | `SceneStateEvent` | 事件定义与分发系统 |
| | `SceneStateTasks` | 任务（Task）定义，状态进入/退出时执行的动作 |
| **运行时集成** | `SceneStateGameplay` | 游戏运行时集成（Component / Actor） |
| | `SceneStateBlueprint` | 蓝图资产支持 |
| **图表可视化** | `SceneStateMachineGraph` | 状态机节点图（状态 + 转换） |
| | `SceneStateEventGraph` | 事件图表 |
| | `SceneStateTransitionGraph` | 转换条件图表 |
| **编辑器 UI** | `SceneStateEditor` | 核心编辑器工具 |
| | `SceneStateBlueprintEditor` | 蓝图编辑器集成 |
| | `SceneStateEventEditor` | 事件编辑器 |
| | `SceneStateGameplayEditor` | 游戏集成编辑器 |
| | `SceneStateMachineEditor` | 状态机编辑器 |

## 模块依赖

由于未提供 SceneStateGameplay 模块的 Build.cs 完整内容，以下基于类继承和头文件推断关键依赖：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心状态机运行时，提供 USceneStateObject 和 USceneStatePlayer 基类 |
| `SceneStateEvent` | 事件系统，状态机转换依赖事件触发 |
| `SceneStateBinding` | 数据绑定，将状态数据与外部属性关联 |

> 注：完整依赖列表请参考各模块的 `Build.cs` 文件。所有编辑器相关模块（`*Editor`、`*Graph`）仅在编辑器环境下加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：优化客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了上一个 CL 的修改 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：重新提交通知机制优化 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复数据绑定未检查事件载荷结构体为空的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |

### 维护评价

- **活跃维护**：创建不到 1 年，最近更新在 2026-05，维护频率较高
- **实验性 / Beta**：`IsBetaVersion=true`，仍处于 Beta 阶段，API 可能会有变动
- **从 Experimental 迁移**：2025-08 从 Experimental 分类迁移到 VirtualProduction，说明 Epic 对该插件有明确的发展规划
- **有已知问题**：近期有 Backout 提交，表明该模块仍在快速迭代中
- **推荐使用**：如果你在做虚拟制作 / Motion Design 项目，这是 Epic 官方推荐的状态管理方案。但需注意 Beta 状态，建议关注 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无（插件尚未发布公开文档）
- 测试用例：待确认（424 个源文件中可能包含测试，需进一步分析）