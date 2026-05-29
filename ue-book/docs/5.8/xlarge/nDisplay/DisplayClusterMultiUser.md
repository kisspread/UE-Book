# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台PC进行同步的集群渲染，支持单眼或立体模式）

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产， 预设， 媒体资产等） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 用于管理复杂的、多硬件节点的实时渲染显示系统。它解决了将一个虚拟场景的视图分割、变形、并同步输出到多个物理显示器、投影仪或 LED 墙的核心问题。此插件专为虚拟制片（Virtual Production）、沉浸式穹幕（Dome）、CAVE 系统、多投影仪（Multi-Projector）以及大型舞台监视器（Stage Monitor）等场景设计，确保所有输出节点（称为“节点”）的渲染视图在时间和空间上保持同步，支持单目和立体渲染模式。

## 使用场景

- 你在搭建一个由多台 PC 驱动的 CAVE 或穹幕虚拟现实系统 → 用 nDisplay 定义每个 PC 渲染的视口、投影类型以及同步方式。
- 你正在为虚拟制片（如 LED Volume）配置渲染农场，需要精确同步相机和渲染设置 → 用 nDisplay 的配置资产统一管理所有节点。
- 你需要在大型活动或展览中，将同一画面分屏输出到多个投影仪并进行几何校正 → 用 nDisplay 的投影和变形（Warp）功能。
- 你想在多台电脑上协作编辑同一个 nDisplay 配置 → 用 `DisplayClusterMultiUser` 模块集成的 Multi-User Editing 功能。

## 蓝图用法

由于 nDisplay 功能高度专业化，其蓝图接口主要面向运行时配置和控制，而非通用游戏逻辑。核心交互通常通过配置资产（`.uasset`）完成，但以下提供了一些可能的运行时控制接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register` | 将媒体资产状态管理器注册到多用户会话中，开始监听和同步 Media Plate 状态。 | `FMediaAssetMultiUserManager` |
| `Unregister` | 从多用户会话中注销，停止同步。 | `FMediaAssetMultiUserManager` |
| `OnMediaPlateStateChanged` | 本地 Media Plate 状态改变时触发的回调，用于将状态广播给其他用户。 | `FMediaAssetMultiUserManager` |

### 使用示例（蓝图描述）

在编辑器的多用户协作场景下，当本地用户修改了一个 Media Actor（媒体板）的播放状态（如播放/暂停）时，`FMediaAssetMultiUserManager` 会通过 `OnMediaPlateStateChanged` 回调捕获此事件。该事件会序列化为一个 `FConcertMediaStateChangedEvent` 结构，其中包含受影响 Actor 的路径名和新状态。然后，此事件被发送到 Multi-User 会话的其他端点（远程用户），从而实现状态的远程同步。

## C++ 用法

nDisplay 的 C++ API 侧重于底层配置、渲染管线和模块化架构的扩展。核心类和事件定义在 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块中。

### 头文件引入

```cpp
#include "DisplayClusterModule.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationTypes.h"
```

### 基本用法

以下示例展示了如何通过模块接口访问 nDisplay 的核心服务。
```cpp
// 获取 nDisplay 模块实例
IDisplayClusterModule& DisplayClusterModule = FModuleManager::LoadModuleChecked<IDisplayClusterModule>(TEXT("DisplayCluster"));

// 检查 nDisplay 是否正在运行（是否已成功初始化一个集群配置）
bool bIsClusterRunning = DisplayClusterModule.IsClusterRunning();

// 注册一个回调，当 nDisplay 节点从待机模式变为活动模式时被调用
DisplayClusterModule.GetOnClusterEvent().AddLambda([](EDisplayClusterOperationMode NewMode) {
    if (NewMode == EDisplayClusterOperationMode::Active)
    {
        // 节点现在处于活动模式，开始渲染
    }
});
```
*(来源：基于 `IDisplayClusterModule` 公共接口推断)*

### 进阶用法

以下示例展示了如何在 Multi-User 环境中处理自定义事务和媒体状态同步。
```cpp
// 创建一个多用户事务过滤器，以防止某些 nDisplay 对象被 Multi-User 系统序列化
// 这避免了配置资产在协作编辑时产生冲突
FDisplayClusterMultiUserManager::ShouldObjectBeTransacted(const FConcertTransactionFilterArgs& FilterArgs)
{
    // 检查被修改的对象是否属于 nDisplay 配置资产
    if (FilterArgs.Object->IsA<UDisplayClusterConfigurationData>())
    {
        // 返回 “不应被传输” 以隔离 nDisplay 配置
        return ETransactionFilterResult::Exclude;
    }
    // 否则允许常规事务
    return ETransactionFilterResult::Include;
}

// 在 Multi-User 会话中注册自定义事件（如媒体状态变化）的处理器
void FMediaAssetMultiUserManager::Register(TSharedRef<IConcertClientSession> InSession)
{
    // 监听来自远程端点的 FConcertMediaStateChangedEvent 事件
    InSession->RegisterCustomEventHandler<FConcertMediaStateChangedEvent>(
        FConcertMessageAddress(),
        [this](const FConcertSessionContext& Context, const FConcertMediaStateChangedEvent& Event)
        {
            // 在本地应用远程状态变更
            this->OnStateChangedEvent(Context, Event);
        }
    );
}
```
*(来源：`DisplayClusterMultiUserManager.h` 和 `MediaAssetMultiUserManager.h`)*

## Demo 示例

以下是一个简化的示例，展示了如何创建一个自定义模块，该模块在 nDisplay 运行时监听特定的集群状态变化。这可以作为扩展 nDisplay 功能的起点。

**MyNDisplayListener.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "DisplayClusterModule.h"

class FMyNDisplayListener : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnClusterModeChanged(EDisplayClusterOperationMode NewMode);
    FDelegateHandle OnClusterModeChangedHandle;
};
```

**MyNDisplayListener.cpp**
```cpp
#include "MyNDisplayListener.h"
#include "DisplayClusterModule.h"

#define LOCTEXT_NAMESPACE "FMyNDisplayListenerModule"

void FMyNDisplayListener::StartupModule()
{
    IDisplayClusterModule& DCModule = FModuleManager::LoadModuleChecked<IDisplayClusterModule>(TEXT("DisplayCluster"));
    
    // 订阅集群操作模式改变事件
    OnClusterModeChangedHandle = DCModule.GetOnClusterEvent().AddRaw(this, &FMyNDisplayListener::OnClusterModeChanged);
    
    UE_LOG(LogTemp, Log, TEXT("MyNDisplayListener: 监听器已启动，正在监听 nDisplay 集群事件。"));
}

void FMyNDisplayListener::ShutdownModule()
{
    if (IDisplayClusterModule* DCModule = FModuleManager::GetModulePtr<IDisplayClusterModule>(TEXT("DisplayCluster")))
    {
        DCModule->GetOnClusterEvent().Remove(OnClusterModeChangedHandle);
    }
    UE_LOG(LogTemp, Log, TEXT("MyNDisplayListener: 监听器已关闭。"));
}

void FMyNDisplayListener::OnClusterModeChanged(EDisplayClusterOperationMode NewMode)
{
    switch (NewMode)
    {
    case EDisplayClusterOperationMode::Disabled:
        UE_LOG(LogTemp, Warning, TEXT("nDisplay 集群已禁用。"));
        break;
    case EDisplayClusterOperationMode::Editor:
        UE_LOG(LogTemp, Log, TEXT("nDisplay 进入编辑器模式。"));
        break;
    case EDisplayClusterOperationMode::Active:
        UE_LOG(LogTemp, Log, TEXT("nDisplay 集群已激活，开始渲染。"));
        break;
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyNDisplayListener, MyNDisplayListener)
```

## 模块依赖

nDisplay 插件包含众多子模块，其依赖关系复杂。以下列出该插件依赖的一些关键**非标准**模块。

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 核心配置数据模型，定义集群、节点、视口等。 |
| `DisplayClusterProjection` | 处理投影几何和变形（Warp & Blend）。 |
| `DisplayClusterMedia` | 集成 Media Framework，用于外部视频输入/输出。 |
| `SharedMemoryMedia` | 提供基于共享内存的高性能媒体数据传输。 |
| `ScalableMPCDI` | 第三方库，用于处理 MPCDI（投影仪配置数据接口）格式。 |
| `DisplayClusterMultiUser` | 集成 Unreal Multi-User Editing，同步 nDisplay 相关状态。 |
| `DisplayClusterRemoteControlInterceptor` | 与 Remote Control API 集成，用于远程控制 nDisplay。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加了 EXR 多层支持功能。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将电影渲染管线中的 WarpBlendAlpha 模式合并到 WarpBlend 模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了MRG中拓扑感知相机命名问题以及MPCDI/ICVFX着色器的不透明Alpha问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退路径中支持非默认的显示Gamma设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 插件自 2018 年创建，是 UE 中**活跃维护**的大型专业插件。从最近的提交记录来看，开发团队仍在持续为其添加新功能（如 MovieGraph 集成）并修复关键 Bug（如着色器、显示和渲染管线问题）。尽管其默认未启用，但对于目标使用场景（虚拟制片、大型显示系统）而言，它是 Epic 官方提供的核心解决方案，维护状态非常健康，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档： (无)
- 测试用例：`Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/` (路径推断)