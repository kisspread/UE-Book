# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、着色器、配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

基于源码分析，nDisplay 是一个用于构建**多PC、多显示器同步渲染系统**的框架。它解决的核心问题是：如何让多台计算机（集群节点）作为一个整体，精确同步地渲染同一场景，并输出到由多个物理显示器（如投影仪、LED墙、CAVE系统）组成的复杂显示环境。

它不仅仅是一个简单的多窗口管理器，而是一个完整的分布式渲染解决方案，包含了：
1.  **集群节点管理与同步**：管理集群中的各个PC节点，确保它们渲染同一帧的内容。
2.  **视图（Viewport）管理**：将物理显示器抽象为逻辑视图，并定义每个视图的投影几何（如弯曲屏幕、多投影、全景）。
3.  **媒体流传输**：将渲染好的图像帧从一台PC传输到另一台PC，或从集群节点传输到最终的显示器。
4.  **色彩管理**：在集群中进行统一的色彩校正（Color Grading）和OpenColorIO（OCIO）转换。
5.  **工具链支持**：提供编辑器工具（Configurator）进行可视化配置，以及与Sequencer（MoviePipeline）的集成，用于离线渲染。

插件默认禁用，因为它面向的是特定的硬件和行业应用（如虚拟制片、主题公园、仿真模拟、可视化设计评审）。

## 使用场景

-   你在构建一个**虚拟制片（Virtual Production）LED墙**，需要多台机器同步渲染背景，与实拍演员合成。
-   你在开发一个**多通道投影系统**（如CAVE），需要将一个场景分割渲染到多个环绕用户的大屏幕上。
-   你需要为**大型主题公园**设计驾驶模拟器，使用多台投影仪拼接出巨大的视野。
-   你在进行**高端汽车设计评审**，需要将实时渲染画面输出到高分辨率的LED显示墙，供多人同时观看。
-   你需要一个**高性能的离线渲染管道**，利用多台机器的GPU资源并行渲染高分辨率或高帧率的视频序列。

## 蓝图用法

nDisplay 的核心逻辑和配置主要通过编辑器工具和配置资产完成，直接暴露给蓝图的可调用节点相对有限。主要的蓝图交互点在于配置资产的参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BarrierTimeoutMs` (属性) | 设置网络屏障同步的超时时间（毫秒），用于以太网同步策略。 | `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrierBase` |
| `MarginMs` (属性) | 设置基于阈值的同步策略（如V-blank）的同步容差（毫秒）。 | `UDisplayClusterMediaOutputSynchronizationPolicyThresholdBase` |

### 使用示例（蓝图描述）

1.  **配置同步策略**：在编辑器中打开nDisplay配置资产，在媒体输出节点的属性中，可以创建并分配一个`UDisplayClusterMediaOutputSynchronizationPolicy`的子类实例（如`Vblank`或`EthernetBarrier`）。然后在该策略实例的细节面板中，调整`BarrierTimeoutMs`或`MarginMs`等蓝图可编辑的属性，以优化你的硬件环境下的同步性能。
2.  **操作nDisplay根Actor**：在场景中放置一个`ADisplayClusterRootActor`。通过蓝图可以动态获取它，并访问其集群配置、视口组件等，但直接操控媒体设备（捕获/输入）通常由nDisplay框架内部管理。

## C++ 用法

DisplayClusterMedia 模块负责管理整个 nDisplay 系统中的媒体输入、输出和同步。其C++接口主要用于底层扩展和自定义同步策略。

### 头文件引入

```cpp
#include "DisplayClusterMediaModule.h"
#include "DisplayClusterMediaHelpers.h"
// 包含特定同步策略或媒体设备基类的头文件
#include "Synchronization/DisplayClusterMediaOutputSynchronizationPolicy.h"
```

### 基本用法

以下代码展示了如何通过模块接口访问和管理媒体设备。通常，媒体设备由nDisplay在初始化时根据配置自动创建，但理解其底层管理方式有助于调试和扩展。

```cpp
// 来源: DisplayClusterMediaModule.h - 理解模块如何管理设备
void FDisplayClusterMediaModule::InitializeMedia()
{
    // 此函数在nDisplay实例初始化时被调用
    // 它遍历集群配置，为每个需要媒体功能的视口、ICVFX相机等创建对应的
    // FDisplayClusterMediaCaptureBase 和 FDisplayClusterMediaInputBase 实例
    // 并将它们存储在 CaptureDevices 和 InputDevices TMap中
}

// 手动获取某个媒体捕获设备（仅为演示，通常不直接调用）
void ExampleGetMediaDevice()
{
    // 假设已知设备ID
    FString MediaId = TEXT("MyViewport_Capture_0");
    
    // 通过单例模块访问
    // 注意: FDisplayClusterMediaModule 可能需要从模块管理器获取
    // FDisplayClusterMediaModule* MediaModule = FModuleManager::GetModulePtr<FDisplayClusterMediaModule>(TEXT("DisplayClusterMedia"));
    // if(MediaModule)
    // {
    //     // 内部查找，公共接口可能未直接暴露此查找方法
    //     // TSharedPtr<FDisplayClusterMediaCaptureBase> CaptureDevice = MediaModule->CaptureDevices.FindRef(MediaId);
    // }
}
```

### 进阶用法

实现一个自定义的媒体输出同步策略。这是DisplayClusterMedia模块最典型的扩展点。

```cpp
// 来源: Synchronization/DisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier.h/.cpp 作为参考
// 1. 创建策略处理器接口的实现
class FMyCustomSyncPolicyHandler : public IDisplayClusterMediaOutputSynchronizationPolicyHandler
{
public:
    virtual void Initialize(UMediaOutput* MediaOutput, UMediaCapture* MediaCapture) override
    {
        // 初始化同步机制，例如建立自定义的网络连接或硬件触发
    }
    virtual void StartCapture() override
    {
        // 开始捕获前的同步准备
    }
    virtual void SyncBeforeExportMediaData_RenderThread(FRDGBuilder& GraphBuilder) override
    {
        // 在渲染线程的每一帧，实际导出媒体数据之前执行的同步等待
        // 这是实现精确帧同步的关键函数
        // 例如，等待来自“主节点”的以太网屏障信号
    }
    virtual void StopCapture() override
    {
        // 清理同步资源
    }
};

// 2. 创建同步策略UObject，它持有策略处理器
UCLASS(editinlinenew, Blueprintable)
class UMyCustomSyncPolicy : public UDisplayClusterMediaOutputSynchronizationPolicy
{
    GENERATED_BODY()
public:
    virtual TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> GetHandler() override
    {
        if (!Handler.IsValid())
        {
            Handler = MakeShared<FMyCustomSyncPolicyHandler>();
        }
        return Handler;
    }
protected:
    TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> Handler;
};
```

## Demo 示例

一个最小的C++示例，演示如何注册一个自定义的媒体同步策略。在实际nDisplay项目中，策略的创建和分配由配置器（Configurator）工具完成。

```cpp
// MyCustomSyncPolicy.h
#pragma once

#include "CoreMinimal.h"
#include "Synchronization/DisplayClusterMediaOutputSynchronizationPolicy.h"
#include "MyCustomSyncPolicy.generated.h"

class FMyCustomSyncHandler;

UCLASS(editinlinenew, Blueprintable, meta = (DisplayName = "My Custom Sync"))
class MYPROJECT_API UMyCustomSyncPolicy : public UDisplayClusterMediaOutputSynchronizationPolicy
{
	GENERATED_BODY()

public:
	virtual TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> GetHandler() override;

protected:
	UPROPERTY()
	TObjectPtr<FMyCustomSyncHandler> Handler;
};

// MyCustomSyncPolicy.cpp
#include "MyCustomSyncPolicy.h"
// #include "MyCustomSyncHandler.h" // 假设的处理器头文件

TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> UMyCustomSyncPolicy::GetHandler()
{
	if (!Handler)
	{
		Handler = NewObject<FMyCustomSyncHandler>();
	}
	return Handler->AsShared();
}
```

```cpp
// MyCustomSyncHandler.h
#pragma once

#include "CoreMinimal.h"
#include "Synchronization/IDisplayClusterMediaOutputSynchronizationPolicyHandler.h"

class FMyCustomSyncHandler : public IDisplayClusterMediaOutputSynchronizationPolicyHandler
{
public:
	virtual void Initialize(UMediaOutput* MediaOutput, UMediaCapture* MediaCapture) override;
	virtual void StartCapture() override;
	virtual void SyncBeforeExportMediaData_RenderThread(FRDGBuilder& GraphBuilder) override;
	virtual void StopCapture() override;

private:
	// 自定义同步状态
	bool bIsInitialized = false;
	// ... 其他成员，如网络连接句柄，硬件触发器指针等
};
```

## 模块依赖

`DisplayClusterMedia` 模块的核心依赖如其Build.cs所示：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于编辑器相关的媒体捕获和预览功能。 |
| `D3D12RHI` | 用于深度集成D3D12图形API，实现高性能的跨GPU纹理共享和媒体捕获。 |
| `DisplayClusterConfiguration` | 提供nDisplay集群配置数据的读取能力，媒体模块根据此配置初始化设备。 |
| `MediaUtils`, `MediaAssets` | Unreal Engine标准的媒体框架，用于驱动`UMediaCapture`和`UMediaPlayer`。 |
| `RenderCore`, `RHI` | 底层渲染和图形硬件接口，用于渲染线程的纹理操作和屏障同步。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为MovieGraph和nDisplay集成添加了EXR多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将MoviePipeline中WarpBlendAlpha模式合并到WarpBlend模式中，简化了配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了Movie Render Graph中的相机命名问题，以及MPCDI和ICVFX着色器中的不透明度Alpha通道错误。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了当使用非默认的DisplayGamma时，输出帧编码回退路径未能正确应用Gamma值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时可能导致画面闪烁的问题。 |

### 维护评价

**积极维护中**。

-   **活跃度**：最后的实质性提交发生在2026年5月，距今非常近，且提交内容涉及功能增强和bug修复，表明插件处于**高强度活跃维护**状态。
-   **稳定性**：提交历史显示团队持续在修复边缘案例、优化性能和完善与MoviePipeline等核心系统的集成。
-   **推荐程度**：**强烈推荐**。nDisplay是UE官方支持的专业级集群渲染解决方案，拥有完整的工具链和持续的更新。对于有相应硬件和需求的项目，它是唯一且可靠的选择。唯一需要注意的是其较高的学习曲线和硬件配置要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/) (UE官方文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)