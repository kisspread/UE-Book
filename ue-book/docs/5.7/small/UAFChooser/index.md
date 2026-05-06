# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

将 UAF（Animation Unification Framework）动画变量（Bool、Float、Enum）与 Chooser 系统的参数接口打通，使 Chooser 决策表可以直接读取 UAF 定义的变量值，并根据这些值决定输出的目标对象或对象数组。本质上是一个适配层，让 UAF 数据流能够作为 Chooser 表的输入，从而在 UAF 动画图表中嵌入 Chooser 条件选择逻辑。

## 使用场景

- 在 UAF 动画图或 Control Rig 图中，需要根据运行时动画变量（如 `bIsJumping`, `Speed`, `Stance` 等）选择不同的动画资产或行为树对象。
- 通过 Chooser 表（`UChooserTable`）配置多路条件分支，而不需要手动编写复杂的蓝图切换逻辑。
- 利用 UAF 变量系统与 Chooser 的强类型参数集成，支持 Bool、Float、Enum 三种基本类型。

## 蓝图用法

该插件不暴露蓝图可调用函数（`UFUNCTION(BlueprintCallable)`），而是通过 USTRUCT 和 FRigUnit 节点在 Control Rig / AnimNext 图表中使用。在动画蓝图（或 Rig Graph）中可以放置以下节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` | 评估一个 Chooser 表，输出选中的对象或对象数组。支持 ControlRig 和 AnimNext 上下文。 | `FRigVMDispatch_EvaluateChooser` |
| `Owning Object` | 输出当前执行上下文的拥有对象（通常为动画实例或 Actor）。 | `FRigUnit_OwningObject` |

### 使用示例（蓝图描述）

1. **连接 Owning Object 到 Evaluate Chooser**  
   - 放置 `Owning Object` 节点，其 `Result` 引脚输出当前动画实例（UObject）。  
   - 放置 `Evaluate Chooser` 节点，将 Owning Object 的 `Result` 连接到其 `ContextObject` 输入。  
   - 在 `Chooser` 引脚上指定一个 `UChooserTable` 资产。  
   - 节点执行后，`Result` 引脚输出 Chooser 表选择的结果（UObject），可用于后续动画或逻辑节点。

2. **使用 Bool/Float/Enum 参数列**  
   - 在 Chooser 表的列中，选择参数类型为 `Bool Anim Param`、`Float Anim Param` 或 `Enum Anim Param`。  
   - 这些参数会通过 `FAnimNextVariableReference` 绑定到 UAF 中同名的变量，自动获取运行时值参与决策。

## C++ 用法

### 头文件引入

```cpp
#include "ChooserParameters.h"
#include "RigUnit_EvaluateChooser.h"
#include "RigUnit_OwningObject.h"
```

### 基本用法

**直接使用参数结构体读取/写入 UAF 变量**（以 Bool 为例）：

```cpp
// 假设已有 FChooserEvaluationContext 上下文
FBoolAnimProperty BoolParam;

// 设置要读取的 UAF 变量引用
BoolParam.Variable.VariableName = FName("bIsJumping");

// 评估：从 UAF 上下文读取布尔值
bool bResult = false;
BoolParam.GetValue(Context, bResult);

// 写入（例如用于 Chooser 输出后的反向作用）
BoolParam.SetValue(Context, true);
```

注：`FFloatAnimProperty` 和 `FEnumAnimProperty` 用法类似，`GetValue` 返回 `double` 和 `uint8`。

### 进阶用法

**在自定义 Control Rig 节点中调用 `Evaluate Chooser`**（参考 `FRigUnit_EvaluateChooser` 的实现方式）：

```cpp
// 头文件
USTRUCT(meta = (DisplayName = "MyCustomEvaluate"))
struct FMyRigUnit : public FRigUnit_EvaluateChooser
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;
};

// 实现
void FMyRigUnit::Execute()
{
    // 1. 将 ContextObject 和 Chooser 传递给 Chooser 评估系统
    if (Chooser && ContextObject)
    {
        FChooserEvaluationContext EvalContext;
        EvalContext.SetObject(ContextObject);
        // Chooser 评估内部会使用已注册的参数列（如 FBoolAnimProperty）
        TArray<UObject*> Results = Chooser->EvaluateChooser(EvalContext);
        if (Results.Num() > 0)
        {
            Result = Results[0];
        }
    }
}
```

**获取当前拥有对象**（`FRigUnit_OwningObject`）：

```cpp
FRigUnit_OwningObject Node;
Node.Execute();  // 执行后 Node.Result 指向当前 Rig 的 Outer（如 AnimInstance）
```

## Demo 示例

以下是一个完整的、可直接运行的 Control Rig 节点示例，展示如何组合 `Owning Object` 和 `Evaluate Chooser`（忽略 .Build.cs 中的依赖，详见模块依赖）。

**RigUnit_DemoEvaluate.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Units/RigUnit.h"
#include "Chooser.h"
#include "RigUnit_OwningObject.h"
#include "RigUnit_EvaluateChooser.h"
#include "RigUnit_DemoEvaluate.generated.h"

/**
 * 演示节点：获取当前对象，评估 Chooser 表，输出第一个结果
 */
USTRUCT(meta = (DisplayName = "Demo Evaluate Chooser", Category = "UAF|Demo"))
struct FRigUnit_DemoEvaluate : public FRigUnit_EvaluateChooser
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute() override;
};
```

**RigUnit_DemoEvaluate.cpp**
```cpp
#include "RigUnit_DemoEvaluate.h"
#include "Chooser.h"
#include "ChooserEvaluationContext.h"

void FRigUnit_DemoEvaluate::Execute()
{
    // 1. 获取拥有对象（类似 Owning Object 节点内部逻辑）
    FRigUnit_OwningObject GetOwner;
    GetOwner.Execute();
    ContextObject = GetOwner.Result;

    // 2. 如果未指定 Chooser 表，则不处理
    if (!Chooser || !ContextObject)
    {
        Result = nullptr;
        return;
    }

    // 3. 创建评估上下文，注入 ContextObject
    FChooserEvaluationContext EvalContext;
    EvalContext.SetObject(ContextObject);

    // 4. 评估 Chooser 表，输出结果对象列表
    TArray<UObject*> OutResults = Chooser->EvaluateChooser(EvalContext);

    // 5. 取第一个有效结果作为输出
    Result = (OutResults.Num() > 0) ? OutResults[0] : nullptr;
}
```

## 模块依赖

使用者需要在你的模块 `Build.cs` 的 `PublicDependencyModuleNames` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 变量系统及运行时支持 |
| `UAFAnimGraph` | UAF 动画图表编辑支持（编辑器依赖） |
| `Chooser` | Chooser 表评估核心 |
| `ControlRig` | 提供 RIGVM 执行环境及节点基础 |

**注意**：由于本插件自身已声明这些依赖，链接时无需重复包含 `Core`, `Engine` 等常见模块（系统会自动传递）。

## 维护状态

### 近期更新

- 2025-08-29 `07575a64` — Fix Evaluate chooser rig unit to return null on failure
- 2025-08-28 `66ff996a` — Fix Evalute Chooser rig unit to return null when chooser evaluation fails
- 2025-06-27 `ee0441e9` — UAF: Rename/move plugins

### 维护评价

该插件创建于 2025 年 6 月，尚处早期开发阶段，属于实验性插件（`IsExperimentalVersion: true`）。近期（2025年8月）有两次修复，均为处理 Chooser 评估失败时返回 `null` 的问题。目前处于**维护中**状态，但功能尚不稳定，建议仅在开发/原型阶段使用，生产项目需谨慎。由于是实验性插件，API 可能在未来发生变动，不建议依赖其私有头文件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFChooser)
- [UAF 插件（父目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF)
- [Chooser 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Chooser)