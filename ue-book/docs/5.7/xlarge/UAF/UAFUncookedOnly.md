# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画数据流框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画图、变量绑定、编辑器工具、测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestSuite` (Runtime), `UAFUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

Unreal Animation Framework (UAF) 是一个实验性插件，提供基于 RigVM 的动画系统函数式数据流框架。它允许开发者使用节点图定义动画数据流，支持变量、绑定、导出、编译等流程。

`UAFUncookedOnly` 模块是 UAF 编辑体验的核心部分，负责处理**编辑器（非烘焙）环境下**的资产编译、变量绑定注册、RigVM 图扩展、大纲视图数据以及编辑器 UI 集成。它提供了：

- 将变量绑定到游戏对象（Actor 属性、函数结果）的机制
- 自定义变量绑定类型的注册系统
- 图编译的上下文管理和消息输出
- 共享变量节点（Asset/Struct）的控制器扩展
- 编辑器数据（条目、类别、导出）的抽象和操作

## 使用场景

- **自定义动画数据流**：你需要创建可复用、可编程的动画数据流，替代传统动画蓝图的部分功能。
- **变量绑定至外部数据**：需要将动画变量绑定到游戏对象上，通过 Universal Object Locator 实现动态数据驱动。
- **模块化动画系统**：构建模块化动画系统，将动画逻辑分解为独立模块，通过共享变量进行通信。
- **高级 RigVM 扩展**：扩展 RigVM 图系统，添加自定义节点、函数和编译管道。
- **编辑器自动化**：在编辑器工具或构建流水线中自动创建和配置动画资产。

## 蓝图用法

`UAFUncookedOnly` 模块主要提供 C++ 编辑器扩展，蓝图可用的节点集中在 `UAnimNextControllerBase` 类中，用于在 RigVM 图中添加共享变量节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAssetSharedVariableNode` | 从指定的 `UAnimNextSharedVariables` 资产添加一个共享变量节点 | `UAnimNextControllerBase` |
| `AddStructSharedVariableNode` | 从指定的 `UScriptStruct` 结构体类型添加一个共享变量节点 | `UAnimNextControllerBase` |
| `RefreshSharedVariableNode` | 刷新一个已有的共享变量节点的数据（源对象路径、变量名、类型等） | `UAnimNextControllerBase` |
| `AddSharedVariableNode` | 根据源对象路径字符串（如 `/Game/MyAsset.MyAsset`）添加一个共享变量节点 | `UAnimNextControllerBase` |

### 使用示例（蓝图描述）

在编辑器中通过蓝图自动化创建共享变量节点：
1. 获取目标 RigVM 控制器（`URigVMController`）引用。
2. 调用 `AddAssetSharedVariableNode`，传入参数：
   - `InAsset`：共享变量资产引用（`UAnimNextSharedVariables` 类型）
   - `InVariableName`：要使用的变量名
   - `InCPPType`：CPP类型字符串，如 `"float"`、`"FVector"`
   - `InCPPTypeObject`：类型对象（可选，用于结构体或蓝图类型）
   - `bIsGetter`：是否创建只读获取节点（`true`）还是读写节点（`false`）
   - `InDefaultValue`：默认值字符串
   - `InPosition`：节点在图中放置的位置（可选）
3. 节点创建后自动连接到图的执行链条中。

同样，可使用 `RefreshSharedVariableNode` 在变量属性变化后更新节点，无需重新创建。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNextControllerBase.h"
#include "UncookedOnlyUtils.h"
#include "AnimNextRigVMAssetEditorData.h"
#include "Variables/IAnimNextRigVMVariableInterface.h"
#include "Variables/AnimNextProgrammaticVariable.h"
#include "AnimNextScopedCompileJob.h"
#include "IAnimNextUncookedOnlyModule.h"
```

### 基本用法

从 `FUtils` 获取编辑器数据并编译变量：

```cpp
// 获取与资产关联的编辑器数据
UAnimNextRigVMAsset* MyAsset = ...;
UAnimNextRigVMAssetEditorData* EditorData = UE::UAF::UncookedOnly::FUtils::GetEditorData(MyAsset);

// 创建编译上下文
FRigVMCompileSettings CompileSettings;
FAnimNextRigVMAssetCompileContext CompileContext(EditorData);
FAnimNextGetVariableCompileContext VarContext(CompileContext);

// 编译变量
UE::UAF::UncookedOnly::FUtils::CompileVariables(CompileSettings, MyAsset, VarContext);

// 转换 PinType 与 ParamType
FEdGraphPinType PinType = ...;
FAnimNextParamType ParamType = UE::UAF::UncookedOnly::FUtils::GetParamTypeFromPinType(PinType);
```

来源文件：`Public/UncookedOnlyUtils.h`

### 进阶用法

注册自定义变量绑定类型：

```cpp
class FMyBindingType : public UE::UAF::UncookedOnly::IVariableBindingType
{
    // 实现所有纯虚函数
    virtual TSharedRef<SWidget> CreateEditWidget(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        const FAnimNextParamType& InType) const override { /* ... */ }

    virtual FText GetDisplayText(
        TConstStructView<FAnimNextVariableBindingData> InBindingData) const override { /* ... */ }

    virtual FText GetTooltipText(
        TConstStructView<FAnimNextVariableBindingData> InBindingData) const override { /* ... */ }

    virtual void BuildBindingGraphFragment(
        const FRigVMCompileSettings& InSettings,
        const FBindingGraphFragmentArgs& InArgs,
        URigVMPin*& OutExecTail,
        FVector2D& OutLocation) const override { /* ... */ }
};

void MyModule::StartupModule()
{
    IAnimNextUncookedOnlyModule& UAFModule =
        FModuleManager::LoadModuleChecked<IAnimNextUncookedOnlyModule>("UAFUncookedOnly");
    TSharedPtr<FMyBindingType> BindingType = MakeShared<FMyBindingType>();
    UAFModule.RegisterVariableBindingType(TEXT("MyBindingData"), BindingType);
}
```

来源文件：`Public/IAnimNextUncookedOnlyModule.h`

使用 `FScopedCompileJob` 进行作用域编译和日志：

```cpp
void CompileMyAsset(UAnimNextRigVMAsset* InAsset)
{
    UE::UAF::UncookedOnly::FScopedCompileJob Job(
        NSLOCTEXT("MyModule", "Compile", "Compiling asset"), InAsset);
    
    UAnimNextRigVMAssetEditorData* EditorData = 
        UE::UAF::UncookedOnly::FUtils::GetEditorData(InAsset);
    
    FAnimNextRigVMAssetCompileContext Context(EditorData);
    Context.Info(FTextFormat::FromString("Starting compilation..."));
    
    // 执行编译步骤...
}
```

来源文件：`Public/AnimNextScopedCompileJob.h`

## Demo 示例

以下是一个完整的最小示例，展示如何注册自定义变量绑定类型并使用编译作用域。

**MyCustomBinding.h**
```cpp
#pragma once
#include "Variables/IVariableBindingType.h"

class FMyCustomBinding : public UE::UAF::UncookedOnly::IVariableBindingType
{
public:
    virtual TSharedRef<SWidget> CreateEditWidget(
        const TSharedRef<IPropertyHandle>& InPropertyHandle,
        const FAnimNextParamType& InType) const override;

    virtual FText GetDisplayText(
        TConstStructView<FAnimNextVariableBindingData> InBindingData) const override;

    virtual FText GetTooltipText(
        TConstStructView<FAnimNextVariableBindingData> InBindingData) const override;

    virtual void BuildBindingGraphFragment(
        const FRigVMCompileSettings& InSettings,
        const FBindingGraphFragmentArgs& InArgs,
        URigVMPin*& OutExecTail,
        FVector2D& OutLocation) const override;
};
```

**MyCustomBinding.cpp**
```cpp
#include "MyCustomBinding.h"
#include "ScopedTransaction.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Text/STextBlock.h"
#include "RigVMModel/RigVMController.h"

TSharedRef<SWidget> FMyCustomBinding::CreateEditWidget(
    const TSharedRef<IPropertyHandle>& InPropertyHandle,
    const FAnimNextParamType& InType) const
{
    return SNew(STextBlock).Text(NSLOCTEXT("MyBinding", "Info", "Custom binding editing not implemented"));
}

FText FMyCustomBinding::GetDisplayText(
    TConstStructView<FAnimNextVariableBindingData> InBindingData) const
{
    return NSLOCTEXT("MyBinding", "Display", "Custom Binding");
}

FText FMyCustomBinding::GetTooltipText(
    TConstStructView<FAnimNextVariableBindingData> InBindingData) const
{
    return NSLOCTEXT("MyBinding", "Tooltip", "A custom variable binding example");
}

void FMyCustomBinding::BuildBindingGraphFragment(
    const FRigVMCompileSettings& InSettings,
    const FBindingGraphFragmentArgs& InArgs,
    URigVMPin*& OutExecTail,
    FVector2D& OutLocation) const
{
    // 简单实现：添加一个常量节点作为绑定值
    const FName VariableName = InArgs.Inputs[0].VariableName;
    const FString CPPType = InArgs.Inputs[0].CPPType;
    URigVMController* Controller = InArgs.Controller;
    
    URigVMNode* ConstantNode = Controller->AddConstantNode(
        VariableName, CPPType, InArgs.Inputs[0].CPPTypeObject,
        FString::Printf(TEXT("0")), true, OutLocation, TEXT(""), true, true);
    
    OutExecTail = ConstantNode->FindPin(TEXT("Value"));
    OutLocation += FVector2D(200, 0);
}
```

**MyModule.cpp**（在模块 StartupModule 中注册）
```cpp
#include "Modules/ModuleManager.h"
#include "IAnimNextUncookedOnlyModule.h"
#include "MyCustomBinding.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        IAnimNextUncookedOnlyModule& UAFModule =
            FModuleManager::LoadModuleChecked<IAnimNextUncookedOnlyModule>("UAFUncookedOnly");
        TSharedPtr<FMyCustomBinding> BindingType = MakeShared<FMyCustomBinding>();
        UAFModule.RegisterVariableBindingType(TEXT("MyCustomBindingData"), BindingType);
    }

    virtual void ShutdownModule() override
    {
        IAnimNextUncookedOnlyModule* UAFModule =
            FModuleManager::GetModulePtr<IAnimNextUncookedOnlyModule>("UAFUncookedOnly");
        if (UAFModule)
        {
            UAFModule->UnregisterVariableBindingType(TEXT("MyCustomBindingData"));
        }
    }
};

IMPLEMENT_MODULE(FMyModule, MyCustomModule);
```

## 模块依赖

根据 `UAFUncookedOnly.Build.cs`，该模块的公共依赖如下（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 支持实时 C++ 代码重载，无需重启编辑器即可应用代码更改 |

其他依赖均为常见模块（CoreUObject、Engine、Slate、UnrealEd 等），已省略。

## 维护状态

### 近期更新

- 2025-10-02 `ef1c8b52` Fix double binding to IsEnabled
- 2025-10-02 `f75459b5` Fix crash from selecting non-Actor derived blueprint to modify in UAF asset wizard
- 2025-10-01 `6f23619b` Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various impleme
- 2025-09-30 `737f1f42` Crash fixes for LODPose
- 2025-09-25 `2f8943cd` Honor `ShrinkByDefault` in various existing array classes.

### 维护评价

- 创建于 2025-09-25，仅约 0.1 年，处于**极早期开发阶段**。
- 近期更新频率高，几乎每天都有多次提交，包含 Bug 修复和功能改进。
- 插件标记为**实验性**（`IsExperimentalVersion=true`），接口可能频繁变动，不建议用于生产环境。
- 当前没有已知的废弃标记或严重限制。
- **推荐状态**：可用于技术原型和实验性项目，但需要注意未来可能的破坏性更改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)
- [官方文档]（暂无，DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite)（UAFTestSuite 模块）