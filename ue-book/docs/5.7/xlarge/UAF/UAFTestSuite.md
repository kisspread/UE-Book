# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestSuite` (Runtime), `UAFUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

**UAF（Unreal Animation Framework）** 是一个实验性插件，旨在为动画系统提供**功能性数据流**定义框架。它基于参数化、可组合的节点图（类似 RigVM），允许用户以声明式方式描述动画数据的处理逻辑（如混合、修改、条件分支等），从而摆脱传统动画蓝图的事件驱动模型。

- **为什么存在**：现有的动画蓝图（AnimBP）虽然灵活，但在大型项目中容易产生复杂的事件流和状态管理。UAF 尝试通过纯数据流（Dataflow）的方式简化动画逻辑，使动画系统更可预测、更易于调试和重用。
- **解决什么问题**：
  - 动画逻辑的模块化与组合
  - 减少事件驱动的副作用
  - 支持运行时参数化（如通过 ParamType 系统）
  - 为未来的动画系统升级提供基础（如 AnimNext）

> ⚠️ 该插件当前处于**实验性**阶段，API 可能频繁变更，不建议用于生产环境。

## 使用场景

- 你需要在运行时动态组合动画混合逻辑，而不想手动管理 AnimGraph；
- 你希望将动画逻辑拆分为纯数据转换的“单元”，并重用它们；
- 你在研究未来动画系统的可能性（如 AnimNext 项目的前身）；
- 你进行动画相关功能的自动化测试，UAFTestSuite 提供了测试基础设施。

## 蓝图用法

UAF 目前未提供公开的蓝图节点（所有相关类标记为 `BlueprintInternalUseOnly`）。其核心逻辑主要在 C++ 中通过继承 `URigVMStruct` 或自定义 UObject 实现。若需在蓝图中使用，需开发者自行暴露或等待后续版本。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （暂无公开蓝图节点） | — | — |

> 内部测试用蓝图库（如 `AnimNextVariablesTest`）仅用于自动测试，不推荐外部使用。

## C++ 用法

### 头文件引入

```cpp
#include "UAF/UAF.h"                // 主模块
#include "Tests/AnimNextTest.h"     // 测试辅助（仅用于测试）
#include "TestVariables/AnimNextVariablesTest.h" // 变量测试结构
```

### 基本用法

从测试代码可以看出 UAF 数据流的基本单元是 `FPParamType`（参数类型）和 `FRigVMStruct`。以下示例演示如何定义一个简单的数据流结构并注册参数：

```cpp
// 定义自定义数据流节点（继承自 FRigVMStruct 或使用 UPROPERTY 标记的 USTRUCT）
USTRUCT(BlueprintInternalUseOnly)
struct FMyAnimationNode : public FRigVMStruct
{
    GENERATED_BODY()

    // 输入参数
    UPROPERTY()
    float InputAlpha = 0.5f;

    // 输出参数
    UPROPERTY()
    float OutputBlendValue = 0.0f;

    // 执行逻辑（由 RigVM 调用）
    virtual void Execute(const FRigVMExtendedExecuteContext& Context, FOutputArgumentOutput& Output) const override
    {
        OutputBlendValue = InputAlpha * 2.0f;
    }
};
```

```cpp
// 注册参数类型（通过 FAnimNextParamType 描述）
FAnimNextParamType MyType = FAnimNextParamType::Make<float>();
// 在数据流图中使用
// ...
```

具体用法可参考 `Engine/Plugins/Experimental/UAF/UAF/Source/UAF/Public/Param/ParamType.h` 中的类型系统。

### 进阶用法

结合 UAFTestSuite 的测试代码，可看到如何构造测试数据并验证执行结果：

```cpp
// 来源：Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite/Private/AnimNextVariablesTest.cpp

#include "Misc/AutomationTest.h"
#include "AnimNextVariablesTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFVariableTest, "UAF.Variables.Basic", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

bool FUAFVariableTest::RunTest(const FString& Parameters)
{
    // 使用 FAnimNextParamTypeTestStruct 测试不同类型参数的序列化与还原
    FAnimNextParamTypeTestStruct TestStruct;
    TestStruct.Float = 42.0f;
    TestStruct.Int32 = 100;
    // ... 设置其他字段

    // 通过 AnimNext Component 或直接操作 Param 系统进行数据流测试
    // 注意：此处仅示意，实际需要 UAnimNextComponent 或 UAF 内部管道
    // ...

    // 清理测试残留
    UE::UAF::Tests::FUtils::CleanupAfterTests();
    return true;
}
```

更复杂的用法涉及 `UAnimNextComponent`、`UAFUncookedOnly` 模块的编译时生成逻辑等，请参考插件的测试套件。

## Demo 示例

本插件暂无独立的 Demo 示例。以下为**最小测试用例**（将 `UAFTestSuite` 启用后运行自动化测试）：

```cpp
// MyTest.h
#pragma once
#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "AnimNextTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyUAFDemoTest, "UAF.Demo.Basic", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

// MyTest.cpp
#include "MyTest.h"

bool FMyUAFDemoTest::RunTest(const FString& Parameters)
{
    // 使用 FAnimNextParamType 定义参数
    FAnimNextParamType ParamType(FAnimNextParamType::Make<float>());
    // 在你的数据流图中创建并连接节点...
    // 由于 UAF 尚未公开稳定 API，此处仅示意

    UE::UAF::Tests::FUtils::CleanupAfterTests();
    return true;
}
```

> 完整可运行示例需等待 UAF API 稳定化后补充。

## 模块依赖

启用 UAF 插件时，你的模块需要添加以下依赖（`PublicDependencyModuleNames`）：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 运行时热重载 C++ 代码（UAF、UAFUncookedOnly 模块依赖） |

其他模块均为内部依赖，对外透明。若使用 UAF 主模块功能，通常只需：

```cpp
PublicDependencyModuleNames.AddRange(new string[] { "UAF" });
```

## 维护状态

### 近期更新

- 2025-10-02 `ef1c8b52` — Fix double binding to IsEnabled  
- 2025-10-02 `f75459b5` — Fix crash from selecting non-Actor derived blueprint to modify in UAF asset wizard  
- 2025-10-01 `6f23619b` — Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various implementations  
- 2025-09-30 `737f1f42` — Crash fixes for LODPose  
- 2025-09-25 `2f8943cd` — Honor `ShrinkByDefault` in various existing array classes  

### 维护评价

- **创建时间**：2025-09-25，插件诞生仅约 **2 个月**。
- **最近更新**：非常频繁，最近一周内有多次修复和优化。
- **活跃度**：极高，开发团队正在积极迭代。
- **已知问题**：存在崩溃、绑定错误等问题，但均在快速修复中。
- **推荐程度**：❌ **不推荐用于生产**。实验性阶段，API 未稳定，可能随时不兼容。仅供研究和测试使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/ExperimentalFeatures/)（插件无单独文档页，参考实验特性总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite)