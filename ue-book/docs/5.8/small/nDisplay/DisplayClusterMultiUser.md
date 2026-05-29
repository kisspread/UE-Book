# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterMultiUser` (Runtime), ... (共28个模块) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现**多 PC 集群渲染**的 Unreal Engine 插件。它解决的核心问题是**如何将多个 PC（节点）的渲染输出无缝、同步地拼接成一个大型、高分辨率的显示画面**。

该插件不仅支持单个视点的拼接，还支持**立体渲染（Stereo Rendering）**，即为左右眼分别渲染并拼接。这使得它成为构建 CAVE（Cave Automatic Virtual Environment）、穹顶、大型 LED 屏幕墙、驾驶模拟器等**沉浸式显示环境**的关键技术。

它存在是为了让虚幻引擎能够驱动专业的、多节点的可视化系统，满足主题公园、虚拟制片、建筑可视化、培训模拟等对高分辨率、低延迟集群渲染的需求。

## 使用场景

-   你需要将游戏或应用的渲染输出到一个由多个显示器或投影仪组成的、物理上环绕观众的巨大曲面上。
-   你在进行**虚拟制片（Virtual Production）**，需要在 LED 影棚的墙壁和天花板上实时渲染出高清、同步的虚拟背景。
-   你正在开发一个飞行模拟器或驾驶模拟器，需要为多个窗口（如前视、侧视）提供同步且无撕裂的视图。
-   你需要实现单个 UE 项目同时在多台电脑上运行，并协调它们以渲染同一个大型场景的不同部分或不同视角。
-   你使用 **Multi-User Editing** 功能，并希望 Media Plate（媒体板）的状态（如播放、暂停）能够在所有协作编辑者的机器上同步。

## 蓝图用法

当前模块 `DisplayClusterMultiUser` 主要提供 C++ 层面的会话同步管理，其内部功能（如 `FMediaAssetMultiUserManager`）并未直接暴露为蓝图节点。多用户协作的核心逻辑由引擎的 **Concert/Multi-User Editing** 框架驱动，本插件主要负责处理与 Media Plate 状态相关的同步事件。

对于 nDisplay 的整体配置（如节点、投影、输出），通常通过编辑器中的 **nDisplay Configurator** 工具和 `.ndisplay` 配置文件进行，而非直接使用蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMultiUserModule.h"
// 通常还需要引入 Concert 相关头文件以建立会话
#include "IConcertClientSession.h"
```

### 基本用法

本模块的核心是管理 Media Plate 在多用户编辑会话中的状态同步。它通过监听本地和远程的媒体状态变更事件来实现。

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMultiUser/Private/MediaAssetMultiUserManager.h
// 基本用法示例（通常由模块内部的 Manager 管理，开发者无需直接调用）
void SetupMultiUserMediaSync()
{
    // 假设我们已经获得了一个有效的 Concert 会话引用
    TSharedRef<IConcertClientSession> MySession = GetConcertSession();

    // 1. 创建媒体资源的多用户管理器
    // 注意: FMediaAssetMultiUserManager 是内部类，通常通过模块的生命周期管理
    // 这里仅演示其核心交互逻辑
    FMediaAssetMultiUserManager MediaMUManager;

    // 2. 向会话注册，开始监听和广播 Media Plate 状态事件
    MediaMUManager.Register(MySession);

    // 3. 当本地发生 Media Plate 状态变化（例如，被编辑或蓝图改变状态）时，会调用：
    // MediaMUManager.OnMediaPlateStateChanged(ActorPaths, NewState, false);
    // 该管理器会将 `FConcertMediaStateChangedEvent` 发送给会话中的其他端点。

    // 4. 当从远程端点收到状态变化事件时，管理器内部会调用：
    // MediaMUManager.OnStateChangedEvent(Context, ReceivedEvent);
    // 然后它会更新本地对应的 Media Plate 对象的状态。
}
```

### 进阶用法：理解同步流程

一个完整的同步流程涉及事件发布与订阅：

1.  **本地状态变更 -> 广播**：当客户端 A 上的 Media Plate 状态改变（如开始播放），它会广播一个 `FConcertMediaStateChangedEvent`。
2.  **接收并应用**：客户端 B 收到该事件后，`FMediaAssetMultiUserManager::OnStateChangedEvent` 被调用，查找对应的 Media Plate 并更新其状态，使其与客户端 A 同步。
3.  **事务过滤**：同时，模块中的 `FDisplayClusterMultiUserManager` 会通过 `ShouldObjectBeTransacted` 过滤掉不需要在多用户同步中处理的 nDisplay 相关对象，避免不必要的同步冲突。

## Demo 示例

由于 `DisplayClusterMultiUser` 模块深度集成于引擎的多用户编辑框架，其功能在启用 Multi-User Editing 并操作 Media Plate 时自动生效。以下是一个概念性的 C++ 示例，展示如何创建一个自定义的、需要多用户同步的组件逻辑，其模式与本插件处理 Media Plate 的方式类似。

**MySyncedMediaController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MySyncedMediaController.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMySyncedMediaController : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "MultiUser")
    bool bIsPlaying = false;

    // 模拟广播状态变更（在实际项目中，这里会通过 Concert API 广播）
    UFUNCTION(BlueprintCallable, Category = "MultiUser")
    void SetPlaybackState(bool bNewPlayingState);

protected:
    virtual void BeginPlay() override;

private:
    // 模拟接收远程状态更新
    void OnRemotePlaybackStateUpdated(bool bRemotePlayingState);
};
```

**MySyncedMediaController.cpp**
```cpp
#include "MySyncedMediaController.h"
// 注意：这里仅为演示逻辑，实际应集成 IConcertClientSession
// #include "IConcertClientSession.h"

void UMySyncedMediaController::SetPlaybackState(bool bNewPlayingState)
{
    if (bIsPlaying != bNewPlayingState)
    {
        bIsPlaying = bNewPlayingState;
        
        // 1. 本地状态已更新，可以触发本地逻辑（如控制媒体播放）
        UE_LOG(LogTemp, Log, TEXT("Local playback state set to: %s"), bIsPlaying ? TEXT("Playing") : TEXT("Stopped"));
        
        // 2. 【关键】在这里广播事件到多用户会话
        // ConcertManager->SendCustomEvent(TEXT("MediaStateChanged"), GetOwner()->GetPathName(), bIsPlaying);
        // (此处省略了实际的 Concert 网络代码)
    }
}

void UMySyncedMediaController::BeginPlay()
{
    Super::BeginPlay();
    
    // 【关键】在这里订阅来自多用户会话的远程状态更新事件
    // ConcertSession->RegisterCustomEventHandler(TEXT("MediaStateChanged"), 
    //     FConcertCustomEventHandler::CreateUObject(this, &UMySyncedMediaController::OnRemotePlaybackStateUpdated));
    // (此处省略了实际的 Concert 网络代码)
}

void UMySyncedMediaController::OnRemotePlaybackStateUpdated(bool bRemotePlayingState)
{
    if (bIsPlaying != bRemotePlayingState)
    {
        // 避免因接收自己的广播而产生循环
        bIsPlaying = bRemotePlayingState;
        UE_LOG(LogTemp, Log, TEXT("Remote playback state updated to: %s"), bIsPlaying ? TEXT("Playing") : TEXT("Stopped"));
        // 应用远程状态到本地对象
    }
}
```

## 模块依赖

本插件（特指 `DisplayClusterMultiUser` 模块）的独特依赖已融入引擎核心。使用者通常无需直接依赖此模块，它是 nDisplay 插件的**内部组件**。如果你正在构建自定义的、需要与 nDisplay 多用户功能交互的编辑器插件，你可能需要依赖 `DisplayCluster` 核心模块或通过 Concert 接口进行交互。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该模块的功能通过引擎的 Concert/Multi-User Editing 框架实现，其依赖已包含在基础引擎模块中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加 EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 电影管线优化：将 WarpBlendAlpha 模式合并到 WarpBlend 中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名问题；修复 MPCDI/ICVFX 着色器的不透明度 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay 在输出帧编码回退时，尊重非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时导致的闪烁问题。 |

### 维护评价

**活跃维护**。nDisplay 作为 Epic 为虚拟制片和大型沉浸式体验提供的核心插件之一，处于**非常活跃的维护状态**。

-   **创建时间**：插件创建于 2018 年，是成熟的解决方案。
-   **更新频率**：仅从提供的最近 5 次提交（均集中在 2026 年 5 月）来看，更新非常频繁，且内容集中在**功能增强**（如 EXR 多层支持）和**关键问题修复**（着色器、闪烁、兼容性）。
-   **功能演进**：提交信息显示其功能在持续演进，例如与 **MovieGraph** 的集成，表明它紧密跟随 UE 的最新工作流发展。
-   **实验性**：虽然该插件默认禁用（`EnabledByDefault: false`），但这更多是因为它针对专业硬件和特定使用场景，而非其本身不稳定。它并非实验性功能。

**推荐使用**：如果你正从事需要集群渲染、虚拟制片或多屏输出的项目，nDisplay 是官方推荐且必不可少的工具。其文档和社区支持相对成熟，但学习曲线较陡峭。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/) (UE5 官方文档中有详细指南)