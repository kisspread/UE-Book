# Motion Design (Avalanche)

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

---

## 用途

Motion Design（内部代号 Avalanche）是 UE5 中面向**虚拟制作（Virtual Production）**的**实时动态图形设计与播出系统**。它解决的核心问题是：在 Unreal Engine 内提供一套完整的、类似 After Effects / CasparCG 的 2D/3D 动态图形（Motion Graphics）工作流，包括：

1. **场景编排**：通过 `AAvaScene` 管理一个独立的 Motion Design 场景，包含场景树（Scene Tree）、属性容器（Attribute Container）、序列（Sequence）和远程控制预设
2. **元素创建与编辑**：提供 Null Actor（空组节点）、Spline Actor、Ticker Actor（滚动字幕）、Cine Camera Actor 等专用 Actor，以及形状（Shapes）、文本（Text3D）、SVG 导入等 2D/3D 元素
3. **动画与序列**：基于 Sequencer 的序列系统，支持属性动画（Property Animator）、过渡（Transition）和状态树驱动的场景切换
4. **实时播出**：通过 `UAvaGameInstance` 创建独立的游戏实例，将场景渲染到 `UTextureRenderTarget2D`，支持输出通道（Output Channel）管理，实现广播级实时输出
5. **远程控制集成**：与 Remote Control 插件深度集成，支持通过 RC 控制器驱动序列播放和过渡条件判断
6. **视口与质量控制**：自定义视口质量设置、后处理、吸附系统（Snap Points）和 Gizmo 系统

简而言之，Motion Design 让虚拟制作团队可以在 UE 内直接设计和播出动态图形，无需外部工具。

---

## 使用场景

- 你在做**虚拟制作直播**，需要实时叠加动态图形（Logo、字幕、比分板）→ 使用 Motion Design 的场景系统和输出通道
- 你需要设计**可交互的 2D/3D 动态图形模板**，在播出时通过 Remote Control 实时控制 → 使用 RC Sequence Behavior 和 Transition 系统
- 你要创建**滚动字幕（Ticker）**效果 → 使用 `AAvaTickerActor` 和 `UAvaTickerComponent`
- 你需要在 Motion Design 场景中管理**复杂的元素层级和分组** → 使用 `AAvaNullActor`（空组节点）和 Scene Tree
- 你要为 Motion Design 场景添加**基于状态树的过渡动画**（如场景切换时的淡入淡出）→ 使用 Transition 模块的 Task 和 Condition 系统
- 你需要在 Motion Design 视口中精确**对齐和吸附**元素 → 使用 Snap Point 系统
- 你要将 Motion Design 场景渲染为**独立的 Render Target** 用于合成 → 使用 `UAvaGameInstance` 的渲染管线

---

## 蓝图用法

```
┌─────────────────────────────────────────────────────┐
│                   Motion Design                      │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  Scene    │  │ Sequence │  │  Remote Control   │  │
│  │ (AAvaScene│  │ Provider │  │  Integration      │  │
│  │  + Tree)  │  │          │  │                   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │                 │             │
│  ┌────▼──────────────▼─────────────────▼──────────┐  │
│  │          UAvaSceneSubsystem (World)             │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                              │
│  ┌────────────────────▼───────────────────────────┐  │
│  │          UAvaGameInstance (Playback)            │  │
│  │  ┌─────────────┐  ┌──────────────────────────┐ │  │
│  │  │ Viewport    │  │ RenderTarget → Output    │ │  │
│  │  │ Client      │  │ Channel                  │ │  │
│  │  └─────────────┘  └──────────────────────────┘ │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │ Shapes   │ │ Text3D   │ │ SVG      │ │ Media  │  │
│  │ Modifiers│ │ Mask     │ │ Effects  │ │ MRQ    │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
└─────────────────────────────────────────────────────┘
```
### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `QueueActor` | 将 Actor 加入滚动字幕队列 | `UAvaTickerComponent` |
| `CanQueueElements` | 检查队列是否还能添加元素 | `UAvaTickerComponent` |
| `SetStartLocation` | 设置滚动字幕起始位置 | `UAvaTickerComponent` |
| `SetDestroyDistance` | 设置元素销毁距离 | `UAvaTickerComponent` |
| `SetVelocity` | 设置滚动字幕速度 | `UAvaTickerComponent` |
| `SetQueueLimitType` | 设置队列满时的策略（禁止入队/丢弃最旧） | `UAvaTickerComponent` |
| `ToggleGizmo` | 切换对象是否显示为 Gizmo | `IAvaGizmoObjectInterface` |

### 场景属性管理（通过 State Tree Task）

Motion Design 的过渡系统基于 UE5 的 State Tree，以下 Task 可在蓝图/State Tree 编辑器中使用：

| Task | 说明 |
|---|---|
| `Add tag attribute to this scene` | 向当前场景添加标签属性 |
| `Remove tag attribute from this scene` | 从当前场景移除标签属性 |

### 过渡条件

| 条件 | 说明 |
|---|---|
| `A scene contains tag attribute` | 检查场景是否包含指定标签属性 |
| `Compare RC Controller Values` | 比较两个过渡上下文中的 Remote Control 控制器值 |

### 使用示例（蓝图描述）

**创建滚动字幕**：
1. 在场景中放置 `AAvaTickerActor`
2. 获取其 `UAvaTickerComponent` 引用
3. 调用 `SetStartLocation` 设置起始位置（世界坐标）
4. 调用 `SetVelocity` 设置滚动方向和速度
5. 调用 `SetDestroyDistance` 设置元素超出多远后自动销毁
6. 当需要添加新内容时，Spawn 一个 Actor 并调用 `QueueActor` 将其加入队列

**通过 Remote Control 驱动序列播放**：
1. 在 Remote Control Preset 中创建控制器
2. 创建 `UAvaRCSequenceBehavior` 并附加到 RC 控制器
3. 配置 `UAvaRCSequenceBehaviorNode` 的 `SequenceName` 和 `SequenceAction`（Play/Stop 等）
4. 当 RC 控制器值变化时，自动触发对应序列的播放/停止

---

## C++ 用法

### 头文件引入

```cpp
#include "IAvaSceneInterface.h"
#include "AvaSceneSubsystem.h"
#include "AvaAttributeContainer.h"
#include "AvaSceneSettings.h"
#include "IAvaModule.h"
```

### 基本用法：获取场景接口

Motion Design 的核心是 `IAvaSceneInterface`，通过 `UAvaSceneSubsystem` 获取。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/AvaSceneSubsystem.h

// 获取当前世界的 Motion Design 场景接口
UAvaSceneSubsystem* SceneSubsystem = World->GetSubsystem<UAvaSceneSubsystem>();
IAvaSceneInterface* SceneInterface = SceneSubsystem->GetSceneInterface();

if (SceneInterface)
{
    // 获取场景设置
    UAvaSceneSettings* Settings = SceneInterface->GetSceneSettings();
    
    // 获取属性容器（运行时场景属性）
    UAvaAttributeContainer* Attributes = SceneInterface->GetAttributeContainer();
    
    // 获取场景树
    FAvaSceneTree& SceneTree = SceneInterface->GetSceneTree();
    
    // 获取远程控制预设
    URemoteControlPreset* RCPreset = SceneInterface->GetRemoteControlPreset();
    
    // 获取序列提供者
    IAvaSequenceProvider* SeqProvider = SceneInterface->GetSequenceProvider();
}
```

### 基本用法：场景属性操作

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/AvaAttributeContainer.h

UAvaAttributeContainer* AttrContainer = SceneInterface->GetAttributeContainer();

// 添加标签属性
FAvaTagHandle TagHandle; // 从标签系统获取
AttrContainer->AddTagAttribute(TagHandle);

// 检查是否包含某标签属性
if (AttrContainer->ContainsTagAttribute(TagHandle))
{
    // 场景包含该属性
}

// 移除标签属性
AttrContainer->RemoveTagAttribute(TagHandle);

// 名称属性操作
AttrContainer->AddNameAttribute(FName("MyAttribute"));
bool bContains = AttrContainer->ContainsNameAttribute(FName("MyAttribute"));
AttrContainer->RemoveNameAttribute(FName("MyAttribute"));
```

### 基本用法：运行时统计控制

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/IAvaModule.h

IAvaModule& AvaModule = IAvaModule::Get();

// 启用运行时统计处理
AvaModule.SetRuntimeStatProcessingEnabled(true);

// 启用特定统计项
AvaModule.SetRuntimeStatEnabled(TEXT("fps"), true);

// 检查是否有启用的统计
if (AvaModule.ShouldShowRuntimeStats())
{
    TArray<FString> EnabledStats = AvaModule.GetEnabledRuntimeStats();
}
```

### 进阶用法：创建独立的 Motion Design 游戏实例并渲染

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/Framework/AvaGameInstance.h

// 创建 Motion Design 游戏实例
UAvaGameInstance* GameInstance = UAvaGameInstance::Create(OuterObject);

// 创建游戏世界
GameInstance->CreateWorld();

// 准备播放设置
FAvaInstancePlaySettings PlaySettings;
PlaySettings.Settings = InstanceSettings;       // FAvaInstanceSettings
PlaySettings.ChannelName = FName("Output1");
PlaySettings.RenderTarget = RenderTarget;        // UTextureRenderTarget2D*
PlaySettings.ViewportSize = FIntPoint(1920, 1080);
PlaySettings.QualitySettings = QualitySettings;  // FAvaViewportQualitySettings

// 开始播放
GameInstance->BeginPlayWorld(PlaySettings);

// 监听渲染目标就绪
// GameInstance->GetOnRenderTargetReady() 绑定委托

// 更新输出通道大小（运行时调整分辨率）
GameInstance->UpdateSceneViewportSize(FIntPoint(3840, 2160));

// 更新渲染目标
GameInstance->UpdateRenderTarget(NewRenderTarget);

// 结束播放（会在下一 Tick 执行，避免在 Tick 内销毁世界）
GameInstance->RequestEndPlayWorld(false);

// 关闭时强制立即结束
GameInstance->RequestEndPlayWorld(true);
```

### 进阶用法：视口质量设置

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/Viewport/AvaViewportQualitySettings.h

// 使用默认质量设置
FAvaViewportQualitySettings DefaultSettings = FAvaViewportQualitySettings::Default();

// 使用预设（如 "No Lumen"、"Reduced"）
FAvaViewportQualitySettings NoLumen = FAvaViewportQualitySettings::Preset(FAvaViewportQualitySettingsPreset::NoLumen);

// 从 FEngineShowFlags 构造
FEngineShowFlags ShowFlags(EShowFlagInitMode::ESFIM_All0);
FAvaViewportQualitySettings FromFlags(ShowFlags);

// 应用到引擎显示标志
DefaultSettings.Apply(ShowFlags);

// 禁用特定特性
DefaultSettings.EnableFeaturesByName(false, {TEXT("Lumen"), TEXT("RayTracing")});
```

### 进阶用法：吸附点系统

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/Viewport/Interaction/AvaSnapPoint.h

// 创建不同类型的吸附点
FAvaSnapPoint ScreenSnap = FAvaSnapPoint::CreateScreenSnapPoint(EAvaAnchors::Center, FVector2f(960, 540));
FAvaSnapPoint GuideSnap = FAvaSnapPoint::CreateGuideSnapPoint(100.0f, EOrientation::Orient_Horizontal);
FAvaSnapPoint ActorSnap = FAvaSnapPoint::CreateActorSnapPoint(MyActor, EAvaAnchors::TopLeft, FVector2D(0, 0));
FAvaSnapPoint ComponentSnap = FAvaSnapPoint::CreateComponentSnapPoint(MyComponent, EAvaAnchors::BottomRight, FVector2D(100, 100));
FAvaSnapPoint BoundsSnap = FAvaSnapPoint::CreateBoundsSnapPoint(EAvaAnchors::Center, FVector(0, 0, 0), EAvaDepthAlignment::Front);

// 实现自定义吸附点生成器
// 继承 IAvaSnapPointGenerator 接口
class UMySnapPointGenerator : public UObject, public IAvaSnapPointGenerator
{
    virtual TArray<FAvaSnapPoint> GetLocalSnapPoints() const override
    {
        TArray<FAvaSnapPoint> Points;
        Points.Add(FAvaSnapPoint::CreateLocalActorSnapPoint(EAvaAnchors::Center, FVector2D(0, 0)));
        return Points;
    }
};
```

### 进阶用法：材质参数检查

```cpp
// 来源: Engine/Plugins/VirtualProduction/Avalanche/Source/Avalanche/Public/Materials/AvaMaterialUtils.h

UMaterialInterface* Material = /* ... */;

// 检查材质是否包含特定参数
bool bHasParam = UE::Ava::MaterialHasParameter(*Material, FName("Color"), EMaterialParameterType::Vector);

// 批量检查多个参数
TArray<TPair<FName, EMaterialParameterType>> RequiredParams = {
    {FName("BaseColor"), EMaterialParameterType::Vector},
    {FName("Opacity"), EMaterialParameterType::Scalar},
    {FName("NormalMap"), EMaterialParameterType::Texture}
};
TArray<FString> MissingParams;
bool bAllPresent = UE::Ava::MaterialHasParameters(*Material, RequiredParams, MissingParams);

if (!bAllPresent)
{
    for (const FString& Missing : MissingParams)
    {
        UE_LOG(LogAva, Warning, TEXT("Missing material parameter: %s"), *Missing);
    }
}
```

---

## Demo 示例

### 最小示例：创建 Motion Design 场景并操作属性

```cpp
// MyMotionDesignManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IAvaSceneInterface.h"
#include "AvaSceneSubsystem.h"
#include "AvaAttributeContainer.h"
#include "AvaTagHandle.h"
#include "MyMotionDesignManager.generated.h"

UCLASS()
class AMyMotionDesignManager : public AActor
{
    GENERATED_BODY()

public:
    AMyMotionDesignManager();

    UFUNCTION(BlueprintCallable)
    void ActivateSceneAttribute(FAvaTagHandle InTagHandle);

    UFUNCTION(BlueprintCallable)
    void DeactivateSceneAttribute(FAvaTagHandle InTagHandle);

    UFUNCTION(BlueprintPure)
    bool IsSceneAttributeActive(FAvaTagHandle InTagHandle) const;

private:
    IAvaSceneInterface* GetSceneInterface() const;
};
```

```cpp
// MyMotionDesignManager.cpp
#include "MyMotionDesignManager.h"
#include "AvaSceneSubsystem.h"
#include "AvaAttributeContainer.h"
#include "AvaLog.h"

AMyMotionDesignManager::AMyMotionDesignManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

IAvaSceneInterface* AMyMotionDesignManager::GetSceneInterface() const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return nullptr;
    }

    UAvaSceneSubsystem* Subsystem = World->GetSubsystem<UAvaSceneSubsystem>();
    if (!Subsystem)
    {
        return nullptr;
    }

    return Subsystem->GetSceneInterface();
}

void AMyMotionDesignManager::ActivateSceneAttribute(FAvaTagHandle InTagHandle)
{
    IAvaSceneInterface* Scene = GetSceneInterface();
    if (!Scene)
    {
        UE_LOG(LogAva, Warning, TEXT("No Motion Design scene found"));
        return;
    }

    UAvaAttributeContainer* Attrs = Scene->GetAttributeContainer();
    if (Attrs)
    {
        Attrs->AddTagAttribute(InTagHandle);
        UE_LOG(LogAva, Log, TEXT("Scene attribute activated"));
    }
}

void AMyMotionDesignManager::DeactivateSceneAttribute(FAvaTagHandle InTagHandle)
{
    IAvaSceneInterface* Scene = GetSceneInterface();
    if (!Scene)
    {
        return;
    }

    UAvaAttributeContainer* Attrs = Scene->GetAttributeContainer();
    if (Attrs)
    {
        Attrs->RemoveTagAttribute(InTagHandle);
    }
}

bool AMyMotionDesignManager::IsSceneAttributeActive(FAvaTagHandle InTagHandle) const
{
    IAvaSceneInterface* Scene = GetSceneInterface();
    if (!Scene)
    {
        return false;
    }

    UAvaAttributeContainer* Attrs = Scene->GetAttributeContainer();
    return Attrs ? Attrs->ContainsTagAttribute(InTagHandle) : false;
}
```

---

## 模块依赖

由于 Motion Design 是一个超大型插件（41 个模块），以下仅列出其**独特**的、不常见的依赖关系。各子模块的具体依赖请参考对应的 `.Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `RemoteControl` / `RemoteControlAPI` | 远程控制集成，驱动序列播放和过渡条件 |
| `Sequencer` | 序列动画系统核心依赖 |
| `StateTree` | 过渡系统基于 State Tree 实现 |
| `GeometryScriptingCore` | 几何脚本，用于形状和网格操作 |
| `GeometryCache` | 几何缓存，用于缓存动画几何体 |
| `MediaCompositing` | 媒体合成，用于视频/图像合成输出 |
| `MediaIOFramework` | 媒体 IO 框架，用于外部设备输入输出 |
| `Text3D` | 3D 文本渲染 |
| `SVGImporter` | SVG 文件导入 |
| `DynamicMaterial` | 动态材质系统 |
| `ActorModifierCore` | Actor 修改器核心 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `AdvancedRenamer` | 高级重命名工具 |
| `CustomDetailsView` | 自定义详情面板视图 |

---

## 维护状态

### 近期更新

```
- 71ee63af603e Motion Design: added sequence behavior for remote control
- 37d3c9e24e2c Motion Design: small fixes from previous sequence preset change
- 3e1bf2b58a66 Motion Design: Repurposed 'add' button in md sequence to now give additional options for presets for faster creation of sequences. In addition to that, new motion design levels auto-create 4 sequences for TL.
```

### 维护评价

- **创建时间**：2024 年 1 月，是一个相对较新的插件
- **更新频率**：活跃开发中，近期有功能性更新（序列行为、预设系统改进）
- **维护状态**：**活跃维护** — 由 Epic Games 官方团队持续开发，属于 Virtual Production 工作流的核心组件
- **规模**：2991 个源文件、41 个模块，是 UE5 中最大的插件之一
- **已知限制**：
  - 模块全部标记为 Runtime 类型（包括编辑器功能模块），这在打包时可能需要额外配置
  - 依赖大量其他插件（Remote Control、Text3D、SVG Importer 等），启用时需确保所有依赖可用
  - 部分 API 标记为 `UE_DEPRECATED(5.7)`，表明正在经历 API 重构（如 `UAvaSceneState` → `UAvaAttributeContainer`）
- **推荐使用**：✅ **强烈推荐**用于虚拟制作和实时动态图形场景。这是 Epic 官方维护的专业级工具，API 虽在演进中但整体稳定

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/)