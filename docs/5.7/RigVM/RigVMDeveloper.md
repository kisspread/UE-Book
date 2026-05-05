# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、图表数据） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (UncookedOnly), `RigVMEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 Unreal Engine 的**可视化编程语言运行时框架**，为 ControlRig 等动画系统提供底层的图表模型、编译器和虚拟机执行引擎。

它解决的核心问题是：**如何将节点图表（Node Graph）高效编译为字节码并在运行时执行**。RigVM 不仅是一个图表编辑器，更是一个完整的编译管线——从图表模型（Model）到抽象语法树（AST）再到字节码（ByteCode），最终由轻量级虚拟机（VM）执行。

RigVM 的存在使得 ControlRig 能够：
- 在编辑器中通过可视化节点图定义骨骼动画逻辑
- 将图表编译为高效的字节码，避免运行时解释开销
- 支持模板化节点（Template Nodes）实现类型安全的多态
- 通过函数库（Function Library）实现可复用的图表函数
- 支持 Dispatch 工厂模式实现灵活的节点扩展

## 使用场景

- 你在开发 **ControlRig** 动画蓝图 → RigVM 提供图表模型、编译器和运行时
- 你需要创建**自定义可视化编程语言** → 使用 RigVM 的图表模型和编译管线
- 你需要将**节点图表编译为高效字节码** → 使用 FRigVMCompiler 和 URigVM
- 你需要实现**模板化多态节点**（如支持多种数据类型的 Add 节点）→ 使用 URigVMTemplateNode 和 FRigVMTemplate
- 你需要创建**可复用的图表函数库** → 使用 URigVMFunctionLibrary 和 URigVMFunctionReferenceNode
- 你需要通过 **Python 脚本**操作 RigVM 图表 → 使用 RigVMPythonUtils

## 模块架构

```
RigVM Plugin
├── RigVM (Runtime)           ← 核心运行时：VM、字节码、类型注册
├── RigVMDeveloper (UncookedOnly) ← 开发工具：图表模型、编译器、蓝图集成
└── RigVMEditor (Editor)      ← 编辑器 UI：图表编辑器、节点面板
```

### 核心概念

| 概念 | 说明 |
|---|---|
| **Graph** (URigVMGraph) | 图表容器，包含节点和连接 |
| **Node** (URigVMNode) | 图表中的节点，有多种子类型 |
| **Pin** (URigVMPin) | 节点上的输入/输出引脚 |
| **Link** (URigVMLink) | 两个引脚之间的连接 |
| **Template** (FRigVMTemplate) | 节点的类型模板，支持多态 |
| **Dispatch** (FRigVMDispatchFactory) | 节点工厂，动态创建节点 |
| **Function Library** (URigVMFunctionLibrary) | 存储可复用的图表函数 |

### 节点类型层次

```
URigVMNode
├── URigVMTemplateNode          ← 模板节点基类
│   ├── URigVMUnitNode          ← 调用 USTRUCT 上的 RIGVM_METHOD
│   ├── URigVMDispatchNode      ← 通过工厂动态创建的节点
│   ├── URigVMLibraryNode       ← 函数库节点基类
│   │   ├── URigVMCollapseNode  ← 折叠子图节点
│   │   │   └── URigVMAggregateNode ← 聚合节点（如多输入 Add）
│   │   └── URigVMFunctionReferenceNode ← 引用外部函数
│   └── URigVMFunctionInterfaceNode ← 函数入口/出口基类
│       ├── URigVMFunctionEntryNode
│       └── URigVMFunctionReturnNode
├── URigVMVariableNode          ← 变量读写节点
├── URigVMEnumNode              ← 枚举常量节点
├── URigVMRerouteNode           ← 路由节点（纯视觉）
├── URigVMCommentNode           ← 注释节点（纯视觉）
└── URigVMInvokeEntryNode       ← 调用其他入口节点
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNodes` | 获取图表中所有节点 | `URigVMGraph` |
| `GetLinks` | 获取图表中所有连接 | `URigVMGraph` |
| `FindNodeByName` | 按名称查找节点 | `URigVMGraph` |
| `GetEntryNode` | 获取函数入口节点 | `URigVMGraph` |
| `GetReturnNode` | 获取函数返回节点 | `URigVMGraph` |
| `GetVariableDescriptions` | 获取所有变量描述 | `URigVMGraph` |
| `GetFunctions` | 获取函数库中所有函数 | `URigVMFunctionLibrary` |
| `FindFunction` | 按名称查找函数 | `URigVMFunctionLibrary` |
| `GetSourcePin` | 获取连接的源引脚 | `URigVMLink` |
| `GetTargetPin` | 获取连接的目标引脚 | `URigVMLink` |
| `GetVariableName` | 获取变量名 | `URigVMVariableNode` |
| `IsGetter` | 是否为变量读取节点 | `URigVMVariableNode` |
| `GetCommentText` | 获取注释文本 | `URigVMCommentNode` |
| `GetEntryName` | 获取要调用的入口名 | `URigVMInvokeEntryNode` |
| `Get` | 获取工作流注册表单例 | `URigVMUserWorkflowRegistry` |
| `RegisterProvider` | 注册工作流提供者 | `URigVMUserWorkflowRegistry` |
| `GetWorkflows` | 获取指定类型的工作流 | `URigVMUserWorkflowRegistry` |

### 使用示例（蓝图描述）

**遍历图表中的所有节点：**
1. 获取目标 `URigVMGraph` 对象
2. 调用 `GetNodes` 节点获取 `TArray<URigVMNode*>`
3. 使用 `ForEachLoop` 遍历数组
4. 对每个节点调用 `GetNodeTitle` 获取标题

**查找并操作变量：**
1. 调用 `GetVariableDescriptions` 获取所有变量描述
2. 遍历数组，检查每个 `FRigVMGraphVariableDescription` 的 `Name`
3. 使用 `FindNodeByName` 找到对应的变量节点
4. 调用 `IsGetter` 判断是读取还是写入

**注册自定义工作流：**
1. 调用 `URigVMUserWorkflowRegistry::Get` 获取注册表
2. 创建 `FRigVMUserWorkflowProvider` 委托
3. 调用 `RegisterProvider` 注册，传入目标结构体类型和委托
4. 保存返回的 Handle 用于后续取消注册

## C++ 用法

### 头文件引入

```cpp
// 核心图表模型
#include "RigVMModel/RigVMGraph.h"
#include "RigVMModel/RigVMNode.h"
#include "RigVMModel/RigVMPin.h"
#include "RigVMModel/RigVMLink.h"

// 特定节点类型
#include "RigVMModel/Nodes/RigVMUnitNode.h"
#include "RigVMModel/Nodes/RigVMVariableNode.h"
#include "RigVMModel/Nodes/RigVMFunctionReferenceNode.h"
#include "RigVMModel/Nodes/RigVMCollapseNode.h"

// 编译器和代码生成
#include "RigVMCompiler/RigVMCodeGenerator.h"
#include "RigVMCompiler/RigVMASTProxy.h"

// 蓝图工具
#include "RigVMBlueprintUtils.h"
#include "RigVMBlueprintCompiler.h"

// Python 工具
#include "RigVMPythonUtils.h"

// 工作流注册
#include "RigVMUserWorkflowRegistry.h"
```

### 基本用法：遍历图表节点

```cpp
// 来源: RigVMModel/RigVMGraph.h
void IterateGraphNodes(URigVMGraph* InGraph)
{
    if (!InGraph) return;
    
    // 获取所有节点
    const TArray<URigVMNode*>& Nodes = InGraph->GetNodes();
    for (URigVMNode* Node : Nodes)
    {
        UE_LOG(LogTemp, Log, TEXT("Node: %s, Title: %s"), 
            *Node->GetName(), *Node->GetNodeTitle());
        
        // 获取节点的所有引脚
        const TArray<URigVMPin*>& Pins = Node->GetPins();
        for (URigVMPin* Pin : Pins)
        {
            UE_LOG(LogTemp, Log, TEXT("  Pin: %s"), *Pin->GetName());
        }
    }
    
    // 获取所有连接
    const TArray<URigVMLink*>& Links = InGraph->GetLinks();
    for (URigVMLink* Link : Links)
    {
        URigVMPin* Source = Link->GetSourcePin();
        URigVMPin* Target = Link->GetTargetPin();
        UE_LOG(LogTemp, Log, TEXT("Link: %s -> %s"),
            *Link->GetSourcePinPath(), *Link->GetTargetPinPath());
    }
}
```

### 基本用法：操作变量节点

```cpp
// 来源: RigVMModel/Nodes/RigVMVariableNode.h
void InspectVariableNode(URigVMVariableNode* VariableNode)
{
    if (!VariableNode) return;
    
    // 获取变量信息
    FName VarName = VariableNode->GetVariableName();
    bool bIsGetter = VariableNode->IsGetter();
    FString CPPType = VariableNode->GetCPPType();
    FString DefaultValue = VariableNode->GetDefaultValue();
    
    // 判断变量类型
    bool bExternal = VariableNode->IsExternalVariable();
    bool bLocal = VariableNode->IsLocalVariable();
    bool bInputArg = VariableNode->IsInputArgument();
    
    // 获取变量描述（包含完整元数据）
    FRigVMGraphVariableDescription Desc = VariableNode->GetVariableDescription();
    
    UE_LOG(LogTemp, Log, TEXT("Variable '%s': Type=%s, Getter=%s, External=%s"),
        *VarName.ToString(), *CPPType, 
        bIsGetter ? TEXT("true") : TEXT("false"),
        bExternal ? TEXT("true") : TEXT("false"));
}
```

### 基本用法：使用函数库

```cpp
// 来源: RigVMModel/RigVMFunctionLibrary.h
void WorkWithFunctionLibrary(URigVMFunctionLibrary* Library)
{
    if (!Library) return;
    
    // 获取所有函数
    TArray<URigVMLibraryNode*> Functions = Library->GetFunctions();
    for (URigVMLibraryNode* Func : Functions)
    {
        UE_LOG(LogTemp, Log, TEXT("Function: %s, Category: %s"),
            *Func->GetNodeTitle(), *Func->GetNodeCategory());
    }
    
    // 按名称查找函数
    URigVMLibraryNode* FoundFunc = Library->FindFunction(FName("MyFunction"));
    if (FoundFunc)
    {
        // 获取函数标识符
        FRigVMGraphFunctionIdentifier Identifier = FoundFunc->GetFunctionIdentifier();
        
        // 获取函数头信息
        FRigVMGraphFunctionHeader Header = FoundFunc->GetFunctionHeader();
        
        // 获取函数的所有引用
        Library->ForEachReference(FName("MyFunction"), 
            [](URigVMFunctionReferenceNode* RefNode)
            {
                UE_LOG(LogTemp, Log, TEXT("  Reference at: %s"), 
                    *RefNode->GetPathName());
            });
    }
}
```

### 进阶用法：工作流注册

```cpp
// 来源: RigVMModel/RigVMUserWorkflowRegistry.h
void RegisterCustomWorkflow()
{
    URigVMUserWorkflowRegistry* Registry = URigVMUserWorkflowRegistry::Get();
    
    // 创建工作流提供者委托
    FRigVMUserWorkflowProvider Provider;
    Provider.BindLambda([](const UObject* InSubject) -> TArray<FRigVMUserWorkflow>
    {
        TArray<FRigVMUserWorkflow> Workflows;
        
        FRigVMUserWorkflow Workflow;
        Workflow.Title = FText::FromString(TEXT("My Custom Action"));
        Workflow.Tooltip = FText::FromString(TEXT("Performs a custom action"));
        Workflow.Type = ERigVMUserWorkflowType::NodeContext;
        
        Workflows.Add(Workflow);
        return Workflows;
    });
    
    // 注册到特定结构体类型
    int32 Handle = Registry->RegisterProvider(
        FMyRigVMStruct::StaticStruct(), Provider);
    
    // ... 使用完毕后取消注册
    // Registry->UnregisterProvider(Handle);
}
```

### 进阶用法：Python 工具函数

```cpp
// 来源: RigVMPythonUtils.h
void GeneratePythonCode()
{
    // 将 UE 名称转换为 Python 风格
    FString PythonName = RigVMPythonUtils::PythonizeName(
        TEXT("MyVariableName"), 
        RigVMPythonUtils::EPythonizeNameCase::Lower);
    // 结果: "my_variable_name"
    
    FString UpperName = RigVMPythonUtils::PythonizeName(
        TEXT("MyVariableName"),
        RigVMPythonUtils::EPythonizeNameCase::Upper);
    // 结果: "MY_VARIABLE_NAME"
    
    // 转换 Transform 为 Python 字符串
    FTransform Transform(FRotator(0, 90, 0), FVector(100, 0, 0));
    FString TransformStr = RigVMPythonUtils::TransformToPythonString(Transform);
    
    // 转换颜色为 Python 字符串
    FLinearColor Color(1.0f, 0.0f, 0.0f, 1.0f);
    FString ColorStr = RigVMPythonUtils::LinearColorToPythonString(Color);
    
    // 转换枚举值为 Python 字符串
    FString EnumStr = RigVMPythonUtils::EnumValueToPythonString<EMyEnum>(
        static_cast<int64>(EMyEnum::Value1));
}
```

### 进阶用法：蓝图工具函数

```cpp
// 来源: RigVMBlueprintUtils.h
void BlueprintUtilities(UBlueprint* Blueprint)
{
    // 重建所有蓝图节点（例如在类型更改后）
    FRigVMBlueprintUtils::HandleReconstructAllBlueprintNodes(Blueprint);
    
    // 刷新所有节点
    FRigVMBlueprintUtils::HandleRefreshAllBlueprintNodes(Blueprint);
    
    // 遍历所有 RigVM 结构体
    FRigVMBlueprintUtils::ForAllRigVMStructs([](UScriptStruct* Struct)
    {
        UE_LOG(LogTemp, Log, TEXT("RigVM Struct: %s"), *Struct->GetName());
    });
    
    // 验证名称有效性
    FName ValidName = FRigVMBlueprintUtils::ValidateName(
        Blueprint, TEXT("NewNodeName"));
    
    // 通过 GUID 查找节点
    UEdGraphNode* Node = FRigVMBlueprintUtils::GetNodeByGUID(
        Blueprint, FGuid(/* ... */));
    
    // 查找唯一变量名
    FName UniqueName = FRigVMBlueprintUtils::FindUniqueVariableName(
        Blueprint, TEXT("MyVar"));
}
```

## Demo 示例

### 自定义 RigVM 图表分析器

```cpp
// RigVMAnalyzer.h
#pragma once

#include "CoreMinimal.h"
#include "RigVMModel/RigVMGraph.h"
#include "RigVMModel/Nodes/RigVMVariableNode.h"
#include "RigVMModel/Nodes/RigVMUnitNode.h"

class FRigVMGraphAnalyzer
{
public:
    struct FGraphStats
    {
        int32 TotalNodes = 0;
        int32 VariableNodes = 0;
        int32 UnitNodes = 0;
        int32 TotalLinks = 0;
        TArray<FName> VariableNames;
        TArray<FString> UnitMethodNames;
    };

    static FGraphStats AnalyzeGraph(URigVMGraph* InGraph);
    static TArray<URigVMVariableNode*> FindExternalVariables(URigVMGraph* InGraph);
    static TArray<URigVMLink*> FindLinksToNode(URigVMGraph* InGraph, URigVMNode* InNode);
};
```

```cpp
// RigVMAnalyzer.cpp
#include "RigVMAnalyzer.h"
#include "RigVMModel/Nodes/RigVMUnitNode.h"

FRigVMGraphAnalyzer::FGraphStats FRigVMGraphAnalyzer::AnalyzeGraph(URigVMGraph* InGraph)
{
    FGraphStats Stats;
    if (!InGraph) return Stats;

    const TArray<URigVMNode*>& Nodes = InGraph->GetNodes();
    Stats.TotalNodes = Nodes.Num();

    for (URigVMNode* Node : Nodes)
    {
        // 统计变量节点
        if (URigVMVariableNode* VarNode = Cast<URigVMVariableNode>(Node))
        {
            Stats.VariableNodes++;
            Stats.VariableNames.Add(VarNode->GetVariableName());
        }
        // 统计单元节点
        else if (URigVMUnitNode* UnitNode = Cast<URigVMUnitNode>(Node))
        {
            Stats.UnitNodes++;
            Stats.UnitMethodNames.Add(UnitNode->GetMethodName().ToString());
        }
    }

    Stats.TotalLinks = InGraph->GetLinks().Num();
    return Stats;
}

TArray<URigVMVariableNode*> FRigVMGraphAnalyzer::FindExternalVariables(URigVMGraph* InGraph)
{
    TArray<URigVMVariableNode*> Result;
    if (!InGraph) return Result;

    for (URigVMNode* Node : InGraph->GetNodes())
    {
        if (URigVMVariableNode* VarNode = Cast<URigVMVariableNode>(Node))
        {
            if (VarNode->IsExternalVariable())
            {
                Result.Add(VarNode);
            }
        }
    }
    return Result;
}

TArray<URigVMLink*> FRigVMGraphAnalyzer::FindLinksToNode(
    URigVMGraph* InGraph, URigVMNode* InNode)
{
    TArray<URigVMLink*> Result;
    if (!InGraph || !InNode) return Result;

    for (URigVMLink* Link : InGraph->GetLinks())
    {
        if (Link->GetSourceNode() == InNode || Link->GetTargetNode() == InNode)
        {
            Result.Add(Link);
        }
    }
    return Result;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Kismet` | 蓝图编译框架，RigVMDeveloper 和 RigVMEditor 依赖此模块进行蓝图编译集成 |
| `StructUtils` | 结构体工具（PropertyBag），用于 Trait 默认值管理 |

## 维护状态

### 近期更新

```
- 0b81028c1891 RigVMController: Guard against garbage collected injection nodes
- e4c1796bad0d [ControlRig & RigVM] replace function graph task with ExecuteOnGameThread to avoid scheduling tasks during package save, which can lead random crashes
- 4e95ae7b6fb3 Fixed a crash in ControlRig when expanding a function reference from a different graph that contains a private function inside. Now the user will receive a localize request to make a local copy of the function
```

### 维护评价

**活跃维护** ✅

- **创建时间**：2023-03-28（约 3 年），但代码中存在大量 `Deprecated` 节点（如 `UDEPRECATED_RigVMBranchNode`、`UDEPRECATED_RigVMArrayNode`、`UDEPRECATED_RigVMIfNode`、`UDEPRECATED_RigVMSelectNode`），表明该系统经历了多轮 API 演进
- **最近更新**：近期 commit 集中在**稳定性修复**——垃圾回收保护、任务调度崩溃修复、跨图函数引用崩溃修复
- **代码规模**：802 个源文件，是 UE5 中最大的插件之一，架构成熟
- **API 演进**：多个节点类型被标记为 Deprecated（5.1/5.2），说明 API 在持续优化
- **推荐使用**：✅ 强烈推荐。RigVM 是 ControlRig 的核心基础设施，由 Epic 官方维护，是 UE5 动画系统的基石

**注意事项**：
- 部分节点类型已废弃（`RigVMBranchNode`、`RigVMArrayNode`、`RigVMIfNode`、`RigVMSelectNode`），新代码应使用对应的模板节点或 Dispatch 节点
- `RigVMParameterNode` 在 5.1 中被废弃，应使用 `RigVMVariableNode` 替代
- `RigVMDeveloper` 模块类型为 `UncookedOnly`，仅在编辑器和开发构建中可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM)
- [官方文档]()（暂无）