# DMX Pixel Mapping

> Tools set for map LED digital pixel strip or fixture arrays regardless of shape or size

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping) | |

## 用途

DMX Pixel Mapping 是 UE5 虚拟制片工具链中的 LED 像素映射系统。它解决的核心问题是：**如何将任意形状和尺寸的 LED 灯带、灯具阵列与 DMX 协议数据进行精确映射**。

在虚拟制片场景中，LED 墙（LED Volume）通常由大量像素组成，这些像素需要通过 DMX 协议控制。DMX Pixel Mapping 提供了一套完整的工具链：

1. **像素布局设计**：在编辑器中可视化地定义 LED 像素的空间排列（支持任意形状）
2. **DMX 通道映射**：将像素位置映射到 DMX 宇宙（Universe）中的具体通道
3. **实时渲染**：将场景中的渲染内容捕获并转换为 DMX 数据流
4. **蓝图集成**：通过自定义蓝图节点在运行时动态控制像素映射

该插件是 UE5 虚拟制片（Virtual Production）工作流的关键组件，与 DMX 插件生态系统紧密集成。

## 使用场景

- 你在搭建 LED Volume 虚拟制片环境 → 用 DMX Pixel Mapping 将 LED 墙的像素映射到 DMX 控制器
- 你需要控制大量 LED 灯带组成的艺术装置 → 用 DMX Pixel Mapping 定义像素布局并实时驱动
- 你在做演唱会/舞台灯光的虚拟预览 → 用 DMX Pixel Mapping 将渲染画面输出到 DMX 网络
- 你需要在蓝图中动态获取或修改像素映射组件 → 用 DMXPixelMappingBlueprintGraph 提供的自定义节点

## 模块概览

本插件包含 6 个模块，各司其职：

| 模块 | 类型 | 职责 |
|---|---|---|
| `DMXPixelMappingCore` | Runtime | 核心数据结构、像素映射基础类型定义 |
| `DMXPixelMappingRuntime` | Runtime | 运行时逻辑，像素映射的执行引擎 |
| `DMXPixelMappingRenderer` | Runtime | 渲染器，将场景内容捕获并转换为 DMX 数据 |
| `DMXPixelMappingBlueprintGraph` | Runtime | 自定义蓝图 K2 节点，用于蓝图中访问像素映射组件 |
| `DMXPixelMappingEditor` | Runtime | 编辑器工具，像素映射的可视化编辑界面 |
| `DMXPixelMappingEditorWidgets` | Runtime | 编辑器 UI 控件库 |

## 蓝图用法

DMXPixelMappingBlueprintGraph 模块提供了自定义的蓝图节点，允许在蓝图中通过组件名称动态获取像素映射组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Renderer Component` | 通过组件名称（FName）从 Pixel Mapping 对象中获取 Renderer 组件指针 | `UK2Node_PixelMappingRendererComponent` |

### 节点特性

- **纯函数节点**（Pure Node）：所有像素映射蓝图节点都是纯函数，不执行任何副作用，仅返回数据
- **动态组件查找**：通过 FName 而非直接引用来查找组件，解决了非公开 UObject 引用无法跨 uasset 保存的问题
- **自动验证**：节点在编译时会验证输入的 Pixel Mapping 对象和组件名称是否有效

### 使用示例（蓝图描述）

1. 在蓝图中添加 **"Get Renderer Component"** 节点
2. 连接一个 **DMX Pixel Mapping** 对象到 `InPixelMapping` 输入引脚
3. 在 `InRendererComponent` 引脚中输入目标 Renderer 组件的名称（FName）
4. `OutRendererComponent` 输出引脚将返回对应的 Renderer 组件对象引用
5. 可以将输出连接到其他需要 Renderer 组件的节点

## C++ 用法

### 头文件引入

```cpp
#include "K2Node_PixelMappingRendererComponent.h"
#include "K2Node_PixelMappingBaseComponent.h"
```

### 基本用法 — 自定义 K2 节点扩展

DMXPixelMappingBlueprintGraph 模块的 K2 节点采用继承体系设计。基类 `UK2Node_PixelMappingBaseComponent` 提供了通用的蓝图节点框架，子类只需实现特定的组件查找逻辑。

```cpp
// 自定义一个获取特定类型组件的 K2 节点
// 参考: K2Node_PixelMappingRendererComponent.h

UCLASS()
class UMyCustomPixelMappingNode : public UK2Node_PixelMappingBaseComponent
{
    GENERATED_BODY()

public:
    // 纯函数节点，不执行副作用
    virtual bool IsNodePure() const override { return true; }

    // 定义节点的输入输出引脚
    virtual void AllocateDefaultPins() override
    {
        Super::AllocateDefaultPins();
        // 基类已创建 InPixelMapping 引脚
        // 添加自定义的组件名称输入引脚
        CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Name, 
                  TEXT("ComponentName"));
        // 添加组件对象输出引脚
        CreatePin(EGPD_Output, UEdGraphSchema_K2::PC_Object, 
                  TEXT("OutComponent"));
    }

    // 节点标题
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
    {
        return NSLOCTEXT("MyModule", "NodeTitle", 
                         "Get My Custom Component");
    }

    // 编译时展开节点逻辑
    virtual void ExpandNode(FKismetCompilerContext& CompilerContext,
                            UEdGraph* SourceGraph) override
    {
        Super::ExpandNode(CompilerContext, SourceGraph);
        // 使用基类的 ExecuteExpandNode 辅助方法
        ExecuteExpandNode(
            CompilerContext,
            SourceGraph,
            GET_FUNCTION_NAME_CHECKED(UDMXPixelMappingSubsystem, 
                                      GetMyComponent),
            FindPin(TEXT("ComponentName")),
            FindPin(TEXT("OutComponent"))
        );
    }

    // 注册到蓝图动作数据库
    virtual void GetMenuActions(
        FBlueprintActionDatabaseRegistrar& ActionRegistrar) const override
    {
        UClass* ActionKey = GetClass();
        if (ActionRegistrar.IsOpenForRegistration(ActionKey))
        {
            AddBlueprintAction(ActionKey, ActionRegistrar);
        }
    }
};
```

### 进阶用法 — 响应像素映射变更

基类提供了 `OnPixelMappingChanged` 回调机制，当像素映射对象发生变化时自动刷新蓝图图：

```cpp
// 当 Pixel Mapping 对象中的组件发生重命名或结构变化时
// 节点会自动更新引脚和默认值
virtual void OnPixelMappingChanged(UDMXPixelMapping* InDMXPixelMapping) override
{
    // 基类提供了辅助方法来处理名称变更
    UEdGraphPin* ComponentNamePin = FindPin(InComponentNamePinName);
    TryModifyBlueprintOnNameChanged(InDMXPixelMapping, ComponentNamePin);
    
    // 刷新图以反映新的组件结构
    TryRefreshGraphCheckInputPins(GetInPixelMappingPin(), ComponentNamePin);
}
```

### 编译时验证

```cpp
// 在蓝图编译前验证输入的有效性
virtual void EarlyValidation(FCompilerResultsLog& MessageLog) const override
{
    Super::EarlyValidation(MessageLog);
    
    UEdGraphPin* ComponentPin = FindPin(InRendererComponentPinName);
    if (ComponentPin)
    {
        // 使用基类的验证辅助方法
        ExecuteEarlyValidation(MessageLog, ComponentPin);
    }
}
```

## Demo 示例

### 自定义像素映射蓝图节点

以下示例展示如何创建一个自定义的 K2 节点，用于从 DMX Pixel Mapping 中获取特定类型的组件：

**MyPixelMappingNode.h**
```cpp
#pragma once

#include "K2Node_PixelMappingBaseComponent.h"
#include "MyPixelMappingNode.generated.h"

/**
 * 自定义蓝图节点：从 Pixel Mapping 获取 Fixture 组件
 */
UCLASS()
class MYPROJECT_API UMyPixelMappingFixtureNode 
    : public UK2Node_PixelMappingBaseComponent
{
    GENERATED_BODY()

public:
    //~ Begin UEdGraphNode Interface
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual FText GetTooltipText() const override;
    virtual void AllocateDefaultPins() override;
    virtual void PinDefaultValueChanged(UEdGraphPin* ChangedPin) override;
    //~ End UEdGraphNode Interface

    //~ Begin UK2Node Interface
    virtual bool IsNodePure() const override { return true; }
    virtual void ExpandNode(class FKismetCompilerContext& CompilerContext,
                            UEdGraph* SourceGraph) override;
    virtual void GetMenuActions(
        FBlueprintActionDatabaseRegistrar& ActionRegistrar) const override;
    virtual void EarlyValidation(class FCompilerResultsLog& MessageLog) const override;
    //~ End UK2Node Interface

    //~ Begin UK2Node_PixelMappingBaseComponent Interface
    virtual void OnPixelMappingChanged(UDMXPixelMapping* InDMXPixelMapping) override;
    //~ End UK2Node_PixelMappingBaseComponent Interface

public:
    UEdGraphPin* GetInFixtureComponentPin() const;
    UEdGraphPin* GetOutFixtureComponentPin() const;

    static const FName InFixtureComponentPinName;
    static const FName OutFixtureComponentPinName;
};
```

**MyPixelMappingNode.cpp**
```cpp
#include "MyPixelMappingFixtureNode.h"
#include "KismetCompiler.h"
#include "DMXPixelMapping.h"

const FName UMyPixelMappingFixtureNode::InFixtureComponentPinName = 
    TEXT("InFixtureComponent");
const FName UMyPixelMappingFixtureNode::OutFixtureComponentPinName = 
    TEXT("OutFixtureComponent");

FText UMyPixelMappingFixtureNode::GetNodeTitle(
    ENodeTitleType::Type TitleType) const
{
    return NSLOCTEXT("MyModule", "GetFixtureComponent", 
                     "Get Fixture Component");
}

FText UMyPixelMappingFixtureNode::GetTooltipText() const
{
    return NSLOCTEXT("MyModule", "GetFixtureComponentTooltip",
                     "Gets a Fixture Component from a Pixel Mapping "
                     "object by its name");
}

void UMyPixelMappingFixtureNode::AllocateDefaultPins()
{
    // 调用基类创建 InPixelMapping 引脚
    Super::AllocateDefaultPins();

    // 输入：组件名称
    UEdGraphPin* InNamePin = CreatePin(
        EEdGraphPinDirection::EGPD_Input,
        UEdGraphSchema_K2::PC_Name,
        InFixtureComponentPinName);
    InNamePin->PinFriendlyName = 
        NSLOCTEXT("MyModule", "FixtureName", "Fixture Name");

    // 输出：组件对象引用
    UEdGraphPin* OutPin = CreatePin(
        EEdGraphPinDirection::EGPD_Output,
        UEdGraphSchema_K2::PC_Object,
        UObject::StaticClass(),
        OutFixtureComponentPinName);
    OutPin->PinFriendlyName = 
        NSLOCTEXT("MyModule", "FixtureComponent", "Fixture Component");
}

void UMyPixelMappingFixtureNode::PinDefaultValueChanged(
    UEdGraphPin* ChangedPin)
{
    if (ChangedPin && ChangedPin->PinName == InFixtureComponentPinName)
    {
        UEdGraphPin* PixelMappingPin = GetInPixelMappingPin();
        TryRefreshGraphCheckInputPins(PixelMappingPin, ChangedPin);
    }
}

void UMyPixelMappingFixtureNode::ExpandNode(
    FKismetCompilerContext& CompilerContext,
    UEdGraph* SourceGraph)
{
    Super::ExpandNode(CompilerContext, SourceGraph);

    UEdGraphPin* InNamePin = FindPinChecked(InFixtureComponentPinName);
    UEdGraphPin* OutPin = FindPinChecked(OutFixtureComponentPinName);

    // 使用基类的 ExpandNode 辅助方法连接到子系统函数
    ExecuteExpandNode(
        CompilerContext,
        SourceGraph,
        GET_FUNCTION_NAME_CHECKED(UDMXPixelMappingSubsystem, 
                                  GetFixtureComponent),
        InNamePin,
        OutPin
    );
}

void UMyPixelMappingFixtureNode::GetMenuActions(
    FBlueprintActionDatabaseRegistrar& ActionRegistrar) const
{
    UClass* ActionKey = GetClass();
    if (ActionRegistrar.IsOpenForRegistration(ActionKey))
    {
        AddBlueprintAction(ActionKey, ActionRegistrar);
    }
}

void UMyPixelMappingFixtureNode::EarlyValidation(
    FCompilerResultsLog& MessageLog) const
{
    Super::EarlyValidation(MessageLog);

    UEdGraphPin* ComponentPin = FindPin(InFixtureComponentPinName);
    if (ComponentPin)
    {
        ExecuteEarlyValidation(MessageLog, ComponentPin);
    }
}

void UMyPixelMappingFixtureNode::OnPixelMappingChanged(
    UDMXPixelMapping* InDMXPixelMapping)
{
    UEdGraphPin* ComponentNamePin = FindPin(InFixtureComponentPinName);
    TryModifyBlueprintOnNameChanged(InDMXPixelMapping, ComponentNamePin);
    TryRefreshGraphCheckInputPins(GetInPixelMappingPin(), ComponentNamePin);
}

UEdGraphPin* UMyPixelMappingFixtureNode::GetInFixtureComponentPin() const
{
    return FindPinChecked(InFixtureComponentPinName);
}

UEdGraphPin* UMyPixelMappingFixtureNode::GetOutFixtureComponentPin() const
{
    return FindPinChecked(OutFixtureComponentPinName);
}
```

## 模块依赖

### DMXPixelMappingBlueprintGraph

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingCore` | 像素映射核心数据类型 |
| `DMXPixelMappingRuntime` | 运行时子系统访问 |
| `KismetCompiler` | 蓝图编译器框架，用于 K2 节点展开 |
| `BlueprintGraph` | 蓝图图编辑器支持 |

### DMXPixelMappingCore / DMXPixelMappingRuntime / DMXPixelMappingRenderer

无特殊依赖（仅标准 Core/Engine/Slate 等）

### DMXPixelMappingEditor / DMXPixelMappingEditorWidgets

无特殊依赖（仅标准编辑器模块）

## 维护状态

### 近期更新

```
- f333b1c99a59 DMX - Remove type aliases to improve readability of pixel mapping code, reduce inclusion of monolithic headers
- 5612575f47c8 DMX - Fix various PixelMapping UX bugs
- d3cf046ac7a9 Lay groundwork for avoiding SGraphPanel refreshes after making a change to a single node by adding a NotifyNodeChanged routine to UEdGraph, currently implemented to just invoke NotifyGraphChanged with no additional context #rb Justin.Hare, Andrew.Davidson #preflight 640a9da7d778f88975ed4702 #jira UE-158391
```

- `f333b1c99a59`：代码可读性改进，移除类型别名，减少巨型头文件包含 — 表明代码正在进行现代化重构
- `5612575f47c8`：修复多个像素映射 UX 问题 — 持续的用户体验优化
- `d3cf046ac7a9`：为避免 SGraphPanel 不必要的刷新做基础工作 — 性能优化，涉及蓝图图编辑器的响应性改进

### 维护评价

**活跃维护** ✅

- **创建时间**：2020 年 9 月，约 5 年历史，属于成熟的虚拟制片工具
- **更新频率**：近期有持续的功能改进和 bug 修复，包括代码重构、UX 修复和性能优化
- **维护团队**：由 Epic Games 官方维护，有明确的 reviewer 和 jira 工单追踪
- **代码质量**：正在进行代码现代化（移除类型别名、减少头文件依赖），表明团队重视长期可维护性
- **推荐使用**：✅ 作为 UE5 虚拟制片工作流的核心组件，推荐在 LED Volume 和 DMX 控制场景中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping)
- [官方文档]()（暂无）
- [测试用例]()（待确认）