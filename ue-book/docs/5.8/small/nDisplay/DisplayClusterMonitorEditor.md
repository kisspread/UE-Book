# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，编辑器工具，材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于**多机集群同步渲染**的核心插件。它解决的核心问题是：如何让多台 PC（节点）协同工作，各自负责渲染一个大场景（如 LED 墙、CAVE 环境、球幕）的一部分，并保持画面的完全同步。

该插件的存在是为了满足虚拟制片（VP）、大型沉浸式体验、科研可视化等对超大分辨率或特殊投影格式有需求的场景。`DisplayClusterMonitorEditor` 模块作为其编辑器扩展，专门用于在编辑器内**监控和管理**整个渲染集群的运行状态、会话和媒体流，是集群调试和运维的关键工具。

## 使用场景

- 你在搭建一个 VP 虚拟制片影棚，使用多块 LED 屏幕组合成一面墙 → 使用 nDisplay 配置屏幕拓扑，并通过 `DisplayClusterMonitorEditor` 监控每块屏幕节点的渲染状态和延迟。
- 你需要为 CAVE 洞穴式 VR 环境（由多个投影仪驱动）设置同步渲染 → 使用 nDisplay 进行投影校正和集群同步，并使用监控面板检查各投影节点的健康状况。
- 你在调试一个复杂的多机渲染项目，需要实时查看各节点渲染的最终画面 → 使用 `DisplayClusterMonitorEditor` 的会话视图，远程预览任意节点的后缓冲、UI 层或摄像机画面。

## 蓝图用法

`DisplayClusterMonitorEditor` 模块主要提供编辑器 UI 和底层集群管理逻辑，其核心功能通过 C++ 接口暴露。在蓝图中直接调用的节点较少，主要通过编辑器面板交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无主要公开蓝图节点） | 该模块的功能集成在编辑器窗口和 C++ API 中 | `FClusterMonitorController` |

## C++ 用法

### 头文件引入

```cpp
#include "IClusterMonitorController.h"
#include "IClusterObservable.h"
```

### 基本用法

获取集群监控控制器并监听事件。
(来源: `Private/Core/ClusterMonitorController.h`, `Private/Core/IClusterMonitorController.h`)

```cpp
// 假设你有一个对 IClusterMonitorController 的有效引用
TSharedPtr<IClusterMonitorController> MonitorController = ...;

// 开始集群发现和通信
bool bStarted = MonitorController->StartCommunication();

// 绑定事件：当有新的可观测对象（节点、视口等）被发现时
MonitorController->OnObservableJoined().AddLambda([](const TSharedRef<IClusterObservable>& Observable) {
    UE_LOG(LogTemp, Log, TEXT("New Observable Found: %s"), *Observable->GetName());
});

// 请求启动某个可观测对象的会话（开始接收其媒体流）
FGuid ObservableId = ...; // 从某个来源获取
MonitorController->RequestSessionStart(ObservableId);
```

### 进阶用法

管理可观测对象的状态并响应会话变化。
(来源: `Private/Core/IClusterObservable.h`, `Private/Core/ClusterObservable.h`)

```cpp
// 获取一个具体的可观测对象
TSharedPtr<IClusterObservable> Observable = MonitorController->GetObservable(ObservableId);
if (Observable.IsValid())
{
    // 获取其基本信息
    FString Name = Observable->GetName();
    EDCObservableType Type = Observable->GetType();
    FIntPoint Resolution = Observable->GetResolution();

    // 绑定会话状态变化事件
    Observable->OnSessionStateChanged().AddLambda([](IClusterObservable::ESessionState NewState) {
        switch (NewState)
        {
        case IClusterObservable::ESessionState::Active:
            UE_LOG(LogTemp, Log, TEXT("Session is active and streaming."));
            break;
        case IClusterObservable::ESessionState::Error:
            UE_LOG(LogTemp, Error, TEXT("Session encountered an error."));
            break;
        // ...
        }
    });

    // 如果会话已启动，可以控制媒体播放
    if (Observable->IsSessionRunning())
    {
        Observable->Pause(); // 暂停流
        Observable->Play();  // 恢复播放
    }
}
```

## Demo 示例

一个最小化的监控控制器使用示例，展示如何创建控制器并处理基本事件。
```cpp
// MyClusterMonitorActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IClusterMonitorController.h"
#include "MyClusterMonitorActor.generated.h"

UCLASS()
class AMyClusterMonitorActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<IClusterMonitorController> ClusterMonitor;

    // 事件处理函数
    void HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable);
    void HandleSessionStarted(const TSharedRef<IClusterObservable>& Observable);
};
```

```cpp
// MyClusterMonitorActor.cpp
#include "MyClusterMonitorActor.h"

void AMyClusterMonitorActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建并初始化监控控制器（通常由编辑器模块管理，此处为演示）
    // 注意：在实际编辑器代码中，控制器实例通常是单例或由模块持有。
    ClusterMonitor = MakeShared<FClusterMonitorController>();

    // 绑定事件
    ClusterMonitor->OnObservableJoined().AddUObject(this, &AMyClusterMonitorActor::HandleObservableJoined);
    ClusterMonitor->OnSessionStarted().AddUObject(this, &AMyClusterMonitorActor::HandleSessionStarted);

    // 启动通信
    ClusterMonitor->StartCommunication();
    UE_LOG(LogTemp, Log, TEXT("Cluster Monitor Communication Started."));
}

void AMyClusterMonitorActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ClusterMonitor.IsValid())
    {
        // 解绑事件
        ClusterMonitor->OnObservableJoined().RemoveAll(this);
        ClusterMonitor->OnSessionStarted().RemoveAll(this);

        // 停止通信并释放资源
        ClusterMonitor->StopCommunication();
        ClusterMonitor.Reset();
    }

    Super::EndPlay(EndPlayReason);
}

void AMyClusterMonitorActor::HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable)
{
    UE_LOG(LogTemp, Log, TEXT("Actor Detected New Observable: %s (Type: %d)"),
        *Observable->GetName(),
        static_cast<int32>(Observable->GetType()));
}

void AMyClusterMonitorActor::HandleSessionStarted(const TSharedRef<IClusterObservable>& Observable)
{
    UE_LOG(LogTemp, Log, TEXT("Session Started for: %s. Media source available: %s"),
        *Observable->GetName(),
        Observable->GetMediaSource() ? TEXT("Yes") : TEXT("No"));
}
```

## 模块依赖

从 `DisplayClusterMonitorEditor.Build.cs` 分析，该模块是一个**编辑器模块**，其功能依赖于 Unreal Engine 的编辑器框架。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于创建编辑器面板、工具栏、Tab 等 UI 组件。 |

**注意**：该插件包含大量其他模块（如 `DisplayCluster`, `DisplayClusterProjection`, `DisplayClusterMedia` 等），这些是核心运行时模块，拥有更广泛的依赖（如 `Core`, `Engine`, `RHI`, `Media`, `Networking` 等）。`DisplayClusterMonitorEditor` 作为其编辑器部分，本身依赖较少，但使用整个 nDisplay 系统需要所有这些模块协同工作。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影管线（MovieGraph）和 nDisplay 添加 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线：将 WarpBlendAlpha 模式合并到 WarpBlend 功能中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机的命名问题；修复 MPCDI/ICVFX 着色器中的不透明度通道。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退路径中，遵守非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时发生的闪烁问题。 |

### 维护评价

**活跃维护**。

nDisplay 作为 Epic Games 重点维护的大型企业级功能插件，持续收到更新。从提供的 git 历史看，最近一次提交在 **2026年5月**，内容涉及新特性支持（EXR 多层）、电影管线集成、着色器 Bug 修复和编辑器体验优化，表明该项目仍在**积极开发和完善中**。

尽管插件创建于 2018 年（约8年），但其功能复杂且面向专业领域，持续有稳定的功能迭代和问题修复。**强烈推荐在有相关需求的项目中使用**。需要注意的是，该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) (通用 nDisplay 文档)