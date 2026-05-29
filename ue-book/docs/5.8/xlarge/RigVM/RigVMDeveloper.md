# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | RigVM 可视化编程 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (Runtime), `RigVMEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM) | |

## 用途
RigVM 是一个**视觉编程语言的前端（图形编辑器）和后端（编译器与虚拟机）**。它提供了一套完整的框架，用于创建、编辑、编译和执行基于节点的图形化程序（RigVM Graphs）。
这个插件解决了以下核心问题：
1.  **视觉逻辑实现**：允许开发者或技术美术通过拖拽节点和连接引脚来构建复杂的逻辑和程序，而无需编写代码。这在动画控制（ControlRig）、程序化内容生成（PCG）等领域至关重要。
2.  **高效的运行时**：编译后的 RigVM 图形被转化为紧凑的字节码，由一个轻量级的虚拟机（`URigVMHost`）执行，保证了运行时的高性能。
3.  **可扩展性**：它是一个通用的框架，任何系统（如 ControlRig、PCG）都可以实现其特定的资产接口（`IRigVMEditorAssetInterface`）和模式（`URigVMSchema`），从而复用 RigVM 的整个编译、执行和编辑基础设施。

简单来说，如果你需要在 UE 中创建一个“蓝图式”的、但专注于特定领域（如骨骼操控、植被生成）的视觉脚本系统，RigVM 就是底层的引擎。

## 使用场景
-   你在开发一个 **ControlRig**（动画控制工具） → 使用 RigVM 来定义和执行骨骼修改逻辑。
-   你在制作一个 **PCG（程序化内容生成）** 框架 → 使用 RigVM 来构建生成场景的规则图。
-   你需要为游戏逻辑创建一个**面向策划的视觉编辑器** → 基于 RigVM 构建自定义的图表资产和编辑器。
-   你需要一个**可序列化、可调试、高性能**的图形化脚本运行时 → 使用 RigVM 的编译器和虚拟机。

## 蓝图用法
RigVM 主要通过其 C++ API 和编辑器界面进行操作。在蓝图中，你可以通过获取 `URigVMBlueprint` 或 `URigVMGraph` 实例来调用一些高级管理函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Model` | 获取关联的 RigVM 图形对象 | `URigVMBlueprint` |
| `Get All Models` | 获取资产中的所有 RigVM 图形 | `URigVMBlueprint` |
| `Get Controller` | 获取用于修改指定图形的控制器 | `URigVMBlueprint` |
| `Recompile VM` | 手动触发 VM 重新编译 | `URigVMBlueprint` |
| `Add Model` | 向资产中添加一个新的图形 | `URigVMBlueprint` |
| `Remove Model` | 从资产中移除一个图形 | `URigVMBlueprint` |
| `Get Nodes` | 获取图形中的所有节点 | `URigVMGraph` |
| `Find Node By Name` | 按名称查找节点 | `URigVMGraph` |
| `Get Functions` | 获取函数库中的所有函数 | `URigVMFunctionLibrary` |
| `Find Function` | 按名称查找函数 | `URigVMFunctionLibrary` |

### 使用示例（蓝图描述）
在蓝图中，通常先通过 `GetRigVMBlueprint()` 或类似方法获取你的 RigVM 资产实例，然后：
1.  调用 `GetDefaultModel()` 获取主图形。
2.  用 `GetController()` 获取该图形的控制器。
3.  使用控制器的函数（如 `AddUnitNode`, `AddLink`）来程序化地构建或修改图形。
4.  最后调用 `RecompileVM()` 使更改生效。

## C++ 用法
RigVM 的真正强大之处在于其 C++ API。开发者主要使用以下组件：
-   `URigVMGraph`, `URigVMNode`, `URigVMPin`, `URigVMLink`: 表示图形模型。
-   `URigVMController`: 对图形进行修改的唯一权威接口（添加/删除节点、连接引脚等）。
-   `FRigVMParserAST`: 将图形模型解析为抽象语法树。
-   `URigVMCompiler`: 将 AST 编译为 `URigVM` 的字节码。
-   `URigVMHost`: 运行时执行字节码的虚拟机。

### 头文件引入
```cpp
#include “RigVMDeveloper/RigVMGraph.h”
#include “RigVMDeveloper/RigVMController.h”
#include “RigVMDeveloper/RigVMCompiler.h”
#include “RigVM/RigVM.h”
#include “RigVM/RigVMHost.h”
```

### 基本用法
以下是一个简化的流程，展示如何通过 C++ API 创建一个简单的图表并编译运行。
```cpp
// 假设我们有一个 URigVMGraph* Graph 和一个 URigVMController* Controller
// （通常从 URigVMBlueprint 获取）

// 1. 创建一个节点（例如，一个数学乘法单元）
FName UnitNodeName = Controller->AddUnitNode(
    FMath::Multiply::StaticStruct(), // 你自定义的 RIGVM_METHOD 结构体
    NAME_None,
    FVector2D(0, 0),
    TEXT(“Multiply”),
    true // bSetupUndoRedo
);

// 2. 创建变量节点（例如，一个浮点数变量）
FName VariableNodeName = Controller->AddVariableNode(
    TEXT(“MyFloat”),
    TEXT(“float”),
    nullptr,
    true,
    FVector2D(-200, 0),
    TEXT(“MyFloatNode”),
    true
);

// 3. 连接引脚（将变量的值连接到乘法节点的第一个输入）
URigVMPin* SourcePin = Graph->FindPin(FString::Printf(TEXT(“%s.Value”), *VariableNodeName));
URigVMPin* TargetPin = Graph->FindPin(FString::Printf(TEXT(“%s.A”), *UnitNodeName));
Controller->AddLink(SourcePin, TargetPin, true);

// 4. 编译图形
// 通常通过 IRigVMEditorAssetInterface::RecompileVM() 触发，这里展示内部步骤
FRigVMParserAST AST({Graph});
URigVM* CompiledVM = NewObject<URigVM>();
FRigVMCompileSettings Settings;
URigVMCompiler Compiler;
Compiler.Compile(&AST, CompiledVM, Settings);

// 5. 创建宿主并运行
URigVMHost* Host = NewObject<URigVMHost>();
Host->SetVM(CompiledVM);
Host->Execute(); // 需要设置好外部变量和上下文
```

### 进阶用法
更复杂的用法涉及**函数库**、**折叠节点**和**模板系统**。
-   **使用函数库**：通过 `URigVMFunctionLibrary` 管理可复用的图形函数，并通过 `URigVMFunctionReferenceNode` 在其他地方引用。
-   **模板与调度**：`URigVMTemplateNode` 和 `URigVMDispatchNode` 允许创建基于类型的多态节点，编译器会根据连接的类型自动解析到正确的函数实现。
-   **AST 操作**：`FRigVMParserAST` 不仅用于编译，还可以用于**语法分析**和**依赖关系检查**（例如，调用 `CanLink` 来检测两个引脚连接是否会产生循环）。
-   **调试与诊断**：通过 `FRigVMParserASTSettings` 配置 AST 解析的详细级别，并使用 `DumpText()` 或 `DumpDot()` 输出调试信息。

## Demo 示例
以下是一个最小可运行示例，演示如何通过 C++ 创建一个 RigVM 图形，编译并执行一个简单的操作（将一个浮点数乘以 2）。这个示例省略了完整的资产管理流程，专注于核心编译与执行。

**MyRigVMExample.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “RigVMDeveloper/RigVMGraph.h”
#include “RigVMDeveloper/RigVMController.h”

class FMyRigVMExample
{
public:
    void Run();

private:
    URigVMGraph* Graph = nullptr;
    URigVMController* Controller = nullptr;
};
```

**MyRigVMExample.cpp**
```cpp
#include “MyRigVMExample.h”
#include “RigVMDeveloper/RigVMCompiler.h”
#include “RigVM/RigVMHost.h”
#include “RigVM/RigVM.h”

// 假设我们有一个简单的数学单元结构体
USTRUCT()
struct FMyMultiplyUnit
{
    GENERATED_BODY()

    RIGVM_METHOD()
    virtual void Execute()
    {
        Result = A * 2.0f;
    }

    UPROPERTY(BlueprintReadWrite, Category = “Math”)
    float A = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = “Math”)
    float Result = 0.0f;
};

void FMyRigVMExample::Run()
{
    // 1. 创建图表和控制器
    Graph = NewObject<URigVMGraph>();
    Controller = NewObject<URigVMController>();
    Controller->SetGraph(Graph);

    // 2. 添加一个变量节点 (输入 A)
    Controller->AddVariableNode(
        TEXT(“InputA”),
        TEXT(“float”),
        nullptr,
        false, // false = getter (output pin)
        FVector2D(-300, 0),
        TEXT(“GetInputA”)
    );

    // 3. 添加一个单元节点 (执行乘法)
    Controller->AddUnitNode(
        FMyMultiplyUnit::StaticStruct(),
        NAME_None,
        FVector2D(0, 0),
        TEXT(“MultiplyBy2”)
    );

    // 4. 添加一个变量节点 (输出 Result)
    Controller->AddVariableNode(
        TEXT(“OutputResult”),
        TEXT(“float”),
        nullptr,
        true, // true = setter (input pin)
        FVector2D(300, 0),
        TEXT(“SetOutputResult”)
    );

    // 5. 连接引脚: InputA.Value -> MultiplyBy2.A
    URigVMPin* PinA = Graph->FindPin(TEXT(“GetInputA.Value”));
    URigVMPin* PinB = Graph->FindPin(TEXT(“MultiplyBy2.A”));
    Controller->AddLink(PinA, PinB, true);

    // 6. 连接引脚: MultiplyBy2.Result -> SetOutputResult.Value
    URigVMPin* PinC = Graph->FindPin(TEXT(“MultiplyBy2.Result”));
    URigVMPin* PinD = Graph->FindPin(TEXT(“SetOutputResult.Value”));
    Controller->AddLink(PinC, PinD, true);

    // 7. 编译
    FRigVMParserAST AST({Graph});
    URigVM* VM = NewObject<URigVM>();
    FRigVMCompileSettings Settings = FRigVMCompileSettings::Fast();
    URigVMCompiler Compiler;
    if (Compiler.Compile(&AST, VM, Settings))
    {
        UE_LOG(LogTemp, Log, TEXT(“Compilation Successful!”));
    }

    // 8. 准备宿主并设置变量
    URigVMHost* Host = NewObject<URigVMHost>();
    Host->SetVM(VM);

    // 创建变量容器 (假设我们的宿主有这些变量)
    FRigVMExternalVariable InputVar = FRigVMExternalVariable::Make(
        FGuid(), TEXT(“InputA”), TEXT(“float”), nullptr, false, false
    );
    FRigVMExternalVariable OutputVar = FRigVMExternalVariable::Make(
        FGuid(), TEXT(“OutputResult”), TEXT(“float”), nullptr, false, true
    );
    TArray<FRigVMExternalVariable> Variables = {InputVar, OutputVar};

    // 初始化宿主内存
    FRigVMExtendedExecuteContext Context;
    Host->Init(Variables, Context);

    // 设置输入值
    float* InputValuePtr = static_cast<float*>(Host->GetVariableMemory(TEXT(“InputA”)));
    *InputValuePtr = 10.0f;

    // 9. 执行
    Host->Execute(Context);

    // 读取输出值
    float* OutputValuePtr = static_cast<float*>(Host->GetVariableMemory(TEXT(“OutputResult”)));
    UE_LOG(LogTemp, Log, TEXT(“Execution Result: %f (Expected: 20.0)”), *OutputValuePtr);

    // 清理
    Graph->MarkAsGarbage();
    Controller->MarkAsGarbage();
    VM->MarkAsGarbage();
    Host->MarkAsGarbage();
}
```

## 模块依赖
从 `RigVMDeveloper.Build.cs` 和 `RigVMEditor.Build.cs` 分析，其依赖主要集中在编辑器功能上。
要使用 RigVM 的核心功能（模型、编译、运行时），你的模块需要依赖 `RigVM` 模块。如果你需要访问其开发工具（如 Controller）或编辑器集成，则还需要依赖 `RigVMDeveloper` 和 `RigVMEditor`。

| 模块 | 用途 |
|---|---|
| `Kismet` | 提供蓝图编辑器的基础架构，用于集成 RigVM 图形编辑器。 |
| `PropertyEditor` | 用于在细节面板中自定义 RigVM 资产和节点的属性显示。 |
| `RigVM` | **核心依赖**：提供运行时 VM、字节码和基础数据结构。 |
| `RigVMDeveloper` | 提供用于程序化操作图表的 API（Controller, Graph Model）。 |
| `RigVMEditor` | 提供编辑器 UI 集成，如图表编辑器、节点工厂和 Schema。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `dfee5052` | Control Rig: Fix missing dependency in ControlRigModules | 修复了 ControlRig 模块中缺失的依赖项。 |
| 2026-05-22 | `e51b24ac` | Cherry-picking fix CL from Sara Schvartzman | 合并了 Sara Schvartzman 提交的一个修复。 |
| 2026-05-21 | `fee6a0dc` | Control Rig: Fix renaming a variable in some cases leaves a duplicate | 修复了重命名变量有时会留下副本的问题。 |
| 2026-05-18 | `5d1db13f` | Fix crash when debug pins are orphaned | 修复了调试引脚孤立时导致的崩溃。 |
| 2026-05-15 | `0b718514` | Control RIg: Defensive fix when function of a unit struct is nullptr | 对单元结构体的函数为空指针的情况进行了防御性修复。 |

### 维护评价
-   **创建时间**：该插件于 2023 年 3 月从引擎模块迁移而来，历史相对较短。
-   **维护频率**：**极度活跃**。最近的提交集中在 2026 年 5 月，每周都有多次更新，主要涉及 Bug 修复和与 ControlRig 的集成改进。
-   **维护状态**：**积极维护中**。作为 ControlRig 和 PCG 等核心系统的基础设施，由 Epic 的专业团队负责开发，质量有保障。
-   **推荐使用**：**强烈推荐**。这是 Epic 官方支持的、用于构建高性能视觉编程系统的核心框架。如果你的需求是创建自定义的图形化工具或脚本系统，RigVM 是首选且成熟的解决方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM/Tests) (路径可能为 `Tests` 或 `RigVMTest`)