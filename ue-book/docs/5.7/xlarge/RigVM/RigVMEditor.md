# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器样式） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (UncookedOnly), `RigVMEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 UE5 的**可视化编程语言运行时与编辑器框架**，为 ControlRig 等动画蓝图系统提供底层的节点图执行引擎。它解决的核心问题是：在运行时高效执行基于节点图的程序逻辑，同时在编辑器中提供完整的可视化编辑体验。

RigVM 不仅仅是一个"节点图编辑器"——它是一套完整的**编译型可视化编程语言**，包含：
- **前端（Frontend）**：节点图模型（`URigVMGraph`）、控制器（`URigVMController`）、EdGraph 表示层
- **后端（Backend）**：字节码编译器、虚拟机执行栈、内存存储系统
- **编辑器（Editor）**：自定义节点渲染、引脚控件、右键菜单、调试工具

该插件是 ControlRig 的核心依赖，也被其他需要可视化编程能力的系统（如动画蓝图、程序化生成）使用。

## 使用场景

- 你在开发 **ControlRig** 或类似的骨骼动画控制系统 → RigVM 是其底层执行引擎
- 你需要一个**高性能的可视化编程运行时**，支持字节码编译和优化 → 用 RigVM
- 你在构建自定义的**节点图编辑器**，需要完整的模型-视图-控制器架构 → 基于 RigVM 扩展
- 你需要在运行时执行**基于节点图的程序逻辑**，且对性能有要求 → RigVM 的 VM 比解释执行更快

## 蓝图用法

RigVMEditor 模块主要提供编辑器扩展，不直接暴露蓝图节点。核心的蓝图可调用 API 位于 RigVM（Runtime）和 RigVMDeveloper 模块中。

### 编辑器扩展接口

RigVMEditor 提供的主要是 C++ 层面的编辑器扩展点，用于自定义 RigVM 图的编辑体验：

| 扩展点 | 说明 | 所在类 |
|---|---|---|
| 自定义节点渲染 | 为 RigVM 节点提供自定义 Slate 控件 | `FRigVMEdGraphPanelNodeFactory` |
| 自定义引脚渲染 | 为不同类型的引脚提供专用控件 | `FRigVMEdGraphPanelPinFactory` |
| 节点生成器 | 在右键菜单中注册可创建的节点类型 | `URigVMEdGraphUnitNodeSpawner`, `URigVMEdGraphTemplateNodeSpawner` |
| 编辑器标签页 | 注册执行栈、图浏览器、详情面板等 | `FRigVMExecutionStackTabSummoner`, `FRigVMEditorGraphExplorerTabSummoner` |

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块 - 核心 VM
#include "RigVMCore/RigVM.h"
#include "RigVMModel/RigVMGraph.h"
#include "RigVMModel/RigVMController.h"

// Editor 模块 - 编辑器扩展
#include "EdGraph/RigVMEdGraphPanelNodeFactory.h"
#include "EdGraph/RigVMEdGraphPanelPinFactory.h"
#include "Editor/RigVMMinimalEnvironment.h"
```

### 基本用法：自定义节点引脚控件

RigVMEditor 通过工厂模式为不同类型的引脚提供自定义 UI。以下是创建自定义引脚控件的模式：

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVMEditor/Public/Widgets/SRigVMGraphPinQuat.h
// 四元数引脚使用旋转器输入框替代默认文本框

class SRigVMGraphPinQuat : public SGraphPin
{
public:
    SLATE_BEGIN_ARGS(SRigVMGraphPinQuat)
        : _ModelPin(nullptr)
    {}
        SLATE_ARGUMENT(URigVMPin*, ModelPin)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, UEdGraphPin* InGraphPinObj);

protected:
    virtual TSharedRef<SWidget> GetDefaultValueWidget() override;

    TOptional<FRotator> GetRotator() const;
    void OnRotatorCommitted(FRotator InRotator, ETextCommit::Type InCommitType, bool bUndoRedo);

    URigVMPin* ModelPin;
};
```

### 基本用法：注册自定义引脚工厂

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVMEditor/Public/EdGraph/RigVMEdGraphPanelPinFactory.h
// 引脚工厂根据引脚类型创建对应的 Slate 控件

class FRigVMEdGraphPanelPinFactory : public FGraphPanelPinFactory
{
public:
    virtual FName GetFactoryName() const;
    virtual TSharedPtr<SGraphPin> CreatePin(UEdGraphPin* InPin) const override;
    virtual TSharedPtr<SGraphPin> CreatePin_Internal(UEdGraphPin* InPin) const;
};
```

### 进阶用法：MinimalEnvironment 预览系统

`FRigVMMinimalEnvironment` 提供了一个轻量级的 RigVM 编辑环境，用于节点预览等场景，无需打开完整的蓝图编辑器：

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVMEditor/Public/Editor/RigVMMinimalEnvironment.h

// 创建一个最小化环境用于节点预览
FRigVMMinimalEnvironment Environment(MyRigVMBlueprintClass);

// 设置要预览的节点
Environment.SetNode(MyModelNode);

// 获取模型和控制器进行操作
URigVMGraph* Graph = Environment.GetModel();
URigVMController* Controller = Environment.GetController();

// 监听变化
Environment.OnChanged().AddLambda([]() {
    // 节点图发生变化，更新预览
});

// 在 Tick 中驱动更新
Environment.Tick_GameThead(DeltaTime);
```

### 进阶用法：节点生成器（Node Spawner）

RigVM 使用节点生成器模式在右键菜单中注册可创建的节点：

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVMEditor/Public/EdGraph/NodeSpawners/RigVMEdGraphUnitNodeSpawner.h
// 为 UScriptStruct 上的方法创建节点生成器

// 创建一个 Unit 节点生成器（基于结构体方法）
URigVMEdGraphUnitNodeSpawner* Spawner = new URigVMEdGraphUnitNodeSpawner(
    MyStruct,                    // UScriptStruct* 包含 RigVM 方法
    FName("Execute"),            // 方法名
    LOCTEXT("Execute", "Execute"), // 菜单显示名
    LOCTEXT("MyCategory", "My"),   // 菜单分类
    LOCTEXT("Tooltip", "Executes the operation") // 工具提示
);

// Template 节点生成器（基于模板符号）
URigVMEdGraphTemplateNodeSpawner* TemplateSpawner = new URigVMEdGraphTemplateNodeSpawner(
    FName("Add"),                // 模板符号 (notation)
    LOCTEXT("Add", "Add"),
    LOCTEXT("Math", "Math"),
    LOCTEXT("AddTooltip", "Adds two values")
);
```

### 进阶用法：连接绘制策略

```cpp
// 来源: Engine/Plugins/Runtime/RigVM/Source/RigVMEditor/Public/EdGraph/RigVMEdGraphConnectionDrawingPolicy.h
// 自定义节点间的连线绘制，支持 reroute 节点和类型兼容性可视化

class FRigVMEdGraphConnectionDrawingPolicy : public FKismetConnectionDrawingPolicy
{
public:
    // 自定义不兼容引脚的高亮显示
    virtual void SetIncompatiblePinDrawState(
        const TSharedPtr<SGraphPin>& StartPin,
        const TSet<TSharedRef<SWidget>>& VisiblePins) override;

    // 自定义连线样式（颜色、粗细等）
    virtual void DetermineWiringStyle(
        UEdGraphPin* OutputPin,
        UEdGraphPin* InputPin,
        FConnectionParams& Params) override;
};
```

## Demo 示例

以下示例展示如何创建一个自定义的 RigVM 引脚控件，用于编辑浮点曲线引脚：

```cpp
// MyCurvePinWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SWidget.h"
#include "SCurveEditor.h"
#include "Curves/CurveFloat.h"
#include "SGraphPin.h"

class SMyCurvePinWidget : public SGraphPin, public FCurveOwnerInterface
{
public:
    SLATE_BEGIN_ARGS(SMyCurvePinWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, UEdGraphPin* InGraphPinObj);

    // FCurveOwnerInterface
    virtual TArray<FRichCurveEditInfoConst> GetCurves() const override;
    virtual TArray<FRichCurveEditInfo> GetCurves() override;
    virtual void ModifyOwner() override;
    virtual TArray<const UObject*> GetOwners() const override;
    virtual void MakeTransactional() override;
    virtual void OnCurveChanged(const TArray<FRichCurveEditInfo>& ChangedCurveEditInfos) override;
    virtual bool IsValidCurve(FRichCurveEditInfo CurveInfo) override;

protected:
    virtual TSharedRef<SWidget> GetDefaultValueWidget() override;

private:
    TSharedPtr<SCurveEditor> CurveEditor;
    FRuntimeFloatCurve Curve;
};
```

```cpp
// MyCurvePinWidget.cpp
#include "MyCurvePinWidget.h"

void SMyCurvePinWidget::Construct(const FArguments& InArgs, UEdGraphPin* InGraphPinObj)
{
    SGraphPin::Construct(SGraphPin::FArguments(), InGraphPinObj);
}

TSharedRef<SWidget> SMyCurvePinWidget::GetDefaultValueWidget()
{
    CurveEditor = SNew(SCurveEditor)
        .ViewMinInput(0.0f)
        .ViewMaxInput(1.0f)
        .ViewMinOutput(0.0f)
        .ViewMaxOutput(1.0f)
        .InputSnap(0.1f)
        .OutputSnap(0.1f);

    return CurveEditor.ToSharedRef();
}

TArray<FRichCurveEditInfoConst> SMyCurvePinWidget::GetCurves() const
{
    return { FRichCurveEditInfoConst(&Curve.GetRichCurve()) };
}

TArray<FRichCurveEditInfo> SMyCurvePinWidget::GetCurves()
{
    return { FRigCurveEditInfo(&Curve.GetRichCurve()) };
}

void SMyCurvePinWidget::ModifyOwner() {}
TArray<const UObject*> SMyCurvePinWidget::GetOwners() const { return {}; }
void SMyCurvePinWidget::MakeTransactional() {}

void SMyCurvePinWidget::OnCurveChanged(const TArray<FRichCurveEditInfo>& ChangedCurveEditInfos)
{
    // 将曲线数据序列化回引脚默认值
}

bool SMyCurvePinWidget::IsValidCurve(FRichCurveEditInfo CurveInfo)
{
    return CurveInfo.CurveToEdit == &Curve.GetRichCurve();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Kismet` | 蓝图编辑器基础设施，RigVMEditor 和 RigVMDeveloper 依赖它来集成蓝图编辑流程 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：RigVM（Runtime）模块的依赖未在提供的信息中完整列出，但作为运行时模块，它可能依赖 `CoreUObject`、`Engine` 等标准模块。RigVMDeveloper 模块依赖 `Kismet` 用于蓝图编译集成。

## 维护状态

### 近期更新

```
- e4c1796 [ControlRig & RigVM] replace function graph task with ExecuteOnGameThread to avoid scheduling tasks during package save, which can lead random crashes
- b273253 Avoid a crash in Control Rig editor when deleting the current graph and trying to add a new item using the add button, as there is no current focused model
- 8b798f4 Fixed RigVM local variable customization not showing value for local variables not used in the graph and losing value after compiling by avoiding the use of the VM memory and using a local instanced struct instead
```

### 维护评价

- **活跃维护**：RigVM 是 ControlRig 的核心基础设施，由 Epic Games 持续维护
- **近期更新**：最近的提交集中在**崩溃修复**和**编辑器稳定性**改进上，表明该插件处于成熟稳定阶段
- **代码规模**：802 个源文件，属于超大型插件，说明功能非常完善
- **架构成熟**：采用模型-视图-控制器架构（Model/Controller/EdGraph），支持完整的撤销/重做、编译、调试流程
- **推荐使用**：如果你在开发 ControlRig 相关功能或需要可视化编程运行时，这是官方推荐的基础设施。作为 Runtime 模块默认启用，说明 Epic 认为其足够稳定

⚠️ **注意**：虽然插件本身稳定，但其 API 变化较快（从头文件中大量 `UE_DEPRECATED(5.7, ...)` 标记可见），升级引擎版本时需要注意 API 迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM)
- [官方文档]()（暂无独立文档，参考 ControlRig 文档）
- [测试用例]()（测试文件位于 Engine/Tests/ 目录下）