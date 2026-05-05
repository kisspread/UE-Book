# Motion Design Scene State

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、状态机模板） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是一套面向 **虚拟制作（Virtual Production）和 Motion Design** 的**可视化状态机运行时框架**。它解决的核心问题是：在实时场景中，如何以数据驱动、可蓝图编辑的方式管理复杂的状态逻辑、状态转换和任务编排。

与 UE 内置的 Gameplay Ability System（GAS）或行为树不同，Scene State 专注于**场景级别的状态管理**——它不关心角色战斗数值，而是关心"当前场景处于什么状态、该播放什么动画/特效/灯光序列、何时切换到下一个状态"这类问题。

核心架构采用 **模板-实例分离** 设计：
- **模板数据（USceneStateTemplateData）**：编译时生成，包含所有状态、状态机、任务、转换的不可变定义
- **执行上下文（FSceneStateExecutionContext）**：运行时实例数据，包含任务实例、状态实例等可变数据
- **生成类（USceneStateGeneratedClass）**：蓝图编译产物，持有模板数据

这种设计使得同一份状态定义可以被多个实例共享，同时每个实例拥有独立的运行时状态。

## 使用场景

- 你在做虚拟制作的灯光/特效序列编排 → 用 Scene State 定义场景状态和转换条件
- 你需要在 Motion Design 项目中管理复杂的场景切换逻辑 → 用 Scene State 的状态机
- 你想让设计师通过蓝图可视化编辑状态转换 → 用 Scene State 的蓝图任务和状态机图
- 你需要事件驱动的场景状态切换 → 用 Scene State 的事件系统和转换评估
- 你想在运行时动态运行嵌套状态机 → 用 `FSceneStateMachineTask`

## 蓝图用法

### 核心节点

#### Scene State Object（USceneStateObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetContextObject` | 获取场景状态的上下文对象 | `USceneStateObject` |
| `GetEventStream` | 获取事件流，用于添加/查询事件 | `USceneStateObject` |
| `IsActive` | 判断根状态是否处于活跃状态 | `USceneStateObject` |
| `ReceiveEnter` | 蓝图可实现事件：状态进入时调用 | `USceneStateObject` |
| `ReceiveTick` | 蓝图可实现事件：每帧调用 | `USceneStateObject` |
| `ReceiveExit` | 蓝图可实现事件：状态退出时调用 | `USceneStateObject` |

#### Blueprintable Task（USceneStateBlueprintableTask）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReceiveStart` | 蓝图可实现事件：任务开始时调用 | `USceneStateBlueprintableTask` |
| `ReceiveTick` | 蓝图可实现事件：任务每帧调用（需设置 Ticks 标志） | `USceneStateBlueprintableTask` |
| `ReceiveStop` | 蓝图可实现事件：任务结束时调用 | `USceneStateBlueprintableTask` |
| `FinishTask` | 标记任务完成，触发状态转换评估 | `USceneStateBlueprintableTask` |
| `GetRootState` | 获取拥有此任务的根 Scene State Object | `USceneStateBlueprintableTask` |
| `GetContextObject` | 获取上下文对象 | `USceneStateBlueprintableTask` |
| `GetEventStream` | 获取事件流 | `USceneStateBlueprintableTask` |

### 使用示例（蓝图描述）

**创建自定义蓝图任务：**

1. 在内容浏览器中右键 → Blueprint Class → 选择 `USceneStateBlueprintableTask` 作为父类
2. 在蓝图编辑器中实现 `ReceiveStart`、`ReceiveTick`、`ReceiveStop` 事件
3. 在 `ReceiveStop` 或任意时刻调用 `FinishTask` 节点来标记任务完成
4. 在状态机图中将此蓝图任务添加到某个状态的节点上

**使用 Scene State Player：**

1. 创建一个 `USceneStatePlayer` 子类或在 Actor 中持有该对象
2. 设置 `SceneStateClass` 属性指向你的 Scene State Object 蓝图类
3. 在 Actor 的 `BeginPlay` 中调用 `Setup()` → `Begin()`
4. 在 Actor 的 `Tick` 中调用 `Tick(DeltaTime)`
5. 在 Actor 的 `EndPlay` 中调用 `End()`

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateObject.h"
#include "SceneStatePlayer.h"
#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "SceneStateExecutionContext.h"
```

### 基本用法：定义自定义 C++ 任务

C++ 任务遵循**逻辑与实例数据分离**的设计模式。任务结构体（`FSceneStateTask`）持有不可变逻辑，任务实例结构体（`FSceneStateTaskInstance`）持有可变运行时数据。

```cpp
// MyCustomTask.h
#pragma once

#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "MyCustomTask.generated.h"

// 实例数据：运行时可变
USTRUCT()
struct FMyCustomTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    // 自定义运行时数据
    float Timer = 0.f;
    bool bConditionMet = false;
};

// 任务逻辑：运行时不可变
USTRUCT(DisplayName="My Custom Task", Category="Custom")
struct FMyCustomTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstance;

    FMyCustomTask();

protected:
    //~ Begin FSceneStateTask
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override;
    virtual void OnBuildTaskInstance(UObject* InOuter, FStructView InTaskInstance) const override;
#endif
    virtual void OnSetup(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override;
    virtual void OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const override;
    //~ End FSceneStateTask

    // 可选：配置属性（编译时不可变）
    UPROPERTY(EditAnywhere, Category="Settings")
    float Duration = 5.f;
};
```

```cpp
// MyCustomTask.cpp
#include "MyCustomTask.h"

FMyCustomTask::FMyCustomTask()
{
    // 设置任务标志：允许 Tick
    TaskFlags = ESceneStateTaskFlags::Ticks;
}

#if WITH_EDITOR
const UScriptStruct* FMyCustomTask::OnGetTaskInstanceType() const
{
    return FMyCustomTaskInstance::StaticStruct();
}

void FMyCustomTask::OnBuildTaskInstance(UObject* InOuter, FStructView InTaskInstance) const
{
    // 初始化实例数据中的对象等
}
#endif

void FMyCustomTask::OnSetup(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    // 状态进入时调用，所有任务都会收到此调用（即使最终不运行）
}

void FMyCustomTask::OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    // 任务开始运行
    FMyCustomTaskInstance& Instance = InTaskInstance.Get<FMyCustomTaskInstance>();
    Instance.Timer = 0.f;
}

void FMyCustomTask::OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const
{
    FMyCustomTaskInstance& Instance = InTaskInstance.Get<FMyCustomTaskInstance>();
    Instance.Timer += InDeltaSeconds;

    if (Instance.Timer >= Duration)
    {
        // 标记任务完成
        Finish(InContext, InTaskInstance);
    }
}

void FMyCustomTask::OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const
{
    // 清理逻辑
}
```

### 进阶用法：使用 TaskExecutionContext 安全访问任务

`FTaskExecutionContext` 是一个可安全拷贝的辅助结构，适用于 lambda 捕获和延迟回调场景。它通过 InstanceId 机制确保即使原始任务实例已被销毁或替换，也不会访问到无效数据。

```cpp
// 来源: SceneStateTaskExecutionContext.h
void FMyCustomTask::OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    // 创建安全的执行上下文，可被捕获到 lambda 中
    UE::SceneState::FTaskExecutionContext TaskContext(*this, InContext);

    // 模拟异步操作
    AsyncTask(ENamedThreads::GameThread, [TaskContext]()
    {
        // 安全检查：如果任务实例仍然有效
        FStructView TaskInstance = TaskContext.GetTaskInstance();
        if (TaskInstance.IsValid())
        {
            // 安全地完成任务
            TaskContext.FinishTask();
        }
    });
}
```

### 进阶用法：属性解析

使用 `UE::SceneState::ResolveProperty` 在执行上下文中解析属性绑定引用：

```cpp
// 来源: SceneStatePropertyUtils.h
#include "SceneStatePropertyUtils.h"

void ResolveBoundProperty(const FSceneStateExecutionContext& InContext, 
                          const FSceneStatePropertyReference& InPropertyRef)
{
    // 方式一：获取原始指针
    UE::SceneState::FResolvePropertyResult Result;
    if (UE::SceneState::ResolveProperty(InContext, InPropertyRef, Result))
    {
        // Result.ValuePtr 指向解析后的属性值
        // Result.ResolvedReference 包含解析后的绑定引用信息
    }

    // 方式二：模板版本，直接获取类型化指针
    float* FloatValue = UE::SceneState::ResolveProperty<float>(InContext, InPropertyRef);
    if (FloatValue)
    {
        float CurrentValue = *FloatValue;
    }
}
```

## Demo 示例

以下是一个最小可编译的自定义任务示例，实现一个简单的延时等待任务：

```cpp
// WaitTask.h
#pragma once

#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "SceneStateExecutionContext.h"
#include "WaitTask.generated.h"

USTRUCT()
struct FWaitTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    float ElapsedTime = 0.f;
};

USTRUCT(DisplayName="Wait", Category="Utility")
struct FWaitTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FWaitTaskInstance;

    FWaitTask()
    {
        TaskFlags = ESceneStateTaskFlags::Ticks;
    }

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FWaitTaskInstance::StaticStruct();
    }

    virtual void OnBuildTaskInstance(UObject* InOuter, FStructView InTaskInstance) const override
    {
    }
#endif

    virtual void OnSetup(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
    }

    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
        InTaskInstance.Get<FWaitTaskInstance>().ElapsedTime = 0.f;
    }

    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override
    {
        FWaitTaskInstance& Instance = InTaskInstance.Get<FWaitTaskInstance>();
        Instance.ElapsedTime += InDeltaSeconds;
        if (Instance.ElapsedTime >= WaitDuration)
        {
            Finish(InContext, InTaskInstance);
        }
    }

    virtual void OnStop(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, ESceneStateTaskStopReason InStopReason) const override
    {
    }

    UPROPERTY(EditAnywhere, Category="Settings")
    float WaitDuration = 3.f;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | PropertyBag、InstancedStructContainer 等结构化数据工具 |
| `PropertyBinding` | 属性绑定系统，用于状态机中的数据绑定和解析 |

## 维护状态

### 近期更新

```
- 73214c120f99 Motion Design Scene State: changed error log to warning.
- 6cbfc95aef06 Default initialize raw ptr to null + fixed outdated comment
- 26c5be73ff3d Motion Design Scene State: fixed issue where uobjects instanced to the generated class and saved in the shared struct were getting marked as unreachable and garbage collected. This was done by changing the template data from being a struct (was being used as a shared struct) to a uobject. This uobject approach has the benefit that task uobjects can now be outered to the template data uobject directly rather than the owning class.
```

### 维护评价

- **创建时间**：2025-04-22，非常新的插件（约 3 个月）
- **更新频率**：近期有实质性架构改进（将模板数据从 Struct 改为 UObject 以修复 GC 问题），说明处于**活跃开发阶段**
- **实验性标记**：`IsBetaVersion=true`，`Category=Experimental`，`EnabledByDefault=false`——这是一个实验性插件，API 可能发生破坏性变更
- **规模**：701 个源文件、14 个模块，架构复杂且完整
- **已知风险**：作为实验性 Beta 插件，不建议在生产环境中依赖；API 稳定性无保障
- **推荐**：适合在虚拟制作/Motion Design 项目中**探索性使用**，关注后续版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)