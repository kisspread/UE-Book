# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、示例） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design (Avalanche) 是一个集成在 Unreal Engine 中的专业级动态图形（Motion Graphics）设计与合成工具套件。它旨在为虚拟制片、广播图形、实时合成和互动媒体内容创作提供一站式工作流程。

其核心目标是解决传统动态图形制作流程繁琐、与实时引擎割裂的问题。该插件通过深度集成 Unreal Engine 的渲染、材质、动画和编辑器功能，让用户能够直接在引擎内设计、预览和输出高品质的动态图形与合成效果，极大简化了从设计到直播或最终输出的过程。

## 使用场景

*   **广播与直播图形**：创建用于电视节目、体育赛事、新闻直播的实时 Lower Thirds（字幕条）、全屏图形、比分牌、天气预报等。
*   **虚拟舞台与场景**：为虚拟制片（Virtual Production）设计和构建包含动态元素（如粒子、文字、形状、材质动画）的虚拟场景。
*   **宣传片与内容包装**：快速制作产品宣传片、频道ID、片头片尾等需要动态设计和合成的内容。
*   **互动媒体与体验**：为博物馆、展览、互动装置设计实时交互的视觉内容。
*   **复杂场景合成**：在场景中组合多种几何体（文字、形状）、材质、动画、媒体源，并精确控制它们的层次和混合模式。

## 蓝图用法

Motion Design 主要通过编辑器内的专用工具、面板和资产进行操作。其核心蓝图交互体现在对资产的创建、编辑和驱动上。

### 核心资产类型

| 资产 | 说明 | 创建方式 |
|---|---|---|
| `Ava Tag Collection` | 标签集合，用于组织和管理动画标签、事件等。 | 内容浏览器右键 → Animation → Ava Tag Collection |
| `Ava Material` | 动态材质，用于在 Motion Design 中驱动复杂的材质动画。 | 内容浏览器右键 → Materials & Textures → Ava Material |
| `Ava Scene` | 场景资产，用于存储和管理复杂的 Motion Design 场景布局、动画和状态。 | 通过 Motion Design 编辑器创建 |

### 设计器用法

1.  **Motion Design 编辑器**：通过主工具栏的“Motion Design”按钮打开。这是进行场景布局、动画编辑和实时预览的核心界面。
2.  **标签系统**：使用 `Ava Tag Collection` 定义标签，在 `AvaTagHandle` 等结构体中引用这些标签，用于驱动动画状态机、事件触发或逻辑分支。
3.  **资产选择器**：在细节面板中，带有 `Ava Tag Handle` 类型的属性会显示一个自定义的下拉选择器（如 `SAvaTagPicker`），用于快速选择和配置标签。

## C++ 用法

### 头文件引入

由于 Motion Design 是一个庞大的插件集合，具体的头文件引入取决于你使用的功能模块。通常，你会包含对应功能模块的头文件。例如，使用标签编辑器功能时：

```cpp
#include "AvalancheTagEditor/AvaTagEditorModule.h"
```

### 基本用法（以标签系统为例）

标签系统允许你定义和管理用于驱动各种逻辑的命名标签。以下是其核心概念的伪代码示例。

```cpp
// 假设在某个自定义类中需要引用一个标签
#include "AvalancheTag/AvaTagHandle.h"

UCLASS()
class UMyAnimController : public UObject
{
    GENERATED_BODY()

public:
    // 在类中定义一个标签句柄属性，可在编辑器中配置
    UPROPERTY(EditAnywhere, Category = "Animation")
    FAvaTagHandle ActiveStateTag;

    // 函数：检查当前标签是否匹配
    void CheckAnimationState()
    {
        if (ActiveStateTag.IsValid())
        {
            // 使用标签进行逻辑判断或驱动动画
            UE_LOG(LogTemp, Log, TEXT("Current animation state tag: %s"), *ActiveStateTag.ToString());
        }
    }
};
```

`AvalancheTagEditor` 模块提供了自定义的细节面板（`FAvaTagHandleCustomization`），使得在编辑器中选择和配置 `FAvaTagHandle` 属性变得非常直观。

### 进阶用法（自定义属性定制）

`AvalancheTagEditor` 展示了如何为自定义结构体实现高级的属性编辑器UI。你可以参考其模式（`IAvaTagHandleCustomizer` 接口，`SAvaTagPicker` 控件）来为自己的插件创建类似的定制化编辑器体验。

```cpp
// 1. 定义你的自定义结构体
USTRUCT(BlueprintType)
struct FMyCustomData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    FAvaTagHandle RequiredTag;

    UPROPERTY(EditAnywhere)
    FName DisplayValue;
};

// 2. (在编辑器模块中) 创建一个定制类，实现 IPropertyTypeCustomization
class FMyCustomDataCustomization : public IPropertyTypeCustomization
{
public:
    virtual void CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, FDetailWidgetRow& Row, IPropertyTypeCustomizationUtils& Utils) override
    {
        // 使用类似 SAvaTagPicker 的逻辑，创建自定义的下拉选择器
        Row.NameContent()
            [PropertyHandle->CreatePropertyNameWidget()]
        .ValueContent()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("Custom Picker Here")))
                // 实际应用中，这里会放置一个组合按钮和列表
            ];
    }
};

// 3. 在编辑器模块的 StartupModule 中注册
void FMyEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomPropertyTypeLayout("MyCustomData", FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMyCustomDataCustomization::MakeInstance));
}
```

## Demo 示例

以下是一个最小化的示例，展示如何创建一个简单的类，使用 Motion Design 的标签系统来管理状态。请注意，运行此示例需要启用 `AvalancheTag` 和 `AvalancheTagEditor` 插件。

### MyStatefulActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvalancheTag/AvaTagHandle.h" // 引入标签句柄头文件
#include "MyStatefulActor.generated.h"

UCLASS()
class AMyStatefulActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStatefulActor();

protected:
    virtual void BeginPlay() override;

public:
    // 在编辑器中设置的“激活”标签
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "State")
    FAvaTagHandle ActiveState;

    // 在编辑器中设置的“待机”标签
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "State")
    FAvaTagHandle IdleState;

    UFUNCTION(BlueprintCallable, Category = "State")
    void Activate();

    UFUNCTION(BlueprintCallable, Category = "State")
    void Deactivate();

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* VisualMesh;
};
```

### MyStatefulActor.cpp
```cpp
#include "MyStatefulActor.h"
#include "UObject/ConstructorHelpers.h"

AMyStatefulActor::AMyStatefulActor()
{
    PrimaryActorTick.bCanEverTick = false;

    VisualMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisualMesh"));
    RootComponent = VisualMesh;

    // 简单加载一个立方体网格体
    static ConstructorHelpers::FObjectFinder<UStaticMesh> MeshAsset(TEXT("/Engine/BasicShapes/Cube"));
    if (MeshAsset.Succeeded())
    {
        VisualMesh->SetStaticMesh(MeshAsset.Object);
    }
}

void AMyStatefulActor::BeginPlay()
{
    Super::BeginPlay();
    // 初始状态设为待机
    // 实际使用时，可能需要从 Ava Tag Collection 中查找标签，这里简化为直接创建
    IdleState = FAvaTagHandle(FName("Idle"));
}

void AMyStatefulActor::Activate()
{
    // 将当前状态设置为“激活”标签
    // 实际项目中，通常会从某个 Ava Tag Collection 资产中获取预定义的标签句柄
    ActiveState = FAvaTagHandle(FName("Active"));
    UE_LOG(LogTemp, Log, TEXT("Actor %s activated with tag: %s"), *GetName(), *ActiveState.ToString());
}

void AMyStatefulActor::Deactivate()
{
    // 切换回“待机”状态
    ActiveState = IdleState;
    UE_LOG(LogTemp, Log, TEXT("Actor %s deactivated, switched to tag: %s"), *GetName(), *ActiveState.ToString());
}
```

## 模块依赖

Motion Design 是一个大型插件，其核心模块依赖众多。要使用其完整功能，你的项目或模块需要依赖以下插件/模块（根据你的具体需求选择）：

| 模块/插件 | 用途 |
|---|---|
| `AdvancedRenamer` | 提供高级重命名工具，用于批量管理资产。 |
| `CustomDetailsView` | 提供自定义细节面板视图，是编辑器UI定制的基础。 |
| `DynamicMaterial` | 提供动态材质编辑和创建功能，用于 Motion Design 的材质动画。 |
| `GeometryCache` | 用于几何体缓存，可能用于导入或缓存复杂动画几何体。 |
| `GeometryScripting` | 提供蓝图和脚本中的几何体操作能力。 |
| `MediaCompositing` | 提供媒体合成功能，用于在场景中混合视频、图像等媒体源。 |
| `MediaIOFramework` | 媒体输入输出框架，处理硬件视频捕获和输出。 |
| `MeshModelingToolsetExp` | 实验性网格建模工具集，可能用于创建或编辑形状。 |
| `RemoteControl` | 远程控制协议，用于外部应用（如 TouchDesigner, Vizrt）控制 Unreal 中的参数。 |
| `SVGImporter` | SVG文件导入器，用于导入矢量图形作为形状资产。 |
| `Text3D` | 提供3D文字生成功能。 |
| `ActorModifierCore` | Actor修改器核心，用于应用批量修改或动画。 |
| `ClonerEffector` | 克隆器与效果器，用于创建基于规则的实例化（粒子、阵列）效果。 |
| `GeometryMask` | 几何遮罩，用于实现高级遮罩和合成效果。 |
| `OperatorStack` | 操作器栈，用于构建复杂的、节点式的数据处理流程。 |
| `PropertyAnimator` / `PropertyAnimatorCore` | 属性动画器，用于在时间线上对任何属性进行关键帧动画。 |
| `StormSync` | 场景同步协议，用于多机同步播放或备份。 |
| `Sequencer` | UE 的核心序列编辑器，用于创建电影和动画序列。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的场景设置和大纲视图标签页在关卡编辑器中独立分组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用节目单页面设置时，增加了影片渲染队列（MRQ）的分析统计。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、选中），并增加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用Text3D和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口代码，当客户端关联或取消关联时进行通知，以减少重复代码。 |

### 维护评价

Motion Design (Avalanche) 插件正处于**极其活跃**的维护期。
*   **创建时间**：虽然首次提交记录于2025年5月，但这是从实验性分支迁移而来的官方记录，其实际开发历史更长。
*   **更新频率**：最近的提交记录显示，截至2026年5月，该插件仍在**按周甚至按日**进行密集的功能更新和优化。更新内容涉及编辑器UX、性能分析、项目设置、视口优化等多个方面。
*   **功能范围**：它作为一个“全家桶”式的解决方案，集成了动态图形设计所需的几乎所有子系统（形状、文字、材质、特效、媒体、动画、远程控制等），且这些子模块（如ClonerEffector， PropertyAnimator）都得到了同步维护。
*   **评价**：这是 Epic Games 官方为虚拟制片和广播行业打造的战略性产品，享有最高的开发优先级。**强烈推荐**给需要进行实时动态图形设计、广播图形或虚拟制片的团队使用。它功能全面、更新及时，并能与 UE 的最新特性保持同步。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档（暂无特定链接，通常集成在 UE 官方文档的 Virtual Production 或 Motion Graphics 板块）
- 测试用例（插件内部包含 `AvalancheFunctionalTest` 模块，路径为 `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest/`）