# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheMedia` (Runtime), `AvalancheShapes` (Runtime), `AvalancheText` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheTransition` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheSequencer` (Runtime), ... (共43个模块) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个专为**虚拟制作和广播**设计的综合性动态图形（Motion Graphics）设计与播出工具集。它解决的核心问题是：在 UE 实时渲染环境中，提供一套完整的工作流来设计、排版、编辑和控制复杂的动态图形元素，并能够与媒体播放、远程控制和序列器深度集成，最终实现类似广播级节目包装或虚拟舞台背景的实时输出。

它不仅仅是几个小工具的集合，而是一个庞大的系统，包含了从基础图元（形状、文本）、材质编辑、修改器（变形、克隆、效果器）、场景搭建（摄像机、灯光、布局）、过渡动画到最终通过 Movie Render Queue 渲染或直接播出控制的完整管线。

## 使用场景

-   你在制作一个虚拟新闻演播室，需要实时设计并控制动态背景板、Lower Thirds、天气预报图等动态图形。
-   你需要在电视转播或大型活动直播中，通过 Rundown 系统（播控单）精确控制多个动态图形画面的切换和播放。
-   你希望创建复杂的、可程序化控制的动态材质效果，例如流动的光效、数据驱动的图表。
-   你需要利用 MediaIO 将外部视频源与 UE 中的动态图形进行实时合成。
-   你希望使用非破坏性的修改器工作流（如克隆、扭曲、路径动画）来快速迭代动态图形设计。

## 蓝图用法

基于该插件的模块结构和典型用法，其核心蓝图功能围绕设计、控制和渲染展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Ava Shape` | 创建一个基础几何形状（矩形、圆形等）作为动态图形元素。 | `UAvaShapesSubsystem` |
| `Apply Effectors` | 将克隆器、扭曲器等效果器应用到一组 Actor 上，产生程序化动画。 | `UAvaClonerSubsystem` / `UAvaEffectorSubsystem` |
| `Open Rundown Page` | 在 Rundown（播控单）中打开指定页面，触发该页面下的所有图形和播放逻辑。 | `UAvaRundownSubsystem` |
| `Start Remote Control Preset` | 启动一个远程控制预设，用于通过外部设备（如 Stream Deck）控制动态图形参数。 | `UAvaRemoteControlSubsystem` |
| `Trigger Transition` | 在两个动态图形场景或状态之间触发预设的过渡动画。 | `UAvaTransitionSubsystem` |
| `Set Media Source` | 为动态图形元素（如屏幕面）设置媒体源，用于播放视频或捕获实时画面。 | `UAvaMediaSubsystem` |

### 使用示例（蓝图描述）

1.  **创建基础元素**：在关卡蓝图中，使用 `Create Ava Shape` 节点，选择形状类型（如 `Rectangle`），生成一个 Actor。通过该 Actor 的暴露属性（如 `Size`, `Material`）在蓝图中进行调整。
2.  **应用效果器**：创建多个形状 Actor 作为“种子”，然后使用一个 `Ava Cloner` Actor，将这些种子 Actor 设置为克隆源。再将一个 `Ava Effector` (如 `Radial Effector`) Actor 放置到场景中，并将其指定给克隆器，即可通过移动效果器来驱动整个克隆阵列的动画。
3.  **控制播出**：在 UI 蓝图中，创建一个列表显示 `Rundown` 中的页面。当用户点击某个页面项时，调用 `Open Rundown Page` 节点并传入对应的 Page ID，插件会自动加载并显示该页面下的所有图形布局和预设动画。

## C++ 用法

该插件的模块化程度很高，C++ 集成主要通过其核心子系统和组件进行。

### 头文件引入

```cpp
// 核心功能
#include "AvaSceneRig/AvaSceneSubsystem.h"
#include "AvaShapes/AvaShapeActor.h"
#include "AvaMedia/AvaMediaSubsystem.h"

// 编辑器工具（仅在编辑器模块中使用）
#include "AvaEditorCore/AvaEditorSubsystem.h"
```

### 基本用法

以下示例展示了如何在 C++ 中程序化地创建一个基础形状并获取其子系统。

```cpp
// 创建一个矩形动态图形元素
FActorSpawnParameters SpawnParams;
SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
AAvaShapeRectangleActor* Rectangle = GetWorld()->SpawnActor<AAvaShapeRectangleActor>(AAvaShapeRectangleActor::StaticClass(), FTransform::Identity, SpawnParams);

if (Rectangle)
{
    // 通过蓝图可读写的属性进行配置
    Rectangle->SetSize(FVector2D(1920, 1080));
    Rectangle->SetMaterial(0, MyDynamicMaterial);
    UE_LOG(LogTemp, Log, TEXT("Created Motion Design Rectangle."));
}

// 获取子系统以进行高级控制
if (UAvaSceneSubsystem* SceneSubsystem = GEngine->GetEngineSubsystem<UAvaSceneSubsystem>())
{
    // 使用子系统管理场景中的所有 Motion Design 元素
    SceneSubsystem->SelectActors({Rectangle});
}
```

### 进阶用法

结合远程控制和 Rundown 实现程序化播出。

```cpp
// 假设我们已经有了一个 Rundown 资产和一个页面ID
UObject* RundownAsset = LoadObject<UObject>(nullptr, TEXT("/Game/MotionDesign/MyRundown"));
const int32 TargetPageId = 1001;

// 通过子系统直接控制播出
if (UAvaRundownSubsystem* RundownSubsystem = GEngine->GetEngineSubsystem<UAvaRundownSubsystem>())
{
    RundownSubsystem->OpenPageByPageId(RundownAsset, TargetPageId, /*bInKeepPlaying=*/ true);
}

// 设置远程控制
if (UAvaRemoteControlSubsystem* RCSubsystem = GEngine->GetEngineSubsystem<UAvaRemoteControlSubsystem>())
{
    // 假设 Preset 已在编辑器中设置好
    RCSubsystem->StartPreset(MyRemoteControlPreset);
}
```
*(注：以上代码为基于插件模块结构和通用 UE 开发模式推断的示例，具体 API 名称请参考实际源码。)*

## Demo 示例

以下是一个创建简单动态形状并修改其颜色的最小 C++ 示例。

**MyMotionDesignDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMotionDesignDemo.generated.h"

class AAvaShapeRectangleActor;

UCLASS()
class AMyMotionDesignDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyMotionDesignDemo();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<AAvaShapeRectangleActor> MotionDesignRect;
};
```

**MyMotionDesignDemo.cpp**
```cpp
#include "MyMotionDesignDemo.h"
#include "AvaShapes/AvaShapeRectangleActor.h" // 来自 AvalancheShapes 模块
#include "Materials/MaterialInstanceDynamic.h"

AMyMotionDesignDemo::AMyMotionDesignDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMotionDesignDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 生成一个矩形动态图形 Actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    MotionDesignRect = GetWorld()->SpawnActor<AAvaShapeRectangleActor>(
        AAvaShapeRectangleActor::StaticClass(),
        GetActorTransform(),
        SpawnParams
    );

    if (MotionDesignRect)
    {
        // 2. 设置尺寸
        MotionDesignRect->SetSize(FVector2D(500.0f, 300.0f));

        // 3. 创建一个动态材质实例并应用
        UMaterialInterface* BaseMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MotionDesign/M_DefaultShape"));
        if (BaseMaterial)
        {
            UMaterialInstanceDynamic* DynamicMat = UMaterialInstanceDynamic::Create(BaseMaterial, this);
            DynamicMat->SetVectorParameterValue(FName("BaseColor"), FLinearColor::Red);
            MotionDesignRect->SetMaterial(0, DynamicMat);
        }

        UE_LOG(LogTemp, Warning, TEXT("Motion Design Demo Actor Spawned and Configured."));
    }
}
```

## 模块依赖

该插件依赖于多个 Epic 提供的其他插件和模块。在你的项目模块 Build.cs 中添加对 `Avalanche` 或特定子模块的引用时，会自动解析这些传递性依赖。

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 媒体合成，用于将外部媒体源与场景元素结合。 |
| `RemoteControl` | 远程控制，用于通过网络或本地设备控制 UE 属性。 |
| `GeometryScripting` / `GeometryCache` | 几何体脚本和缓存，用于程序化网格操作。 |
| `Text3D` | 3D 文本渲染，是动态图形中文本元素的基础。 |
| `ActorModifierCore` / `ActorModifier` | Actor 修改器框架，为非破坏性修改提供基础。 |
| `CustomDetailsView` | 自定义细节面板，用于提供更强大的属性编辑 UI。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group. | 将动态设计的编辑器标签页归类到独立分组，优化编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting. | 为 Movie Render Queue 添加了使用“播控单页面”设置时的分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added page preview to the rundown widget. | 播控工具栏增加了页面加载选项（全部、下一个、选中），并为播控单组件增加了页面预览。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了一个项目设置，可以强制禁用 3D 文本和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with an editor viewport client. | 重构视口客户端关联逻辑，减少代码重复。 |

### 维护评价

-   **活跃维护**：尽管插件于 2025 年 5 月才正式迁移到 `VirtualProduction` 目录，但从 git 记录看，**它在 2026 年 5 月仍有持续的功能性更新**（如 Rundown 增强、MRQ 集成、编辑器 UX 改进）。
-   **功能成熟**：模块数量庞大（40+），覆盖了从设计到播出的全流程，表明这是一个高度成熟且持续演进的系统。
-   **集成深度**：深度集成了 Media IO, Remote Control, Sequencer, MRQ 等 UE 核心/高级系统，说明其在 Epic 内部被用于真实的虚拟制作项目。
-   **推荐使用**：**强烈推荐**。对于任何涉及虚拟制作中动态图形设计、实时播出控制的项目，Avalanche (Motion Design) 都是一个功能强大且维护活跃的首选工具集。它虽然庞大，但模块化设计允许开发者只使用所需的部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/DesignAndGraphics/MotionDesign/) (预估链接，需以官方发布为准)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)