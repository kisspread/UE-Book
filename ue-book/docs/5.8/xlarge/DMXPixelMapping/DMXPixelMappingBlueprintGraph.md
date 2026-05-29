# DMX Pixel Mapping Blueprint Graph

> 蓝图图形系统集成模块，提供用于访问和操作DMX像素映射组件的专用蓝图节点和相关编辑器工具。

| 属性 | 值 |
|---|---|
| 中文名 | 像素映射蓝图图 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DMXPixelMappingBlueprintGraph` (Runtime), `DMXPixelMappingCore` (Runtime), `DMXPixelMappingEditor` (Runtime), `DMXPixelMappingEditorWidgets` (Runtime), `DMXPixelMappingRenderer` (Runtime), `DMXPixelMappingRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-08-04 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingBlueprintGraph) | |

## 用途

该模块是 DMXPixelMapping 插件的蓝图系统集成层，其核心功能是**扩展蓝图编辑器**，为设计师提供可在蓝图中使用的、用于访问和驱动DMX像素映射组件的专用节点和接口。它解决了在蓝图中直接引用和操作DMX像素映射器（`UDMXPixelMapping`）中非公开的内部组件（如渲染器组件）的难题。通过提供自定义的K2节点和引脚控件，使得设计师无需编写C++代码，即可在蓝图图表中构建复杂的DMX像素映射控制工作流。

## 使用场景

- 你在开发一个基于蓝图的虚拟制作节目，并需要**在蓝图中动态控制DMX LED阵列的渲染器组件**。
- 你需要创建一个**自定义的蓝图节点**，用于从特定的像素映射器对象中获取渲染器组或组件，并执行进一步操作。
- 你希望**改进蓝图编辑器中像素映射组件引脚的选择体验**，使用用户友好的名称而非技术性FName进行组件选择。

## 蓝图用法

此模块主要通过提供自定义蓝图节点（K2 Node）和增强蓝图引脚（Graph Pin）来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Pixel Mapping Renderer Component` | 根据输入的像素映射对象和渲染器组件名称（FName），动态获取并输出对应的渲染器组件对象。这是一个纯函数节点。 | `UK2Node_PixelMappingRendererComponent` |

### 使用示例（蓝图描述）

1.  **获取渲染器组件**：
    *   在蓝图中添加 `Get Pixel Mapping Renderer Component` 节点。
    *   为 `In Pixel Mapping` 引脚连接你的 `UDMXPixelMapping` 对象（例如通过变量或其它节点获取）。
    *   在 `In Renderer Component` 引脚的下拉菜单中，从当前像素映射器中选择一个渲染器组件。该下拉列表由 `SDMXPixelMappingComponentPin` 提供，显示的是用户友好的组件名称。
    *   节点的 `Out Renderer Component` 引脚将输出对应的组件对象引用，可用于后续的属性设置或函数调用。

## C++ 用法

该模块主要用于编辑器扩展和蓝图系统定制，其公共API相对集中。

### 头文件引入

```cpp
#include "DMXPixelMappingBlueprintGraph.h"
```

### 基本用法：创建自定义K2节点

以下示例展示了如何创建一个基于 `UK2Node_PixelMappingBaseComponent` 的自定义节点。
（来源：`Public/K2Node_PixelMappingRendererComponent.h` 和 `Public/K2Node_PixelMappingBaseComponent.h`）

```cpp
#include "K2Node_PixelMappingBaseComponent.h"

UCLASS()
class UMyCustomPixelMappingNode : public UK2Node_PixelMappingBaseComponent
{
    GENERATED_BODY()

public:
    // 重写此函数以定义节点的标题
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
    {
        return FText::FromString(TEXT("My Custom PM Node"));
    }

    // 重写此函数以创建节点的输入输出引脚
    virtual void AllocateDefaultPins() override
    {
        Super::AllocateDefaultPins();
        // 添加自定义引脚...
        CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Boolean, TEXT("MyInput"));
        CreatePin(EGPD_Output, UEdGraphSchema_K2::PC_Float, TEXT("MyOutput"));
    }

    // 重写此函数以定义编译时的展开逻辑（将节点扩展为更低级的蓝图操作）
    virtual void ExpandNode(FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph) override
    {
        Super::ExpandNode(CompilerContext, SourceGraph);
        // 使用基类提供的辅助函数 ExecuteExpandNode 来连接到C++子系统函数
        // 例如：ExecuteExpandNode(CompilerContext, SourceGraph, GET_FUNCTION_NAME_CHECKED(UMySubsystem, MyFunction), MyComponentNamePin, MyOutputPin);
    }

    // 监听像素映射器变化，可重写以更新节点状态（例如刷新引脚选项）
    virtual void OnPixelMappingChanged(UDMXPixelMapping* InDMXPixelMapping) override
    {
        // 调用基类实现以触发图刷新等逻辑
        Super::OnPixelMappingChanged(InDMXPixelMapping);
        // 自定义响应逻辑...
    }
};
```

### 进阶用法：自定义蓝图引脚控件

`SDMXPixelMappingComponentPin` 是一个模板类，用于为特定类型的像素映射组件创建带有下拉选择框的引脚控件。
（来源：`Private/Widgets/SDMXPixelMappingComponentPin.h`）

```cpp
// 假设我们有一个自定义的组件类 UDMXMyCustomComponent
#include "Widgets/SDMXPixelMappingComponentPin.h"

// 在你的 GraphPinFactory (FDMXPixelMappingPinFactory) 中，根据引脚类型创建不同的控件
TSharedPtr<SGraphPin> FDMXPixelMappingPinFactory::CreatePin(UEdGraphPin* InPin) const
{
    // 检查引脚元数据，判断是否需要创建自定义的像素映射组件选择控件
    if (InPin->PinType.PinCategory == TEXT("MyCustomComponentPin"))
    {
        // 获取关联的像素映射对象
        UDMXPixelMapping* PixelMapping = /* 从上下文获取 */;
        // 创建模板实例化的控件，例如用于 UDMXMyCustomComponent 类型
        return SNew(SDMXPixelMappingComponentPin<UDMXMyCustomComponent>, InPin, PixelMapping);
    }
    return nullptr;
}
```

## Demo 示例

一个最小化的自定义蓝图节点，演示如何继承基类并设置基本结构。

**MySimplePixelMappingNode.h**
```cpp
#pragma once
#include "K2Node_PixelMappingBaseComponent.h"
#include "MySimplePixelMappingNode.generated.h"

UCLASS()
class UMySimplePixelMappingNode : public UK2Node_PixelMappingBaseComponent
{
    GENERATED_BODY()

public:
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual void AllocateDefaultPins() override;
    virtual bool IsNodePure() const override { return true; }
    virtual void ExpandNode(FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph) override;
    virtual void GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar) const override;

    // 自定义输入引脚名
    static const FName InMyDataPinName;
    // 自定义输出引脚名
    static const FName OutResultPinName;
};
```

**MySimplePixelMappingNode.cpp**
```cpp
#include "MySimplePixelMappingNode.h"
#include "K2Node_PixelMappingBaseComponent.h"
#include "BlueprintActionDatabaseRegistrar.h"
#include "BlueprintNodeSpawner.h"
#include "KismetCompiler.h"

const FName UMySimplePixelMappingNode::InMyDataPinName(TEXT("MyData"));
const FName UMySimplePixelMappingNode::OutResultPinName(TEXT("Result"));

FText UMySimplePixelMappingNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
    return FText::FromString(TEXT("Simple PM Node"));
}

void UMySimplePixelMappingNode::AllocateDefaultPins()
{
    Super::AllocateDefaultPins(); // 创建基类像素映射器引脚
    CreatePin(EGPD_Input, UEdGraphSchema_K2::PC_Int, InMyDataPinName);
    CreatePin(EGPD_Output, UEdGraphSchema_K2::PC_Float, OutResultPinName);
}

void UMySimplePixelMappingNode::ExpandNode(FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph)
{
    Super::ExpandNode(CompilerContext, SourceGraph);
    // 此处添加编译期节点展开逻辑，将此节点连接到实际执行计算的C++函数
    // 通常使用 CompilerContext 和 SourceGraph 来生成中间节点
}

void UMySimplePixelMappingNode::GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar) const
{
    UClass* ActionKey = GetClass();
    if (ActionRegistrar.IsOpenForRegistration(ActionKey))
    {
        UBlueprintNodeSpawner* Spawner = UBlueprintNodeSpawner::Create(GetClass());
        check(Spawner);
        ActionRegistrar.AddBlueprintAction(ActionKey, Spawner);
    }
}
```

## 模块依赖

`DMXPixelMappingBlueprintGraph` 模块依赖于以下DMX相关模块：

| 模块 | 用途 |
|---|---|
| `DMXPixelMappingCore` | 提供核心的像素映射器 (`UDMXPixelMapping`) 和组件 (`UDMXPixelMappingComponent`) 类定义。 |
| `DMXPixelMappingRuntime` | 提供运行时逻辑，是此蓝图节点在编译后执行计算的基础。 |

*(注：此模块也依赖标准的编辑器模块如 `UnrealEd`, `Kismet`, `BlueprintGraph` 等用于蓝图编辑器集成，这些为常见依赖，已省略。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `5f2a2a90` | DMX - Fix a crash when pixel mapping has unpatched components and draws patch colors | 修复当像素映射包含未打补丁组件并绘制补丁颜色时发生的崩溃。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport... | 重构视口相关逻辑，当客户端与视口关联/解除关联时进行通知。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的某个提交（CL53913857）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport... | 视口逻辑重构的另一部分，与上条相关。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生警告的代码。 |

### 维护评价

该模块**仍在活跃维护**。从Git历史看，最近一次更新（2026-05-20）修复了一个具体的运行时崩溃问题，表明开发团队仍在处理缺陷和保证稳定性。虽然更新频率不算密集，但持续的错误修复表明它是一个被持续关注的、对虚拟制作工作流有实际用途的模块。对于需要在蓝图中深度集成DMX像素映射功能的用户来说，它是一个可靠且推荐使用的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Source/DMXPixelMappingBlueprintGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXPixelMapping/Tests) (通常包含在插件的Tests目录下)