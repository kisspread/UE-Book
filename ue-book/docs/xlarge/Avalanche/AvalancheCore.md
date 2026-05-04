# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、媒体处理、序列化支持） |
| 模块 | `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequencer` (Runtime), ... 等41个模块 |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 Unreal Engine 中一个用于虚拟制片和广播的综合性 Motion Design 系统。它不仅仅是一个简单的合成工具，而是一个完整的图形设计、动画和实时播出框架。该插件的核心目的是为广播图形、体育直播、虚拟演播室和实时图形包装提供一个在引擎内完成设计、预览和播出的端到端解决方案。它解决了传统上需要在外部图形软件（如 After Effects）中设计，再导入引擎的繁琐流程，实现了设计与实时渲染的无缝集成。

## 使用场景

-   **虚拟制片与广播**：你需要在虚拟演播室中实时生成动态的 lower-thirds（字幕条）、比分板、天气预报图形等，并需要在直播中实时控制和更新它们。
-   **体育直播**：你需要一个可实时编辑、动画化并播出的计分板、球员数据统计和赛事回放图形系统。
-   **活动与演出**：你需要为现场活动（如发布会、演唱会）设计和控制复杂的实时视觉特效和动态背景。
-   **动态图形设计**：你希望直接在 UE 编辑器中像使用专业 Motion Graphics 软件一样，设计复杂的图形动画序列，并利用 UE 的渲染能力进行高质量预览。

## 蓝图用法

Avalanche 的核心功能主要通过其丰富的编辑器工具和自定义资产类型暴露，而非传统的蓝图函数节点。其设计哲学是提供一个完整的“Motion Design”编辑器环境。主要的交互发生在：

1.  **Avalanche 编辑器面板**：一个专门的编辑器模式或面板，用于创建和管理“场景”（Scenes）、“元素”（Elements，如文本、形状、SVG）以及它们的动画。
2.  **Sequencer 集成**：动画通过与 Sequencer 深度集成的自定义轨道进行控制，允许在时间轴上精确编排图形元素的属性动画。
3.  **远程控制**：通过 `AvalancheRemoteControl` 模块，可以在运行时或通过外部协议（如 OSC）远程控制图形参数，实现直播中的实时更新。

### 核心节点

由于该插件主要面向编辑器和运行时图形系统，其公开的 `BlueprintCallable` API 相对较少，更多是内部引擎和编辑器工具链。核心的交互和控制逻辑封装在编辑器工具和 Sequencer 轨道中。

## C++ 用法

Avalanche 插件建立了一套自己的类型系统和基础架构，主要在 `AvalancheCore` 模块中定义。

### 头文件引入

```cpp
#include "AvaType.h"
#include "AvaTypeId.h"
#include "AvaPropertyChangeDispatcher.h"
#include "AvaWorldSubsystemUtils.h"
```

### 基本用法

**1. 定义自定义的 Ava 类型**
Avalanche 使用 `FAvaTypeId` 和 `UE_AVA_TYPE` 宏来建立其内部的类型识别系统，用于元素和属性的动态类型转换。
```cpp
// MyMotionElement.h
#include "AvaType.h"

class UMyMotionElement : public UObject
{
    GENERATED_BODY()
public:
    // 声明这是一个 Ava 类型，并指定其父类型
    UE_AVA_TYPE(UMyMotionElement, UAvaBaseElement)
    
    // ... 元素逻辑
};
```
*来源：`AvalancheCore/Public/AvaType.h`*

**2. 响应属性变更**
`TAvaPropertyChangeDispatcher` 是一个编辑器辅助工具，用于将 UObject 属性的变更（例如在细节面板中修改）映射到特定的成员函数调用。
```cpp
// MyMotionElement.cpp
#include "AvaPropertyChangeDispatcher.h"

#if WITH_EDITOR
// 定义属性变更分发器，将属性名映射到处理函数
static const TAvaPropertyChangeDispatcher<UMyMotionElement> PropertyChangeDispatcher = {
    { GET_MEMBER_NAME_CHECKED(UMyMotionElement, TextContent), &UMyMotionElement::OnTextContentChanged },
    { GET_MEMBER_NAME_CHECKED(UMyMotionElement, Color), &UMyMotionElement::OnColorChanged },
};

void UMyMotionElement::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);
    // 使用分发器处理属性变更
    PropertyChangeDispatcher.OnPropertyChanged(this, PropertyChangedEvent);
}

void UMyMotionElement::OnTextContentChanged()
{
    // 更新文本渲染逻辑
    UpdateTextRender();
}
#endif
```
*来源：`AvalancheCore/Public/AvaPropertyChangeDispatcher.h`*

**3. 获取世界子系统**
`TAvaWorldSubsystemInterface` 提供了一个便捷的模板方法，用于安全地获取与特定世界上下文关联的子系统。
```cpp
#include "AvaWorldSubsystemUtils.h"
#include "MyAvalancheSubsystem.h" // 假设你有一个自定义子系统

void SomeFunction(const UObject* WorldContextObject)
{
    // 安全地获取自定义的 Avalanche 子系统
    UMyAvalancheSubsystem* Subsystem = UMyAvalancheSubsystem::Get(WorldContextObject, /*bGenerateErrors=*/true);
    if (Subsystem)
    {
        Subsystem->DoSomething();
    }
}
```
*来源：`AvalancheCore/Public/AvaWorldSubsystemUtils.h`*

### 进阶用法

Avalanche 的复杂功能，如媒体合成、序列器集成和远程控制，需要组合使用多个模块。例如，创建一个可远程控制的动态文本元素，可能涉及：
1.  继承自 `AvalancheText` 模块中的文本元素基类。
2.  使用 `AvalancheSequencer` 模块为其添加自定义的 Sequencer 轨道以控制动画。
3.  通过 `AvalancheRemoteControl` 模块将其属性暴露给远程控制协议。
4.  在 `AvalancheMedia` 模块的管理下，将其输出作为媒体源进行合成或播出。

## Demo 示例

以下是一个最小化的示例，展示如何定义一个自定义的 Motion Design 元素并处理其属性变更。

**MySimpleShapeElement.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AvaType.h"
#include "UObject/NoExportTypes.h"
#include "MySimpleShapeElement.generated.h"

UCLASS()
class UMySimpleShapeElement : public UObject
{
    GENERATED_BODY()

public:
    UE_AVA_TYPE(UMySimpleShapeElement, UObject)

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shape")
    FLinearColor ShapeColor = FLinearColor::White;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shape")
    float Size = 100.0f;

#if WITH_EDITOR
    void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif

private:
#if WITH_EDITOR
    void OnShapeColorChanged();
    void OnSizeChanged();
#endif
};
```

**MySimpleShapeElement.cpp**
```cpp
#include "MySimpleShapeElement.h"
#include "AvaPropertyChangeDispatcher.h"

#if WITH_EDITOR
static const TAvaPropertyChangeDispatcher<UMySimpleShapeElement> ShapePropertyDispatcher = {
    { GET_MEMBER_NAME_CHECKED(UMySimpleShapeElement, ShapeColor), &UMySimpleShapeElement::OnShapeColorChanged },
    { GET_MEMBER_NAME_CHECKED(UMySimpleShapeElement, Size), &UMySimpleShapeElement::OnSizeChanged },
};

void UMySimpleShapeElement::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);
    ShapePropertyDispatcher.OnPropertyChanged(this, PropertyChangedEvent);
}

void UMySimpleShapeElement::OnShapeColorChanged()
{
    UE_LOG(LogTemp, Log, TEXT("Shape color changed to: %s"), *ShapeColor.ToString());
    // 在此处更新渲染颜色
}

void UMySimpleShapeElement::OnSizeChanged()
{
    UE_LOG(LogTemp, Log, TEXT("Shape size changed to: %f"), Size);
    // 在此处更新渲染尺寸
}
#endif
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*注：该插件本身依赖众多其他插件（如 Media Compositing, Sequencer, Text3D 等），但作为使用者，你的项目模块通常只需依赖 `AvalancheCore` 或具体的 `AvalancheXxx` 运行时模块，这些模块的依赖已在插件内部处理。*

## 维护状态

### 近期更新

```
- 2024-01-30 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

-   **创建时间**：2024年1月，是一个相对较新的插件。
-   **最近更新**：最近的提交记录是将其从 `Experimental` 目录正式迁移至 `VirtualProduction` 目录。这标志着该插件已通过实验阶段，成为官方虚拟制片工具链的一部分。但自迁移后，暂无更多公开的功能性更新记录。
-   **活跃度**：作为 Epic Games 官方维护的虚拟制片核心组件，预计会持续维护和更新，但其更新节奏可能与 UE 版本发布周期绑定。
-   **已知限制**：这是一个极其庞大和复杂的系统（xlarge 级别），学习曲线陡峭。其内部架构（如自定义类型系统）可能与 UE 的标准实践有所不同。
-   **推荐使用**：**强烈推荐**给所有从事虚拟制片、广播图形和实时动态设计的团队。它是 UE 在该领域的官方解决方案，功能强大且与引擎深度集成。对于新项目，应直接使用此插件而非寻找第三方替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/) (UE 官方文档中的 Motion Design 章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Tests)