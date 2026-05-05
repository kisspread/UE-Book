# Motion Design Scene State

> Motion Design Scene State

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态机资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是一套面向 **虚拟制片（Virtual Production）/ Motion Design** 的**场景状态机系统**。它解决的核心问题是：在实时 Motion Design 工作流中，如何以数据驱动的方式管理场景对象的属性变化和状态切换。

该插件提供了一套完整的状态机框架，包含：

- **状态机引擎**（`SceneState`）：管理状态的创建、切换和执行上下文
- **属性绑定系统**（`SceneStateBinding`）：将状态机任务与场景对象的属性关联起来
- **任务系统**（`SceneStateTasks`）：内置的属性设置器（Setter）、延时、打印、生成 Actor 等任务
- **函数系统**（`SceneStateTasks`）：内置的数学运算、布尔逻辑、字符串转换等数据处理函数
- **事件系统**（`SceneStateEvent`）：外部事件触发状态转换
- **游戏逻辑集成**（`SceneStateGameplay`）：与 Gameplay 框架的集成
- **可视化编辑器**（`SceneStateMachineGraph`、`SceneStateEventGraph`、`SceneStateTransitionGraph`）：基于节点图的状态机编辑界面

与蓝图不同，Scene State 采用 **USTRUCT 数据驱动**架构——任务和函数都是纯数据结构体，通过 `FSceneStateExecutionContext` 执行上下文运行，没有 UObject 的开销，适合高频、大量实例的 Motion Design 场景。

## 使用场景

- 你在做 **LED 墙虚拟制片**，需要根据拍摄进度自动切换场景内容和灯光配置 → 用 Scene State 管理场景状态
- 你在做 **Motion Design 实时图形**，需要多个场景元素按时间线或条件联动变化 → 用 Scene State 的任务和属性绑定
- 你需要 **非程序员也能配置场景行为**，通过可视化状态机编辑器定义状态和转换 → 用 SceneStateMachineGraph 编辑器
- 你需要 **事件驱动的场景响应**，比如接收到外部信号时切换场景状态 → 用 SceneStateEvent 系统
- 你需要 **在状态切换时执行具体操作**，如设置属性值、生成/销毁 Actor、延时等待 → 用 SceneStateTasks 内置任务

## 蓝图用法

Scene State 的任务和函数以 **USTRUCT** 形式定义，在状态机图编辑器中以节点形式使用。每个任务/函数通过 `DisplayName` 和 `Category` 元数据在编辑器面板中分类展示。

### 核心任务节点

#### Setter 任务（属性设置器）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Boolean` | 设置目标布尔属性值 | `FSceneStateSetBoolTask` |
| `Set Float` | 设置目标浮点属性值（支持 double/float） | `FSceneStateSetFloatTask` |
| `Set Integer` | 设置目标整数属性值 | `FSceneStateSetIntegerTask` |
| `Set String` | 设置目标字符串属性值 | `FSceneStateSetStringTask` |
| `Set Text` | 设置目标 FText 属性值 | `FSceneStateSetTextTask` |

#### Core 任务

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Delay` | 等待指定秒数后继续 | `FSceneStateDelayTask` |
| `Print String` | 打印消息到屏幕和/或日志 | `FSceneStatePrintStringTask` |
| `Spawn Actor` | 根据模板生成一个 Actor | `FSceneStateSpawnActorTask` |

### 核心函数节点

#### 数学函数（整数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add` | 整数加法 (Left + Right) | `FSceneStateAddIntegerFunction` |
| `Subtract` | 整数减法 (Left - Right) | `FSceneStateSubtractIntegerFunction` |
| `Multiply` | 整数乘法 (Left * Right) | `FSceneStateMultiplyIntegerFunction` |
| `Divide` | 整数除法 (Left / Right) | `FSceneStateDivideIntegerFunction` |

#### 数学函数（浮点）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add` | 浮点加法 (Left + Right) | `FSceneStateAddDoubleFunction` |
| `Subtract` | 浮点减法 (Left - Right) | `FSceneStateSubtractDoubleFunction` |
| `Multiply` | 浮点乘法 (Left * Right) | `FSceneStateMultiplyDoubleFunction` |
| `Divide` | 浮点除法 (Left / Right) | `FSceneStateDivideDoubleFunction` |

#### 布尔函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `And` | 布尔与 (Left AND Right) | `FSceneStateBooleanAndFunction` |
| `Or` | 布尔或 (Left OR Right) | `FSceneStateBooleanOrFunction` |
| `XOr` | 布尔异或 (Left XOR Right) | `FSceneStateBooleanXorFunction` |
| `Not` | 布尔非 (NOT Input) | `FSceneStateBooleanNotFunction` |

#### 字符串函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Concatenate String` | 拼接两个字符串 (Left + Right) | `FSceneStateConcatenateStringFunction` |
| `Text to String` | FText 转 FString | `FSceneStateTextToStringFunction` |
| `Name to String` | FName 转 FString | `FSceneStateNameToStringFunction` |
| `Integer to String` | int32 转 FString | `FSceneStateIntegerToStringFunction` |
| `String to Text` | FString 转 FText | `FSceneStateTextFromStringFunction` |
| `String to Name` | FString 转 FName | `FSceneStateNameFromStringFunction` |

### 使用示例（编辑器操作描述）

**场景：当进入某个状态时，将场景中一个灯光的强度设置为 1.5，并等待 2 秒后打印一条消息。**

1. 在状态机图编辑器中创建一个新状态
2. 向该状态添加 **Set Float** 任务：
   - `Target`：通过属性绑定选择目标灯光组件的 `Intensity` 属性
   - `Value`：设置为 `1.5`
3. 添加 **Delay** 任务：
   - `Delay`：设置为 `2.0` 秒
4. 添加 **Print String** 任务：
   - `Message`：输入 `"灯光已调整"`
   - `PrintSettings.bPrintToScreen`：勾选
5. 连接状态转换条件，定义何时进入/离开该状态

所有任务按顺序执行：先设置属性 → 等待 2 秒 → 打印消息。

## C++ 用法

### 头文件引入

```cpp
// 核心任务基类
#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"

// 函数基类
#include "Functions/SceneStateFunction.h"

// 属性绑定
#include "SceneStatePropertyReference.h"

// 执行上下文
#include "SceneStateExecutionContext.h"

// Setter 工具
#include "SceneStateSetterUtils.h"
```

### 基本用法：创建自定义 Setter 任务

所有 Setter 任务遵循相同的模式：一个 Instance 结构体持有 `Target`（属性引用）和 `Value`（要设置的值），任务在 `OnStart` 中调用 `SetValue` 完成属性写入。

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTasks/Public/Setters/SceneStateSetFloatTask.h

// 1. 定义任务实例数据
USTRUCT()
struct FSceneStateSetFloatTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 目标浮点属性 */
    UPROPERTY(EditAnywhere, Category="Setter", meta=(RefType="double,float"))
    FSceneStatePropertyReference Target;

    /** 要设置的浮点值 */
    UPROPERTY(EditAnywhere, Category="Setter")
    double Value = 0.0;
};

// 2. 定义任务
USTRUCT(DisplayName="Set Float", Category="Setter")
struct FSceneStateSetFloatTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FSceneStateSetFloatTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override;
#endif
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
};
```

### 基本用法：创建自定义函数

函数系统使用 `FSceneStateFunction` 基类，通过 `OnExecute` 执行计算逻辑：

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTasks/Public/Functions/SceneStateStringFunctions.h

// 1. 定义函数实例数据（输入 + 输出）
USTRUCT()
struct FSceneStateConcatenateStringFunctionInstance
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="String")
    FString Left;

    UPROPERTY(EditAnywhere, Category="String")
    FString Right;

    UPROPERTY(EditAnywhere, Category="String", meta=(Output))
    FString Output;
};

// 2. 定义函数
USTRUCT(DisplayName="Concatenate String", Category="String")
struct FSceneStateConcatenateStringFunction : public FSceneStateFunction
{
    GENERATED_BODY()

    using FInstanceDataType = FSceneStateConcatenateStringFunctionInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetFunctionDataType() const override;
#endif
    virtual void OnExecute(const FSceneStateExecutionContext& InContext, FStructView InFunctionInstance) const override;
};
```

### 进阶用法：Spawn Actor 任务

`FSceneStateSpawnActorTask` 展示了更复杂的任务模式——支持 Actor 模板、生成变换、碰撞处理，以及将生成的 Actor 通过属性引用输出：

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTasks/Public/SceneStateSpawnActorTask.h

USTRUCT()
struct FSceneStateSpawnActorTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** Actor 模板 */
    UPROPERTY(EditAnywhere, Category="Scene State", meta=(NoBindingSelfOnly))
    FSceneStateActorTemplate ActorTemplate;

    /** 生成变换 */
    UPROPERTY(EditAnywhere, Category="Scene State")
    FTransform SpawnTransform = FTransform::Identity;

    /** 碰撞处理方式 */
    UPROPERTY(EditAnywhere, Category="Scene State")
    ESpawnActorCollisionHandlingMethod SpawnCollisionHandling = ESpawnActorCollisionHandlingMethod::Undefined;

    /** 可选：将生成的 Actor 写入此属性引用 */
    UPROPERTY(EditAnywhere, Category="Scene State", meta=(RefType="/Script/Engine.Actor"))
    FSceneStatePropertyReference SpawnedActor;
};
```

Spawn Actor 任务还提供了虚函数扩展点：
- `ShouldSpawnActor()` — 控制是否应该生成 Actor
- `OnActorSpawned()` — Actor 生成后的额外处理

### 进阶用法：Setter 工具模板

`SceneStateSetterUtils.h` 提供了通用的属性设置工具，使用 C++20 Concepts 约束类型安全：

```cpp
// 来源: Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateTasks/Public/Setters/SceneStateSetterUtils.h

namespace UE::SceneState
{
    // Setter 任务实例必须有 Value 和 Target 成员
    template<typename InTaskInstanceType>
    concept CSetterTaskInstanceTypeable = requires(const InTaskInstanceType& InTaskInstance)
    {
        InTaskInstance.Value;
        { InTaskInstance.Target }->UE::CDecaysTo<FSceneStatePropertyReference>;
    };

    // 通用设置值函数，自动处理属性绑定解析和 Setter 调用
    template<typename... InTargetTypes, CSetterTaskTypeable InTaskType>
    bool SetValue(const InTaskType& InTask, const FSceneStateExecutionContext& InContext, FStructView InTaskInstance);
}
```

## Demo 示例

以下是一个完整的自定义任务示例——一个"设置颜色"任务，将颜色值写入绑定的属性：

### MySetColorTask.h

```cpp
#pragma once

#include "SceneStatePropertyReference.h"
#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "MySetColorTask.generated.h"

USTRUCT()
struct FMySetColorTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 目标颜色属性 */
    UPROPERTY(EditAnywhere, Category="Setter", meta=(RefType="LinearColor,FColor"))
    FSceneStatePropertyReference Target;

    /** 要设置的颜色值 */
    UPROPERTY(EditAnywhere, Category="Setter")
    FLinearColor Value = FLinearColor::White;
};

/** 将颜色值设置到绑定的属性引用 */
USTRUCT(DisplayName="Set Color", Category="Setter")
struct FMySetColorTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMySetColorTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override;
#endif
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override;
};
```

### MySetColorTask.cpp

```cpp
#include "MySetColorTask.h"
#include "SceneStateSetterUtils.h"

#if WITH_EDITOR
const UScriptStruct* FMySetColorTask::OnGetTaskInstanceType() const
{
    return FInstanceDataType::StaticStruct();
}
#endif

void FMySetColorTask::OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const
{
    // 使用通用 SetValue 模板，自动解析属性绑定并写入值
    // 支持 FLinearColor 和 FColor 两种目标类型
    UE::SceneState::SetValue<FLinearColor, FColor>(*this, InContext, InTaskInstance);
}
```

## 模块依赖

从源码头文件的 `#include` 分析，`SceneStateTasks` 模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心框架：`FSceneStateTask`、`FSceneStateFunction`、`FSceneStateExecutionContext` 基类 |
| `SceneStateBinding` | 属性绑定：`FSceneStatePropertyReference`、属性解析 |
| `PropertyBinding` | UE 内置属性绑定数据视图：`FPropertyBindingDataView` |

若要使用此插件，你的模块需要在 Build.cs 中添加对 `SceneStateTasks`（或直接对 `SceneState`）的依赖。

## 维护状态

### 近期更新

```
- d53130edebd0 Motion Design Scene State: added actor reference for the spawned actor to be useable outside its task
- 7512ce3b9f23 Motion Design: small fixes to function categories + added boolean and concatenate string functions
- 2b15ef0ee0c0 Motion Design: updated comments for clarity on double-precision floats
```

### 维护评价

- **创建时间**：2025-04-22，非常新的插件（约 6 个月）
- **开发状态**：Beta 版本（`IsBetaVersion=true`），仍在积极开发中
- **近期活动**：最近的提交显示功能持续完善——添加了 Spawn Actor 的外部引用能力、新增布尔和字符串函数、改进注释质量
- **模块规模**：14 个模块、701 个源文件，架构完整且模块化良好
- **已知限制**：Beta 版本，API 可能发生变化；Description 为空说明文档尚不完善
- **推荐程度**：⚠️ **仅推荐用于实验性项目**。作为 Virtual Production / Motion Design 工作流的状态机系统，架构设计合理，但处于 Beta 阶段，不建议用于生产环境。适合提前了解和试用 Epic 在 Motion Design 领域的方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无（.uplugin 中 DocsURL 为空）