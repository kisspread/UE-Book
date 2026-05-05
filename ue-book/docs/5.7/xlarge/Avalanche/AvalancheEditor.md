# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个为虚拟制片和广播场景设计的综合性动态图形（Motion Graphics）创作与合成工具集。它并非一个单一功能的插件，而是一个庞大的生态系统，旨在将 Unreal Engine 转变为一个专业的实时动态图形设计工作站和广播输出引擎。

它解决的核心问题是：在 Unreal Engine 中高效地创建、编辑、合成和播出复杂的 2D/3D 动态图形内容。传统上，这类工作需要在 After Effects 等专用软件中完成，而 Avalanche 将这些能力深度集成到 UE 的实时渲染和场景管理流程中，特别适合需要实时预览和播出的虚拟制片、电视广播、现场活动等场景。

## 使用场景

- **电视广播与新闻包装**：设计和播出实时更新的新闻标题、比分板、天气图表、选举数据可视化等。
- **现场活动与演唱会**：为舞台 LED 屏幕创建和控制实时动态背景、歌词、特效和互动视觉。
- **虚拟制片**：在 LED Volume 拍摄中，实时生成和调整背景图形、虚拟广告牌、UI 元素。
- **企业演示与产品发布**：制作高保真度的产品展示动画、数据可视化图表和品牌宣传片。
- **教育内容制作**：创建交互式教学动画和科学可视化。

## 蓝图用法

由于插件规模巨大（xlarge），其蓝图 API 分布在众多子模块中。核心功能通常通过 `AvalancheMedia`、`AvalancheSequencer`、`AvalancheShapes` 等模块暴露。以下为基于模块结构推断的核心功能节点分类：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Output` | 创建一个媒体输出目标（如 NDI, SDI） | `UAvaMediaSubsystem` |
| `Play Sequence` | 播放一个 Motion Design 序列 | `UAvaSequencePlayer` |
| `Spawn Shape Actor` | 在场景中生成一个基础图形（矩形、圆形等） | `UAvaShapeLibrary` |
| `Apply Modifier` | 对一个图形或 Actor 应用修改器（如扭曲、变形） | `UAvaModifierComponent` |
| `Set Remote Control Value` | 通过远程控制协议设置参数值 | `UAvaRemoteControlSubsystem` |

### 使用示例（蓝图描述）

1.  **创建一个动态标题**：
    - 使用 `Spawn Text3D Actor` 节点生成一个 3D 文字。
    - 通过 `Set Text` 和 `Set Material` 节点配置其内容和外观。
    - 使用 `Create Property Animation` 节点为其添加位置、旋转或缩放动画。
    - 最后，通过 `Add to Sequence` 节点将其加入到一个 `AvaSequence` 中进行时间线控制。

2.  **实时合成到视频流**：
    - 使用 `Create Media Output` 节点配置一个 NDI 输出。
    - 将包含动态图形的 `AvaScene` 或 `AvaSequence` 连接到该输出。
    - 调用 `Start Media Output` 节点，即可将实时渲染的图形作为视频流发送到导播台或其他软件。

## C++ 用法

由于插件模块众多，C++ 用法高度依赖于具体功能。以下示例基于通用模式和测试框架推断。

### 头文件引入

```cpp
// 引入核心媒体模块
#include "AvalancheMediaModule.h"
// 引入序列模块
#include "AvalancheSequenceModule.h"
// 引入图形模块
#include "AvalancheShapesModule.h"
```

### 基本用法

以下代码演示如何通过 C++ 创建一个简单的图形并控制其属性。

```cpp
// 假设在某个 Actor 或 Subsystem 中
#include "AvalancheShapes/Public/AvaShapeRectangleActor.h"
#include "AvalancheSequence/Public/AvaSequence.h"

void UMyMotionDesignManager::CreateSimpleGraphic()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 1. 生成一个矩形图形 Actor
    FActorSpawnParameters SpawnParams;
    AAvaShapeRectangleActor* RectActor = World->SpawnActor<AAvaShapeRectangleActor>(
        AAvaShapeRectangleActor::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams
    );

    if (RectActor)
    {
        // 2. 设置其尺寸和颜色
        RectActor->SetSize(FVector2D(200.f, 100.f));
        RectActor->SetFillColor(FLinearColor::Blue);

        // 3. (可选) 将其添加到一个序列中进行动画控制
        UAvaSequence* MySequence = FindObject<UAvaSequence>(World->GetCurrentLevel(), TEXT("MyAnimSequence"));
        if (MySequence)
        {
            MySequence->AddActor(RectActor);
        }
    }
}
```

### 进阶用法

结合远程控制，实现外部数据驱动图形。

```cpp
#include "AvalancheRemoteControl/Public/AvaRemoteControlPreset.h"
#include "AvalancheRemoteControl/Public/AvaRemoteControlSubsystem.h"

void UMyMotionDesignManager::BindGraphicToRemoteControl(AAvaShapeRectangleActor* InRectActor, UAvaRemoteControlPreset* InPreset)
{
    if (!InRectActor || !InPreset) return;

    // 获取远程控制子系统
    UAvaRemoteControlSubsystem* RCSubsystem = GetWorld()->GetSubsystem<UAvaRemoteControlSubsystem>();
    if (!RCSubsystem) return;

    // 将矩形的“填充颜色”属性暴露给远程控制预设
    FRemoteControlPresetExposeArgs Args;
    Args.Label = TEXT("RectangleColor");
    RCSubsystem->ExposeProperty(InPreset, InRectActor, GET_MEMBER_NAME_CHECKED(AAvaShapeRectangleActor, FillColor), Args);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何注册一个自定义的 Motion Design 修改器。

```cpp
// MyCustomModifier.h
#pragma once

#include "AvalancheModifiers/Public/AvaModifier.h"
#include "MyCustomModifier.generated.h"

UCLASS()
class UMyCustomModifier : public UAvaModifier
{
    GENERATED_BODY()

public:
    // 修改器的主执行函数
    virtual void ApplyModifier(UAvaModifierComponent* InComponent) override;

    // 在编辑器细节面板中显示的属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "My Modifier")
    float Intensity = 1.0f;
};
```

```cpp
// MyCustomModifier.cpp
#include "MyCustomModifier.h"
#include "AvalancheModifiers/Public/AvaModifierComponent.h"

void UMyCustomModifier::ApplyModifier(UAvaModifierComponent* InComponent)
{
    if (!InComponent) return;

    // 获取被修改的目标 Actor
    AActor* TargetActor = InComponent->GetOwner();
    if (!TargetActor) return;

    // 示例：根据 Intensity 缩放目标 Actor
    FVector NewScale = TargetActor->GetActorScale() * Intensity;
    TargetActor->SetActorScale3D(NewScale);

    // 这里可以添加更复杂的几何或材质修改逻辑
}
```

## 模块依赖

Avalanche 插件依赖于众多 UE 子系统和第三方插件。在你的项目模块中使用其功能时，需要在 `Build.cs` 中添加相应依赖。

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 核心媒体合成框架，用于视频输入输出和合成 |
| `MediaIOFramework` | 媒体 IO 硬件抽象层，支持 SDI, NDI 等 |
| `RemoteControl` | 远程控制 API，用于外部数据驱动和参数暴露 |
| `Text3D` | 3D 文字渲染和动画 |
| `GeometryScripting` | 程序化几何体生成和操作 |
| `SVGImporter` | SVG 矢量图形导入 |
| `DynamicMaterial` | 运行时动态材质创建和编辑 |
| `ActorModifierCore` | Actor 修改器系统核心框架 |
| `Sequencer` | 核心动画序列器，Avalanche 序列的基础 |

## 维护状态

### 近期更新

```
- 019444fdaa28 Motion Design: added ticker section bubble for ticker properties
- b1cb14ebd90a Motion Design: The spawn defaults buttons are now localized.
- bdd5a9cb6d2e Motion Design: fix issue where having an operator stack, or material designer details opened would cause sequencer to not be closeable
```

### 维护评价

- **活跃维护**：插件创建于 2024 年初，非常年轻（🆕）。从最近的提交记录看，开发团队正在积极添加新功能（如 ticker 属性面板）、进行本地化工作并修复关键的 UI 交互 Bug。这表明该插件处于**活跃开发和维护**阶段。
- **推荐使用**：对于虚拟制片和广播领域的项目，Avalanche 是 Epic 官方提供的强大且不断进化的解决方案。尽管作为新插件，其 API 和功能可能仍在快速迭代中，但它是该领域在 UE 内的未来方向，**强烈推荐**相关项目评估和使用。需要注意其庞大的依赖关系和可能的学习曲线。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/) (UE 5.7 文档中的 Motion Design 章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEditor/Internal/Tests) (AvalancheEditor 模块内的测试框架)