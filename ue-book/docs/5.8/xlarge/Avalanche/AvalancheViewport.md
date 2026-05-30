# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（视口工具、交互操作、场景树、媒体集成、远程控制、属性动画等大量功能模块） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche 是一个庞大的工具集，为 Unreal Engine 提供专业级的运动设计、合成和广播能力。它不是一个单一的插件，而是一个包含 30 多个子模块的生态系统，旨在帮助设计师和广播工程师在引擎内直接创建、编辑和回放复杂的动态图形（Motion Graphics）和广播节目。

该插件的核心是 **Motion Design 视口**（`AvalancheViewport` 模块），它将标准编辑器视口扩展为一个带有 2D 设计辅助功能（如吸附、网格、指南线、安全框）的工作空间。其他模块则提供了创建形状、文本、克隆器/效果器、材质动画、场景过渡、媒体合成、远程控制以及基于时间线的序列编辑等功能。

**它解决的问题**：在传统的 UE 工作流中，创建用于电视广播、现场活动或虚拟制作的动态图形（如图标、下三分之一字幕、转场动画）通常需要导出到专用的广播软件中完成。Avalanche 将这些功能直接集成到引擎中，允许设计师在场景内、实时地设计和预览最终效果，并与 Sequencer 深度集成以实现精确的时间线控制。

## 使用场景

- **电视节目制作**：为新闻节目、体育转播或颁奖典礼创建动态的图标、字幕条和转场动画。
- **虚拟演播室/LED 墙内容**：在虚拟场景中设计和排版用于实时渲染的图形和 UI 元素。
- **交互式媒体装置**：创建响应传感器数据或用户输入的实时动态图形。
- **现场活动**：用于演唱会、发布会或展览的现场视觉控制和图形渲染。
- **节目包装和品牌动画**：在引擎中直接设计和预览频道 ID、节目片头等品牌元素。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSnapState` | 获取当前视口的吸附状态（全局、屏幕、网格、Actor 等）。 | `UAvaViewportSettings` |
| `SetSnapState` | 设置当前视口的吸附状态。 | `UAvaViewportSettings` |
| `HasSnapState` | 检查当前是否启用了指定的吸附状态。 | `UAvaViewportSettings` |
| `BroadcastSettingChanged` | 广播视口设置已更改的通知。 | `UAvaViewportSettings` |

`UAvaViewportSettings` 提供了大量 `BlueprintReadWrite` 属性，允许在运行时或编辑器中通过蓝图读写视口配置。这些属性按功能分组：

- **视口叠加** (`bEnableViewportOverlay`, `bEnableBoundingBoxes`)
- **背景与棋盘格** (`ViewportBackgroundMaterial`, `ViewportCheckerboardColor0`, `bEnableShapesEditorOverlay`)
- **屏幕网格** (`bGridEnabled`, `GridSize`, `GridColor`)
- **像素网格** (`bPixelGridEnabled`, `PixelGridColor`)
- **吸附** (`SnapState`, `bSnapIndicatorsEnabled`, `SnapIndicatorColor`)
- **参考线** (`bGuidesEnabled`, `GuideConfigPath`, `EnabledGuideColor`)
- **安全框** (`bSafeFramesEnabled`, `SafeFrames`)
- **纹理叠加** (`bEnableTextureOverlay`, `TextureOverlayTexture`, `TextureOverlayOpacity`)

### 使用示例（蓝图描述）

1.  **配置安全框**：在您的 Motion Design 蓝图中，获取 `UAvaViewportSettings` 的实例（例如，通过 `GetMutableDefault<UAvaViewportSettings>()` 或开发者设置面板）。将 `bSafeFramesEnabled` 设置为 `True`，然后添加一个 `FAvaLevelViewportSafeFrame` 结构到 `SafeFrames` 数组中，设置其 `ScreenPercentage`（如 90）和 `Color`。
2.  **切换吸附模式**：使用 `SetSnapState` 节点，传入 `EAvaViewportSnapState::Grid | EAvaViewportSnapState::Screen` 以同时启用网格和屏幕吸附。
3.  **响应设置变更**：绑定到 `UAvaViewportSettings` 的 `OnChange` 多播委托。当设置发生变化时（例如，通过 UI 面板修改），该委托将被调用，并提供更改的设置名称 (`FName`)。您可以根据此信息更新您自己的 UI 或逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "AvaViewportSettings.h"
#include "AvaViewportUtils.h"
#include "IAvaViewportClient.h"
#include "AvaScreenAlignmentUtils.h"
#include "AvaSnapOperation.h"
```

### 基本用法

**访问和修改视口设置**

```cpp
// 获取默认的视口设置对象 (Config = EditorPerProjectUserSettings)
UAvaViewportSettings* ViewportSettings = GetMutableDefault<UAvaViewportSettings>();
if (ViewportSettings)
{
    // 启用网格
    ViewportSettings->bGridEnabled = true;
    ViewportSettings->GridSize = 32;
    ViewportSettings->GridColor = FLinearColor::White;

    // 设置吸附状态 (使用位掩码)
    ViewportSettings->SnapState = static_cast<int32>(EAvaViewportSnapState::Grid | EAvaViewportSnapState::Screen);
    ViewportSettings->PostEditChange();
}
```

**使用坐标转换工具 (`IAvaViewportWorldCoordinateConverter`)**

```cpp
// 假设您有一个指向 IAvaViewportClient 的共享指针
TSharedPtr<IAvaViewportClient> AvaViewportClient = FAvaViewportUtils::GetAsAvaViewportClient(MyEditorViewportClient);
if (AvaViewportClient.IsValid())
{
    // 获取视口大小
    FVector2f ViewportSize = AvaViewportClient->GetViewportSize();

    // 将视口屏幕坐标 (500, 300) 转换为世界坐标 (在某个深度，例如 100 个单位)
    FVector2f ScreenPosition(500.0f, 300.0f);
    double WorldDepth = 100.0;
    FVector WorldPosition = AvaViewportClient->ViewportPositionToWorldPosition(ScreenPosition, WorldDepth);

    // 反向转换
    FVector2f OutScreenPosition;
    double OutDistance;
    AvaViewportClient->WorldPositionToViewportPosition(WorldPosition, OutScreenPosition, OutDistance);
}
```

### 进阶用法

**执行屏幕对齐操作**

```cpp
// 对齐一组 Actor 到屏幕中心
TArray<AActor*> ActorsToAlign;
// ... 填充 ActorsToAlign 数组

TSharedPtr<IAvaViewportClient> AvaViewportClient = ...;
if (AvaViewportClient.IsValid())
{
    // 获取坐标转换器接口
    TSharedRef<IAvaViewportWorldCoordinateConverter> Converter = AvaViewportClient.ToSharedRef();

    // 水平居中对齐所有选中的 Actor
    FAvaScreenAlignmentUtils::AlignActorsHorizontal(
        Converter,
        ActorsToAlign,
        EAvaHorizontalAlignment::Center, // 对齐到水平中心
        EAvaAlignmentSizeMode::Self, // 只考虑 Actor 自身边界
        EAvaAlignmentContext::SelectedActors // 对齐上下文为当前选择
    );
}
```

**使用吸附操作进行拖拽**

```cpp
// 在开始拖拽 Actor 时启动吸附操作
TSharedPtr<FAvaSnapOperation> SnapOperation = AvaViewportClient->StartSnapOperation();
if (SnapOperation.IsValid())
{
    // 为当前被拖拽的 Actor 生成吸附点
    AActor* DraggedActor = ...;
    SnapOperation->GenerateActorSnapPoints({DraggedActor}, {});

    // 在鼠标移动时，尝试吸附屏幕位置
    FVector2f CurrentMousePos = ...; // 获取当前鼠标在视口中的位置
    SnapOperation->SnapScreenLocation(CurrentMousePos);
    // CurrentMousePos 现在可能已被吸附到最近的点

    // 结束拖拽时清理
    AvaViewportClient->EndSnapOperation();
}
```

## Demo 示例

以下示例展示如何创建一个简单的 C++ 类，该类在初始化时配置视口设置，并提供一个函数来对齐 Actor 到屏幕。

```cpp
// MyMotionDesignHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MyMotionDesignHelper.generated.h"

class AActor;
class IAvaViewportClient;

UCLASS()
class UMyMotionDesignHelper : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintCallable, Category = "Motion Design")
    void AlignActorToScreenCenter(AActor* ActorToAlign);

protected:
    TWeakPtr<IAvaViewportClient> CachedViewportClient;
};
```

```cpp
// MyMotionDesignHelper.cpp
#include "MyMotionDesignHelper.h"
#include "AvaViewportSettings.h"
#include "AvaViewportUtils.h"
#include "IAvaViewportClient.h"
#include "AvaScreenAlignmentUtils.h"

void UMyMotionDesignHelper::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 配置默认的视口设置
    UAvaViewportSettings* Settings = GetMutableDefault<UAvaViewportSettings>();
    if (Settings)
    {
        Settings->bGridEnabled = true;
        Settings->GridSize = 64;
        Settings->bSafeFramesEnabled = true;
        // 添加一个 90% 的安全框
        FAvaLevelViewportSafeFrame SafeFrame;
        SafeFrame.ScreenPercentage = 90.f;
        SafeFrame.Color = FLinearColor::Yellow;
        Settings->SafeFrames.Add(SafeFrame);
        Settings->PostEditChange();
    }

    // 尝试缓存一个有效的 AvaViewportClient
    // 注意：在游戏线程中，可能需要延迟获取或监听视口创建事件
    // CachedViewportClient = FAvaViewportUtils::GetAsAvaViewportClient(...);
}

void UMyMotionDesignHelper::AlignActorToScreenCenter(AActor* ActorToAlign)
{
    if (!ActorToAlign || !CachedViewportClient.IsValid())
    {
        return;
    }

    TSharedRef<IAvaViewportWorldCoordinateConverter> Converter = CachedViewportClient.ToSharedRef();
    TArray<AActor*> Actors = {ActorToAlign};

    // 水平垂直都居中
    FAvaScreenAlignmentUtils::AlignActorsHorizontal(Converter, Actors, EAvaHorizontalAlignment::Center, EAvaAlignmentSizeMode::Self, EAvaAlignmentContext::Screen);
    FAvaScreenAlignmentUtils::AlignActorsVertical(Converter, Actors, EAvaVerticalAlignment::Center, EAvaAlignmentSizeMode::Self, EAvaAlignmentContext::Screen);
}
```

## 模块依赖

从插件的依赖声明和模块结构推断，使用 `AvalancheViewport` 模块时，你的模块需要依赖以下独特模块（省略了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 提供 Motion Design 的核心类型、接口和基础功能。 |
| `AvalancheTag` | 用于标记和管理 Motion Design 系统中的对象。 |
| `AvalancheAttribute` | 定义和管理 Actor 和组件的自定义属性。 |
| `AvalancheOutliner` | 提供 Motion Design 专用的大纲视图系统。 |
| `AvalancheSceneTree` | 管理 Motion Design 场景中的层次结构和父子关系。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro... | 将Motion Design的场景设置和大纲视图标签页在关卡编辑器中进行分组优化。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting. | 在使用节目单页面设置时增加了Movie Render Queue的分析数据收集。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde... | 为节目控制工具栏添加了页面加载选项（全部、下一个、选中）。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 重构视口逻辑，通过在客户端关联/解关联时发送通知来减少冗余代码。 |

### 维护评价

**活跃维护**。该插件于 2025 年 5 月首次创建，但从实验性目录迁移而来，意味着其开发历史更长。最近的提交记录（2026 年 5 月）表明它仍在**积极开发和迭代**中，包含功能增强（如新的工具栏选项、分析功能）、UI/UX 优化和 Bug 修复。

由于这是一个功能庞大且面向专业领域（虚拟制作/广播）的插件，其维护状态良好。建议生产环境中使用时关注官方的发布说明和更新日志，以了解重大变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)