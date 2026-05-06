# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF 测试工具 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFTests) | |

## 用途

UAF Tests 是 UAF（Animation Future，动画未来）系统的**自动化测试辅助插件**，提供一组 C++ 工具函数，用于在编辑器中快速创建和设置 UAF 资产（如 AnimNext 资产）、图节点、变量、引脚等，从而便于编写**单元测试**和**集成测试**。它不提供运行时功能，仅作用于开发测试场景。

该插件解决了 UAF 系统测试时**重复编写资产创建逻辑**的问题，将常用的测试步骤封装为静态函数，降低测试编写门槛。

## 使用场景

- 你在为 UAF（AnimNext）系统编写自动化测试用例 → 使用本插件的工具函数构建测试环境。
- 你需要验证 UAF 图编译、节点连接、变量访问等功能的正确性 → 使用 `AddUnitNode`、`AddVariableNode` 等函数。
- 你希望对 UAF 资产进行参数化测试 → 使用 `CreateFactoryObject` 创建特定类型的资产实例。

## 蓝图用法

本插件所有功能均为 C++ 静态函数，**未暴露蓝图节点**，无法在蓝图中调用。

## C++ 用法

### 头文件引入

```cpp
#include "UAFTestsUtilities.h"
```

### 基本用法

以下示例来自 `UAFTestsUtilities.h` 的文档注释，展示了如何创建资产、添加节点并进行引脚连接。

```cpp
// 引入测试工具命名空间
using namespace UAFTestsUtilities;

// 1. 使用工厂创建 UAnimNextRigVMAsset 实例
UAnimNextRigVMAsset* AnimNextAsset = Cast<UAnimNextRigVMAsset>(
    UAFTestsUtilities::CreateFactoryObject(
        NewObject<UAnimNextRigVMAssetFactory>(),
        UAnimNextRigVMAsset::StaticClass(),
        TEXT("/Temp/TestAsset")
    )
);
check(AnimNextAsset);

// 2. 获取默认入口图（通常为 "Graph"）
UEdGraph* EntryGraph = AnimNextAsset->GetDefaultEntryGraph();

// 3. 添加一个 RigUnit 节点并连接输出引脚
TArray<UEdGraphPin*> FromPins;
UEdGraphNode* NewNode = UAFTestsUtilities::AddUnitNode(
    EntryGraph,
    TEXT("RigVM::Execute"),       // 脚本结构路径
    FromPins,
    FVector2f(100.0f, 100.0f)
);
check(NewNode);

// 4. 添加一个函数节点
URigVMLibraryNode* FuncNode = UAFTestsUtilities::AddFunctionNode(
    AnimNextAsset,
    TEXT("MyFunction")
);
check(FuncNode);

// 5. 添加一个变量 (整数类型)
FAnimNextParamType IntType; // 假设已设置
IntType.Type = EPropertyBagPropertyType::Int;
UAnimNextVariableEntry* VarEntry = UAFTestsUtilities::AddVariable(
    AnimNextAsset,
    IntType,
    TEXT("MyIntVar"),
    TEXT("0")
);
check(VarEntry);
```

来源：`Source/UAFTests/Public/UAFTestsUtilities.h`

### 进阶用法

组合多个工具函数，构建完整的图测试场景。

```cpp
// 测试变量读取节点
// 1. 创建资产并获取图
UAnimNextRigVMAsset* Asset = /* 同上创建 */;
UEdGraph* Graph = Asset->GetDefaultEntryGraph();

// 2. 添加变量到资产
FAnimNextParamType FloatType;
FloatType.Type = EPropertyBagPropertyType::Float;
UAnimNextVariableEntry* Var = UAFTestsUtilities::AddVariable(Asset, FloatType, TEXT("Speed"), TEXT("0.5"));

// 3. 在图内添加变量获取节点
TArray<UEdGraphPin*> DummyFromPins;
UEdGraphNode* VarNode = UAFTestsUtilities::AddVariableNode(
    Graph,
    Asset,                                      // 源对象
    TEXT("Speed"),
    FloatType,
    FAnimNextSchemaAction_Variable::EVariableAccessorChoice::Read,
    DummyFromPins,
    FVector2f(200.0f, 200.0f)
);
check(VarNode);

// 4. 添加算术节点并连接变量输出
TArray<UEdGraphPin*> VarOutPins = VarNode->Pins.FilterByPredicate([](UEdGraphPin* Pin) {
    return Pin->Direction == EGPD_Output && Pin->GetFName() == TEXT("Value");
});
UEdGraphNode* AddNode = UAFTestsUtilities::AddUnitNode(
    Graph,
    TEXT("RigVMFunction_MathFloatAdd"),
    VarOutPins,
    FVector2f(400.0f, 200.0f)
);
check(AddNode);
```

## Demo 示例

以下是一个完整的 C++ 自动化测试案例，使用本插件工具函数。假设你的项目已启用 UAFTests 插件。

**MyUAFTest.cpp**

```cpp
#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "UAFTestsUtilities.h"
#include "AnimNextRigVMAsset.h"
#include "AnimNextRigVMAssetEditorData.h"
#include "Factories/AnimNext.h" // 工厂头文件

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFBasicGraphTest, "UAF.BasicGraphTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FUAFBasicGraphTest::RunTest(const FString& Parameters)
{
    using namespace UAFTestsUtilities;

    // 创建临时资产
    UAnimNextRigVMAsset* Asset = Cast<UAnimNextRigVMAsset>(
        UAFTestsUtilities::CreateFactoryObject(
            NewObject<UAnimNextRigVMAssetFactory>(),
            UAnimNextRigVMAsset::StaticClass(),
            TEXT("/Temp/GraphTestAsset")
        )
    );
    if (!Asset) { AddError("Failed to create asset"); return false; }

    // 添加变量
    FAnimNextParamType IntType;
    IntType.Type = EPropertyBagPropertyType::Int;
    UAnimNextVariableEntry* Var = UAFTestsUtilities::AddVariable(Asset, IntType, TEXT("Count"), TEXT("10"));
    if (!Var) { AddError("Failed to add variable"); return false; }

    // 添加函数节点
    URigVMLibraryNode* FuncNode = UAFTestsUtilities::AddFunctionNode(Asset, TEXT("TestFunc"));
    if (!FuncNode) { AddError("Failed to add function"); return false; }

    // 添加单位节点并连接（此处简单验证图结构无崩溃）
    UEdGraph* Graph = Asset->GetDefaultEntryGraph();
    TArray<UEdGraphPin*> EmptyPins;
    UEdGraphNode* UnitNode = UAFTestsUtilities::AddUnitNode(Graph, TEXT("RigVMFunction_MathIntAdd"), EmptyPins, FVector2f(100,100));
    if (!UnitNode) { AddError("Failed to add unit node"); return false; }

    return true;
}
```

编译并运行该测试，确认测试通过。

## 模块依赖

使用 UAFTests 插件时，你的模块需要在 `Build.cs` 中添加以下依赖（标准 Core/Engine 等忽略）：

| 模块 | 用途 |
|---|---|
| `Workspace` | 工作空间管理，提供资产包的上下文 |
| `UAF` | UAF 核心模块，包含 AnimNext 运行时与资产基础类 |
| `UAFAnimGraph` | UAF 动画图编辑器模块，提供图操作功能 |
| `UAFStateTree` | UAF 状态树模块，可能用于状态机测试 |
| `RigVM` | RigVM 虚拟机模块，提供 RigUnit 和图节点执行 |

示例 `Build.cs`:

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Workspace",
    "UAF",
    "UAFAnimGraph",
    "UAFStateTree",
    "RigVM"
});
```

## 维护状态

### 近期更新

- 2025-08-27 `a9351826` — Move UAF Test plugin out of Restricted/NotForLicensees directory （仅迁移，无功能更新）

### 维护评价

- **创建时间**：2025-08-27，距今不足 1 年，属于全新插件。
- **最近更新**：仅一次迁移提交，无功能性改动，也未出现修复或扩展。
- **活跃度**：不活跃。自创建后未提交任何实质性代码变更。
- **风险**：**实验性标记**（IsExperimentalVersion=true），且默认不启用。不建议用于生产环境。该插件可能随着 UAF 系统演进而废弃或重构。
- **推荐程度**：仅推荐 UAF 相关测试开发者使用，且需自担风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFTests)
- [测试工具头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/UAF/UAFTests/Source/UAFTests/Public/UAFTestsUtilities.h)
- [UAF 主插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF)