# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产、示例地图） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于专业虚拟制片 (Virtual Production) 和高端可视化的**核心解决方案**。它不仅仅支持简单的多PC集群渲染，更是一个完整的、用于管理复杂显示集群和实时合成工作流的框架。其主要解决以下问题：

1.  **同步渲染与合成**：在多台PC（集群）上实时同步渲染同一场景的不同部分（视图），并将它们无缝拼接成一个连续的超宽、全景或立体3D画面。
2.  **LED墙虚拟制片**：为电影和电视制作中的“LED Volume”（虚拟摄影棚）提供实时、高保真度的背景渲染和前景合成。这是目前 nDisplay 最主要的应用场景。
3.  **多投影与几何校正**：管理复杂的多投影仪系统（如穹顶、CAVE环境），并处理投影图像的几何校正（Warping）和边缘融合（Blending）。
4.  **集群渲染的电影输出**：通过 `DisplayClusterMoviePipeline` 模块，支持以集群方式渲染高分辨率的电影序列帧（EXR 多图层），极大提升渲染效率。
5.  **协作与远程控制**：通过 `DisplayClusterMultiUser` 等模块，支持多人在编辑器中协同工作，并能远程控制集群中的显示状态。

简而言之，nDisplay 将 Unreal Engine 从一个单机游戏引擎，转变为一个能够驱动大型、专业级显示集群的**实时渲染中心**。

## 使用场景

- **电影虚拟制片**：你需要为一个使用巨型LED墙的摄影棚搭建实时渲染系统，让演员在 LED 屏幕前表演时，背景能根据摄像机角度实时变化。
- **主题公园体验**：你正在开发一个穹顶影院或大型沉浸式投影体验项目，需要多台投影仪同步渲染并完美融合。
- **汽车设计评审室**：你需要一个由多块屏幕组成的CAVE环境，用于展示1:1比例的汽车全尺寸模型，并支持立体3D。
- **高分辨率渲染农场**：你需要将一帧 16K 的图像分割到 8 台 PC 上并行渲染，以缩短渲染时间。
- **现场直播与活动**：你需要在演唱会或大型活动中，用多台服务器驱动不同位置的LED屏幕，并保持内容完全同步。

## 蓝图用法

nDisplay 主要通过其**配置资产**（`.ndisplay` 文件）进行设置，该资产可在编辑器中创建和编辑。蓝图交互主要用于运行时动态控制。由于这是一个高度复杂的系统，公开的蓝图API相对聚焦。

### 核心节点

以下节点来自 `DisplayClusterMultiUser` 模块，展示了多人协作场景下的关键API：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register` | 将媒体资产状态同步管理器注册到多人协作会话中，开始监听和广播状态变化。 | `FMediaAssetMultiUserManager` |
| `Unregister` | 从多人协作会话中注销管理器，停止同步。 | `FMediaAssetMultiUserManager` |
| `OnMediaPlateStateChanged` | 当本地或远程媒体板状态发生变化时触发的回调。`bRemoteBroadcast` 参数标识事件来源。 | `FMediaAssetMultiUserManager` |

### 使用示例（蓝图描述）

1.  **初始化与注册**：
    - 在游戏模式或某个持久性Actor的 `BeginPlay` 事件中，调用 `FMediaAssetMultiUserManager` 的 `Register` 函数，并传入当前的 `IConcertClientSession` 引用。这通常需要 C++ 代码暴露给蓝图。
    - 一旦注册成功，管理器将自动开始监听多人协作会话中的 `FConcertMediaStateChangedEvent` 事件。

2.  **响应状态变化**：
    - 当集群中任何一台机器的“媒体板”（Media Plate，用于在LED墙上播放视频或渲染内容）状态发生变化（如播放、暂停、跳转）时，本地的 `OnMediaPlateStateChanged` 事件会被触发。
    - 蓝图可以绑定到这个事件，并执行相应的逻辑，例如在本地UI上更新播放状态指示器。

3.  **发送状态变化**：
    - 当用户在本地通过UI控制媒体板（例如点击“播放”按钮）时，蓝图需要调用一个函数（该函数内部会触发 `OnMediaPlateStateChanged` 并设置 `bRemoteBroadcast = false`）。
    - 该函数会将状态变化（如 `State = 播放`）和对应的媒体板路径（`ActorsPathNames`）打包成 `FConcertMediaStateChangedEvent`，通过多人协作会话发送给所有其他参与者。
    - 其他参与者收到事件后，会找到本地对应路径的媒体板，并应用相同的状态变化。

## C++ 用法

nDisplay 的 C++ 接口庞大且复杂，以下示例聚焦于 `DisplayClusterMultiUser` 模块的核心功能，展示如何在 C++ 中集成多人协作的状态同步。

### 头文件引入

```cpp
#include "MediaAssetMultiUserManager.h"
#include "IConcertClientSession.h"
```

### 基本用法

以下代码展示了如何创建并管理 `FMediaAssetMultiUserManager` 的生命周期，以实现媒体板状态的跨会话同步。
*（此代码逻辑基于 `FMediaAssetMultiUserManager` 的公共接口和 `FDisplayClusterMultiUserModule` 的实现模式推断）*

```cpp
// 在某个持久化对象（如 GameInstance 或 Subsystem）中持有管理器实例
TUniquePtr<FMediaAssetMultiUserManager> MediaMUManager;

void UMyGameSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    MediaMUManager = MakeUnique<FMediaAssetMultiUserManager>();
}

void UMyGameSubsystem::ConnectToMultiUserSession(TSharedRef<IConcertClientSession> Session)
{
    if (MediaMUManager)
    {
        // 将管理器注册到当前的多人协作会话
        MediaMUManager->Register(Session);
    }
}

void UMyGameSubsystem::DisconnectFromMultiUserSession(TSharedRef<IConcertClientSession> Session)
{
    if (MediaMUManager)
    {
        // 从会话中注销管理器
        MediaMUManager->Unregister(Session);
    }
}
```

### 进阶用法

手动处理状态变化事件。这允许你在蓝图或C++层对状态同步进行更精细的控制。

```cpp
// 假设你有一个自定义的媒体板Actor
class AMyMediaPlate : public AActor
{
    // ... 其他代码 ...

    // 当状态变化时（例如，用户在编辑器中点击播放）
    void HandleLocalStateChange(uint8 NewState)
    {
        // 更新本地状态
        CurrentState = NewState;
        
        // 获取这个Actor的路径，用于在其他机器上定位对应的Actor
        TArray<FString> PathNames;
        PathNames.Add(GetPathName());
        
        // 通知管理器：这是一个本地触发的事件 (bRemoteBroadcast = false)
        // 管理器内部会将此事件广播给会话中的其他人
        if (MediaMUManager.IsValid())
        {
            MediaMUManager->OnMediaPlateStateChanged(PathNames, NewState, false);
        }
    }
    
    // 远程状态变化的回调
    UFUNCTION()
    void OnRemoteStateChanged(const TArray<FString>& InNameId, uint8 InEnumState)
    {
        // 检查路径是否匹配
        if (InNameId.Contains(GetPathName()))
        {
            // 应用远程状态
            CurrentState = InEnumState;
            // 执行相应的逻辑，如控制媒体播放器
            // ...
        }
    }
};
```

## Demo 示例

一个最小化的示例，演示如何在 C++ 中创建一个订阅了 `OnMediaPlateStateChanged` 事件的简单 Actor。

```cpp
// SyncedMediaPlate.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SyncedMediaPlate.generated.h"

UCLASS()
class ASyncedMediaPlate : public AActor
{
    GENERATED_BODY()

public:
    ASyncedMediaPlate();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 绑定到管理器事件的回调
    UFUNCTION()
    void OnStateChanged(const TArray<FString>& PathNames, uint8 State, bool bRemote);

    // 模拟的状态（例如：0=停止, 1=播放, 2=暂停）
    UPROPERTY()
    uint8 PlateState;
};
```

```cpp
// SyncedMediaPlate.cpp
#include "SyncedMediaPlate.h"
#include "MediaAssetMultiUserManager.h"
#include "DisplayClusterMultiUserModule.h"

ASyncedMediaPlate::ASyncedMediaPlate()
{
    PrimaryActorTick.bCanEverTick = false;
    PlateState = 0; // 初始化为停止
}

void ASyncedMediaPlate::BeginPlay()
{
    Super::BeginPlay();

    // 获取多用户管理器模块（假设全局唯一且已初始化）
    FDisplayClusterMultiUserModule* MuModule = FModuleManager::GetModulePtr<FDisplayClusterMultiUserModule>("DisplayClusterMultiUser");
    if (MuModule && MuModule->GetMediaAssetMUManager())
    {
        // 注意：实际绑定需要管理器提供事件委托。以下为示意性代码。
        // 在真实nDisplay代码中，FMediaAssetMultiUserManager 内部使用了 FOnMediaPlateStateChangedEvent。
        // 你可能需要通过模块接口访问该事件。
        // MuModule->GetMediaAssetMUManager()->OnMediaPlateStateChangedHandle = ...
        // 此处为简化，假设有一个全局可访问的管理器实例。
        FMediaAssetMultiUserManager* Manager = /* 获取实例 */;
        if (Manager)
        {
            // 绑定事件（这通常需要管理器暴露一个委托）
            // Manager->OnStateChangedEvent.AddDynamic(this, &ASyncedMediaPlate::OnStateChanged);
        }
    }
}

void ASyncedMediaPlate::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 解绑事件
    // ...
    Super::EndPlay(EndPlayReason);
}

void ASyncedMediaPlate::OnStateChanged(const TArray<FString>& PathNames, uint8 State, bool bRemote)
{
    // 检查这个事件是否是针对“我”这个Actor的
    if (PathNames.Contains(GetPathName()))
    {
        PlateState = State;
        UE_LOG(LogTemp, Log, TEXT("Media Plate state changed to %u. Remote: %s"), PlateState, bRemote ? TEXT("True") : TEXT("False"));
        // 在这里执行状态变化后的逻辑
    }
}
```

## 模块依赖

nDisplay 插件包含众多模块，使用者的核心模块（如 `DisplayCluster`）依赖了许多专属和外部模块。下表列出**非通用**的依赖。

| 模块 | 用途 |
|---|---|
| `Concert` | Epic 的多人协作框架，是 `DisplayClusterMultiUser` 模块实现跨机器同步的核心基础。 |
| `MediaUtils` | 提供媒体播放器和媒体资产的基础功能，`DisplayClusterMedia` 模块依赖它来驱动 LED 墙上的视频播放。 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口，`DisplayClusterMedia` 和 `SharedMemoryMedia` 模块依赖它进行高性能的 GPU 资源共享和纹理传输。 |
| `RenderCore` | 底层渲染核心库，所有涉及渲染和着色器的模块都依赖它。 |
| `InputCore` | 用于处理输入（如控制器），`DisplayClusterOperator` 模块可能依赖它进行现场操作。 |
| `HTTP` | 用于网络通信，`DisplayClusterRemoteControlInterceptor` 模块依赖它实现远程控制接口。 |
| `Json` | 用于解析配置文件（`.ndisplay` 是 JSON 格式），`DisplayClusterConfiguration` 模块核心依赖。 |
| `ScalableMPCDI` (External) | 第三方库，用于处理 MPCDI（Multi-Projector Configuration Data Interchange）标准文件，是实现复杂投影几何校正和边缘融合的关键。 |

**注意**：`DisplayCluster` 主模块在 `Build.cs` 中还依赖了 `UnrealEd`、`EditorWidgets`、`LevelEditor` 等编辑器模块，表明其功能深度集成在编辑器中。对于运行时构建，这些依赖可能通过条件编译（`#if WITH_EDITOR`）进行管理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为nDisplay的电影渲染管线添加了对多层EXR图像输出的支持，提升后期合成灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了电影管线中的WarpBlendAlpha模式到通用的WarpBlend模式，简化配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了MRG中拓扑感知摄像机命名问题，并修复了MPCDI和ICVFX着色器中的不透明Alpha通道错误。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码的降级路径中，正确处理了非默认的DisplayGamma设置，保证色彩准确性。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时可能发生的闪烁问题。 |

### 维护评价

nDisplay 是 Unreal Engine 虚拟制片工具链中的**核心且活跃维护**的组件。
- **活跃维护**：从近期的 git 历史看，更新非常频繁（过去一周内有多次提交），内容涵盖新功能支持（多层EXR）、现有功能优化、重要Bug修复（闪烁、色彩、命名）和着色器问题。这表明 Epic 团队仍在积极投入资源进行开发和维护。
- **成熟度**：插件自 2018 年创建，已发展超过 8 年，功能非常成熟和稳定，是经过大量商业项目验证的行业解决方案。
- **推荐**：**强烈推荐**有虚拟制片、大型显示墙或多机集群渲染需求的项目使用。虽然初始配置和学习曲线较陡，但其带来的能力和收益是巨大的。建议通过官方示例项目和文档入手。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)