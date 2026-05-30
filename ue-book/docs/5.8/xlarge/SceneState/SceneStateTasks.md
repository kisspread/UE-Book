# Motion Design Scene State

> （Description 为空，基于源码分析）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是面向虚拟制片（Motion Design）的**场景状态机系统**。它提供了一套基于可视化图表的状态机框架，让美术和设计师能够通过拖拽节点来定义场景中的行为逻辑，而无需编写代码。

核心设计思想：

- **状态机（State Machine）**：通过图编辑器定义场景中各个状态及其转换关系
- **任务（Task）**：状态内的执行单元，如延时、打印、生成 Actor、设置属性值等
- **函数（Function）**：纯计算节点，支持数学运算、字符串处理、布尔逻辑等
- **事件（Event）**：驱动状态转换的触发机制
- **绑定（Binding）**：将状态机数据与场景对象属性连接，实现数据流驱动
- **数据链接（Data Link）**：跨模块的数据通信机制

该插件从 Experimental 目录迁移至 VirtualProduction，表明 Epic 正在将其推向正式产品化。`SceneStateTasks` 模块是内置的任务和函数库，提供了开箱即用的常用操作节点。

## 使用场景

- 你在做虚拟制片/Motion Graphics 项目，需要控制场景元素的动态行为 → 用 Scene State 状态机
- 你需要在不写代码的情况下定义复杂的场景逻辑（如"播放动画 → 等待 2 秒 → 生成粒子效果 → 设置材质参数"）→ 用 Scene State 图表
- 你需要事件驱动的场景行为（如"当用户点击按钮时切换场景状态"）→ 用 Scene State 事件系统
- 你需要将状态机数据绑定到 Actor 属性上，实现数据驱动的动画效果 → 用 Scene State 绑定系统

## 蓝图用法

> **重要说明**：Scene State 系统中的节点（Task/Function）不是传统的 `BlueprintCallable` 函数。它们是 `USTRUCT` 数据类型，通过 Scene State 图编辑器以可视化节点的形式使用。`DisplayName` 和 `Category` 元数据决定了节点在编辑器中的显示名称和分类。

### 内置任务节点

| 节点 | 分类 | 说明 | 所在类 |
|---|---|---|---|
| `Delay` | Utility | 等待指定秒数后继续执行 | `FSceneStateDelayTask` |
| `Print String` | Utility | 将消息打印到屏幕和/或日志 | `FSceneStatePrintStringTask` |
| `Spawn Actor` | Utility | 根据模板生成一个 Actor 实例 | `FSceneStateSpawnActorTask` |
| `Set Boolean` | Setter | 设置绑定目标的布尔属性值 | `FSceneStateSetBoolTask` |
| `Set Float` | Setter | 设置绑定目标的浮点属性值 | `FSceneStateSetFloatTask` |
| `Set Integer` | Setter | 设置绑定目标的整数属性值 | `FSceneStateSetIntegerTask` |
| `Set String` | Setter | 设置绑定目标的字符串属性值 | `FSceneStateSetStringTask` |
| `Set Text` | Setter | 设置绑定目标的文本属性值 | `FSceneStateSetTextTask` |

### 内置函数节点

**布尔运算（Math）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `And` | 布尔与运算 (Left AND Right) | `FSceneStateBooleanAndFunction` |
| `Or` | 布尔或运算 (Left OR Right) | `FSceneStateBooleanOrFunction` |
| `XOr` | 布尔异或运算 (Left XOR Right) | `FSceneStateBooleanXorFunction` |
| `Not` | 布尔非运算 | `FSceneStateBooleanNotFunction` |

**整数运算（Math）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add` | 整数加法 (Left + Right) | `FSceneStateAddIntegerFunction` |
| `Subtract` | 整数减法 (Left - Right) | `FSceneStateSubtractIntegerFunction` |
| `Multiply` | 整数乘法 (Left × Right) | `FSceneStateMultiplyIntegerFunction` |
| `Divide` | 整数除法 (Left ÷ Right) | `FSceneStateDivideIntegerFunction` |

**浮点运算（Math）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add` | 浮点加法 (Left + Right) | `FSceneStateAddDoubleFunction` |
| `Subtract` | 浮点减法 (Left - Right) | `FSceneStateSubtractDoubleFunction` |
| `Multiply` | 浮点乘法 (Left × Right) | `FSceneStateMultiplyDoubleFunction` |
| `Divide` | 浮点除法 (Left ÷ Right) | `FSceneStateDivideDoubleFunction` |

**字符串操作（String）**：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Concatenate String` | 连接两个字符串 | `FSceneStateConcatenateStringFunction` |
| `Text to String` | FText 转 FString | `FSceneStateTextToStringFunction` |
| `Name to String` | FName 转 FString | `FSceneStateNameToStringFunction` |
| `Integer to String` | int32 转 FString | `FSceneStateIntegerToStringFunction` |
| `Float to String` | double 转 FString | `FSceneStateDoubleToStringFunction` |
| `String to Text` | FString 转 FText | `FSceneStateTextFromStringFunction` |
| `String to Name` | FString 转 FName | `FSceneStateNameFromStringFunction` |

### 使用示例（图表描述）

在 Scene State 图编辑器中构建一个典型的状态机流程：

1. **创建状态机**：在资产编辑器中新建 Scene State 资产，添加状态节点
2. **添加任务**：在某个状态中，添加 `Delay` 节点设置等待 2 秒
3. **设置转换条件**：添加一个事件触发器连接到下一个状态
4. **在目标状态中**：添加 `Spawn Actor` 节点，配置 Actor 类和生成位置
5. **绑定属性**：使用 `Set Float` 节点，通过 `FSceneStatePropertyReference` 绑定到目标 Actor 的某个浮点属性
6. **添加计算**：使用 `Add` (Float) 函数节点计算新值，连接到 `Set Float` 的 Value 输入

## C++ 用法

### 头文件引入

```cpp
// 核心任务基类
#include "Tasks/SceneStateTask.h"

// 内置任务
#include "SceneStateTasks/Public/SceneStateDelayTask.h"
#include "SceneStateTasks/Public/SceneStatePrintStringTask.h"
#include "SceneStateTasks/Public/SceneStateSpawnActorTask.h"

// Setter 任务
#include "SceneStateTasks/Public/Setters/SceneStateSetFloatTask.h"
#include "SceneStateTasks/Public/Setters/SceneStateSetterUtils.h"

// 内置函数
#include "SceneStateTasks/Public/Functions/SceneStateBooleanFunctions.h"
#include "SceneStateTasks/Public/Functions/SceneStateFloatFunctions.h"
```

### 基本用法：创建自定义 Task

以下示例展示如何继承 `FSceneStateTask` 创建自定义任务。模式基于 SceneStateTasks 模块中所有内置任务的通用结构。

```cpp
// 来源: 基于 SceneStateDelayTask.h / SceneStatePrintStringTask.h 的模式

// 1. 定义任务实例数据（存储任务运行时的配置和状态）
USTRUCT()
struct FMyCustomTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 用户可编辑的参数 */
    UPROPERTY(EditAnywhere, Category="Custom")
    float Duration = 1.0f;

    /** 运行时状态（不需要编辑） */
    float ElapsedTime = 0.f;
};

// 2. 定义任务本身
USTRUCT(DisplayName="My Custom Task", Category="Custom", meta=(UtilityTask))
struct FMyCustomTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMyCustomTaskInstance;

protected:
    //~ Begin FSceneStateTask
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
#endif
    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
        FMyCustomTaskInstance& Instance = InTaskInstance.Get<FMyCustomTaskInstance>();
        Instance.ElapsedTime = 0.f;
        // 任务开始时的初始化逻辑
    }

    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override
    {
        FMyCustomTaskInstance& Instance = InTaskInstance.Get<FMyCustomTaskInstance>();
        Instance.ElapsedTime += InDeltaSeconds;
        // 持续执行的逻辑
    }
    //~ End FSceneStateTask
};
```

### 基本用法：创建自定义 Function

以下示例展示如何继承 `FSceneStateFunction` 创建自定义计算函数。模式基于内置的数学函数和字符串函数。

```cpp
// 来源: 基于 SceneStateFloatFunctions.h / SceneStateBooleanFunctions.h 的模式

// 1. 定义函数实例数据
USTRUCT()
struct FMyClampFloatFunctionInstance
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="Math")
    double Value = 0.0;

    UPROPERTY(EditAnywhere, Category="Math")
    double Min = 0.0;

    UPROPERTY(EditAnywhere, Category="Math")
    double Max = 1.0;

    UPROPERTY(EditAnywhere, Category="Math", meta=(Output))
    double Output = 0.0;
};

// 2. 定义函数
USTRUCT(DisplayName="Clamp Float", Category="Math")
struct FMyClampFloatFunction : public FSceneStateFunction
{
    GENERATED_BODY()

    using FInstanceDataType = FMyClampFloatFunctionInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetFunctionDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
#endif

    virtual void OnExecute(const FSceneStateExecutionContext& InContext, FStructView InFunctionInstance) const override
    {
        FMyClampFloatFunctionInstance& Instance = InFunctionInstance.Get<FMyClampFloatFunctionInstance>();
        Instance.Output = FMath::Clamp(Instance.Value, Instance.Min, Instance.Max);
    }
};
```

### 进阶用法：创建带属性绑定的 Setter Task

Setter Task 使用 `FSceneStatePropertyReference` 将值写入绑定的目标属性。核心工具函数在 `SceneStateSetterUtils.h` 中。

```cpp
// 来源: 基于 SceneStateSetFloatTask.h + SceneStateSetterUtils.h 的模式

// Setter Task 必须满足 CSetterTaskTypeable 概念：
// - Instance 类型必须有 Value 成员
// - Instance 类型必须有 Target (FSceneStatePropertyReference) 成员

USTRUCT()
struct FMySetVectorTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 目标向量属性的绑定引用 */
    UPROPERTY(EditAnywhere, Category="Setter", meta=(RefType="Vector"))
    FSceneStatePropertyReference Target;

    /** 要设置的向量值 */
    UPROPERTY(EditAnywhere, Category="Setter")
    FVector Value = FVector::ZeroVector;
};

USTRUCT(DisplayName="Set Vector", Category="Setter", meta=(CoreTask))
struct FMySetVectorTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FMySetVectorTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
#endif

    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
        // 使用 Setter 工具函数将值写入绑定的属性
        // SetValue 会自动尝试调用属性的 Setter（如果存在），否则直接写入内存
        UE::SceneState::SetValue<FVector>(*this, InContext, InTaskInstance);
    }
    //~ End FSceneStateTask
};
```

**Setter 工作原理**：`UE::SceneState::SetValue` 内部流程：
1. 通过 `ResolveProperty` 解析 `FSceneStatePropertyReference` 获取目标属性指针
2. 尝试调用 `FProperty::CallSetter`（如果目标属性定义了 Setter）
3. 如果没有 Setter，直接通过指针写入属性内存

## Demo 示例

一个完整的自定义任务，实现"倒计时后触发回调"功能：

```cpp
// CountdownTask.h
#pragma once

#include "Tasks/SceneStateTask.h"
#include "Tasks/SceneStateTaskInstance.h"
#include "CountdownTask.generated.h"

USTRUCT()
struct FCountdownTaskInstance : public FSceneStateTaskInstance
{
    GENERATED_BODY()

    /** 倒计时时长（秒） */
    UPROPERTY(EditAnywhere, Category="Countdown", meta=(ClampMin="0"))
    float CountdownDuration = 3.0f;

    /** 当前剩余时间（运行时状态） */
    float RemainingTime = 0.f;
};

USTRUCT(DisplayName="Countdown", Category="Utility", meta=(UtilityTask))
struct FCountdownTask : public FSceneStateTask
{
    GENERATED_BODY()

    using FInstanceDataType = FCountdownTaskInstance;

protected:
#if WITH_EDITOR
    virtual const UScriptStruct* OnGetTaskInstanceType() const override
    {
        return FInstanceDataType::StaticStruct();
    }
#endif

    virtual void OnStart(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance) const override
    {
        FCountdownTaskInstance& Instance = InTaskInstance.Get<FCountdownTaskInstance>();
        Instance.RemainingTime = Instance.CountdownDuration;
    }

    virtual void OnTick(const FSceneStateExecutionContext& InContext, FStructView InTaskInstance, float InDeltaSeconds) const override
    {
        FCountdownTaskInstance& Instance = InTaskInstance.Get<FCountdownTaskInstance>();
        Instance.RemainingTime -= InDeltaSeconds;

        if (Instance.RemainingTime <= 0.f)
        {
            // 倒计时结束，完成任务（触发状态转换）
            FinishTask(InContext, InTaskInstance);
        }
    }
};
```

```cpp
// CountdownTask.cpp
#include "CountdownTask.h"

// 此模块为纯 USTRUCT 定义，大部分实现在头文件中内联完成。
// 如需额外的 .cpp 逻辑（如资源加载），可在此文件中实现。
```

## 模块依赖

以下为 SceneStateTasks 模块的依赖关系（其他模块的依赖类似）：

| 模块 | 用途 |
|---|---|
| `SceneState` | 核心框架：FSceneStateTask、FSceneStateFunction、FSceneStateExecutionContext 基类 |
| `SceneStateBinding` | 属性绑定系统：FSceneStatePropertyReference、属性解析和绑定解析 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：优化客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退变更 CL53913857 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：客户端关联通知机制（首次提交后被回退再重提） |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复绑定系统未检查空事件载荷结构体导致的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志调用迁移到 UE_LOGF 格式 |

### 维护评价

- **状态**：🟢 **活跃开发中**
- **创建时间**：2025-08-27，不到 1 年的新插件
- **最近更新**：2026-05-14（距今约 8 天），更新非常频繁
- **开发进展**：从 Experimental 目录迁移至 VirtualProduction，表明已进入产品化阶段
- **已知限制**：`IsBetaVersion=true`，API 可能在后续版本中发生变化
- **推荐程度**：**谨慎使用**。该插件处于活跃开发中，功能不断完善，但作为 Beta 版本，接口可能随 UE 版本迭代而变动。适合在 Motion Design/虚拟制片项目中进行原型开发和测试，不建议在需要长期稳定的生产环境中深度依赖。密切关注 Epic 的更新日志和迁移指南。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档（暂无）
- 测试用例（暂未发现公开的自动化测试文件）