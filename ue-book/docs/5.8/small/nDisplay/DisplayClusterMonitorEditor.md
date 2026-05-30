# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、配置资产、着色器等） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个强大的 UE5 插件，其核心功能是实现**跨多台计算机的同步渲染集群**。它解决了在大型显示系统（如 CAVE 洞穴系统、LED 虚拟墙、多投影仪组合显示）中，将单个 UE 应用程序的渲染画面精确、同步地分配到多个渲染节点（PC）上的问题。通过 nDisplay，开发者可以构建沉浸式体验、舞台灯光预览、虚拟制片 (VP) 或任何需要扩展视场角或超高分辨率的应用。该插件包含了从配置、投影映射、几何校正 (Warp/Blend)、色彩管理、媒体集成到实时监控和调试的完整工具链。

## 使用场景

- **虚拟制片 (Virtual Production)**：你需要在 LED 墙上同步渲染主场景和摄像机视口，使用多个渲染节点来驱动整面墙的不同区域。
- **CAVE/穹顶投影**：你需要将游戏画面无缝投射到一个由多个投影仪组成的房间或球幕上，每个投影仪由一台独立的 PC 驱动。
- **大型公共显示器**：你需要创建一个由多个显示屏拼接而成的超宽全景显示器，所有屏幕内容保持完全同步。
- **线下渲染 (Render Farm)**：你需要将一个场景的不同部分或不同视图分发给多台机器同时渲染，用于最终影片或预览。
- **实时监控与调试**：在分布式渲染系统中，你需要一个统一的编辑器面板来查看所有集群节点的状态、实时预览各个节点的渲染输出，并进行会话控制。

## 蓝图用法

nDisplay 主要是一个编辑器和运行时框架，其核心配置通过 `.ndisplay` 配置资产完成。许多操作通过编辑器 UI（如 nDisplay Configurator 面板）进行。`DisplayClusterMonitorEditor` 模块提供的监控面板也主要通过编辑器菜单触发。根据提供的源码分析，`DisplayClusterMonitorEditor` 模块中的类（如 `SClusterMonitorPanel`）主要是编辑器 Slate 界面组件，**没有发现直接暴露的 `BlueprintCallable` 函数**。其交互主要通过编辑器 UI 命令和内部事件系统驱动。

### 核心编辑器 UI

| UI 元素 | 说明 | 所在模块 |
|---|---|---|
| nDisplay Configurator 面板 | 用于编辑 `.ndisplay` 配置文件，设置集群拓扑、视口、投影仪、ICVFX 等。 | `DisplayClusterConfigurator` |
| Cluster Monitor 面板 | 实时监控集群中所有节点的状态、可观测对象，并可以启动/停止媒体观察会话。 | `DisplayClusterMonitorEditor` |
| nDisplay Cluster Editor 面板 | 用于预览和调试集群配置的主编辑器面板。 | `DisplayClusterEditor` |
| Light Card 编辑器 | 用于在场景中放置和管理虚拟灯光卡（用于反射、补光等）。 | `DisplayClusterLightCardEditor` |

## C++ 用法

nDisplay 的运行时逻辑和编辑器扩展深度使用 C++。以下示例基于 `DisplayClusterMonitorEditor` 模块的核心接口。

### 头文件引入

```cpp
// 引入集群监控控制器接口
#include "Core/IClusterMonitorController.h"

// 引入可观测对象接口
#include "Core/IClusterObservable.h"

// 引入集群居住地（节点）接口
#include "Core/IClusterResidence.h"
```

### 基本用法（通过控制器交互）

以下代码展示了如何获取集群监控控制器并查询集群信息。
*（来源：基于 `IClusterMonitorController.h` 接口定义）*

```cpp
// 假设已经通过某种方式获取了集群监控控制器的实例
TSharedPtr<IClusterMonitorController> MonitorController = GetClusterMonitorController();

if (MonitorController.IsValid())
{
    // 开始网络通信，发现集群节点
    MonitorController->StartCommunication();

    // 获取当前发现的可观测对象（如视口、摄像头）数量
    int32 ObservableCount = MonitorController->GetObservablesNum();

    // 遍历并处理所有可观测对象
    // 注意：实际中需要通过事件（如 OnObservableJoined）来动态响应，这里仅为演示接口
    // 此处假设有一个获取所有可观测对象GUID的方法（接口未直接提供，通常在控制器内部管理）

    // 请求为某个特定的可观测对象启动观察会话（例如，开始接收其媒体流）
    FGuid TargetObservableGuid = ...; // 从某处获取
    MonitorController->RequestSessionStart(TargetObservableGuid);

    // 注册事件委托以响应集群状态变化
    MonitorController->OnObservableJoined().AddLambda([](const TSharedRef<IClusterObservable>& NewObservable)
    {
        UE_LOG(LogTemp, Log, TEXT("New Observable Discovered: %s"), *NewObservable->GetName());
        // 可以在这里启动对该新对象的观察会话
    });
}
```

### 进阶用法（处理媒体流）

以下代码展示了如何与单个 `IClusterObservable` 实体交互，控制其媒体会话。
*（来源：基于 `IClusterObservable.h` 接口定义）*

```cpp
// 假设通过控制器的事件或查询获得了某个可观察对象
TSharedPtr<IClusterObservable> Observable = ...;

if (Observable.IsValid())
{
    // 查询其基本信息
    FString Name = Observable->GetName();
    EDCObservableType Type = Observable->GetType();
    FIntPoint Resolution = Observable->GetResolution();
    IClusterObservable::ESessionState State = Observable->GetSessionState();

    // 检查并启动其观察会话
    if (!Observable->IsSessionRunning())
    {
        Observable->StartSession();
    }

    // 控制媒体播放器
    Observable->Play();
    // Observable->Pause();
    // Observable->Stop();

    // 获取关联的媒体资产用于自定义渲染或UI显示
    UMediaPlayer* Player = Observable->GetMediaPlayer();
    UMediaTexture* Texture = Observable->GetMediaTexture();

    // 监听该对象的状态变化
    Observable->OnSessionStateChanged().AddLambda([](IClusterObservable::ESessionState NewState)
    {
        if (NewState == IClusterObservable::ESessionState::Error)
        {
            // 处理会话错误
        }
    });
}
```

## Demo 示例

以下是一个最小化的编辑器模块示例，展示了如何在自定义的编辑器工具中集成对 nDisplay 集群监控器的访问。
*（这是一个编辑器工具示例，不是独立应用程序）*

### MyClusterToolModule.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class IClusterMonitorController;

class FMyClusterToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnClusterMonitorControllerCreated(const TSharedRef<IClusterMonitorController>& Controller);
    void OnClusterMonitorControllerDestroyed();

    void HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable);

    TSharedPtr<IClusterMonitorController> CachedMonitorController;
};
```

### MyClusterToolModule.cpp
```cpp
#include "MyClusterToolModule.h"
#include "Core/IClusterMonitorController.h"
#include "Core/IClusterObservable.h"

// 假设存在一个全局或静态的访问器来获取 MonitorController
extern TSharedPtr<IClusterMonitorController> GetGlobalClusterMonitorController();

void FMyClusterToolModule::StartupModule()
{
    // 尝试获取已存在的控制器（可能在其他模块如DisplayClusterMonitorEditor启动时创建）
    CachedMonitorController = GetGlobalClusterMonitorController();

    if (CachedMonitorController.IsValid())
    {
        // 直接绑定事件
        CachedMonitorController->OnObservableJoined().AddRaw(this, &FMyClusterToolModule::HandleObservableJoined);
    }
    else
    {
        // 监听控制器被创建的事件（实现方式取决于架构）
        // OnClusterMonitorControllerCreatedDelegate.AddRaw(...);
    }
}

void FMyClusterToolModule::ShutdownModule()
{
    if (CachedMonitorController.IsValid())
    {
        CachedMonitorController->OnObservableJoined().RemoveAll(this);
    }
}

void FMyClusterToolModule::OnClusterMonitorControllerCreated(const TSharedRef<IClusterMonitorController>& Controller)
{
    CachedMonitorController = Controller;
    CachedMonitorController->OnObservableJoined().AddRaw(this, &FMyClusterToolModule::HandleObservableJoined);

    // 开始监控，触发初始的集群节点发现
    CachedMonitorController->StartCommunication();
}

void FMyClusterToolModule::OnClusterMonitorControllerDestroyed()
{
    CachedMonitorController.Reset();
}

void FMyClusterToolModule::HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable)
{
    // 当一个新的可观测对象（如新视口上线）被发现时，这里会被调用
    UE_LOG(LogTemp, Display, TEXT("[MyClusterTool] New observable joined: %s (Type: %d)"),
        *Observable->GetName(), static_cast<int32>(Observable->GetType()));

    // 可以在此处自动为特定类型的对象启动观察会话
    if (Observable->GetType() == EDCObservableType::Viewport)
    {
        Observable->StartSession();
    }
}
```

## 模块依赖

从各模块的 Build.cs 文件分析，使用者（特别是创建扩展或工具的开发者）需要注意以下**特殊依赖**：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时逻辑，管理集群节点、通信、渲染同步等。 |
| `DisplayClusterConfiguration` | 处理 `.ndisplay` 配置文件的解析和管理。 |
| `DisplayClusterProjection` | 负责投影映射、几何校正（Warp/Blend）算法。 |
| `DisplayClusterMedia` | 集成媒体框架，用于从集群节点接收或发送视频流。 |
| `SharedMemoryMedia` | 提供基于共享内存的高性能媒体传输方案，用于本地节点间通信。 |
| `DisplayClusterWarp` | 实现高级的几何校正和变形网格。 |
| `DisplayClusterShaders` | nDisplay 专用的着色器和材质功能。 |
| `D3D12RHI` (部分模块依赖) | 用于支持 D3D12 下的共享内存和特定渲染特性。 |

**注意**：由于 nDisplay 插件包含大量编辑器工具，`DisplayClusterEditor`, `DisplayClusterConfigurator`, `DisplayClusterMonitorEditor` 等模块都依赖 `UnrealEd`。在编写游戏逻辑时通常不需要直接依赖这些编辑器模块，只需依赖运行时核心模块。

## 维护状态

nDisplay 是 Epic Games 官方维护的核心企业级功能插件，用于支持其虚拟制片和大型显示解决方案。它在持续更新中。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|--- |--- |
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 增加了 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在 MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了拓扑感知相机命名问题以及 MPCDI/ICVFX 着色器中的不透明 alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 使 nDisplay 在输出帧编码回退时遵守非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

- **活跃维护**：nDisplay 插件至今（2026年）仍在积极开发，最近一个月有多次功能性更新和 Bug 修复。
- **核心企业功能**：作为 Epic Games 虚拟制片战略的核心组件，预计会长期维护和更新。
- **复杂性高**：插件规模巨大（1300+ 文件，29个模块），架构复杂，深度集成引擎渲染管线和编辑器，学习曲线陡峭。
- **硬件依赖性**：功能效果严重依赖具体的硬件配置（GPU、显示设备、网络）和驱动程序。
- **推荐使用**：如果你需要实现上述“使用场景”中的分布式渲染需求，nDisplay 是 UE 中唯一且官方的解决方案，尽管它复杂且通常不默认启用。对于简单的多屏输出，可以考虑更轻量级的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档 (无，.uplugin 中 DocsURL 为空)
- 测试用例 (位于 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`)