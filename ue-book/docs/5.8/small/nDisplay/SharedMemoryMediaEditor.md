# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台PC进行同步的集群渲染，支持单目或立体模式）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图、编辑器工具、媒体资产、着色器、测试资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE 中用于实现**同步集群渲染**的核心插件。它解决的核心问题是将一个 UE 场景的渲染任务分配给多台联网的 PC（节点），并将每个节点渲染的画面（可能用于投影到不同形状的屏幕或用于不同眼睛的立体视图）同步组合，形成一个统一、连贯的大型或沉浸式显示环境。

**为什么存在？**
- **虚拟制片 (VP)**: 在 LED 墙拍摄中，需要多块屏幕显示与摄像机运动实时同步的背景环境。
- **沉浸式环境 & CAVE 系统**: 驱动由多台投影仪或显示器组成的环绕式或房间大小的虚拟现实系统。
- **大型主题公园或博物馆装置**: 控制分布在多个物理位置的屏幕，保持内容同步。
- **立体 3D (S3D) 渲染**: 为头戴式显示器 (HMD) 或立体投影系统同步渲染左右眼视图。

其核心价值在于提供了一个统一的框架来管理渲染节点、定义屏幕几何与投影、处理帧同步与数据传输（包括共享内存和媒体框架），使得开发者无需从零开始构建复杂的分布式渲染系统。

## 使用场景

-   **你正在搭建一个由多块 LED 屏幕组成的虚拟制片影棚** -> 使用 nDisplay 定义每块屏幕的几何、投影以及对应的渲染节点，实现同步拍摄背景。
-   **你需要创建一个 CAVE（洞穴自动虚拟环境）系统，房间四面都是投影屏幕** -> 使用 nDisplay 配置投影几何、处理边缘融合，并分配渲染任务到多台渲染主机。
-   **你要为一个大型博物馆安装一个环绕式交互投影装置** -> 使用 nDisplay 管理分布在多个房间的显示终端的同步渲染和内容更新。
-   **你需要在 VR 中实现超高分辨率或宽视场角的立体渲染，单台 PC 性能不足** -> 使用 nDisplay 将左右眼视图或画面分块分配到多台 PC 上渲染并同步。
-   **你想在多屏系统中实现跨屏的颜色校正和统一调色** -> nDisplay 的色彩分级（ColorGrading）模块可以帮助你。

## 蓝图用法

由于 nDisplay 主要是一个系统级框架，其核心蓝图接口围绕**配置、控制和查询**展开。功能分布在多个子模块中。以下为按功能分组的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node Id` | 获取当前运行的集群节点 ID。 | `UDisplayClusterBlueprintAPI` |
| `Is Primary Node` | 判断当前节点是否为主节点（控制节点）。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Nodes Ids` | 获取所有集群节点的 ID 列表。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Rect` | 根据视口 ID 获取其在窗口中的矩形区域。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Id` | 根据视口名称获取其 ID。 | `UDisplayClusterBlueprintAPI` |
| `Is Viewport Rendered On This Node` | 判断指定视口是否在本节点上渲染。 | `UDisplayClusterBlueprintAPI` |
| `Get All Viewports` | 获取本节点负责渲染的所有视口信息。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **启动时查询本机角色**:
    -   你可以在 `BeginPlay` 中调用 `Get Cluster Node Id` 和 `Is Primary Node` 来判断当前 PC 是主控机（输出渲染到物理屏幕）还是渲染节点（负责计算特定视口内容）。
2.  **动态调整渲染**:
      - 通过 `Get Viewport Rect` 和 `Is Viewport Rendered On This Node`，你可以编写逻辑，在渲染节点上仅对属于自己的视口进行后处理或 UI 叠加，避免无用计算。
3.  **多用户控制**:
    -   结合 `DisplayClusterMultiUser` 模块，蓝图可以处理来自多用户的同步输入和控制命令。

**重要提示**: nDisplay 的大量核心配置和渲染逻辑通过 C++ 或配置文件 (.ndisplay) 管理，蓝图主要用于运行时查询、简单控制和集成其他游戏逻辑。

## C++ 用法

由于 nDisplay 系统庞大，此处的 C++ 用法基于提供的 `SharedMemoryMediaEditor` 模块示例，展示如何扩展其媒体初始化功能。

### 头文件引入

```cpp
#include "DisplayClusterMediaModule.h" // 基础媒体模块
#include "SharedMemoryMediaInitializerFeature.h" // 来自 SharedMemoryMediaEditor 模块的媒体初始化特性
```

### 基本用法（来自模块结构）

以下代码展示了如何创建一个自定义的媒体初始化器特性（`IDisplayClusterModularFeatureMediaInitializer` 接口的实现）。此类用于告知 nDisplay 系统如何处理特定类型的媒体对象（如共享内存媒体源/输出）。

**文件路径**: `Engine/Plugins/Runtime/nDisplay/Source/SharedMemoryMediaEditor/Private/ModularFeatures/SharedMemoryMediaInitializerFeature.h`
```cpp
// 继承自接口 IDisplayClusterModularFeatureMediaInitializer
class FSharedMemoryMediaInitializerFeature
	: public IDisplayClusterModularFeatureMediaInitializer
{
public:
	//~ Begin IDisplayClusterModularFeatureMediaInitializer
	virtual bool IsMediaObjectSupported(const UObject* MediaObject) override;
	virtual bool AreMediaObjectsCompatible(const UObject* MediaSource, const UObject* MediaOutput) override;
	virtual bool GetSupportedMediaPropagationTypes(const UObject* MediaSource, const UObject* MediaOutput, EMediaStreamPropagationType& OutPropagationTypes) override;
	virtual void InitializeMediaObjectForTile(UObject* MediaObject, const FMediaObjectOwnerInfo& OnwerInfo, const FIntPoint& TilePos) override;
	virtual void InitializeMediaObjectForFullFrame(UObject* MediaObject, const FMediaObjectOwnerInfo& OnwerInfo) override;
	//~ End IDisplayClusterModularFeatureMediaInitializer
};
```

### 进阶用法（特性注册）

nDisplay 通过“模块化特性”（Modular Features）系统来动态发现和注册扩展点。一个典型的模块会这样注册其特性：

**文件路径**: `Engine/Plugins/Runtime/nDisplay/Source/SharedMemoryMediaEditor/Private/SharedMemoryMediaEditorModule.h`
```cpp
class FSharedMemoryMediaEditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	void RegisterModularFeatures()
	{
		// 创建特性实例并注册到模块化特性系统
		MediaInitializer = MakeUnique<FSharedMemoryMediaInitializerFeature>();
		IModularFeatures::Get().RegisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::GetModularFeatureName(), MediaInitializer.Get());
	}

	void UnregisterModularFeatures()
	{
		if (MediaInitializer)
		{
			IModularFeatures::Get().UnregisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::GetModularFeatureName(), MediaInitializer.Get());
		}
	}

private:
	TUniquePtr<FSharedMemoryMediaInitializerFeature> MediaInitializer;
};
```
这段代码在模块启动时将 `FSharedMemoryMediaInitializerFeature` 注册到引擎，使得 nDisplay 核心系统在处理媒体对象时能够找到并调用它。

## Demo 示例

由于 nDisplay 的部署和运行需要真实的多台PC硬件和特定的网络/投影环境，很难提供一个可在编辑器中直接运行的完整 Demo。
一个最小的“集成测试”示例通常是在编辑器中配置一个简单的 nDisplay 集群，使用“PIE (多玩家)”模式并开启 nDisplay 插件，指定一个包含多个视口的 `.ndisplay` 配置文件。运行时，主编辑器窗口将模拟主节点，并创建额外的窗口用于其他“节点”的渲染预览。

一个概念性的 C++ 自定义初始化器骨架如下：

**`MyMediaInitializer.h`**
```cpp
#pragma once
#include "DisplayClusterMediaInterfaces.h"

class FMyMediaInitializer : public IDisplayClusterModularFeatureMediaInitializer
{
public:
    // 实现所有纯虚函数，决定你的自定义媒体类型如何被处理
    virtual bool IsMediaObjectSupported(const UObject* MediaObject) override
    {
        // 检查 MediaObject 是否是你的自定义媒体源或输出类
        // 例如: return MediaObject->IsA<UMyCustomMediaSource>();
        return false;
    }
    // ... 实现其他接口函数 ...
};
```

**`MyPluginModule.cpp`** (在你的插件中)
```cpp
#include "MyMediaInitializer.h"
#include "IModularFeatures.h"
#include "DisplayClusterMediaInterfaces.h"

class FMyPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        MediaInitializer = MakeUnique<FMyMediaInitializer>();
        IModularFeatures::Get().RegisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::GetModularFeatureName(), MediaInitializer.Get());
    }

    virtual void ShutdownModule() override
    {
        IModularFeatures::Get().UnregisterModularFeature(IDisplayClusterModularFeatureMediaInitializer::GetModularFeatureName(), MediaInitializer.Get());
    }

private:
    TUniquePtr<FMyMediaInitializer> MediaInitializer;
};
```

## 模块依赖

由于 nDisplay 插件规模巨大（包含近30个模块），其自身的模块依赖关系非常复杂。对于**使用者**（你的游戏或应用模块）而言，通常不需要直接依赖所有这些模块。最常见的用法是：

1.  **启用插件**: 在你的项目的 `.uplugin` 或 `.uproject` 文件中启用 `nDisplay` 插件。
2.  **依赖核心模块**: 如果你需要通过 C++ 或蓝图与 nDisplay 系统交互（如获取集群信息、视口信息），你的模块通常需要依赖 `DisplayCluster` 或 `DisplayClusterBlueprintAPI`。
3.  **特定功能依赖**: 如果你需要使用特定的功能（如媒体、监控、电影渲染管线集成），则需要依赖对应的模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，包含集群管理、同步、渲染等主要逻辑。**（最常被外部引用）** |
| `DisplayClusterConfiguration` | 处理 `.ndisplay` 配置文件的加载和解析。 |
| `DisplayClusterProjection` | 负责将渲染画面投影到各种屏幕几何上（平面、曲面、网格等）。 |
| `DisplayClusterMedia` | 提供基于 UE Media Framework 的媒体流（如 Spout, NDI, 共享内存）传输框架。 |
| `DisplayClusterWarp` | 处理几何变形（Warping）和边缘融合（Blending），常用于投影仪校准。 |
| `DisplayClusterMoviePipeline` | 集成 UE 的 Movie Render Queue/MovieGraph，用于录制 nDisplay 集群的输出。 |
| `SharedMemoryMedia` | 提供基于共享内存的高性能节点间媒体数据传输实现。 |

**对于文档使用者**：你的项目通常只需要在 `.uproject` 中启用 `nDisplay` 插件，然后就可以使用其蓝图和 C++ API。仅当你要编写深度集成代码或自定义扩展时，才需要在你的 `Build.cs` 中添加对具体子模块（如 `DisplayCluster`）的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线功能合并，将 WarpBlendAlpha 模式整合进 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机的命名问题，以及 MPCDI/ICVFX 着色器的不透明 Alpha 通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码回退时未正确应用非默认显示 Gamma 值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

-   **活跃度**: **高**。基于最近的 Git 历史，nDisplay 在 **2026年5月** 仍有频繁的功能更新和 Bug 修复。这表明该插件仍在被 Epic Games 积极开发和维护。
-   **稳定性与成熟度**: 作为服务于虚拟制片等专业领域的工具，经过多年迭代，其核心框架已相当稳定和成熟。
-   **已知限制**:
    -   **启用**: 需要手动在项目设置中启用。
    -   **复杂性**: 配置和部署一个多节点集群需要专业知识和测试。
    -   **硬件依赖**: 功能和性能高度依赖于网络、GPU 和显示硬件。
    -   **平台**: 目前主要支持 Windows (Win64) 和 Linux。
-   **推荐使用**: **强烈推荐**给需要实现多屏幕、投影或集群渲染的项目。虽然学习曲线较陡，但它是 UE 生态中解决此类问题的唯一官方、集成的解决方案，且拥有持续的技术支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) (Unreal Engine Documentation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (位于 `DisplayClusterTests` 模块内)