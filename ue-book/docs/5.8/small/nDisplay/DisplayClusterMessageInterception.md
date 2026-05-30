# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、测试资源、蓝图工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于多台PC（集群）进行同步渲染的复杂系统。它解决的核心问题是**在多个物理显示器或投影仪（例如LED墙、CAVE系统、穹顶影院）上，实时、无撕裂、帧同步地渲染同一个虚拟场景**。这远超简单的多显示器拼接，涉及到集群间的同步通信、每台机器独立视角的投影校正（Warping & Blending）、以及内容与硬件输出的精确映射。它是虚拟制片、大型沉浸式体验、驾驶模拟器等高端应用的基石。

## 使用场景

- **虚拟制片 (Virtual Production)**：在拍摄现场搭建巨大的LED墙，用nDisplay集群渲染背景，演员在前景表演，相机实时合成。
- **主题乐园与沉浸式娱乐**：驱动CAVE系统、穹顶影院、多面环绕的沉浸式体验室。
- **汽车与航空模拟**：为驾驶模拟器提供环绕视野，每台PC负责一个显示区域的渲染。
- **大型可视化**：用于建筑、城市规划、科学数据的超大规模、高分辨率实时可视化。
- **军事与科研仿真**：需要多机同步渲染的训练或研究环境。

## 蓝图用法

nDisplay的蓝图接口主要面向场景设置和运行时控制，而非底层渲染。核心蓝图节点通常与`UDisplayClusterConfigurationData`（配置资产）和`UDisplayClusterClusterManager`（集群管理器）交互。

### 核心节点

由于nDisplay功能庞大，蓝图节点分散在各个子模块中。以下是基于其核心功能的典型节点示例：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Manager` | 获取当前世界的集群管理器单例，用于运行时控制。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Node ID` | 获取当前运行的集群节点ID（例如 “node_0”, “node_1”）。 | `UDisplayClusterBlueprintAPI` |
| `Is Primary` | 判断当前节点是否是主节点（负责同步的控制端）。 | `UDisplayClusterBlueprintAPI` |
| `Get Scene View Extensions` | 获取当前场景的视图扩展列表，可用于定制渲染。 | `UDisplayClusterBlueprintAPI` |
| `Set Viewport Override` | 运行时动态覆盖某个视口的参数（如纹理、分辨率）。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **启动同步**：通常在GameMode的BeginPlay中，通过`Get Cluster Manager`节点获取管理器，然后调用其`Start`方法，基于配置资产初始化整个集群。
2.  **节点判断**：在需要根据节点执行不同逻辑的地方（如只有主节点播放声音），使用`Is Primary`节点进行分支判断。
3.  **动态控制**：在运行时，可以调用`Set Viewport Override`等节点，根据游戏逻辑动态调整某个投影面的显示内容或参数。

## C++ 用法

nDisplay的C++ API庞大，核心功能涉及集群管理、渲染控制和投影算法。以下示例基于其测试用例，展示了基础集成和同步消息的使用。

### 头文件引入

```cpp
#include "DisplayCluster/Public/IDisplayCluster.h"
#include "DisplayClusterConfiguration/Public/DisplayClusterConfigurationTypes.h"
```

### 基本用法：获取nDisplay插件并启动

从测试用例中可以看到如何检查和获取插件实例。`IDisplayCluster`是访问所有核心功能的入口点。

```cpp
// 来自 Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/Private/DisplayClusterTestBlueprintAPI.cpp
// 检查nDisplay插件是否已加载并可用
IDisplayCluster* DisplayClusterAPI = FModuleManager::GetModulePtr<IDisplayCluster>(TEXT("DisplayCluster"));
if (DisplayClusterAPI)
{
    // 获取集群管理器
    IDisplayClusterClusterManager* ClusterManager = DisplayClusterAPI->GetClusterMgr();
    if (ClusterManager)
    {
        // 插件和集群管理器已就绪，可以进一步配置或启动
        UE_LOG(LogTemp, Log, TEXT("nDisplay Cluster Manager is available."));
    }
}
```

### 进阶用法：处理集群同步事件

nDisplay使用一个自定义的集群通信系统。以下代码展示了如何设置和拦截集群事件，用于节点间的自定义同步逻辑。

```cpp
// 来自 Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/Private/DisplayClusterTestClusterEventJson.cpp
// 假设已有一个有效的 IDisplayClusterClusterManager* ClusterManager

// 定义一个事件处理委托
auto ClusterEventHandler = [](const FDisplayClusterClusterEventJson& Event)
{
    // 处理来自其他节点的JSON格式集群事件
    UE_LOG(LogTemp, Log, TEXT("Received Cluster Event from node '%s', category '%s'"),
        *Event.NodeId, *Event.Category);
};

// 绑定事件处理器
ClusterManager->AddClusterEventJsonListener(FOnClusterEventJson::CreateLambda(ClusterEventHandler));

// 发送一个事件给集群中所有节点
FDisplayClusterClusterEventJson MyEvent;
MyEvent.Category = TEXT("Gameplay");
MyEvent.Type = TEXT("PlayerSpawn");
MyEvent.Parameters.Add(TEXT("PlayerID"), TEXT("12345"));
MyEvent.bIsSystemEvent = false;
MyEvent.ShouldDiscardOnRepeat = false;

ClusterManager->SendClusterEventJson(MyEvent, true); // 第二个参数true表示广播给所有节点
```

## Demo 示例

一个最小化的nDisplay集成示例，通常从加载一个.nDisplay配置资产开始，然后启动集群。

```cpp
// MyGameMode.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class IDisplayCluster;
class UDisplayClusterConfigurationData;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMyGameMode();

protected:
    virtual void BeginPlay() override;

private:
    // nDisplay 插件实例指针
    IDisplayCluster* DisplayClusterPlugin;

    // nDisplay 配置资产
    UPROPERTY(EditDefaultsOnly, Category="nDisplay")
    UDisplayClusterConfigurationData* ConfigAsset;

    // 启动集群的函数
    void InitializeDisplayCluster();
};
```

```cpp
// MyGameMode.cpp
#include "MyGameMode.h"
#include "DisplayCluster/Public/IDisplayCluster.h"
#include "DisplayCluster/Public/Cluster/IDisplayClusterClusterManager.h"
#include "DisplayClusterConfiguration/Public/DisplayClusterConfigurationData.h"
#include "Kismet/GameplayStatics.h"

AMyGameMode::AMyGameMode()
    : DisplayClusterPlugin(nullptr)
    , ConfigAsset(nullptr)
{
    // 尝试在构造函数中获取插件，可能还未加载，更安全的做法是在BeginPlay中检查
}

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    InitializeDisplayCluster();
}

void AMyGameMode::InitializeDisplayCluster()
{
    // 1. 检查插件是否加载
    DisplayClusterPlugin = FModuleManager::GetModulePtr<IDisplayCluster>(TEXT("DisplayCluster"));
    if (!DisplayClusterPlugin)
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay plugin is not loaded!"));
        return;
    }

    // 2. 获取集群管理器
    IDisplayClusterClusterManager* ClusterManager = DisplayClusterPlugin->GetClusterMgr();
    if (!ClusterManager)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get Cluster Manager from nDisplay plugin."));
        return;
    }

    // 3. 加载并应用配置 (如果没有通过编辑器预设)
    if (!ConfigAsset)
    {
        // 可以通过资产路径加载
        // ConfigAsset = LoadObject<UDisplayClusterConfigurationData>(nullptr, TEXT("/Game/nDisplay/MyConfig.MyConfig"));
        if (!ConfigAsset)
        {
            UE_LOG(LogTemp, Error, TEXT("nDisplay Configuration Asset is not set!"));
            return;
        }
    }

    // 4. 应用配置并启动集群
    // 这里的具体API调用取决于nDisplay的版本和你的初始化策略
    // 通常集群的启动是由配置资产在某个时机触发的，或者通过编辑器面板。
    // 在游戏逻辑中，你可能更多地是与已经启动的集群管理器交互。
    UE_LOG(LogTemp, Log, TEXT("nDisplay Plugin and Cluster Manager are ready. Configuration asset: %s"),
        ConfigAsset ? *ConfigAsset->GetName() : TEXT("None"));
}
```

## 模块依赖

nDisplay插件包含大量子模块，但用户项目在引用它时，主要需要依赖其核心和运行时模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 核心运行时逻辑，集群管理、渲染主循环。 |
| `DisplayClusterConfiguration` | 解析和管理 `.nDisplay` 配置资产的数据模型。 |
| `DisplayClusterProjection` | 处理投影校正（Warp & Blend）、MPCDI等投影算法。 |
| `DisplayClusterShaders` | nDisplay专用的着色器模块。 |
| `DisplayClusterWarp` | 与投影校正相关的Warp网格等数据的处理。 |
| `SharedMemoryMedia` | 基于共享内存的媒体输入输出，用于节点间高速交换纹理。 |
| `MediaFrameworkUtilities` | 媒体框架工具，支持从各种媒体源（如SMPTE ST 2110）获取输入。 |
| `D3D12RHI` | 直接支持DirectX 12渲染硬件接口，许多高级同步和纹理共享功能依赖于此。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为nDisplay的MovieGraph渲染管线添加EXR多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了WarpBlendAlpha模式到WarpBlend模式，简化了渲染管线选项。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多根渲染图(MRG)中拓扑感知相机的命名问题，并修复了MPCDI/ICVFX着色器中的不透明度处理。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中未遵循非默认DisplayGamma设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时可能导致的画面闪烁问题。 |

### 维护评价

nDisplay插件**仍在积极维护中**，且更新非常频繁。从提交历史看，Epic Games团队持续为其添加新功能（如EXR多层、改进的MovieGraph集成）并修复底层bug。考虑到其创建于2018年，且功能复杂度极高，它是一个成熟且关键的企业级功能插件。

**主要注意事项**：
1.  **启用方式**：`EnabledByDefault`为`false`，必须在项目插件设置中手动启用。
2.  **平台支持**：仅支持Win64和Linux，与大多数高性能图形应用需求一致。
3.  **复杂度**：是一个xlarge级别的插件，学习曲线较陡峭，通常需要专门的硬件设置和配置。
4.  **依赖**：部分功能深度依赖D3D12RHI和媒体框架。

**推荐**：对于需要构建专业级多机渲染集群的项目，nDisplay是官方且功能完备的首选方案。但对于简单的多屏扩展，可能过于复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-unreal-engine/)（Unreal Engine 官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/Private)