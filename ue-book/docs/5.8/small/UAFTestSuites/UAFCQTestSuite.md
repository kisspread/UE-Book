# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试代码） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

UAFTestSuites 是用于 Unreal Animation Framework (UAF) 的**自动化测试套件**。它并非为最终用户（美术师/设计师）设计，而是为 UAF 框架的**开发者和测试人员**提供。其核心作用是验证 UAF 资产（如 RigVM 资产）的创建、编译、图编辑操作以及虚拟机（VM）执行的正确性。它通过一系列蓝图节点和 C++ 工具函数，使开发者能够编写结构化的自动化测试用例，确保 UAF 核心功能的稳定与可靠。

## 使用场景

- **UAF 框架开发**：当您是 UAF 框架的开发者，在添加新功能（如新的节点、图操作）后，需要编写自动化测试来验证功能正确性，并防止后续代码变更引入回归。
- **CI/CD 流程**：在持续集成/持续部署系统中，该插件提供的测试套件可以作为构建验证的一部分，自动运行以确认 UAF 核心模块在最新引擎版本中未被破坏。
- **编写自定义自动化测试**：开发者需要为自定义的 UAF 资产类型或功能编写特定的自动化测试时，可以利用此插件提供的蓝图节点和 C++ 辅助函数来简化测试资产的创建和操作。

## 蓝图用法

该插件主要在蓝图测试中暴露了一系列辅助节点，用于程序化地操作 UAF 资产。核心节点集中在 `UUAFTestBlueprintLibrary` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAsset` | 使用指定的工厂类创建一个新的 `UUAFRigVMAsset` 实例。 | `UUAFTestBlueprintLibrary` |
| `RecompileVM` | 请求对指定的 `UUAFRigVMAsset` 进行 VM 重新编译。 | `UUAFTestBlueprintLibrary` |
| `GetCompilationState` | 获取 `UUAFRigVMAsset` 当前的编译状态。 | `UUAFTestBlueprintLibrary` |
| `GetModel` | 获取资产中指定 `UEdGraph` 对应的 `URigVMGraph` 模型。 | `UUAFTestBlueprintLibrary` |
| `GetDefaultModel` | 获取资产的默认 `URigVMGraph` 模型。 | `UUAFTestBlueprintLibrary` |
| `GetAllModels` | 获取资产中所有的 `URigVMGraph` 模型列表。 | `UUAFTestBlueprintLibrary` |
| `AddModel` | 在资产中添加一个新的 `URigVMGraph` 模型（图）。 | `UUAFTestBlueprintLibrary` |
| `RemoveModel` | 从资产中移除一个指定名称的 `URigVMGraph` 模型。 | `UUAFTestBlueprintLibrary` |
| `GetController` | 获取用于操作指定 `URigVMGraph` 的 `URigVMController`。 | `UUAFTestBlueprintLibrary` |
| `ExecuteVM` | 执行指定 `UUAFSystem` 模块上的 VM 事件，并返回执行结果和输出消息。 | `UUAFTestBlueprintLibrary` |
| `AddUnitNode` | 向图表中添加一个基于 ScriptStruct 的 RigUnit 节点。 | `UAFTestsUtilities` (C++ 辅助，蓝图可通过库调用) |
| `AddVariableNode` | 向图表中添加一个变量读写节点。 | `UAFTestsUtilities` (C++ 辅助) |
| `CollapseNodes` | 将选中的节点折叠成一个 Collapse 节点或函数节点。 | `UAFTestsUtilities` (C++ 辅助) |

### 使用示例（蓝图描述）

一个典型的自动化测试蓝图流程可能如下：
1.  使用 `Create Asset` 节点，传入一个 `UFactory` 子类（如 `UAnimNextAnimGraphFactory`）和一个资产名称，创建一个临时的 `UUAFRigVMAsset`。
2.  使用 `Get Or Create Controller` 获取资产的图控制器。
3.  通过控制器或 `UAFTestsUtilities` 中的函数（需要通过 C++ 调用或封装），在默认图表中添加 `RigUnit` 节点、变量节点，并使用 `Add Link` 等函数连接它们的引脚，构建一个简单的动画逻辑图。
4.  调用 `Recompile VM` 节点，对资产进行编译。
5.  使用 `Get Compilation State` 检查是否编译成功。
6.  如果资产包含可执行的事件，可以使用 `Execute VM` 节点来触发执行，并验证输出是否符合预期。

## C++ 用法

对于更底层或复杂的测试场景，可以直接在 C++ 自动化测试中调用插件提供的工具函数。

### 头文件引入

```cpp
// 使用蓝图库功能
#include “UAFTestBlueprintLibrary.h”

// 使用 C++ 测试工具函数
#include “UAFTestsUtilities.h”
```

### 基本用法

以下示例演示了如何使用 `UAFTestsUtilities` 函数程序化构建一个简单的测试图表。
（来源：基于 `UAFTestsUtilities.h` 的 API 设计推断）

```cpp
#include “UAFTestsUtilities.h”
#include “RigVMModel/Nodes/RigVMUnitNode.h”

// 在自动化测试中
void FMyUAFTest::RunTest()
{
    // 1. 创建测试资产（通常使用插件提供的工厂或特定工厂类）
    UFactory* AnimGraphFactory = NewObject<UAnimNextAnimGraphFactory>();
    UObject* AssetObject = UAFTestsUtilities::CreateFactoryObject(AnimGraphFactory, UAnimNextAnimGraph::StaticClass(), TEXT(“TestAsset”));
    UUAFRigVMAsset* TestAsset = Cast<UUAFRigVMAsset>(AssetObject);

    // 2. 获取默认图表
    URigVMGraph* DefaultModel = TestAsset->GetEditorData()->GetDefaultModel();

    // 3. 添加一个 RigUnit 节点到图表
    TArray<UEdGraphPin*> FromPins; // 通常从之前添加的节点获取输出引脚
    FVector2f NodeLocation(100.f, 200.f);
    // 添加一个名为 “Interpolate” 的单位节点，其内部使用 FAnimNode_Interpolate 结构体
    UEdGraphNode* InterpNode = UAFTestsUtilities::AddUnitNode(DefaultModel,
        TEXT(“/Script/AnimGraphRuntime.AnimNode_Interpolate”),
        FromPins,
        NodeLocation);

    // 4. 添加一个变量
    FAnimNextParamType FloatType;
    FloatType.CPPType = TEXT(“float”);
    UAnimNextVariableEntry* AlphaVar = UAFTestsUtilities::AddVariable(TestAsset, FloatType, TEXT(“Alpha”), TEXT(“0.5”));

    // 5. 添加一个变量读节点
    FVector2f VarNodeLocation(0.f, 200.f);
    TArray<UEdGraphPin*> NoFromPins;
    UEdGraphNode* VarReadNode = UAFTestsUtilities::AddVariableNode(DefaultModel, TestAsset, TEXT(“Alpha”), FloatType,
        FAnimNextSchemaAction_Variable::EVariableAccessorChoice::Read,
        NoFromPins, VarNodeLocation);

    // 6. 连接变量读节点的输出到插值节点的输入
    // 假设 VarReadNode 有一个名为 “Value” 的输出引脚，InterpNode 有一个名为 “Alpha” 的输入引脚
    FString OutputPinPath = VarReadNode->GetName() + TEXT(“.Value”);
    FString InputPinPath = InterpNode->GetName() + TEXT(“.Alpha”);
    UAFTestsUtilities::AddLink(TestAsset, OutputPinPath, InputPinPath);
}
```

### 进阶用法

更复杂的测试会结合使用 `UUAFTestBlueprintLibrary` 中的 C++ 静态函数（它们是蓝图节点的底层实现）和 `UAFTestsUtilities` 的图编辑工具，来模拟完整的资产编译与执行流程。

```cpp
#include “UAFTestBlueprintLibrary.h”
#include “UAFTestsUtilities.h”
#include “AnimNextAsset.h” // 假设资产类型

void FMyAdvancedUAFTest::RunTest()
{
    // ... 创建资产、构建图表（如上所述）...

    // 编译资产
    UUAFTestBlueprintLibrary::RecompileVM(TestAsset);
    EAnimNextRigVMAssetState State = UUAFTestBlueprintLibrary::GetCompilationState(TestAsset);
    TestEqual(TEXT(“Asset should compile successfully”), State, EAnimNextRigVMAssetState::Compiled);

    // 假设图表构建了一个可执行的事件 “Event”
    // 执行 VM 并检查结果
    bool bSuccess = false;
    TArray<FString> OutMessages;
    UUAFTestBlueprintLibrary::ExecuteVM(TestAsset->GetSystem(), FName(“Event”), bSuccess, OutMessages);
    TestTrue(TEXT(“VM execution should succeed”), bSuccess);

    // 可以检查 OutMessages 来验证特定日志或调试信息
    // TestTrue(TEXT(“Expected log message found”), OutMessages.Contains(TEXT(“Log: Interpolation complete”)));
}
```

## Demo 示例

一个最小可编译的 C++ 测试示例，演示如何创建资产并编译。

```cpp
// MyUAFTest.cpp
#include “UAFTestBlueprintLibrary.h”
#include “UAFTestsUtilities.h”
#include “AutomationTest.h”
#include “UAFSystem.h” // 假设 UUAFSystem 是包含 VM 的资产类

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFCompilationTest,
    “MyPlugin.UAF.Compilation”,
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FUAFCompilationTest::RunTest(const FString& Parameters)
{
    // 1. 创建资产
    // 注意：需要提供一个有效的、指向 UUAFRigVMAsset 子类的工厂类。
    // 这里假设有一个 UMyUAFAssetFactory 存在。
    UUAFRigVMAsset* TestAsset = UUAFTestBlueprintLibrary::CreateAsset(UMyUAFAssetFactory::StaticClass(), FName(“TestAssetForCompilation”));
    if (!TestAsset)
    {
        AddError(TEXT(“Failed to create test asset.”));
        return false;
    }

    // 2. 获取编译前状态
    EAnimNextRigVMAssetState InitialState = UUAFTestBlueprintLibrary::GetCompilationState(TestAsset);
    TestEqual(TEXT(“Initial state should be Invalid or Not Compiled”), InitialState, EAnimNextRigVMAssetState::Invalid);

    // 3. 请求编译
    UUAFTestBlueprintLibrary::RecompileVM(TestAsset);

    // 4. 验证编译后状态
    // 注意：编译可能是异步的，实际测试中可能需要等待或使用 Tick。
    EAnimNextRigVMAssetState CompiledState = UUAFTestBlueprintLibrary::GetCompilationState(TestAsset);
    if (CompiledState != EAnimNextRigVMAssetState::Compiled)
    {
        AddError(FString::Printf(TEXT(“Compilation failed. Final state: %d”), static_cast<int32>(CompiledState)));
        return false;
    }

    // 5. 清理（如果资产是临时的）
    TestAsset->MarkAsGarbage();

    return true;
}
```

## 模块依赖

要使用 UAFTestSuites 插件的功能，您的模块可能需要依赖以下模块（具体取决于您使用了哪个部分）：

| 模块 | 用途 |
|---|---|
| `UAFCQTestSuite` | 包含蓝图测试库和 C++ 测试工具的主要模块。 |
| `UAFAnimGraphTestSuite` | 包含针对 AnimGraph 特定功能的测试。 |
| `UAFAnimNodeTestData` | 可能包含用于动画节点测试的数据资产或结构体。 |
| `UAFTestSuite` | 包含更通用或基础的 UAF 测试。 |
| `AnimNextRuntime` | UAF 框架的运行时模块，是测试对象的核心。 |
| `AnimNextEditor` | UAF 框架的编辑器模块，用于创建和编辑资产。 |
| `RigVM` | 虚拟机系统，是 UAF 执行逻辑的基础。 |
| `UncookedOnly` | 提供在编辑器中访问未编译资产数据的工具，被测试库广泛使用。 |

*注意：此插件专为测试设计，通常不应被游戏运行时模块依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，提升跨编译器（MSVC/Clang）兼容性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了日志格式化字符串中，32位与64位参数不匹配的问题。 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复了当 UAF traits 使用 `FBindableXxx` 类型时可能发生的序列化问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 `UE_LOG` 迁移为使用格式化宏 `UE_LOGF`。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 `GetComponent` 函数重命名为 `GetOrAddComponent`，以准确反映其“获取或创建”的功能。 |

### 维护评价

UAFTestSuites 是一个 **活跃维护中** 的实验性插件。
- **年龄与状态**：插件创建于 2026 年初，非常新，并且从 .uplugin 标记来看仍处于 **实验性** 阶段 (`IsExperimentalVersion: true`)。
- **更新频率**：在近 1 个月内有多次提交，主要集中在 **编译警告修复** 和 **代码质量改进**（如函数重命名以匹配功能）。这表明它正在被积极用于测试最新的 UAF 框架开发，并跟随主分支进行维护。
- **功能与定位**：其核心功能（提供测试辅助 API）是稳定且专用的。作为测试套件，其稳定性对于保障 UAF 框架本身的质量至关重要。
- **已知限制**：作为实验性插件，其 API 可能在未来版本中发生 breaking changes。它是为引擎内部测试设计的，不建议作为运行时依赖项。
- **推荐使用**：如果你是 UAF 框架的开发者或贡献者，**强烈推荐** 使用此插件来编写自动化测试。对于最终用户或项目开发者，除非你需要深入调试或验证 UAF 的特定行为，否则通常无需直接使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- 官方文档：无
- 测试用例：插件本身即为测试套件，测试代码位于其 `Source` 目录下的各模块中。