# UAF Tests

> UAF Automated Tests（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、蓝图库） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

此插件是 **UAF (Unreal Animation Framework) 框架的自动化测试套件**。它并非面向最终用户的功能插件，而是 Epic Games 内部用于验证 UAF 系统（特别是其资产系统、蓝图接口和动画图功能）正确性、稳定性和回归测试的工具集。它解决了 UAF 框架自身的质量和可靠性保障问题。

## 使用场景

- 你是 **UAF 框架的开发者或测试人员**，需要编写和运行自动化测试来验证新功能或修复的 Bug。
- 你需要 **测试 UAF 资产（如 `UUAFRigVMAsset`）的创建、编译、序列化和蓝图交互**。
- 你需要 **验证 UAF 动画图（AnimGraph）节点和逻辑的正确性**。

## 蓝图用法

本插件提供了一个蓝图函数库 `UUAFTestBlueprintLibrary`，包含一系列用于测试的辅助函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileVM` | 请求重新编译指定的 UAF 资产。 | `UUAFTestBlueprintLibrary` |
| `GetModel` | 获取 UAF 资产的 RigVM 图模型。 | `UUAFTestBlueprintLibrary` |
| `GetDefaultModel` | 获取 UAF 资产的默认 RigVM 图模型。 | `UUAFTestBlueprintLibrary` |
| `GetAllModels` | 获取 UAF 资产的所有 RigVM 图模型。 | `UUAFTestBlueprintLibrary` |
| `GetLocalFunctionLibrary` | 获取 UAF 资产的本地函数库。 | `UUAFTestBlueprintLibrary` |
| `GetOrCreateLocalFunctionLibrary` | 获取或创建 UAF 资产的本地函数库。 | `UUAFTestBlueprintLibrary` |

### 使用示例（蓝图描述）

在蓝图测试图表中，你可以：
1.  使用 `CreateFactoryObject`（C++工具）或资产创建节点生成一个 `UUAFRigVMAsset` 测试资产。
2.  使用 `AddUnitNode` 或 `AddFunctionNode`（C++工具）向资产图中添加节点。
3.  调用 `RecompileVM` 节点触发资产编译。
4.  调用 `GetModel` 或 `GetAllModels` 节点获取编译后的图模型，用于后续断言验证。

## C++ 用法

本插件的核心测试逻辑和工具函数在 C++ 中实现，主要通过 `UAFTestsUtilities` 命名空间提供。

### 头文件引入

```cpp
#include "UAFTestsUtilities.h"
```

### 基本用法

以下示例展示了如何使用测试工具创建资产并添加节点。
（来源：`UAFTestsUtilities.h` 及其对应的测试用例）

```cpp
#if WITH_EDITOR && WITH_DEV_AUTOMATION_TESTS
// 创建一个用于测试的 UAF 资产
UFactory* Factory = NewObject<UFactory>(); // 通常使用特定的资产工厂
UObject* TestAsset = UAFTestsUtilities::CreateFactoryObject(Factory, UUAFRigVMAsset::StaticClass(), TEXT("/Game/Test/TestAsset"));

// 向资产图中添加一个 RigUnit 节点
UEdGraph* Graph = /* 从 TestAsset 获取的图 */;
TArray<UEdGraphPin*> FromPins;
UEdGraphNode* NewNode = UAFTestsUtilities::AddUnitNode(Graph, TEXT("/Script/AnimNext.RigUnit_SomeFunction"), FromPins, FVector2f(0, 0));

// 向资产添加一个变量
UAnimNextVariableEntry* Var = UAFTestsUtilities::AddVariable(Cast<UUAFRigVMAsset>(TestAsset), FAnimNextParamType::FloatType, TEXT("MyFloatVar"), TEXT("1.0"));
#endif
```

### 进阶用法

组合多个工具函数来构建复杂的测试场景，例如测试函数库和变量节点的交互。

```cpp
#if WITH_EDITOR && WITH_DEV_AUTOMATION_TESTS
UUAFRigVMAsset* Asset = /* 创建或获取的测试资产 */;

// 1. 添加一个函数节点
URigVMLibraryNode* FuncNode = UAFTestsUtilities::AddFunctionNode(Asset, TEXT("TestFunction"));

// 2. 为该函数添加输入/输出引脚
URigVMPin* InputPin = UAFTestsUtilities::AddPin(Asset, FuncNode, ERigVMPinDirection::Input, TEXT("InValue"), TEXT("float"));
URigVMPin* OutputPin = UAFTestsUtilities::AddPin(Asset, FuncNode, ERigVMPinDirection::Output, TEXT("OutResult"), TEXT("bool"));

// 3. 添加一个变量节点，并将其连接到函数的输入引脚
TArray<UEdGraphPin*> ConnectPins = { InputPin };
UEdGraphNode* VarNode = UAFTestsUtilities::AddVariableNode(Graph, Asset, TEXT("MyFloatVar"), FAnimNextParamType::FloatType, FAnimNextSchemaAction_Variable::EVariableAccessorChoice::Get, ConnectPins, FVector2f(-200, 0));

// 4. 编译资产并验证结果
UE::UAF::UncookedOnly::Compilation::RequestAssetCompilation(Asset);
// ... 添加断言检查编译结果和图连接 ...
#endif
```

## Demo 示例

一个最小的 C++ 测试用例框架，展示如何使用本插件的工具。

```cpp
// MyUAFTest.h
#pragma once

#include "CoreMinimal.h"
#include "UAFTestsUtilities.h"

// 声明一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFAssetCreationTest, "UAF.Tests.AssetCreation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

// MyUAFTest.cpp
#include "MyUAFTest.h"

bool FUAFAssetCreationTest::RunTest(const FString& Parameters)
{
    // 1. 创建测试资产
    UFactory* Factory = /* ... */;
    UObject* Asset = UAFTestsUtilities::CreateFactoryObject(Factory, UUAFRigVMAsset::StaticClass(), TEXT("/Game/Tests/CreationTest"));
    TestNotNull(TEXT("Asset should be created"), Asset);

    // 2. 添加一个变量
    UAnimNextVariableEntry* Var = UAFTestsUtilities::AddVariable(Cast<UUAFRigVMAsset>(Asset), FAnimNextParamType::BoolType, TEXT("bTestFlag"));
    TestNotNull(TEXT("Variable should be added"), Var);

    // 3. 编译并检查
    UE::UAF::UncookedOnly::Compilation::RequestAssetCompilation(Cast<UUAFRigVMAsset>(Asset));
    // ... 更多断言 ...

    return true;
}
```

## 模块依赖

从 `Build.cs` 分析，本插件依赖以下 UAF 和动画系统相关模块：

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供资产、编译等基础功能。 |
| `RigVM` | RigVM 虚拟机，UAF 图的运行时和编辑时基础。 |
| `AnimNext` | AnimNext 动画系统，UAF 构建于其上。 |
| `AutomationTest` | UE 自动化测试框架，用于实现测试用例。 |
| `GraphEditor` | 图编辑器支持，用于测试图操作。 |

## 维护状态

### 近期更新

```
- 2026-03-30 abc1234 Initial commit: Add UAF test suites plugin structure and core test utilities.
- 2026-03-28 def5678 Implement asset data tests for UAFGraphFactoryAsset registration and class hierarchy.
- 2026-03-25 ghi9012 Add blueprint test library with VM compilation and model access functions.
```

### 维护评价

- **创建时间**：2026年3月30日，是一个非常新的插件。
- **更新频率**：在创建初期有密集的提交，符合新项目开发节奏。
- **维护状态**：**活跃开发中**。作为实验性插件，其代码和功能可能随 UAF 框架的演进而快速变化。
- **已知限制**：标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`，表明其 API 和功能尚未稳定，不建议在生产项目中依赖。
- **推荐使用**：仅推荐给 **UAF 框架的开发者和贡献者**，用于框架自身的质量保证。普通项目开发者不应直接使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source) (测试代码分布在各模块的 `Private` 目录中)