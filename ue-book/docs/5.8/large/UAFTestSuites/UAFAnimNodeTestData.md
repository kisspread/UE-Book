# UAF Tests

> UAF Automated Tests（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试数据结构） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

该插件是 **UAF (Unreal Animation Framework) 动画框架** 的自动化测试套件。它并非面向最终用户的功能性插件，而是 Epic Games 内部用于验证 UAF 核心功能（特别是动画节点变量绑定、蓝图集成和性能）的测试基础设施。它包含用于测试的数据结构、测试用例以及性能基准测试，确保 UAF 系统在开发过程中的稳定性和正确性。

## 使用场景

- **UAF 框架开发者**：在开发或修改 UAF 动画节点（如 `UAnimNode_*`）时，运行此插件中的测试来验证变量绑定、蓝图集成等功能是否正常工作。
- **集成 UAF 的项目开发者**：在项目中深度集成并扩展 UAF 动画系统时，可以参考或运行这些测试来确保自定义节点与 UAF 核心的兼容性。
- **性能优化**：使用插件中包含的性能基准测试（如 `FUAFAnimNodePerfVars10`）来评估动画节点变量解析的性能开销。

## 蓝图用法

该插件主要提供自动化测试，不包含面向蓝图用户的公开 API。其测试逻辑通过 Unreal Automation Testing Framework 运行，而非通过蓝图节点调用。

## C++ 用法

该插件的核心是提供用于测试的数据结构和测试用例。开发者主要通过编写或运行自动化测试来使用它。

### 头文件引入

```cpp
// 引入测试用的变量结构体
#include "UAFAnimNodeTestVars.h"

// 引入测试用的 Trait 数据
#include "UAFTestBindableTraitData.h"
```

### 基本用法

该插件提供的结构体主要用于定义测试场景中的变量。

**1. 定义测试变量结构体**
`FUAFAnimNodeTestVars` 是一个包含多种常见类型属性的结构体，用于测试 UAF 动画节点的变量绑定功能。
```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h
USTRUCT()
struct FUAFAnimNodeTestVars
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Variables")
    bool bBool = false;

    UPROPERTY(EditAnywhere, Category = "Variables")
    float FloatVal = 0.0f;

    UPROPERTY(EditAnywhere, Category = "Variables")
    double DoubleVal = 0.0;

    UPROPERTY(EditAnywhere, Category = "Variables")
    int32 IntVal = 0;

    UPROPERTY(EditAnywhere, Category = "Variables")
    FVector VectorVar = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, Category = "Variables")
    FQuat QuatVar = FQuat::Identity;

    UPROPERTY(EditAnywhere, Category = "Variables")
    FTransform TransformVar = FTransform::Identity;

    UPROPERTY(EditAnywhere, Category = "Variables")
    FUAFAnimNodeNestedTestStruct NestedVar;
};
```

**2. 定义性能测试变量**
`FUAFAnimNodePerfVars10` 包含大量浮点和向量属性，专门用于变量绑定的性能基准测试。
```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFAnimNodeTestVars.h
USTRUCT()
struct FUAFAnimNodePerfVars10
{
    GENERATED_BODY()

    // 10个浮点目标/源，用于变量绑定基准测试
    UPROPERTY() float f0 = 0.f;
    // ... f1 到 f9 ...

    // 10个向量源，用于子属性绑定基准测试 (绑定 .X -> f0..f9)
    UPROPERTY() FVector v0 = FVector::ZeroVector;
    // ... v1 到 v9 ...
};
```

### 进阶用法

**1. 测试 Trait 的可绑定属性**
`FUAFTestBindableTraitSharedData` 展示了如何为 UAF Trait 定义一个可绑定的布尔属性 (`FBindableBool`)。这用于测试 RigVM 控制器是否能正确检测到通过文本比较进行的 `SetPinDefaultValue` 操作。
```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFTestBindableTraitData.h
USTRUCT()
struct FUAFTestBindableTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Test")
    FBindableBool bTestBool = false;

    // ... 宏定义和属性生成器 ...
};
```

**2. 注册测试 Trait**
`FTestBindableTrait` 是一个最小化的 Trait 实现，它使用上述的共享数据结构。这是为了在 `AddTrait` 操作期间，让 `FRigDecorator_AnimNextCppDecorator` 能够解析共享数据结构到一个已注册的 Trait。
```cpp
// 来源: Source/UAFAnimNodeTestData/Public/UAFTestBindableTraitData.h
namespace UE::UAF
{
    struct FTestBindableTrait : FBaseTrait
    {
        DECLARE_ANIM_TRAIT(FTestBindableTrait, FBaseTrait)
        using FSharedData = FUAFTestBindableTraitSharedData;
    };
}
```

## Demo 示例

以下是一个最小化的示例，展示如何在测试代码中使用 `FUAFAnimNodeTestVars` 来验证变量绑定。

```cpp
// MyAnimNodeTest.cpp
#include "UAFAnimNodeTestVars.h"
#include "UAF/AnimNodeCore/UAFAnimNodeData.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFAnimNodeBindingTest,
    "UAF.AnimNode.VariableBinding",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FUAFAnimNodeBindingTest::RunTest(const FString& Parameters)
{
    // 1. 创建一个测试变量实例
    FUAFAnimNodeTestVars TestVars;
    TestVars.FloatVal = 42.0f;
    TestVars.VectorVar = FVector(1.0f, 2.0f, 3.0f);

    // 2. 模拟创建一个 UAF 资产实例 (实际测试中会使用真实的 UAF 资产)
    // FUAFAssetInstance AssetInstance = ...;

    // 3. 模拟将变量绑定到动画节点的输入引脚
    // FBindableFloat BoundFloat;
    // BoundFloat.BindToVariable(&TestVars, GET_MEMBER_NAME_CHECKED(FUAFAnimNodeTestVars, FloatVal));

    // 4. 验证绑定后的值是否正确
    // TestEqual(TEXT("Float binding should resolve to 42.0f"), BoundFloat.GetValue(), 42.0f);

    // 5. 修改源变量，验证绑定值是否同步更新
    // TestVars.FloatVal = 99.0f;
    // TestEqual(TEXT("Bound value should update after source change"), BoundFloat.GetValue(), 99.0f);

    return true;
}
```

## 模块依赖

该插件的模块主要依赖 UAF 核心框架和动画系统相关模块。

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 动画框架核心模块 |
| `AnimationCore` | 动画核心库 |
| `RigVM` | RigVM 虚拟机，用于动画蓝图逻辑 |
| `AnimNext` | 下一代动画系统（UAF 的一部分） |

## 维护状态

### 近期更新
（由于无法访问实际的 git log，以下为基于插件性质的推测）
- 该插件创建于 2026 年 3 月，非常新。
- 作为实验性 (`IsExperimentalVersion: true`) 且默认禁用的测试插件，其更新会紧密跟随 UAF 核心框架的开发进度。
- 预期会随着 UAF 功能的增加、修改或重构而同步更新测试用例。

### 维护评价
- **状态**：🆕 **新创建且处于实验阶段**。
- **活跃度**：作为 Epic Games 内部 UAF 开发的测试基础设施，预计会**活跃维护**，但其更新节奏取决于 UAF 核心的开发。
- **推荐使用**：**仅推荐给 UAF 框架的深度开发者或贡献者**。对于普通项目开发者，此插件没有直接使用价值，但可以作为理解 UAF 内部工作原理和测试方法的参考。
- **警告**：该插件标记为实验性，其 API 和测试结构可能在 UAF 框架成熟过程中发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source) (测试代码位于各模块的 `Private` 目录下)