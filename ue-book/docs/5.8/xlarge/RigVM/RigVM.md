# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | RigVM 运行时 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数学库、数组操作、字符串/Name 操作、模拟函数等蓝图资产） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (Runtime), `RigVMEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 Unreal Engine 5 中**可视化编程语言的前端和后端运行时**。它为 Control Rig 等骨架动画编辑系统提供底层的虚拟机基础设施。

核心工作流程：
1. **节点图 → 字节码**：用户在可视化编辑器中连接节点，RigVM 编译器将节点图编译为紧凑的字节码（`FRigVMByteCode`）
2. **字节码执行**：运行时虚拟机（`URigVM`）加载字节码，在每帧中高效执行指令
3. **类型系统**：通过 `FRigVMRegistry` 管理所有注册的函数、模板和类型，支持泛型调度（Dispatch）机制
4. **内存管理**：提供字面量内存（Literal）、工作内存（Work）和调试内存（Debug）的分层存储

RigVM 解决的核心问题是：**如何在运行时以接近原生 C++ 的性能执行由可视化节点图编译而来的逻辑**，同时支持泛型类型推导、切片执行（per-slice execution）和延迟求值（lazy evaluation）等高级特性。

## 使用场景

- 你在做**角色骨骼动画**，需要用可视化方式编写 IK、FK 混合、约束等逻辑 → 用 Control Rig（基于 RigVM）
- 你需要一个**高性能的可视化脚本执行环境**，且对每帧调用的性能要求严格 → 用 RigVM 作为后端
- 你要实现**自定义的可视化编程工具**，需要节点图编译器和字节码虚拟机 → 基于 RigVM 的前端/后端架构搭建
- 你需要在运行时**动态调度大量泛型函数**（如数学运算、数组操作），且类型在编译时由模板系统推导 → 用 RigVM 的 Template/Dispatch 机制
- 你需要**将可视化图表 Nativize 为 C++ 代码**以获得最大性能 → RigVM 支持 `URigVMNativized` 子类

## 蓝图用法

RigVM 的大部分蓝图 API 通过 `URigVMHost` 暴露，这是所有 RigVM 宿主的基类（如 ControlRig）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行指定事件名的 VM 逻辑 | `URigVMHost` |
| `SetDeltaTime` | 设置当前帧的 DeltaTime | `URigVMHost` |
| `SetAbsoluteTime` | 设置绝对时间 | `URigVMHost` |
| `GetAbsoluteTime` | 获取当前绝对时间 | `URigVMHost` |
| `GetDeltaTime` | 获取当前帧间隔 | `URigVMHost` |
| `SetFramesPerSecond` | 设置帧率 | `URigVMHost` |
| `GetCurrentFramesPerSecond` | 获取当前帧率 | `URigVMHost` |
| `CanExecute` | 检查是否可执行 | `URigVMHost` |
| `FindRigVMHosts` | 在指定 Outer 下查找所有 RigVM 宿主 | `URigVMHost` |
| `GetScriptAccessibleVariables` | 获取可从脚本访问的变量名列表 | `URigVMHost` |
| `GetVariableType` | 获取变量类型名 | `URigVMHost` |
| `GetVariableAsString` | 以字符串形式获取变量值 | `URigVMHost` |
| `SetVariableFromString` | 以字符串形式设置变量值 | `URigVMHost` |

### 数学函数节点（示例）

RigVM 内置了丰富的数学函数，可在蓝图中使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add (Float)` | 浮点加法 | `FRigVMFunction_MathFloatAdd` |
| `Multiply (Vector)` | 向量乘法 | `FRigVMFunction_MathVectorMul` |
| `From Euler (Quaternion)` | 欧拉角转四元数 | `FRigVMFunction_MathQuaternionFromEuler` |
| `Mirror (Transform)` | 镜像变换 | `FRigVMFunction_MathTransformMirrorTransform` |
| `Alpha Interpolate (Float)` | 带缩放/偏移/插值的 Alpha 混合 | `FRigVMFunction_AlphaInterp` |
| `RBF Quaternion to Float` | RBF 插值（四元数→浮点） | `FRigVMFunction_MathRBFInterpolateQuatFloat` |

### 数组操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Array` | 从多个输入构造数组 | `FRigVMDispatch_ArrayMake` |
| `Num` | 获取数组长度 | `FRigVMDispatch_ArrayGetNum` |
| `At` | 按索引获取元素 | `FRigVMDispatch_ArrayGetAtIndex` |
| `Set Num` | 设置数组大小 | `FRigVMDispatch_ArraySetNum` |
| `Reset` | 清空数组 | `FRigVMDispatch_ArrayReset` |
| `Init` | 用默认值初始化数组 | `FRigVMDispatch_ArrayInit` |
| `IsEmpty` | 判断数组是否为空 | `FRigVMDispatch_ArrayIsEmpty` |

### 字符串/Name 操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Concat` | 字符串/Name 拼接 | `FRigVMFunction_StringConcat` / `FRigVMFunction_NameConcat` |
| `Replace` | 查找替换 | `FRigVMFunction_StringReplace` |
| `Contains` | 是否包含子串 | `FRigVMFunction_StringContains` |
| `To String` | 任意类型转字符串 | `FRigDispatch_ToString` |
| `From String` | 字符串转任意类型 | `FRigDispatch_FromString` |

### 调试绘制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DrawPoint` | 绘制点 | `FRigVMDrawInterface` |
| `DrawLine` | 绘制线段 | `FRigVMDrawInterface` |
| `DrawSphere` | 绘制球体 | `FRigVMDrawInterface` |
| `DrawAxes` | 绘制坐标轴 | `FRigVMDrawInterface` |
| `DrawText` | 绘制文本 | `FRigVMDrawInterface` |

### 使用示例（蓝图描述）

**执行一个 RigVM 宿主**：
1. 获取一个 `URigVMHost` 引用（例如 ControlRig 组件）
2. 连接到 `Execute` 节点，传入事件名（如 `"Backwards"`, `"Forwards"`）
3. 在每帧 Tick 中调用

**查询和修改变量**：
1. 调用 `GetScriptAccessibleVariables` 获取变量名列表
2. 用 `GetVariableType` 查询类型
3. 用 `SetVariableFromString` / `GetVariableAsString` 读写变量值

## C++ 用法

### 头文件引入

```cpp
// 核心 VM 和运行时
#include "RigVMHost.h"
#include "RigVM/RigVM.h"

// 注册表（函数/类型管理）
#include "RigVMCore/RigVMRegistry.h"

// 字节码
#include "RigVMCore/RigVMByteCode.h"

// 数学函数库
#include "RigVMFunctions/Math/RigVMMathLibrary.h"
#include "RigVMFunctions/Math/RigVMFunction_MathFloat.h"
#include "RigVMFunctions/Math/RigVMFunction_MathVector.h"
#include "RigVMFunctions/Math/RigVMFunction_MathTransform.h"

// 外部变量
#include "RigVMCore/RigVMExternalVariable.h"

// 运行时资产
#include "RigVMRuntimeAsset.h"
```

### 基本用法

**1. 创建和执行 RigVM**

```cpp
// 创建一个 RigVM 实例
URigVM* VM = NewObject<URigVM>();

// 初始化扩展执行上下文
FRigVMExtendedExecuteContext Context;
VM->Initialize(Context);

// 注册函数（通常由编译器自动完成）
// VM->AddRigVMFunction(MyStruct::StaticStruct(), TEXT("MyMethod"));

// 执行 VM
ERigVMExecuteResult Result = VM->ExecuteVM(Context, TEXT("Execute"));
```

**2. 通过 RigVMHost 执行**

```cpp
// RigVMHost 是所有 RigVM 宿主的基类
// 通常通过 ControlRig 等子类使用
URigVMHost* Host = ...; // 例如从组件获取

// 初始化
Host->Initialize(true);

// 每帧调用
Host->SetDeltaTime(DeltaTime);
Host->Execute(TEXT("Forwards"));
```

**3. 管理外部变量**

```cpp
// 创建外部变量定义
FRigVMExternalVariable Variable = FRigVMExternalVariable::Make(
    FGuid::NewGuid(),
    TEXT("MyFloat"),
    MyFloatValue  // bool&, float&, FVector& 等
);

// 获取宿主的外部变量
TArray<FRigVMExternalVariable> ExternalVars = Host->GetExternalVariables();

// 按名称查询变量
FRigVMExternalVariable Found = Host->GetVariableByName(TEXT("MyVariable"));
if (Found.IsValid())
{
    float Value = Found.GetValue<float>();
    Found.SetValue<float>(42.0f);
}
```

**4. 使用数学库**

```cpp
// 静态数学函数
float Angle = FRigVMMathLibrary::AngleBetween(FVector::ForwardVector, FVector::UpVector);

// 贝塞尔曲线
FVector Pos, Tangent;
FRigVMFourPointBezier Bezier;
Bezier.A = FVector(0, 0, 0);
Bezier.B = FVector(100, 0, 0);
Bezier.C = FVector(200, 100, 0);
Bezier.D = FVector(300, 100, 0);
FRigVMMathLibrary::FourPointBezier(Bezier, 0.5f, Pos, Tangent);

// 变换插值
FTransform Result = FRigVMMathLibrary::LerpTransform(TransformA, TransformB, 0.5f);

// 缓动函数
float Eased = FRigVMMathLibrary::EaseFloat(0.5f, ERigVMAnimEasingType::CubicEaseInOut);
```

**5. 访问类型注册表**

```cpp
// 获取全局注册表
FRigVMRegistry& Registry = FRigVMRegistry::Get();

// 查找已注册的函数
const FRigVMFunction* Func = Registry.FindFunction(TEXT("FMyStruct::MyExecute"));
if (Func)
{
    FRigVMFunctionPtr Ptr = Func->FunctionPtr;
}

// 查找类型索引
TRigVMTypeIndex TypeIndex = Registry.GetTypeIndex(FRigVMTemplateArgumentType(
    TEXT("float"), nullptr));

// 查找模板
const FRigVMTemplate* Template = Registry.FindTemplate(FName(TEXT("Add")));
```

### 进阶用法

**1. 创建可执行的 RigVM 单元结构**

```cpp
USTRUCT(meta = (DisplayName = "My Custom Node", Category = "Custom"))
struct FRigVMFunction_MyCustomNode : public FRigVMStructMutable
{
    GENERATED_BODY()

    // 输入
    UPROPERTY(meta = (Input))
    float Value;

    // 输出
    UPROPERTY(meta = (Output))
    float Result;

    // 执行逻辑
    RIGVM_METHOD()
    virtual void Execute() override
    {
        Result = Value * 2.0f;
    }
};
```

**2. 使用 RigVMNativized 进行原生化执行**

```cpp
// RigVMNativized 将字节码转换为 C++ 代码
// 子类需要实现具体的执行逻辑
class URigVMMyNativized : public URigVMNativized
{
    GENERATED_BODY()
public:
    virtual ERigVMExecuteResult ExecuteVM(
        FRigVMExtendedExecuteContext& Context,
        const FName& InEntryName = NAME_None) override
    {
        // 直接调用编译生成的 C++ 函数
        // 跳过字节码解释，获得最大性能
        return Super::ExecuteVM(Context, InEntryName);
    }
};
```

**3. 使用调试绘制接口**

```cpp
// 在 RigVM 单元的 Execute() 中使用绘制接口
virtual void Execute() override
{
    FRigVMDrawInterface* DrawInterface = ExecuteContext.GetDrawInterface();
    if (DrawInterface)
    {
        DrawInterface->DrawPoint(
            FTransform::Identity,
            TargetPosition,
            5.0f,
            FLinearColor::Red
        );
        DrawInterface->DrawLine(
            FTransform::Identity,
            StartPosition,
            EndPosition,
            FLinearColor::Green,
            2.0f
        );
    }
}
```

**4. 追踪指令执行（编辑器调试）**

```cpp
#if WITH_EDITOR
// 检查某条指令是否被执行过
bool bVisited = VM->WasInstructionVisitedDuringLastRun(Context, InstructionIndex);

// 获取执行次数
int32 VisitCount = VM->GetInstructionVisitedCount(Context, InstructionIndex);

// 获取指令耗时（需要在 RuntimeSettings 中启用 bEnableProfiling）
double MicroSeconds = VM->GetInstructionMicroSeconds(Context, InstructionIndex);

// 获取完整的执行顺序
TArray<int32> VisitOrder = VM->GetInstructionVisitOrder(Context);
#endif
```

## Demo 示例

以下示例展示如何创建一个最小的可执行 RigVM 单元：

```cpp
// MyRigVMNode.h
#pragma once

#include "RigVMCore/RigVMStruct.h"
#include "MyRigVMNode.generated.h"

USTRUCT(meta = (DisplayName = "Double Float", Category = "Custom|Math"))
struct FRigVMFunction_DoubleFloat : public FRigVMStructMutable
{
    GENERATED_BODY()

    UPROPERTY(meta = (Input))
    float Value = 0.0f;

    UPROPERTY(meta = (Output))
    float Result = 0.0f;

    RIGVM_METHOD()
    virtual void Execute() override
    {
        Result = Value * 2.0f;
    }
};
```

```cpp
// MyRigVMNode.cpp
#include "MyRigVMNode.h"

// RIGVM_METHOD 宏会自动生成必要的注册代码
// 无需额外的 .cpp 实现
```

```cpp
// MyRigVMHost.h
#pragma once

#include "RigVMHost.h"
#include "MyRigVMHost.generated.h"

UCLASS()
class UMyRigVMHost : public URigVMHost
{
    GENERATED_BODY()

public:
    // 可在蓝图中设置的变量
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VM")
    float MyInputValue = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "VM")
    float MyOutputValue = 0.0f;

    // 初始化时设置 VM
    virtual void Initialize(bool bRequestInit = true) override;

    // 执行
    virtual bool Execute(const FName& InEventName) override;
};
```

```cpp
// MyRigVMHost.cpp
#include "MyRigVMHost.h"

void UMyRigVMHost::Initialize(bool bRequestInit)
{
    Super::Initialize(bRequestInit);
    // VM 会从 RuntimeAsset 自动加载
}

bool UMyRigVMHost::Execute(const FName& InEventName)
{
    // 设置输入
    FRigVMExternalVariable InputVar = GetVariableByName(TEXT("MyInputValue"));
    if (InputVar.IsValid())
    {
        InputVar.SetValue<float>(MyInputValue);
    }

    // 执行 VM
    bool bSuccess = Super::Execute(InEventName);

    // 读取输出
    FRigVMExternalVariable OutputVar = GetVariableByName(TEXT("MyOutputValue"));
    if (OutputVar.IsValid())
    {
        MyOutputValue = OutputVar.GetValue<float>();
    }

    return bSuccess;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Kismet` | RigVMDeveloper/RigVMEditor 模块依赖，用于蓝图/编译相关功能 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `dfee5052` | Control Rig: Fix missing dependency in ControlRigModules | 修复 ControlRig 模块缺失依赖问题 |
| 2026-05-22 | `e51b24ac` | Cherry-picking fix CL from Sara Schvartzman | 从主线摘取修复补丁 |
| 2026-05-21 | `fee6a0dc` | Control Rig: Fix renaming a variable in some cases leaves a duplicate | 修复变量重命名后偶现的重复残留问题 |
| 2026-05-18 | `5d1db13f` | Fix crash when debug pins are orphaned | 修复调试引脚孤立时的崩溃 |
| 2026-05-15 | `0b718514` | Control RIg: Defensive fix when function of a unit struct is nullptr | 防御性修复单元结构函数为空时的潜在问题 |

### 维护评价

**活跃维护**：RigVM 是 UE5 Control Rig 系统的核心运行时，由 Epic Games 官方团队持续维护。

- **创建时间**：2023 年 3 月，从 Engine 模块迁移为 Runtime 插件（CL 24819276）
- **近期更新**：最近更新至 2026 年 5 月底，更新频繁且持续
- **成熟度**：作为 Control Rig 的底层引擎，已广泛用于《Fortnite》、《Lyra》等项目
- **代码规模**：528 个源文件，是 UE5 中最大型的运行时插件之一
- **已知限制**：调试绘制功能仅在 WITH_EDITOR 下可用；性能分析需启用 bEnableProfiling
- **推荐使用**：如果你在做骨骼动画/Control Rig 相关开发，RigVM 是必不可少的基础设施；如果要搭建自定义可视化编程系统，RigVM 也是优秀的底层选择

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM)
- 官方文档：无（.uplugin 中 DocsURL 为空）