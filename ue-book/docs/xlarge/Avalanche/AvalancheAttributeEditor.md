# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche) 是一个为 Unreal Engine 5 构建的综合性动态图形设计与虚拟制作工具集。它并非一个简单的功能插件，而是一个完整的、模块化的生产环境，旨在将 After Effects 或 Cinema 4D 等专业动态图形软件的工作流直接引入 UE5 的实时渲染环境中。

该插件的核心目标是解决在游戏引擎中直接进行广播级动态图形设计、实时合成和特效制作的需求。它提供了从基础形状、文本、遮罩、动画到媒体合成、远程控制、序列器集成和最终渲染输出的完整工具链。其模块化架构允许用户根据项目需求灵活启用或禁用特定功能，例如仅使用形状和文本工具，或启用完整的媒体合成管线。

## 使用场景

- **虚拟制作与实时广播**：为虚拟演播室、体育赛事直播或新闻节目创建实时更新的动态图形、比分板、标题和过渡效果。
- **动态图形与视觉特效设计**：直接在 UE5 中设计复杂的动态图形动画、粒子效果和合成镜头，利用引擎的实时渲染能力进行即时预览。
- **交互式内容与展览**：为博物馆、零售店或活动创建交互式数字标牌和视觉装置，内容可通过远程控制实时更新。
- **电影与广告预览**：快速搭建和迭代广告片或电影中的动态图形序列，利用 Sequencer 进行精确的时间线控制。

## 蓝图用法

Motion Design 的蓝图功能高度模块化，分布在各个子模块中。由于当前分析的模块 (`AvalancheAttributeEditor`) 主要提供编辑器扩展，其核心蓝图节点较少。更丰富的蓝图功能存在于如 `AvalancheShapes`、`AvalancheText`、`AvalancheMedia` 等运行时模块中。

### 核心节点 (AvalancheAttributeEditor 模块)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizeAttributes` | 用于在细节面板中定制属性（Attribute）的显示和编辑方式。这是一个编辑器专用函数，通常由系统内部调用以实现自定义UI。 | `IAvaAttributeEditorModule` |

### 使用示例（蓝图描述）

由于 `CustomizeAttributes` 是一个底层编辑器接口，通常不直接在用户蓝图中调用。其使用场景是：当开发者创建了自定义的 `UAvaAttribute` 子类，并希望为其在“细节”面板中提供独特的编辑界面时，需要在 C++ 中实现一个对应的 `IAvaAttributeEditorModule` 扩展，并在该函数中构建自定义的 Slate UI。蓝图层面，用户主要通过 Motion Design 编辑器面板与这些属性交互。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaAttributeEditorModule.h"
```

### 基本用法

以下代码展示了如何获取 `AvalancheAttributeEditor` 模块的实例并调用其核心方法。这通常发生在需要为自定义属性类型提供编辑器支持的场景中。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheAttributeEditor/Public/IAvaAttributeEditorModule.h
// 假设在某个编辑器扩展代码中
if (IAvaAttributeEditorModule::IsLoaded())
{
    IAvaAttributeEditorModule& AttributeEditorModule = IAvaAttributeEditorModule::Get();
    
    // 获取一个属性句柄 (通常来自 IDetailLayoutBuilder)
    TSharedRef<IPropertyHandle> MyAttributeHandle = ...; 
    
    // 获取当前的细节布局构建器
    IDetailLayoutBuilder& DetailBuilder = ...;
    
    // 调用模块方法来定制该属性在细节面板中的显示
    AttributeEditorModule.CustomizeAttributes(MyAttributeHandle, DetailBuilder);
}
```

### 进阶用法

`AvalancheAttributeEditor` 模块是 Motion Design 属性系统的一部分。一个更完整的用法涉及创建自定义属性 (`UAvaAttribute` 子类) 并为其注册编辑器定制器。

1.  **定义自定义属性 (Runtime 模块)**:
    ```cpp
    // MyCustomAttribute.h
    #include "AvaAttribute.h"
    
    UCLASS()
    class UMyCustomAttribute : public UAvaAttribute
    {
        GENERATED_BODY()
    public:
        UPROPERTY(EditAnywhere, BlueprintReadWrite)
        float MyValue;
    };
    ```

2.  **创建编辑器定制器 (Editor 模块)**:
    ```cpp
    // MyCustomAttributeEditor.h
    #include "IAvaAttributeEditorModule.h"
    
    class FMyCustomAttributeEditor : public IAvaAttributeEditorModule
    {
    public:
        virtual void CustomizeAttributes(const TSharedRef<IPropertyHandle>& InAttributesHandle, IDetailLayoutBuilder& InDetailBuilder) override
        {
            // 在这里为 UMyCustomAttribute 构建自定义的 Slate UI
            // 例如，添加一个滑块、一个颜色选择器或一个自定义控件
            TSharedRef<IPropertyHandle> ValueHandle = InAttributesHandle->GetChildHandle(GET_MEMBER_NAME_CHECKED(UMyCustomAttribute, MyValue));
            
            IDetailCategoryBuilder& Category = InDetailBuilder.EditCategory(TEXT("MyCustom"));
            Category.AddCustomRow(TEXT("MyValueRow"))
            .NameContent()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Value")))
            ]
            .ValueContent()
            [
                ValueHandle->CreatePropertyValueWidget()
            ];
        }
    };
    ```

## Demo 示例

以下是一个最小化的示例，演示如何创建一个简单的自定义属性编辑器模块。

**MyAttributeEditorModule.h**
```cpp
#pragma once

#include "IAvaAttributeEditorModule.h"

class FMyAttributeEditorModule : public IAvaAttributeEditorModule
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // IAvaAttributeEditorModule interface
    virtual void CustomizeAttributes(const TSharedRef<IPropertyHandle>& InAttributesHandle, IDetailLayoutBuilder& InDetailBuilder) override;
};
```

**MyAttributeEditorModule.cpp**
```cpp
#include "MyAttributeEditorModule.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "PropertyHandle.h"
#include "Widgets/Input/SVectorInputBox.h"

#define LOCTEXT_NAMESPACE "FMyAttributeEditorModule"

void FMyAttributeEditorModule::StartupModule()
{
    // 模块启动时的初始化代码
}

void FMyAttributeEditorModule::ShutdownModule()
{
    // 模块关闭时的清理代码
}

void FMyAttributeEditorModule::CustomizeAttributes(const TSharedRef<IPropertyHandle>& InAttributesHandle, IDetailLayoutBuilder& InDetailBuilder)
{
    // 这是一个示例：为所有属性添加一个通用的“强度”滑块
    // 实际应用中，你需要检查 InAttributesHandle 指向的具体属性类型
    
    IDetailCategoryBuilder& Category = InDetailBuilder.EditCategory(TEXT("CustomControls"));
    
    // 添加一个自定义行，包含一个标签和一个滑块
    Category.AddCustomRow(LOCTEXT("IntensityRow", "Intensity"))
    .NameContent()
    [
        SNew(STextBlock)
        .Text(LOCTEXT("IntensityLabel", "Effect Intensity"))
        .Font(IDetailLayoutBuilder::GetDetailFont())
    ]
    .ValueContent()
    .MaxDesiredWidth(200.0f)
    [
        SNew(SSlider)
        .Value_Lambda([InAttributesHandle]() -> float
        {
            float Value = 0.0f;
            InAttributesHandle->GetValue(Value);
            return Value;
        })
        .OnValueChanged_Lambda([InAttributesHandle](float NewValue)
        {
            InAttributesHandle->SetValue(NewValue);
        })
    ];
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyAttributeEditorModule, MyAttributeEditor)
```

## 模块依赖

Motion Design 插件依赖众多其他插件和模块来实现其完整功能。以下是其独特的、不常见的依赖项。

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 提供高级的资产重命名功能，用于批量管理场景中的对象。 |
| `CustomDetailsView` | 允许创建高度定制化的“细节”面板视图，是 Motion Design UI 的基础。 |
| `DynamicMaterial` | 提供动态材质实例创建和管理工具，用于实时材质编辑。 |
| `GeometryCache` | 支持几何体缓存，用于导入和播放预计算的网格动画。 |
| `GeometryScripting` | 提供基于蓝图的几何体操作脚本功能。 |
| `MediaCompositing` | 提供媒体合成框架，用于将视频、图像等媒体源与3D场景合成。 |
| `MediaIOFramework` | 提供媒体输入/输出的底层框架支持。 |
| `MeshModelingToolsetExp` | 提供实验性的网格建模工具集，用于在编辑器中直接建模。 |
| `RemoteControl` | 提供远程控制API，允许外部应用程序控制UE编辑器和运行时。 |
| `SVGImporter` | 支持SVG文件的导入，用于创建矢量图形。 |
| `Text3D` | 提供3D文本渲染功能。 |
| `ActorModifierCore` | 提供Actor修改器核心框架，用于程序化修改Actor属性。 |
| `Sequencer` | (AvalanchePropertyAnimator依赖) 与UE5的Sequencer时间线深度集成。 |

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

**活跃维护**。Motion Design (Avalanche) 是 Epic Games 为虚拟制作领域推出的重量级工具集，于 2024 年初正式从实验性阶段迁移至 `VirtualProduction` 目录，标志着其进入生产就绪状态。作为 Epic 官方支持的插件，它得到了持续的开发和维护。其庞大的模块化架构和深度集成的特性表明它是一个长期项目。虽然创建时间不长，但其代码库规模巨大且更新积极，是 UE5 虚拟制作管线中的核心组件之一，**强烈推荐**给所有从事虚拟制作、广播和动态图形设计的用户。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/) (UE5.7 文档中的 Motion Design 章节)