# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一套用于通过网络（HTTP/WebSocket）远程控制 Unreal Engine 的工具集。它解决的核心问题是：**允许第三方应用程序、Web 服务或自动化脚本在编辑器或运行时动态地查询和修改引擎中的对象属性、调用函数，以及执行复杂的逻辑序列**。

其存在意义在于为虚拟制片（Virtual Production）、自动化测试、远程调试和自定义工具链提供强大的集成基础。它不仅仅是简单的属性暴露，更构建了一个包含“控制器”（Controller）、“行为”（Behaviour）和“动作”（Action）的完整逻辑系统，使得远程控制可以具备条件判断、值映射、资产路径解析等高级功能。

## 使用场景

- **虚拟制片**：在片场通过平板电脑或自定义控制面板，远程调整灯光参数、材质颜色、摄像机位置等。
- **自动化测试与批处理**：编写脚本批量修改大量 Actor 的属性，或执行一系列预设操作以测试游戏逻辑。
- **自定义编辑器工具**：开发基于 Web 的编辑器扩展，提供比默认 UI 更灵活或更专业的控制界面。
- **远程调试**：在不直接访问编辑器的情况下，实时查看和修改游戏状态。
- **多用户协作**：结合 `RemoteControlMultiUser` 模块，在多人协作编辑时同步控制状态。

## 蓝图用法

Remote Control 的蓝图 API 主要围绕 `URCController`（控制器）、`URCBehaviour`（行为）和 `URCAction`（动作）这三个核心概念展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddBehaviour` | 为控制器添加一个新的行为节点（如 Bind, Conditional）。 | `URCController` |
| `ExecuteBehaviours` | 触发控制器上所有已添加行为的执行。 | `URCController` |
| `AddAction` | 向行为中添加一个具体的动作（如设置某个属性值）。 | `URCBehaviour` |
| `Execute` | 执行单个动作。 | `URCAction` |
| `IsSupported` | 检查当前行为节点是否支持给定的行为实例。 | `URCBehaviourNode` |
| `OnPassed` | 当行为条件检查通过时调用的事件。 | `URCBehaviourNode` |

### 使用示例（蓝图描述）

1.  **创建控制器**：在 Remote Control Preset 资产中，通过 UI 或蓝图创建一个 `URCController`，并为其指定一个属性类型（如 Float）。
2.  **添加行为**：调用控制器的 `AddBehaviour` 节点，传入一个行为节点类（例如 `URCBehaviourBindNode` 的类引用）。
3.  **配置行为**：获取返回的 `URCBehaviour` 对象，调用其 `AddAction` 节点，传入一个远程控制属性（`FRemoteControlProperty`）的引用，将该属性与控制器绑定。
4.  **触发执行**：当控制器的值发生变化时（例如通过 Web API 修改），调用 `ExecuteBehaviours`。绑定行为会自动将控制器的新值传播到所有绑定的属性上。

## C++ 用法

### 头文件引入

```cpp
#include "Controller/RCController.h"
#include "Behaviour/RCBehaviour.h"
#include "Action/RCAction.h"
#include "Behaviour/Builtin/Bind/RCBehaviourBind.h"
```

### 基本用法

以下代码演示了如何在 C++ 中程序化地创建一个控制器并为其添加一个绑定行为。

```cpp
// 假设 InPreset 是一个有效的 URemoteControlPreset* 指针
// 1. 创建一个 Float 类型的控制器
URCController* Controller = InPreset->GetControllerContainer()->AddProperty(
    TEXT("MyFloatController"),
    URCController::StaticClass(),
    EPropertyBagPropertyType::Float
);

// 2. 为控制器添加一个绑定行为
URCBehaviour* BindBehaviour = Controller->AddBehaviour(URCBehaviourBindNode::StaticClass());

// 3. 假设我们有一个已暴露的远程控制属性 (RemoteControlProperty)
TSharedPtr<FRemoteControlProperty> ExposedProperty = ...; // 获取方式省略

// 4. 向绑定行为中添加一个动作，将控制器与这个属性关联
if (BindBehaviour && ExposedProperty.IsValid())
{
    URCAction* Action = BindBehaviour->AddAction(ExposedProperty.ToSharedRef());
    // Action 现在代表了“将控制器的值设置到该属性”这个逻辑
}

// 5. 当需要触发时，执行控制器的所有行为
Controller->ExecuteBehaviours();
```

### 进阶用法

可以创建自定义的行为节点（Behaviour Node）来实现复杂的逻辑。

```cpp
// MyCustomBehaviourNode.h
#pragma once
#include "Behaviour/RCBehaviourNode.h"
#include "MyCustomBehaviourNode.generated.h"

UCLASS()
class UMyCustomBehaviourNode : public URCBehaviourNode
{
    GENERATED_BODY()
public:
    UMyCustomBehaviourNode();

    virtual bool IsSupported(URCBehaviour* InBehaviour) const override;
    virtual bool Execute(URCBehaviour* InBehaviour) const override;
    virtual void OnPassed(URCBehaviour* InBehaviour) const override;
};

// MyCustomBehaviourNode.cpp
#include "MyCustomBehaviourNode.h"
#include "Behaviour/RCBehaviour.h"

UMyCustomBehaviourNode::UMyCustomBehaviourNode()
{
    DisplayName = NSLOCTEXT("MyBehaviors", "CustomNode", "My Custom Logic");
    BehaviorDescription = NSLOCTEXT("MyBehaviors", "CustomNodeDesc", "Executes custom logic when triggered.");
}

bool UMyCustomBehaviourNode::IsSupported(URCBehaviour* InBehaviour) const
{
    // 在此检查该行为是否适用于当前控制器类型等
    return true;
}

bool UMyCustomBehaviourNode::Execute(URCBehaviour* InBehaviour) const
{
    // 执行核心逻辑，返回 true 表示条件通过，将调用 OnPassed
    // 例如：检查某个全局状态
    return true;
}

void UMyCustomBehaviourNode::OnPassed(URCBehaviour* InBehaviour) const
{
    // 条件通过后，执行所有关联的动作
    InBehaviour->ExecuteInternal(InBehaviour->GetActionContainer()->GetActions());
}
```

## Demo 示例

一个最小的自定义行为节点示例，当控制器值大于 0.5 时，执行其所有绑定的动作。

```cpp
// ThresholdBehaviourNode.h
#pragma once
#include "Behaviour/RCBehaviourNode.h"
#include "ThresholdBehaviourNode.generated.h"

UCLASS()
class UThresholdBehaviourNode : public URCBehaviourNode
{
    GENERATED_BODY()
public:
    UThresholdBehaviourNode();

    virtual bool IsSupported(URCBehaviour* InBehaviour) const override;
    virtual bool Execute(URCBehaviour* InBehaviour) const override;
    virtual void OnPassed(URCBehaviour* InBehaviour) const override;

    /** 阈值，可在蓝图或编辑器中配置 */
    UPROPERTY(EditAnywhere, Category = "Threshold")
    float Threshold = 0.5f;
};
```

```cpp
// ThresholdBehaviourNode.cpp
#include "ThresholdBehaviourNode.h"
#include "Behaviour/RCBehaviour.h"
#include "Controller/RCController.h"
#include "RCVirtualProperty.h"

UThresholdBehaviourNode::UThresholdBehaviourNode()
{
    DisplayName = NSLOCTEXT("Demo", "Threshold", "Threshold Check");
    BehaviorDescription = NSLOCTEXT("Demo", "ThresholdDesc", "Executes actions if the controller value is above a threshold.");
}

bool UThresholdBehaviourNode::IsSupported(URCBehaviour* InBehaviour) const
{
    // 确保关联的控制器是数值类型
    if (URCController* Controller = InBehaviour->GetController())
    {
        EPropertyBagPropertyType ValueType = Controller->GetValueType();
        return ValueType == EPropertyBagPropertyType::Float ||
               ValueType == EPropertyBagPropertyType::Double ||
               ValueType == EPropertyBagPropertyType::Int32 ||
               ValueType == EPropertyBagPropertyType::Int64;
    }
    return false;
}

bool UThresholdBehaviourNode::Execute(URCBehaviour* InBehaviour) const
{
    if (URCController* Controller = InBehaviour->GetController())
    {
        // 获取控制器当前值（假设为 Float）
        TOptional<float> Value = Controller->GetValue<float>();
        if (Value.IsSet())
        {
            // 比较是否超过阈值
            return Value.GetValue() > Threshold;
        }
    }
    return false;
}

void UThresholdBehaviourNode::OnPassed(URCBehaviour* InBehaviour) const
{
    // 条件通过，执行该行为容器下的所有动作
    InBehaviour->ExecuteInternal(InBehaviour->GetActionContainer()->GetActions());
}
```

## 模块依赖

从 `RemoteControlLogic` 模块的头文件和常见依赖推断，使用此插件的核心逻辑部分需要以下依赖：

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 提供远程控制的基础数据结构和通用工具。 |
| `StructUtils` | 提供 `PropertyBag` 等高级结构工具，用于实现虚拟属性容器。 |
| `HTTP` | 用于处理 HTTP 请求（主要在 `WebRemoteControl` 模块中）。 |
| `WebSockets` | 用于处理 WebSocket 通信（主要在 `WebRemoteControl` 模块中）。 |

## 维护状态

### 近期更新

```
- 683817828fdc 2025-10-03 Remote Control: Updated the tooltips and icons for the path behavior again.
- 6217f4e5078a 2025-09-15 Remote Control: Redux for the new path behavior visual indication update.
- 85d0f7b02e8b 2025-08-20 Remote Control: Small fix to path behavior for invalid controllers
```

### 维护评价

Remote Control 插件创建于 2019 年，是一个相对成熟的老牌插件。从近期的 git 历史看，**维护状态活跃**。最近的提交（2025年8月至10月）集中在对“路径行为”（Path Behavior）功能的优化和修复上，包括视觉指示更新和错误处理，表明 Epic 仍在积极开发和完善其功能。

该插件是 Unreal Engine 虚拟制片和自动化工作流的核心组件之一，功能强大且复杂。由于其架构设计良好（模块化、可扩展），并且有持续的维护，**强烈推荐在需要远程控制引擎的场景中使用**。需要注意的是，由于其功能丰富，学习曲线可能较陡峭。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/)