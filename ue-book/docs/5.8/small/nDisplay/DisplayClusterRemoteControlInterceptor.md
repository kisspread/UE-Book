# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式显示集群 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、蓝图资产、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的**分布式集群渲染系统**，用于将一个 UE 场景同步渲染到多台 PC 驱动的多个显示器上，支持单目和立体渲染。其核心解决的是：

- **多通道同步渲染**：在 LED Volume、CAVE 系统、穹顶投影、驾驶模拟器等专业可视化场景中，需要多台机器精确同步地渲染同一场景的不同视角/投影面
- **复杂投影映射**：支持 MPCDI、MPCDI + Warp/Blend、平面/圆柱/球面投影等多种投影几何校正方式
- **集群拓扑管理**：通过配置文件定义集群中各节点的角色（Primary/Cluster）、输入设备映射、同步策略
- **远程控制与监控**：提供远程控制接口（Remote Control）、集群事件系统、舞台监控等运维能力
- **媒体集成**：通过 SharedMemoryMedia 等模块实现高效的跨节点帧数据传输（GPU 共享内存）
- **ICVFX / LED Wall 支持**：与虚拟制片流程深度集成，支持 In-Camera VFX 的 LED Wall 工作流

简单来说，nDisplay 就是 UE 的"多屏多机同步渲染引擎"，是虚拟制片（Virtual Production）、主题娱乐（Location-Based Entertainment）、专业可视化等行业的基础设施。

## 使用场景

- 你在搭建 **LED Volume 虚拟制片舞台**（类似 The Mandalorian 的 LED Wall）→ 用 nDisplay 配置多节点集群渲染
- 你需要 **CAVE 沉浸式显示系统**（多面投影房间）→ 用 nDisplay 定义每个投影面的几何和投影矩阵
- 你在做 **驾驶/飞行模拟器**，需要多台 PC 渲染多个显示器并保持同步 → 用 nDisplay 管理集群同步
- 你需要将渲染结果通过 **GPU 共享内存**高速传输到另一台机器（如视频拼接器）→ 用 SharedMemoryMedia 模块
- 你需要 **远程控制** nDisplay 集群中各节点的渲染参数（如颜色校正、投影参数）→ 用 DisplayClusterRemoteControlInterceptor
- 你需要在 **Sequencer / Movie Render Queue** 中录制多节点渲染输出 → 用 DisplayClusterMoviePipeline 模块

## 蓝图用法

nDisplay 的大部分核心功能通过配置文件驱动，运行时蓝图 API 相对集中在集群事件和远程控制方面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetObjectProperties` | 远程设置对象属性（通过拦截器跨集群复制） | `FDisplayClusterRemoteControlInterceptor` |
| `ResetObjectProperties` | 远程重置对象属性到默认值 | `FDisplayClusterRemoteControlInterceptor` |
| `InvokeCall` | 远程调用对象函数（通过拦截器跨集群复制） | `FDisplayClusterRemoteControlInterceptor` |
| `SetPresetController` | 设置预设控制器（通过拦截器跨集群复制） | `FDisplayClusterRemoteControlInterceptor` |
| `OnClusterEventBinaryHandler` | 集群二进制事件处理（内部回调） | `FDisplayClusterRemoteControlInterceptor` |

### 集群事件系统

nDisplay 提供基于二进制集群事件的通信机制。Remote Control Interceptor 模块利用此机制实现跨集群节点的参数同步：

1. Primary 节点接收到 Remote Control 命令（如 SetObjectProperties）
2. Interceptor 将命令序列化为二进制缓冲区
3. 通过集群事件广播到所有 Cluster 节点
4. 各节点在本地反序列化并执行相同操作

### 配置驱动

nDisplay 的核心配置通过 `.ndisplay` 配置文件定义，而非蓝图：
- 集群拓扑（哪些节点、IP 地址、角色）
- 视口配置（分辨率、投影类型、Eye 编号）
- 输入映射（跟踪设备到视口的映射）
- 同步策略（帧锁、交换链配置）

配置文件可在编辑器中通过 **nDisplay Configurator** 工具可视化编辑。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRemoteControlInterceptorModule.h"
```

### 基本用法

Remote Control Interceptor 实现了 `IRemoteControlInterceptionFeatureInterceptor` 接口，当 Remote Control 插件尝试修改对象属性、调用函数时，拦截器会将操作通过集群事件广播到所有节点。

```cpp
// 拦截器的核心接口方法（由 Remote Control 插件回调）
// 来源: Source/DisplayClusterRemoteControlInterceptor/Private/DisplayClusterRemoteControlInterceptor.h

// 设置对象属性 - 将属性变更通过集群事件复制到所有节点
virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InProperties) override;

// 重置对象属性 - 将属性重置操作通过集群事件复制到所有节点
virtual ERCIResponse ResetObjectProperties(FRCIObjectMetadata& InObject) override;

// 调用函数 - 将函数调用通过集群事件复制到所有节点
virtual ERCIResponse InvokeCall(FRCIFunctionMetadata& InFunction) override;

// 设置预设控制器 - 将控制器变更通过集群事件复制到所有节点
virtual ERCIResponse SetPresetController(FRCIControllerMetadata& InController) override;
```

### 进阶用法

拦截器内部通过队列机制实现高效批处理：

```cpp
// 来源: Source/DisplayClusterRemoteControlInterceptor/Private/DisplayClusterRemoteControlInterceptor.h

// 队列结构：事件类型 -> (唯一路径 -> 序列化缓冲区)
// 同一对象同一字段的多次修改会被去重（只保留最后一次）
TMap<FName, TMap<FName, TArray<uint8>>> InterceptQueueMap;

// 队列会在每帧结束时统一发送（SendReplicationQueue），避免每笔操作都触发网络传输
void QueueInterceptEvent(const FName& InterceptEventType, 
                         const FName& InUniquePath, 
                         TArray<uint8>&& InBuffer);
```

**bInterceptOnPrimaryOnly**：可通过 CVar 控制拦截器是否仅在 Primary 节点生效。

**bForceApply**：可强制应用 ERCIResponse，绕过默认的响应处理逻辑。

## Demo 示例

以下展示如何在自定义模块中监听 nDisplay 集群事件：

```cpp
// MyNDisplayListener.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterClusterEvent.h"

class FMyNDisplayListener
{
public:
    void Initialize();
    void Deinitialize();

private:
    // 集群事件回调
    void OnClusterEventBinary(const FDisplayClusterClusterEventBinary& Event);
    void OnClusterEventJson(const FDisplayClusterClusterEventJson& Event);
    
    FOnClusterEventBinaryListener BinaryListener;
    FOnClusterEventJsonListener JsonListener;
};
```

```cpp
// MyNDisplayListener.cpp
#include "MyNDisplayListener.h"
#include "DisplayClusterModule.h"
#include "IDisplayClusterClusterManager.h"

void FMyNDisplayListener::Initialize()
{
    IDisplayClusterClusterManager* ClusterMgr = 
        IDisplayCluster::Get().GetClusterMgr();
    
    if (ClusterMgr)
    {
        // 注册二进制事件监听
        BinaryListener.BindRaw(this, &FMyNDisplayListener::OnClusterEventBinary);
        ClusterMgr->AddClusterEventBinaryListener(BinaryListener);
        
        // 注册 JSON 事件监听
        JsonListener.BindRaw(this, &FMyNDisplayListener::OnClusterEventJson);
        ClusterMgr->AddClusterEventJsonListener(JsonListener);
    }
}

void FMyNDisplayListener::Deinitialize()
{
    IDisplayClusterClusterManager* ClusterMgr = 
        IDisplayCluster::Get().GetClusterMgr();
    
    if (ClusterMgr)
    {
        ClusterMgr->RemoveClusterEventBinaryListener(BinaryListener);
        ClusterMgr->RemoveClusterEventJsonListener(JsonListener);
    }
}

void FMyNDisplayListener::OnClusterEventBinary(
    const FDisplayClusterClusterEventBinary& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received binary cluster event: %s"), 
        *Event.EventName.ToString());
}

void FMyNDisplayListener::OnClusterEventJson(
    const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received JSON cluster event: %s"), 
        *Event.EventName.ToString());
}
```

## 模块依赖

由于 nDisplay 模块众多，此处仅列出**独特依赖**（非常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 多个模块依赖，用于编辑器集成（配置器、灯光卡编辑器等） |
| `D3D12RHI` | SharedMemoryMedia 和 DisplayClusterMedia 模块用于 GPU 共享内存的 D3D12 实现 |
| `LevelEditor` | DisplayCluster 主模块，用于关卡编辑器集成 |
| `EditorWidgets` | DisplayCluster 主模块，用于编辑器 UI 组件 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 投影映射库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持多层 EXR 输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名和着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**🟢 活跃维护**

nDisplay 是 Unreal Engine 虚拟制片（Virtual Production）和专业可视化的核心基础设施，处于**持续活跃维护**状态：

- **创建于 2018 年**（UE 4.20），已运营约 8 年，是成熟的生产级系统
- **最近更新极为频繁**：仅 2026 年 5 月就有多次功能性更新，涵盖 MovieGraph EXR 多层支持、着色器修复、WarpBlend 重构等
- **拥有 28+ 个模块**，代码规模庞大（1351 个源文件），架构持续演进
- **功能不断扩展**：从基础集群渲染扩展到 ICVFX/LED Wall、Movie Render Queue 集成、共享内存媒体传输等
- **`EnabledByDefault: false`**：默认不启用，需手动在项目设置中开启，这是合理的——多数项目不需要分布式渲染
- **支持 Win64 和 Linux**：覆盖主要的生产和渲染平台
- **已知限制**：模块标注为 Runtime 但部分模块实际依赖 UnrealEd，打包时需注意编辑器模块剥离

**推荐使用**：如果你的项目涉及虚拟制片、多屏显示、集群渲染等专业场景，nDisplay 是官方唯一且持续维护的解决方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)