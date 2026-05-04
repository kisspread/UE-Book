# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、内容资源） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (UncookedOnly), `RigVMEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 UE5 的**可视化编程虚拟机**，专为动画和骨骼控制（Control Rig）系统设计。它提供了一套完整的前端（图表编辑器）和后端（字节码编译器 + 运行时 VM），用于在运行时高效执行基于节点图的程序逻辑。

与蓝图不同，RigVM 专注于**数据驱动的求值循环**——它将节点图编译为紧凑的字节码指令，在预分配的内存寄存器上执行，性能远高于蓝图的反射式调用。核心特性包括：

- **模板化分发系统（Dispatch）**：支持泛型节点（如 If、Select、Print），能根据连接的类型自动推导具体实现
- **控制流**：支持 Branch、For Loop、Sequence 等执行流控制
- **内存管理**：分离的 Literal / Work / Debug 内存区域，支持 CDO 和实例级内存
- **丰富的内置函数库**：数学、动画曲线、物理模拟（Verlet）、调试绘制等
- **Trait 系统**：允许为节点附加可扩展的行为特征
- **蓝图集成**：通过 `URigVMBlueprintGeneratedClass` 与蓝图系统深度整合

简单来说：**如果你在用 Control Rig 做动画蓝图，底层就是在跑 RigVM。**

## 使用场景

- 你在使用 **Control Rig** 制作程序化动画 → RigVM 是其底层执行引擎
- 你需要一个**高性能的可视化脚本系统**用于实时求值 → 用 RigVM 替代蓝图
- 你在开发**自定义的 RigVM 节点/函数** → 继承 `FRigVMStruct` 并注册
- 你需要在运行时执行**骨骼链求解、IK、弹簧模拟** → RigVM 内置了相关函数
- 你需要**调试绘制**（线条、线带等）用于开发可视化工具 → 使用 Debug 函数库

## 蓝图用法

RigVM 本身主要通过 Control Rig 资产间接使用，但其内置函数库提供了大量可在 RigVM 图表中使用的节点。

### 核心节点

#### 执行流控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Branch` | 根据条件执行 True 或 False 分支 | `FRigVMFunction_ControlFlowBranch` |
| `For Loop` | 给定次数迭代执行，输出 Index 和 Ratio | `FRigVMFunction_ForLoopCount` |
| `Sequence` | 单次执行脉冲触发 A、B 两个顺序事件 | `FRigVMFunction_Sequence` |
| `User Defined Event` | 自定义事件入口，可命名多个事件 | `FRigVMFunction_UserDefinedEvent` |
| `Is Asset Editor Open` | 判断图表是否在编辑器中打开（仅编辑器） | `FRigVMFunction_IsHostBeingDebugged` |

#### 泛型分发节点（Dispatch）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `If` | 根据条件选择两个值之一 | `FRigVMDispatch_If` |
| `Select` | 根据整数索引从列表中选取值 | `FRigVMDispatch_SelectInt32` |
| `Switch` | 根据整数索引执行对应分支 | `FRigVMDispatch_SwitchInt32` |
| `Cast` | 将对象转换为目标类型 | `FRigVMDispatch_CastObject` |
| `Constant` | 常量值节点 | `FRigVMDispatch_Constant` |
| `Print` | 将任意值打印到日志 | `FRigVMDispatch_Print` |

#### 动画函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Delta Time` | 返回上一帧到当前帧的时间差 | `FRigVMFunction_GetDeltaTime` |
| `Now` | 返回当前世界时间（年月日时分秒） | `FRigVMFunction_GetWorldTime` |
| `Frames to Seconds` | 帧数转秒数 | `FRigVMFunction_FramesToSeconds` |
| `Seconds to Frames` | 秒数转帧数 | `FRigVMFunction_SecondsToFrames` |
| `Curve` | 提供常量浮点曲线 | `FRigVMFunction_AnimRichCurve` |
| `Evaluate Curve` | 求值曲线，支持源/目标范围映射 | `FRigVMFunction_AnimEvalRichCurve` |
| `Ease` | 缓动函数（支持多种缓动类型） | `FRigVMFunction_AnimEasing` |
| `EaseType` | 缓动类型常量 | `FRigVMFunction_AnimEasingType` |

#### 数学函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Random (Float)` | 生成随机浮点数，支持持续时间和种子 | `FRigVMFunction_RandomFloat` |
| `Random (Vector)` | 生成随机向量 | `FRigVMFunction_RandomVector` |

#### 模拟函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Verlet (Vector)` | 使用 Verlet 积分模拟单点位置（推荐用 SpringInterp 替代） | `FRigVMFunction_VerletIntegrateVector` |

#### 调试函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Draw Line` | 在视口中绘制线段 | `FRigVMFunction_DebugLineNoSpace` |
| `Draw Line Strip` | 在视口中绘制线带 | `FRigVMFunction_DebugLineStripNoSpace` |

### 使用示例（蓝图描述）

在 Control Rig 图表中使用 RigVM 节点的典型流程：

1. **创建缓动动画**：拖入 `Ease` 节点 → 设置 `Type` 为 `CubicEaseInOut` → 连接 `Value` 到时间驱动源 → `Result` 输出到目标变换
2. **条件分支**：拖入 `Branch` 节点 → 连接 `Condition` 布尔输入 → `True` / `False` 输出分别连接不同执行路径
3. **循环迭代**：拖入 `For Loop` 节点 → 设置 `Count` → `Index` 和 `Ratio` 输出用于计算 → `Completed` 连接后续逻辑
4. **调试绘制**：拖入 `Draw Line` 节点 → 设置 `A`、`B` 起止点 → 设置 `Color` 和 `Thickness` → `bEnabled` 控制显示

## C++ 用法

### 头文件引入

```cpp
#include "RigVMCore/RigVMStruct.h"
#include "RigVMCore/RigVM.h"
#include "RigVMFunctions/RigVMFunctionDefines.h"
```

### 基本用法：创建自定义 RigVM 节点

所有 RigVM 函数节点都继承自 `FRigVMStruct`（只读）或 `FRigVMStructMutable`（可修改状态），并通过 `USTRUCT` 宏注册。

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVM/Public/RigVMFunctions/Animation/RigVMFunction_GetDeltaTime.h

// 自定义一个简单的 RigVM 函数节点
USTRUCT(meta=(DisplayName="My Custom Node", Category="Custom", NodeColor="0.1 0.5 0.1"))
struct FMyRigVMFunction : public FRigVMStruct
{
    GENERATED_BODY()

    FMyRigVMFunction()
    {
        InputValue = 0.f;
        OutputValue = 0.f;
    }

    // RIGVM_METHOD 宏标记 Execute 为 VM 可调用
    RIGVM_METHOD()
    virtual void Execute() override;

    // meta=(Input) 标记为输入引脚
    UPROPERTY(meta=(Input))
    float InputValue;

    // meta=(Output) 标记为输出引脚
    UPROPERTY(meta=(Output))
    float OutputValue;
};

void FMyRigVMFunction::Execute()
{
    OutputValue = InputValue * 2.0f;
}
```

### 进阶用法：使用控制流和调试绘制

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVM/Public/RigVMFunctions/Debug/RigVMFunction_DebugLine.h
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVM/Public/RigVMFunctions/Execution/RigVMFunction_ForLoop.h

// 创建一个带调试绘制的 Mutable 节点（可修改外部状态）
USTRUCT(meta=(DisplayName="Debug Draw Transform", Category="Debug", NodeColor="0.83 0.85 0.05"))
struct FMyDebugDrawFunction : public FRigVMFunction_DebugBaseMutable
{
    GENERATED_BODY()

    FMyDebugDrawFunction()
    {
        TargetLocation = FVector::ZeroVector;
        bEnabled = true;
    }

    RIGVM_METHOD()
    virtual void Execute() override;

    UPROPERTY(meta=(Input))
    FVector TargetLocation;

    UPROPERTY(meta=(Input))
    bool bEnabled;
};

void FMyDebugDrawFunction::Execute()
{
    // 使用基类的 DebugDrawSettings 控制深度优先级和生命周期
    if (bEnabled)
    {
        // 绘制从原点到目标位置的线
        // 实际绘制通过 ExecuteContext 的调试系统完成
    }
}
```

### 进阶用法：使用日志报告系统

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVM/Public/RigVMFunctions/RigVMFunctionDefines.h

// 在 Execute 中使用日志宏（仅编辑器生效）
void FMyRigVMFunction::Execute()
{
    if (InputValue < 0.f)
    {
        // 报告警告（仅编辑器构建）
        UE_RIGVMSTRUCT_REPORT_WARNING(TEXT("Input value is negative: %f"), InputValue);
    }

    if (InputValue > 1000.f)
    {
        // 报告错误
        UE_RIGVMSTRUCT_REPORT_ERROR(TEXT("Input value exceeds maximum: %f"), InputValue);
    }

    // 普通日志消息
    UE_RIGVMSTRUCT_LOG_MESSAGE(TEXT("Processing value: %f"), InputValue);

    OutputValue = FMath::Clamp(InputValue, 0.f, 1000.f);
}
```

## Demo 示例

### 自定义 RigVM 函数节点

```cpp
// MyRigVMFunction.h
#pragma once

#include "RigVMCore/RigVMStruct.h"
#include "MyRigVMFunction.generated.h"

/**
 * 将输入值映射到 0-1 范围并应用缓动
 */
USTRUCT(meta=(DisplayName="Remap and Ease", Category="Custom|Math", NodeColor="0.2 0.6 0.2"))
struct FMyRemapAndEaseFunction : public FRigVMStruct
{
    GENERATED_BODY()

    FMyRemapAndEaseFunction()
    {
        Value = 0.f;
        InputMin = 0.f;
        InputMax = 1.f;
        EasingType = ERigVMAnimEasingType::CubicEaseInOut;
        Result = 0.f;
    }

    RIGVM_METHOD()
    RIGVM_API virtual void Execute() override;

    UPROPERTY(meta=(Input))
    float Value;

    UPROPERTY(meta=(Input))
    float InputMin;

    UPROPERTY(meta=(Input))
    float InputMax;

    UPROPERTY(meta=(Input))
    ERigVMAnimEasingType EasingType;

    UPROPERTY(meta=(Output))
    float Result;
};
```

```cpp
// MyRigVMFunction.cpp
#include "MyRigVMFunction.h"
#include "RigVMFunctions/Math/RigVMMathLibrary.h"

void FMyRemapAndEaseFunction::Execute()
{
    // 将输入值从 [InputMin, InputMax] 映射到 [0, 1]
    const float Range = InputMax - InputMin;
    const float Normalized = (Range != 0.f) ? FMath::Clamp((Value - InputMin) / Range, 0.f, 1.f) : 0.f;

    // 应用缓动
    Result = RigVMType::EaseFloat(Normalized, EasingType);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Kismet` | RigVMDeveloper 和 RigVMEditor 模块依赖，用于蓝图编译和编辑器集成 |
| `Curves` | Runtime 模块中动画曲线函数（RichCurve）依赖 |

## 维护状态

### 近期更新

```
- ed910243d3e6 Fix for RigVM memory storage not returning correctly the property value as a string, when the value is default initialized to a value that is not the type default value
- f5ed5678640f Add Damp and Critical Spring Damp RigVM nodes, exposing it to UAF and Control Rig
- 450352751efb Use `UE_AUTORTFM_DECLARE_THREAD_LOCAL_VAR` for `thread_local` variable used in a transaction
```

### 维护评价

**活跃维护** ✅

- **创建时间**：2023 年 3 月，约 2 年历史，属于较新的核心系统
- **更新频率**：持续有功能性更新（新增弹簧阻尼节点、修复内存存储问题、事务系统改进）
- **代码规模**：802 个源文件，是 UE5 动画/骨骼系统的基础设施
- **重要性**：作为 Control Rig 的底层引擎，属于 Epic 重点维护的核心模块
- **已知限制**：Verlet 积分节点已被标记为推荐使用 SpringInterp 替代

**推荐使用**：如果你在做程序化动画或 Control Rig 开发，RigVM 是必经之路。直接使用其 API 开发自定义节点是官方推荐的扩展方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM)
- [Control Rig 文档](https://docs.unrealengine.com/5.7/en-US/control-rig-in-unreal-engine/)（RigVM 的主要使用者）