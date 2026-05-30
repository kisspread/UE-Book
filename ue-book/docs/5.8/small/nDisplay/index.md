# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群渲染**系统，核心解决的问题是：**如何让多台 PC 协同同步渲染同一个虚拟场景，驱动多块屏幕/投影仪组成沉浸式显示环境**。

它不只是简单的"多屏显示"，而是一套完整的分布式渲染管线，包含：

- **拓扑同步**：主机（Primary）向所有从机（Secondary）分发场景状态、时间线、游戏逻辑，确保每台 PC 渲染的是完全同步的世界
- **投影校正**：处理多投影仪的几何校正（Warping）、边缘融合（Blending）、MPCDI 标准支持
- **虚拟制片（ICVFX）**：LED 墙体的 Camera Frustum 实时跟随、Light Card 管理、色彩分级
- **帧同步与通信**：通过共享内存、网络消息实现亚帧级同步

简而言之：**如果你需要多台机器合力渲染一块巨大的画面（LED 墙、投影墙、CAVE），就用 nDisplay**。

## 使用场景

- **LED 虚拟制片**（如 The Mandalorian 风格）：摄影机后方的 LED 墙实时渲染场景，nDisplay 驱动整面墙的多块屏幕同步显示，且画面跟随摄影机视角变化
- **CAVE 沉浸式环境**：多面投影组成的立方体房间，观众佩戴 VR 眼镜体验沉浸式内容
- **多投影仪投影校正**：多台投影仪拼接大面积画面时的几何变形和边缘融合
- **大型场馆多屏展示**：如主题公园、展览馆中的弧幕/环幕投影系统
- **远程渲染集群**：多台渲染 PC 通过网络协同，驱动远程显示终端
- **电影预览与虚拟探查**：导演在 LED 现场实时预览最终合成效果

## 模块概览

### 核心运行时

| 模块 | 说明 |
|---|---|
| `DisplayCluster` | 核心模块，集群同步、帧分发、视口管理、插件框架 |
| `DisplayClusterConfiguration` | nDisplay 配置数据资产的定义与序列化（拓扑、视口、投影等） |
| `DisplayClusterProjection` | 投影策略实现：MPCDI、简单投影、Camera、圆柱体、网格投影等 |
| `DisplayClusterWarp` | Warp/Blend 几何校正与边缘融合核心算法 |
| `DisplayClusterShaders` | nDisplay 专用着色器（WarpBlend、MPCDI、ICVFX 相关） |
| `DisplayClusterColorGrading` | LED 墙和集群渲染的色彩分级后处理 |
| `DisplayClusterReplication` | 集群节点间的网络复制与同步 |
| `DisplayClusterScenePreview` | 场景预览渲染（用于编辑器和 Light Card 预览） |

### 媒体与 I/O

| 模块 | 说明 |
|---|---|
| `DisplayClusterMedia` | 媒体输入/输出集成（视频采集卡、NDI 等外部源） |
| `SharedMemoryMedia` | 基于共享内存的高帧率帧传输（GPU 直传，避免网络延迟） |
| `DisplayClusterMessageInterception` | 拦截和路由集群间的消息通信 |
| `DisplayClusterRemoteControlInterceptor` | 与 Remote Control API 的集成，支持远程参数控制 |

### 编辑器工具

| 模块 | 说明 |
|---|---|
| `DisplayClusterConfigurator` | nDisplay 配置编辑器（可视化配置拓扑、视口、投影） |
| `DisplayClusterEditor` | 编辑器扩展菜单和工作流集成 |
| `DisplayClusterDetails` | 属性细节面板扩展 |
| `DisplayClusterOperator` | 操作员面板（运行时监控与控制） |
| `DisplayClusterLightCardEditor` | Light Card 可视化编辑器（虚拟制片中的补光卡） |
| `DisplayClusterLightCardEditorShaders` | Light Card 编辑器专用着色器 |
| `DisplayClusterMediaEditor` | 媒体源编辑器扩展 |
| `DisplayClusterMonitor` | 运行时监控与诊断工具 |
| `DisplayClusterMonitorEditor` | 监控工具的编辑器 UI |

### 渲染管线扩展

| 模块 | 说明 |
|---|---|
| `DisplayClusterMoviePipeline` | Movie Render Queue 的 nDisplay 集成（集群离线渲染） |
| `DisplayClusterMoviePipelineEditor` | Movie Pipeline nDisplay 配置编辑器 |
| `DisplayClusterFillDerivedDataCache` | 预填充 DDC（确保集群所有节点资产同步） |
| `DisplayClusterStageMonitoring` | 舞台/LED 墙运行状态监控 |
| `DisplayClusterMultiUser` | Multi-User Editing 的 nDisplay 集成 |
| `DisplayClusterTests` | 自动化测试 |

### 第三方

| 模块 | 说明 |
|---|---|
| `ScalableMPCDI` (External) | MPCDI 标准（Multi-Projector Calibration Data Interchange）的第三方实现 |

## 蓝图用法

> 注意：nDisplay 主要通过**配置资产**和**编辑器工具**进行设置，运行时蓝图 API 相对有限。以下为核心可调用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前集群节点标识 | `UDisplayClusterBlueprintAPI` |
| `Get Game Viewport Size` | 获取当前视口尺寸 | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Event Listener` | 设置集群事件监听器 | `UDisplayClusterBlueprintAPI` |
| `Send Cluster Event` | 向集群其他节点发送自定义事件 | `UDisplayClusterBlueprintAPI` |
| `Get nDisplay Configuration` | 获取当前运行时配置引用 | `UDisplayClusterBlueprintAPI` |

### 使用示例

典型的 nDisplay 工作流**不依赖蓝图节点连线**，而是：

1. **创建 nDisplay 配置资产**（`.ndisplay` 文件）：在编辑器中配置集群拓扑、视口、投影
2. **启动时指定配置**：通过命令行 `-dccluster` 或编辑器中的 nDisplay 启动按钮
3. **运行时由系统自动管理**：同步、投影、Warp/Blend 均为引擎内部自动执行

需要自定义事件同步时，可通过蓝图的 `Send Cluster Event` 在集群节点间传递游戏逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "IDisplayCluster.h"
```

### 基本用法：访问 nDisplay 单例接口

```cpp
// 获取 nDisplay 插件单例
IDisplayCluster* DisplayCluster = FModuleManager::GetModulePtr<IDisplayCluster>("DisplayCluster");
if (DisplayCluster)
{
    // 检查当前是否在集群模式下运行
    bool bIsCluster = DisplayCluster->GetClusterMgr()->IsCluster();
    
    // 获取当前节点 ID
    FString NodeId = DisplayCluster->GetClusterMgr()->GetNodeId();
    
    // 获取集群同步策略
    IDisplayClusterClusterManager* ClusterMgr = DisplayCluster->GetClusterMgr();
}
```

### 进阶用法：集群事件通信

```cpp
// 注册自定义集群事件处理
IDisplayCluster* DC = IDisplayCluster::Get();
IDisplayClusterClusterManager* ClusterMgr = DC->GetClusterMgr();

// 监听来自其他节点的事件
ClusterMgr->AddClusterEventJsonListener(
    FOnClusterEventJson::FDelegate::CreateLambda(
        [](const FDisplayClusterClusterEventJson& Event)
        {
            UE_LOG(LogTemp, Log, TEXT("Received event: Category=%s Type=%s"),
                *Event.Category, *Event.Type);
        }
    )
);

// 发送事件到集群
FDisplayClusterClusterEventJson Event;
Event.Category = TEXT("Gameplay");
Event.Type = TEXT("SyncTrigger");
Event.bIsSystemEvent = false;
ClusterMgr->EmitClusterEventJson(Event, true);
```

## Demo 示例

```cpp
// MyClusterSyncActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyClusterSyncActor.generated.h"

UCLASS()
class AMyClusterSyncActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable)
    void BroadcastToCluster(const FString& Message);

private:
    FDelegateHandle EventHandle;
    void OnClusterEvent(const FDisplayClusterClusterEventJson& Event);
};
```

```cpp
// MyClusterSyncActor.cpp
#include "MyClusterSyncActor.h"
#include "IDisplayCluster.h"

void AMyClusterSyncActor::BeginPlay()
{
    Super::BeginPlay();
    
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        if (IDisplayClusterClusterManager* ClusterMgr = DC->GetClusterMgr())
        {
            EventHandle = ClusterMgr->AddClusterEventJsonListener(
                FOnClusterEventJson::FDelegate::CreateUObject(
                    this, &AMyClusterSyncActor::OnClusterEvent));
        }
    }
}

void AMyClusterSyncActor::BroadcastToCluster(const FString& Message)
{
    if (IDisplayCluster* DC = IDisplayCluster::Get())
    {
        FDisplayClusterClusterEventJson Event;
        Event.Category = TEXT("Gameplay");
        Event.Type = TEXT("Message");
        Event.Parameters.Add(TEXT("msg"), Message);
        DC->GetClusterMgr()->EmitClusterEventJson(Event, true);
    }
}

void AMyClusterSyncActor::OnClusterEvent(const FDisplayClusterClusterEventJson& Event)
{
    if (Event.Category == TEXT("Gameplay") && Event.Type == TEXT("Message"))
    {
        const FString* Msg = Event.Parameters.Find(TEXT("msg"));
        if (Msg)
        {
            UE_LOG(LogTemp, Log, TEXT("Cluster message received: %s"), **Msg);
        }
    }
}
```

## 模块依赖

nDisplay 的模块依赖非常广泛，以下是使用者需要关注的**独特依赖**：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | DirectX 12 渲染硬件接口（共享内存媒体传输） |
| `MediaUtils` | 媒体框架工具 |
| `MPCDI` | MPCDI 标准解析（如使用第三方校准数据） |
| `Json` | 配置文件 JSON 序列化 |
| `RenderCore` | 底层渲染管线接口 |
| `RHI` | 渲染硬件抽象层 |
| `ImageWriteQueue` | 截图和离线渲染输出 |
| `MovieRenderPipelineCore` | Movie Render Queue 集成 |
| `DisplayCluster` | 所有子模块均依赖此核心模块 |

> 注意：多个编辑器模块（如 `DisplayClusterConfigurator`、`DisplayClusterMonitor`）依赖 `UnrealEd`、`EditorWidgets`、`LevelEditor`。如果你只在运行时使用 nDisplay 集群渲染，不需要引用这些编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | Movie Pipeline 支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到统一 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄影机命名和 MPCDI/ICVFX 着色器透明度 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复非默认 DisplayGamma 的输出帧编码问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口时的闪烁问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- 29 个模块、1351 个源文件，是 UE5 中规模最大的插件之一
- 2026 年 5 月仍在**每周数次**功能性更新，覆盖 Movie Pipeline 集成、着色器修复、虚拟制片工作流
- 是 Epic 虚拟制片战略的核心组件（配合 ICVFX Stage、LED 墙使用）
- 自 2018 年（UE 4.20）引入以来持续迭代，功能不断扩展
- `EnabledByDefault: false` 是因为其使用场景特定（需要物理多机/多屏环境），不是因为不稳定
- **强烈推荐**用于所有虚拟制片、CAVE、多屏投影项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [nDisplay 子模块文档](DisplayCluster.md) | [DisplayClusterConfiguration](DisplayClusterConfiguration.md) | [DisplayClusterProjection](DisplayClusterProjection.md) | [DisplayClusterWarp](DisplayClusterWarp.md) | [DisplayClusterShaders](DisplayClusterShaders.md) | [DisplayClusterMedia](DisplayClusterMedia.md) | [DisplayClusterConfigurator](DisplayClusterConfigurator.md) | [DisplayClusterMoviePipeline](DisplayClusterMoviePipeline.md) | [DisplayClusterColorGrading](DisplayClusterColorGrading.md) | [DisplayClusterReplication](DisplayClusterReplication.md) | [DisplayClusterOperator](DisplayClusterOperator.md) | [DisplayClusterLightCardEditor](DisplayClusterLightCardEditor.md) | [DisplayClusterMonitor](DisplayClusterMonitor.md) | [SharedMemoryMedia](SharedMemoryMedia.md) | [ScalableMPCDI](ScalableMPCDI.md) | [DisplayClusterTests](DisplayClusterTests.md)