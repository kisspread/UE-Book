# Motion Design

> 综合性虚拟制作与广播工具，提供实时图形设计、合成和播出控制能力。

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计工具 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequence` (Runtime) 等 (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是一个专为**虚拟制作**和**实时广播**场景设计的综合性工具集。它并非解决单一问题，而是提供了一个从**设计、预览到实时播出控制**的完整工作流框架。其核心目的是让设计师、美术师和技术指导能够在虚幻引擎内部，以**所见即所得**的方式快速创建复杂的实时图形元素（如节目标题、动态图表、现场视觉效果、互动场景），并将其无缝集成到虚拟制作或直播的流中。它集成了场景设计、动画、材质、媒体播放和远程控制等功能。

## 使用场景

- 你正在为一场**虚拟演唱会**或**电视节目**设计实时视觉效果和动态图形 → 使用 Motion Design 在引擎内直接设计和预览。
- 你需要一个工具来**快速搭建和动画化**虚拟场景中的复杂元素（如粒子效果、文字动画、几何体变换）→ 使用其内置的材质设计、动画器和效果器。
- 你的**虚拟制作流程**需要从设计阶段平滑过渡到实时渲染和播出，并可能通过远程控制设备进行操控 → 使用其场景装配、序列器集成和远程控制模块。

## 蓝图用法

Motion Design 的功能广泛分布在其众多子模块中。以下是核心功能点的概览：

### 核心设计与动画

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAvaMediaSubsystem` | 管理媒体资源和播放状态的核心子系统 | `UAvaMediaSubsystem` |
| `UAvaSequenceSubsystem` | 管理与 Motion Design 相关的序列资产 | `UAvaSequenceSubsystem` |
| `AvaMediaSubsystem::RegisterMediaAsset` | 注册一个媒体资产以供 Motion Design 流使用 | `UAvaMediaSubsystem` |
| `AvaMediaSubsystem::StartMediaPlayback` | 开始播放一个已注册的媒体资源 | `UAvaMediaSubsystem` |

### 场景控制与远程

| 节点 | 说明 | 所在类 |
|---|---|---|
| `URCAvaSubsystem` | 集成 Remote Control，用于远程触发场景状态或参数变化 | `URCAvaSubsystem` |
| `AvaMediaSubsystem::LoadPage` | 通过页面加载来批量切换场景中的多个元素 | `UAvaMediaSubsystem` |
| `AvaMediaSubsystem::UnloadPage` | 卸载指定的页面，清理相关资源 | `UAvaMediaSubsystem` |

## C++ 用法

Motion Design 的 API 主要通过其核心子系统暴露。

### 头文件引入

```cpp
#include "AvaMediaSubsystem.h"
```

### 基本用法：操作媒体资源

在 C++ 中，通过 `UAvaMediaSubsystem` 管理媒体资源的生命周期。
*来源：测试用例 `AvaMediaSubsystemTest`*

```cpp
// 获取媒体子系统
UAvaMediaSubsystem* MediaSubsystem = GEngine->GetEngineSubsystem<UAvaMediaSubsystem>();

// 注册一个媒体资产
FString MediaAssetPath = TEXT("/Game/MotionDesign/Videos/Opening");
FName MediaAssetName = FName("OpeningVideo");
FString MediaAssetId = MediaSubsystem->RegisterMediaAsset(MediaAssetPath, MediaAssetName);

// 开始播放
MediaSubsystem->StartMediaPlayback(MediaAssetId, EMediaPlaybackState::Playing);

// 在另一个时刻，停止播放
MediaSubsystem->StopMediaPlayback(MediaAssetId);
```

### 进阶用法：页面加载与远程控制

结合页面系统和远程控制，实现复杂的场景状态切换。
*来源：测试用例 `AvaMediaSubsystemPageLoadTest` 和 `RCAvaSubsystemTest`*

```cpp
// 定义并注册媒体资源
UAvaMediaSubsystem* MediaSubsystem = GEngine->GetEngineSubsystem<UAvaMediaSubsystem>();
FString MediaId1 = MediaSubsystem->RegisterMediaAsset(...);
FString MediaId2 = MediaSubsystem->RegisterMediaAsset(...);

// 定义页面，将两个媒体资源分组到一个“开场”页面
FAvaMediaPage NewPage;
NewPage.PageName = FName("ShowOpening");
NewPage.MediaAssetIds.Add(MediaId1);
NewPage.MediaAssetIds.Add(MediaId2);

// 加载（激活）这个页面
MediaSubsystem->LoadPage(NewPage);

// 通过远程控制子系统触发这个页面的加载
URCAvaSubsystem* RCAvaSubsystem = GEngine->GetEngineSubsystem<URCAvaSubsystem>();
RCAvaSubsystem->ExecuteCommand(FString("LoadPage:ShowOpening"));
```

## Demo 示例

创建一个简单的 Motion Design Actor 并通过媒体子系统控制它。
*这是一个概念示例，实际 Actor 类型可能是更具体的如 `AAvaMediaActor`*

```cpp
// MyMotionDesignComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyMotionDesignComponent.generated.h"

UCLASS(ClassGroup=(MotionDesign), meta=(BlueprintSpawnableComponent))
class UMyMotionDesignComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Motion Design")
    void StartMyShow();

    UFUNCTION(BlueprintCallable, Category = "Motion Design")
    void StopMyShow();

private:
    UPROPERTY()
    FString CurrentMediaAssetId;
};
```

```cpp
// MyMotionDesignComponent.cpp
#include "MyMotionDesignComponent.h"
#include "AvaMediaSubsystem.h"

void UMyMotionDesignComponent::BeginPlay()
{
    Super::BeginPlay();
    // 在组件开始时注册媒体资源
    if (UAvaMediaSubsystem* MediaSub = GEngine->GetEngineSubsystem<UAvaMediaSubsystem>())
    {
        CurrentMediaAssetId = MediaSub->RegisterMediaAsset(
            TEXT("/Game/MyProject/Media/MyAnim"),
            GetOwner()->GetFName()
        );
    }
}

void UMyMotionDesignComponent::StartMyShow()
{
    if (UAvaMediaSubsystem* MediaSub = GEngine->GetEngineSubsystem<UAvaMediaSubsystem>())
    {
        if (!CurrentMediaAssetId.IsEmpty())
        {
            MediaSub->StartMediaPlayback(CurrentMediaAssetId, EMediaPlaybackState::Playing);
        }
    }
}

void UMyMotionDesignComponent::StopMyShow()
{
    if (UAvaMediaSubsystem* MediaSub = GEngine->GetEngineSubsystem<UAvaMediaSubsystem>())
    {
        if (!CurrentMediaAssetId.IsEmpty())
        {
            MediaSub->StopMediaPlayback(CurrentMediaAssetId);
        }
    }
}
```

## 模块依赖

Motion Design 是一个庞大且模块化的插件。要使用其完整功能，你的模块需要依赖特定的子模块。以下是关键依赖项：

| 模块 | 用途 |
|---|---|
| `AvalancheMedia` | 核心的媒体资源管理和播放控制 |
| `AvalancheCore` | 提供 Motion Design 的核心类型、接口和子系统 |
| `AvalancheSequence` | 与 Sequencer 集成，用于编辑时间线动画 |
| `AvalancheRemoteControl` | 与 Remote Control 插件集成，用于远程触发和参数控制 |
| `MaterialDesigner` | 动态材质设计工具 |
| `ClonerEffector` | 提供克隆和效果器动画功能 |
| `PropertyAnimatorCore` | 属性动画系统核心 |
| `GeometryCache` | 用于缓存和播放预计算的几何体动画 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro... | 将场景设置和大纲视图等编辑器标签页独立成组，优化编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为“节目单页面”设置添加了 Movie Render Queue 的使用分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde... | 在演出控制工具栏中添加了页面加载选项（全部、下一个、已选），增强控制灵活性。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 3D 文本和形状的碰撞，简化配置。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 优化视口代码，当客户端关联或脱离时通知，重构重复逻辑。 |

### 维护评价

**活跃维护中**。
-   **年龄**：插件于2025年5月正式从实验路径移至虚拟制作路径，至今约2年，仍处于功能快速迭代期。
-   **近期活动**：最近一次更新在2026年5月，且提交内容涉及**新功能添加**（如页面加载选项、MRQ分析）和**用户体验优化**（编辑器布局、项目设置），表明仍在积极开发和改进。
-   **已知限制**：作为功能庞大的系统，可能需要较长的学习曲线。其众多子模块间的依赖关系需要仔细管理。
-   **推荐使用**：**强烈推荐**。它是UE5中面向**虚拟制作**和**广播**领域的专业且全面的工具链。对于相关领域的项目，使用它可以极大提升工作效率。对于新项目，建议直接使用此正式集成的版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-motion-design-in-unreal-engine/)（参考UE5官方文档相关章节）