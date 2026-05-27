# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF 测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

这是一个为 Unreal Animation Framework (UAF) 提供自动化测试的实验性插件。它包含一系列测试用例（CQ 测试和动画图测试等）和测试工具库，用于验证 UAF 系统的各种功能，包括：

- RigVM 资产的编译和执行
- 动画图和动画节点的创建与操作
- 资产数据工厂和对象注册
- 函数库、变量、共享变量的管理

这个插件本身不提供用户可见的功能，而是作为开发和维护 UAF 核心系统的质量保障工具存在。

## 使用场景

- **UAF 核心开发者**：需要编写和运行自动化测试来验证 UAF 功能的正确性和回归问题。
- **动画系统开发者**：在修改 UAF 代码后，运行此测试套件确保没有破坏现有功能。
- **CI/CD 流程**：在持续集成系统中自动执行这些测试，确保代码质量。

## 蓝图用法

这个插件主要提供 C++ 测试工具，但包含一个蓝图函数库 `UUAFTestBlueprintLibrary`，用于在蓝图测试中操作 UAF 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileVM` | 重新编译指定的 UAF RigVM 资产 | `UUAFTestBlueprintLibrary` |
| `GetModel` | 获取资产的 RigVM 图模型 | `UUAFTestBlueprintLibrary` |
| `GetDefaultModel` | 获取资产的默认 RigVM 图模型 | `UUAFTestBlueprintLibrary` |
| `GetAllModels` | 获取资产的所有 RigVM 图模型 | `UUAFTestBlueprintLibrary` |
| `GetLocalFunctionLibrary` | 获取资产的本地函数库 | `UUAFTestBlueprintLibrary` |
| `GetOrCreateLocalFunctionLibrary` | 获取或创建资产的本地函数库 | `UUAFTestBlueprintLibrary` |
| `AddModel` | 向资产添加新的 RigVM 图 | `UUAFTestBlueprintLibrary` |
| `RemoveModel` | 从资产中移除指定名称的 RigVM 图 | `UUAFTestBlueprintLibrary` |
| `GetController` | 获取指定图的 RigVM 控制器 | `UUAFTestBlueprintLibrary` |
| `GetControllerByName` | 根据图名称获取 RigVM 控制器 | `UUAFTestBlueprintLibrary` |
| `GetOrCreateController` | 获取或创建指定图的 RigVM 控制器 | `UUAFTestBlueprintLibrary` |
| `ExecuteVM` | 执行 UAF 系统的虚拟机事件 | `UUAFTestBlueprintLibrary` |
| `CreateAsset` | 使用指定工厂类创建 UAF 资产 | `UUAFTestBlueprintLibrary` |
| `GetCompilationState` | 获取资产的编译状态 | `UUAFTestBlueprintLibrary` |

### 使用示例（蓝图描述）

要创建一个蓝图测试图表来测试 UAF 资产的编译和执行：

1. 从 `UUAFTestBlueprintLibrary` 调用 `CreateAsset` 节点，传入 UAF 资产工厂类（如 `UUAFSystemFactory`）和资产名称，创建一个临时的 UAF 资产。
2. 使用 `GetController` 或 `GetOrCreateController` 获取资产的控制器。
3. 通过控制器节点添加所需的图节点、引脚和连接。
4. 调用 `RecompileVM` 编译资产。
5. 使用 `GetCompilationState` 检查编译是否成功。
6. 调用 `ExecuteVM` 执行资产中的特定事件，并检查执行结果和输出消息。

## C++ 用法

### 头文件引入

```cpp
#include "UAFTestsUtilities.h"
#include "UAFTestBlueprintLibrary.h"
```

### 基本用法

从测试用例中提取的创建工厂对象和添加单元节点的示例（来自 `UAFTestsUtilities.h` 的注释和用法）：

```cpp
// 创建一个工厂对象
UFactory* Factory = GetDefault<URigVMGraphFactory>(); // 假设的工厂类
UClass* AssetClass = URigVMGraph::StaticClass();
UObject* CreatedObject = UAFTestsUtilities::CreateFactoryObject(Factory, AssetClass, TEXT("TestAsset"));

// 向动画图添加一个 RigUnit 节点
UEdGraph* Graph = ...; // 获取或创建的动画图
TArray<UEdGraphPin*> FromPins;
FVector2f Location(100.0f, 100.0f);
UEdGraphNode* NewNode = UAFTestsUtilities::AddUnitNode(Graph, TEXT("/Script/MyModule.MyRigUnit"), FromPins, Location);
```

### 进阶用法

组合使用测试工具库和蓝图函数库来创建复杂的测试场景：

```cpp
// 创建一个 UAF 资产并操作其函数库
UUAFRigVMAsset* TestAsset = UUAFTestBlueprintLibrary::CreateAsset(UUAFSystemFactory::StaticClass(), FName("TestSystem"));
URigVMGraph* Model = UUAFTestBlueprintLibrary::GetModel(TestAsset);
URigVMController* Controller = UUAFTestBlueprintLibrary::GetController(TestAsset, Model);

// 添加一个函数节点
URigVMLibraryNode* FunctionNode = UAFTestsUtilities::AddFunctionNode(TestAsset, TEXT("MyTestFunction"));

// 为函数添加输入引脚
URigVMPin* InputPin = UAFTestsUtilities::AddPin(TestAsset, FunctionNode, ERigVMPinDirection::Input, TEXT("bCondition"), TEXT("bool"));

// 编译并执行
UUAFTestBlueprintLibrary::RecompileVM(TestAsset);
bool bSuccess = false;
TArray<FString> Messages;
UUAFTestBlueprintLibrary::ExecuteVM(Cast<UUAFSystem>(TestAsset), FName("ExecuteEvent"), bSuccess, Messages);
```

## Demo 示例

以下是一个最小的 C++ 测试类示例，用于验证 UAF 资产的编译：

```cpp
// MyUAFTest.h
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"

class FMyUAFCompilationTest : public FAutomationTestBase
{
public:
    FMyUAFCompilationTest(const FString& InName, const bool bInComplexTest)
        : FAutomationTestBase(InName, bInComplexTest)
    {
    }

    virtual uint32 GetTestFlags() const override { return EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter; }
    virtual bool IsStressTest() const { return false; }
    virtual void GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const override
    {
        OutBeautifiedNames.Add(TEXT("UAF Compilation Test"));
        OutTestCommands.Add(FString());
    }
    virtual bool RunTest(const FString& Parameters) override;
};
```

```cpp
// MyUAFTest.cpp
#include "MyUAFTest.h"
#include "UAFTestBlueprintLibrary.h"
#include "UAFSystemFactory.h"

bool FMyUAFCompilationTest::RunTest(const FString& Parameters)
{
    // 1. 创建一个 UAF 资产
    UUAFRigVMAsset* TestAsset = UUAFTestBlueprintLibrary::CreateAsset(UUAFSystemFactory::StaticClass(), FName("TestAsset"));
    if (!TestAsset)
    {
        AddError(TEXT("Failed to create test asset."));
        return false;
    }

    // 2. 编译资产
    UUAFTestBlueprintLibrary::RecompileVM(TestAsset);

    // 3. 检查编译状态
    EAnimNextRigVMAssetState State = UUAFTestBlueprintLibrary::GetCompilationState(TestAsset);
    if (State != EAnimNextRigVMAssetState::CompiledSuccessfully)
    {
        AddError(FString::Printf(TEXT("Asset compilation failed with state: %d"), static_cast<int32>(State)));
        return false;
    }

    AddInfo(TEXT("UAF asset compiled successfully."));
    return true;
}
```

## 模块依赖

由于这是一个测试插件，它依赖于 UAF 核心模块和其他测试相关模块。要使用此插件中的测试工具，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 动画系统的核心基础 |
| `RigVM` | RigVM 虚拟机和图系统 |
| `AnimNextRuntime` | AnimNext 运行时系统 |
| `UnrealEd` | 编辑器功能（用于创建工厂对象等） |
| `AutomationController` | 自动化测试框架 |

此外，插件内部模块之间也有依赖关系，例如 `UAFCQTestSuite` 模块依赖 `UAFTestSuite` 模块提供的基础测试设施。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 之间兼容 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位格式说明符在 64 位参数时的使用，反之亦然 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 FBindableXxx 绑定在 UAF 特性中使用时的序列化问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将 GetComponent 重命名为 GetOrAddComponent 以匹配实际功能 |

### 维护评价

这是一个**活跃维护**的实验性插件，主要用途是为 UAF 系统提供测试保障。

- **创建时间**：2026 年 2 月，是一个相对较新的插件。
- **最近更新**：最近一次更新在 2026 年 5 月，更新频率稳定，主要关注代码质量、跨平台兼容性和核心功能修复。
- **维护状态**：持续活跃维护中，没有废弃迹象。
- **已知问题**：作为实验性插件，其 API 和功能可能随 UAF 系统的发展而变化。
- **推荐使用**：仅推荐用于 UAF 系统的开发和测试，不建议在最终产品中依赖此插件的测试工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFCQTestSuite)