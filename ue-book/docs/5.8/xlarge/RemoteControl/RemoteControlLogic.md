# Remote Control Logic

> 一套用于控制虚幻引擎的工具集，支持在编辑器或运行时通过网络服务器进行控制。允许用户通过HTTP或WebSocket请求远程控制虚幻引擎。该功能允许开发者通过第三方应用程序和网络服务控制虚幻引擎。

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制逻辑 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlLogic` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlLogic) | |

## 用途

`RemoteControlLogic` 模块是 Remote Control 插件的核心逻辑框架。它定义了一套可扩展的 **控制器-行为-动作 (Controller-Behaviour-Action)** 架构，用于实现对远程控制属性（Properties）和函数（Functions）的高级控制逻辑。

**核心解决的问题：**
简单的属性绑定无法满足复杂的虚拟制片工作流需求。例如，你可能需要：
- 根据一个“主控制器”的值，有条件地修改多个不同的属性。
- 将一个控制器的输入范围映射（Remap）到一个属性的不同取值范围。
- 通过一个字符串路径来动态设置资产（如材质、纹理）。
- 在多个条件都满足时才执行特定的动作。

`RemoteControlLogic` 通过抽象出 `URCController`、`URCBehaviour` 和 `URCAction` 三大类，使得这些复杂的逻辑可以通过配置（蓝图或代码）进行组合和复用，而不仅仅是简单的值绑定。

## 使用场景

- **虚拟制片远程控制面板**：你需要在iPad或Web界面上创建一个复杂的控制面板，其中某个滑动条（控制器）不仅能调整灯光亮度（绑定），还能根据滑动位置切换不同的灯光预设（条件行为），或者将输入值映射到一个0-1的范围内来控制材质参数（范围映射行为）。
- **自动化测试与脚本**：在编写自动化测试脚本时，你可以通过创建逻辑控制器和行为，以编程方式模拟复杂的用户交互序列。
- **自定义资产加载工作流**：你需要一个专用的控制器，让用户通过输入一个资产路径字符串，来动态地替换场景中某个模型的材质或网格体。
- **扩展Remote Control功能**：作为插件开发者，你可以基于此模块提供的基类（`URCBehaviour`, `URCBehaviourNode`）创建全新的、可复用的逻辑行为节点。

## 蓝图用法

本模块的类主要通过C++扩展使用，但部分基类和行为节点也暴露了蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行此行为中包含的所有动作。 | `URCBehaviour` |
| `AddAction` | 向行为中添加一个逻辑动作（Identity、Property或Function）。 | `URCBehaviour` |
| `IsSupported` | 检查当前行为节点是否支持给定的输入（如控制器类型）。 | `URCBehaviourNode` |
| `PreExecute` | 行为执行前的回调。 | `URCBehaviourNode` |
| `OnPassed` | 当行为节点的 `Execute` 返回 true 时调用。 | `URCBehaviourNode` |
| `GetBehaviourClass` | 返回此行为节点所关联的 `URCBehaviour` 子类。 | `URCBehaviourNode` |
| `IsSupported` (蓝图实现) | 蓝图可重写事件，用于定义支持逻辑。 | `URCBehaviourBlueprintNode` |
| `Execute` (蓝图实现) | 蓝图可重写事件，用于定义执行逻辑。 | `URCBehaviourBlueprintNode` |

### 使用示例（蓝图描述）

由于无法截图，以下是使用 `URCBehaviourBlueprintNode` 创建自定义行为的蓝图逻辑描述：

1.  **创建自定义行为节点蓝图**：创建一个继承自 `URCBehaviourBlueprintNode` 的蓝图类（例如 `BP_CustomBehaviourNode`）。
2.  **重写事件**：
    - 在 `IsSupported` 事件中，添加逻辑判断输入的 `Behaviour` 是否适合（例如，检查其控制器类型）。
    - 在 `Execute` 事件中，编写当行为被触发时需要执行的逻辑。你可以访问 `Behaviour` 来获取其控制器值和关联的动作。
3.  **在Remote Control面板中使用**：在Remote Control的UI面板中，为某个控制器添加一个新的行为时，就可以选择你创建的 `BP_CustomBehaviourNode` 作为行为类型。该节点的 `DisplayName` 和 `BehaviorDescription` 属性会在UI中显示。

## C++ 用法

### 头文件引入

```cpp
#include "RCController.h"
#include "RCBehaviour.h"
#include "RCBehaviourNode.h"
#include "RCAction.h"
#include "RCPropertyAction.h"
#include "RCActionContainer.h"
```

### 基本用法

以下示例展示了如何程序化地创建一个控制器并为其添加一个简单的“值变化时执行”的行为。
*来源：基于 `Private/Tests/RemoteControlLogicTestData.h` 和模块接口推断。*

```cpp
// 假设你已经拥有一个 URemoteControlPreset* Preset
// 假设你有一个要控制的 FRemoteControlProperty* TargetProperty

// 1. 获取或创建一个控制器（URCController 通常由 Preset 管理，这里假设已存在）
URCController* MyController = Preset->FindControllerByName(TEXT("MyFloatController"));

if (!MyController)
{
    // 创建一个浮点类型的控制器
    FPropertyBagPropertyDesc Desc;
    Desc.ValueType = EPropertyBagPropertyType::Float;
    Desc.Name = TEXT("MyFloatController");
    MyController = Preset->AddController(Desc);
}

// 2. 为控制器添加一个“值变化”行为
TSubclassOf<URCBehaviourNode> NodeClass = URCBehaviourOnValueChangedNode::StaticClass();
URCBehaviour* OnChangedBehaviour = MyController->AddBehaviour(NodeClass);

// 3. 为行为添加一个属性动作，将控制器的值应用到目标属性
TSharedPtr<FRemoteControlField> PropertyField = /* 从 Preset 或其他途径获取目标属性的 Field */;
URCPropertyAction* PropertyAction = Cast<URCPropertyAction>(OnChangedBehaviour->AddAction(PropertyField.ToSharedRef()));

// 4. (可选) 为属性动作设置初始值
if (PropertyAction && PropertyAction->PropertySelfContainer)
{
    PropertyAction->PropertySelfContainer->SetValueFloat(0.5f);
}

// 当 MyController 的值通过UI或代码被修改时，OnChangedBehaviour 将会执行，
// 并将控制器的当前值设置到 PropertyAction 所绑定的远程属性上。
```

### 进阶用法

结合 `URCBehaviourConditional`（条件行为）和 `URCBehaviourBind`（绑定行为）来实现更复杂的逻辑。

```cpp
// 场景：当控制器值 > 0.5 时，将灯光强度绑定到另一个控制器；否则，将灯光强度固定为 0。

// ... 前置代码同上，获取或创建 MyController 和另一个 LightIntensityController ...

// 1. 为 MyController 添加一个条件行为
URCBehaviourConditional* CondBehaviour = Cast<URCBehaviourConditional>(
    MyController->AddBehaviour(URCBehaviourConditionalNode::StaticClass())
);

// 2. 准备比较值
URCVirtualPropertySelfContainer* Comparand = NewObject<URCVirtualPropertySelfContainer>();
Comparand->SetValueFloat(0.5f); // 比较值
CondBehaviour->Comparand = Comparand;

// 3. 添加“大于”的条件动作：当 MyController > 0.5 时，执行绑定
TSharedPtr<FRemoteControlField> LightIntensityField = /* ... */;
URCPropertyAction* BindAction = Cast<URCPropertyAction>(
    CondBehaviour->AddConditionalAction(
        LightIntensityField.ToSharedRef(),
        ERCBehaviourConditionType::IsGreaterThan,
        Comparand
    )
);
// 将这个动作与另一个控制器“绑定”
// ... 此处需要关联 LightIntensityController，具体实现依赖于 Bind 行为逻辑 ...

// 4. 添加“否则”的条件动作：当条件不满足时，将强度设为 0
URCPropertyAction* SetToZeroAction = Cast<URCPropertyAction>(
    CondBehaviour->AddConditionalAction(
        LightIntensityField.ToSharedRef(),
        ERCBehaviourConditionType::Else,
        Comparand // 此处 Comparand 仅为占位，Else 行为不需要比较值
    )
);
if (SetToZeroAction && SetToZeroAction->PropertySelfContainer)
{
    SetToZeroAction->PropertySelfContainer->SetValueFloat(0.0f);
}
```

## Demo 示例

以下是一个完整的、可编译的C++示例，演示了如何创建一个自定义的行为节点。

**MyCustomBehaviourNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Behaviour/RCBehaviourNode.h"
#include "MyCustomBehaviourNode.generated.h"

UCLASS(Blueprintable, EditInlineNew, DefaultToInstanced)
class MYPROJECT_API UMyCustomBehaviourNode : public URCBehaviourNode
{
    GENERATED_BODY()

public:
    UMyCustomBehaviourNode();

    //~ Begin URCBehaviourNode interface
    virtual bool IsSupported(URCBehaviour* InBehaviour) const override;
    virtual bool Execute(URCBehaviour* InBehaviour) const override;
    virtual void OnPassed(URCBehaviour* InBehaviour) const override;
    virtual UClass* GetBehaviourClass() const override;
    //~ End URCBehaviourNode interface

    // 自定义蓝图可编辑属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Custom Node")
    FText CustomMessage;
};
```

**MyCustomBehaviourNode.cpp**
```cpp
#include "MyCustomBehaviourNode.h"
#include "Behaviour/RCBehaviour.h"
#include "Action/RCAction.h"

UMyCustomBehaviourNode::UMyCustomBehaviourNode()
{
    DisplayName = NSLOCTEXT("MyCustomNode", "DisplayName", "My Custom Logic");
    BehaviorDescription = NSLOCTEXT("MyCustomNode", "Description", "Executes actions with a custom message.");
    CustomMessage = FText::FromString(TEXT("Default Message"));
}

bool UMyCustomBehaviourNode::IsSupported(URCBehaviour* InBehaviour) const
{
    // 示例：仅支持具有一个或多个动作的行为
    return InBehaviour && InBehaviour->GetNumActions() > 0;
}

bool UMyCustomBehaviourNode::Execute(URCBehaviour* InBehaviour) const
{
    UE_LOG(LogTemp, Log, TEXT("Executing MyCustomBehaviourNode: %s"), *CustomMessage.ToString());
    // 总是返回 true，表示条件通过，将触发 OnPassed
    return true;
}

void UMyCustomBehaviourNode::OnPassed(URCBehaviour* InBehaviour) const
{
    UE_LOG(LogTemp, Log, TEXT("MyCustomBehaviourNode Passed! Executing all actions."));
    // 调用基类的 OnPassed 来执行所有关联的动作
    Super::OnPassed(InBehaviour);
}

UClass* UMyCustomBehaviourNode::GetBehaviourClass() const
{
    // 返回此节点所关联的行为类，通常使用基类 URCBehaviour
    return URCBehaviour::StaticClass();
}
```

## 模块依赖

`RemoteControlLogic` 模块的 `Build.cs` 显示它依赖于 `RemoteControlCommon` 模块。

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 提供 Remote Control 插件的通用基础结构、类型和接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 为内置动作补充了缺失的颜色轮盘增量应用功能。 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed  uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了函数调用参数中ObjectClass未初始化可能导致的错误。 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 增加了远程函数调用的白名单机制，并指定内置函数的调用权限。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |

### 维护评价

- **活跃维护**：该插件是 Unreal Engine Virtual Production 工作流的核心组件之一。从最近的提交历史看（最近一次更新在2026年5月），它仍在被 Epic Games 积极维护和增强，主要关注功能完善、稳定性提升和与引擎新特性的集成。
- **稳定性与推荐度**：作为成熟的生产工具，其稳定性和可靠性非常高。对于需要高级远程控制、自动化或自定义UI面板的虚拟制片、广播或自动化项目，**强烈推荐使用**。尽管它包含许多复杂概念，但其良好的架构设计使其具备了强大的扩展能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlLogic)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/remote-control-in-unreal-engine/) (Remote Control 插件总览)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlLogic/Tests) (位于模块内的 `Private/Tests` 目录)