# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染系统 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、着色器、配置工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

---

> **⚠️ 注意**：本文档聚焦于 `DisplayClusterConfiguration` 子模块（配置数据定义与加载），这是 nDisplay 的核心配置系统。完整插件包含 28 个子模块、超过 1300 个源文件，本页为主要入口文档。

## 用途

nDisplay 是 UE5 内置的**多机集群渲染系统**，用于将一个 Unreal 应用的渲染画面同步分发到多台 PC 上，驱动大型 LED 墙、投影幕、CAVE 系统等沉浸式显示环境。它解决的核心问题是：

1. **同步渲染**：多台 PC 通过网络保持帧同步（NVIDIA Swap Barrier / Present Barrier、以太网 Barrier 等），确保所有屏幕画面一致。
2. **投影映射**：每个屏幕（Viewport）可配置独立的投影策略（MPCDI、WarpBlend、Camera 等），支持曲面投影和几何校正。
3. **ICVFX（In-Camera VFX）**：为虚拟制片设计，支持 Inner Frustum（摄影机视锥内画面）、Chromakey（色键抠像）、Light Card（灯光卡）等专用渲染通道。
4. **集群管理**：一个 Primary Node 协调多个 Cluster Node，管理节点间通信、故障转移（Failover）和状态同步。

**为什么存在**：虚幻引擎原生只支持单机渲染输出。当需要将画面输出到多块物理屏幕（如环绕投影、LED Volume、CAVE）时，必须使用 nDisplay 来协调多台渲染主机。

## 使用场景

- 你在做**虚拟制片（Virtual Production）**项目，需要驱动 LED Volume 墙体 → 用 nDisplay 配置 ICVFX 摄影机和 Outer Viewports
- 你需要搭建 **CAVE 洞穴投影系统**（6 面投影）→ 用 nDisplay 分配 6 个 Viewport 到不同投影仪
- 你要做**驾驶模拟器**，多台 PC 分别渲染不同屏幕 → 用 nDisplay 集群同步
- 你需要**多投影仪边缘融合**（Edge Blending）→ 用 nDisplay 的 Overscan 配置
- 你要在**多 GPU** 机器上分担负载 → 用 nDisplay 的 GPUIndex 配置将 Viewport 分配到不同 GPU

## 蓝图用法

> 注意：nDisplay 的配置主要通过 .ndisplay 配置文件和编辑器 UI 完成。运行时 API 通过蓝图暴露的功能有限但关键。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportIds` | 获取指定集群节点的所有 Viewport ID 列表 | `UDisplayClusterConfigurationClusterNode` |
| `GetViewport` | 通过 ID 获取 Viewport 配置对象 | `UDisplayClusterConfigurationClusterNode` |
| `GetReferencedMeshNames` | 获取策略引用的所有网格资产名称 | `UDisplayClusterConfigurationClusterNode` |
| `GetNodeIds` | 获取集群中所有节点 ID | `UDisplayClusterConfigurationCluster` |
| `GetNode` | 通过 ID 获取集群节点配置对象 | `UDisplayClusterConfigurationCluster` |
| `AssignPostprocess` | 为指定节点添加后处理效果 | `UDisplayClusterConfigurationData` |
| `RemovePostprocess` | 移除指定节点的后处理效果 | `UDisplayClusterConfigurationData` |
| `GetPostprocess` | 获取指定节点的后处理配置 | `UDisplayClusterConfigurationData` |
| `GetProjectionPolicy` | 获取指定 Viewport 的投影策略 | `UDisplayClusterConfigurationData` |
| `LoadConfig` (接口) | 从 .ndisplay 文件加载配置数据 | `IDisplayClusterConfiguration` |
| `SaveConfig` (接口) | 将配置数据保存到 .ndisplay 文件 | `IDisplayClusterConfiguration` |

### 使用示例（蓝图描述）

**运行时读取配置并遍历节点：**

1. 获取 `IDisplayClusterConfiguration` 模块接口（通过 `FModuleManager::GetModuleChecked`，蓝图中需自定义 Blueprint Function Library 封装）
2. 调用 `LoadConfig` 加载 .ndisplay 配置文件，获得 `UDisplayClusterConfigurationData` 对象
3. 从 `Data->Cluster` 调用 `GetNodeIds` 获取所有节点 ID
4. 对每个节点 ID 调用 `GetNode`，再从节点对象调用 `GetViewportIds` 遍历 Viewport

**运行时动态添加后处理：**

1. 获取 `UDisplayClusterConfigurationData` 引用
2. 调用 `AssignPostprocess(NodeId, "MyPP", "Type", Parameters, Order)` 为指定节点添加后处理

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterConfigurationTypes_ICVFX.h"
#include "DisplayClusterConfigurationTypes_Viewport.h"
```

### 基本用法

**加载和查询 nDisplay 配置文件：**

```cpp
// 来源：Public/IDisplayClusterConfiguration.h + Private/DisplayClusterConfigurationModule.h
#include "IDisplayClusterConfiguration.h"

// 加载配置文件
IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(TEXT("/Game/Configs/MyStage.ndisplay"));

if (ConfigData)
{
    // 获取集群信息
    UDisplayClusterConfigurationCluster* Cluster = ConfigData->Cluster;
    
    // 遍历所有集群节点
    TArray<FString> NodeIds;
    Cluster->GetNodeIds(NodeIds);
    
    for (const FString& NodeId : NodeIds)
    {
        UDisplayClusterConfigurationClusterNode* Node = Cluster->GetNode(NodeId);
        if (Node)
        {
            UE_LOG(LogTemp, Log, TEXT("Node %s, Host: %s"), *NodeId, *Node->Host);
            
            // 遍历该节点的所有 Viewport
            TArray<FString> ViewportIds;
            Node->GetViewportIds(ViewportIds);
            
            for (const FString& ViewportId : ViewportIds)
            {
                UDisplayClusterConfigurationViewport* Viewport = Node->GetViewport(ViewportId);
                if (Viewport && Viewport->IsViewportEnabled())
                {
                    UE_LOG(LogTemp, Log, TEXT("  Viewport %s, Region: %d,%d %dx%d"),
                        *ViewportId,
                        Viewport->Region.X, Viewport->Region.Y,
                        Viewport->Region.W, Viewport->Region.H);
                }
            }
        }
    }
}
```

### 进阶用法

**读取 ICVFX 摄影机配置和 Light Card 设置：**

```cpp
// 来源：Public/DisplayClusterConfigurationTypes_ICVFX.h
#include "DisplayClusterConfigurationTypes_ICVFX.h"

if (ConfigData && ConfigData->Cluster)
{
    // 访问 Stage 级 ICVFX 设置
    const FDisplayClusterConfigurationICVFX_StageSettings& StageSettings = ConfigData->StageSettings;
    
    // 检查 Inner Frustum 是否启用
    bool bInnerFrustumEnabled = StageSettings.bEnableInnerFrustums;
    
    // 获取默认帧分辨率
    int32 DefaultWidth = StageSettings.DefaultFrameSize.Width;   // 默认 2560
    int32 DefaultHeight = StageSettings.DefaultFrameSize.Height;  // 默认 1440
    bool bAdaptToFilmback = StageSettings.DefaultFrameSize.bAdaptSize;
    
    // 获取 Light Card 设置
    const FDisplayClusterConfigurationICVFX_LightcardSettings& LightcardSettings = StageSettings.Lightcard;
    
    // 查询全局 Chromakey 设置
    const FDisplayClusterConfigurationICVFX_GlobalChromakeySettings& Chromakey = StageSettings.GlobalChromakey;
    
    // 查询 Viewport 级 ICVFX 设置（在 UDisplayClusterConfigurationViewport 上）
    TArray<FString> NodeIds;
    ConfigData->Cluster->GetNodeIds(NodeIds);
    
    for (const FString& NodeId : NodeIds)
    {
        UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(NodeId);
        if (!Node) continue;
        
        TArray<FString> ViewportIds;
        Node->GetViewportIds(ViewportIds);
        
        for (const FString& ViewportId : ViewportIds)
        {
            UDisplayClusterConfigurationViewport* Viewport = Node->GetViewport(ViewportId);
            if (!Viewport) continue;
            
            // 获取 ICVFX 标志位
            EDisplayClusterViewportICVFXFlags Flags = Viewport->GetViewportICVFXFlags(StageSettings);
            
            // 检查该 Viewport 是否允许 ICVFX
            bool bAllowICVFX = Viewport->ICVFX.bAllowICVFX;
            bool bAllowInnerFrustum = Viewport->ICVFX.bAllowInnerFrustum;
            
            // 检查立体渲染设置
            EDisplayClusterConfigurationViewport_StereoMode StereoMode = Viewport->RenderSettings.StereoMode;
            
            // 检查 Overscan 配置
            const FDisplayClusterConfigurationViewport_Overscan& Overscan = Viewport->RenderSettings.Overscan;
            if (Overscan.bEnabled)
            {
                UE_LOG(LogTemp, Log, TEXT("Viewport %s overscan: L=%f R=%f T=%f B=%f"),
                    *ViewportId, Overscan.Left, Overscan.Right, Overscan.Top, Overscan.Bottom);
            }
        }
    }
}
```

**查询媒体输出配置：**

```cpp
// 来源：Public/DisplayClusterConfigurationTypes_Media.h
#include "DisplayClusterConfigurationTypes_Media.h"

// 全局媒体延迟设置
int32 MediaLatency = ConfigData->MediaSettings.Latency;

// 检查节点级媒体设置
for (const FString& NodeId : NodeIds)
{
    UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(NodeId);
    if (!Node) continue;
    
    const FDisplayClusterConfigurationMediaNodeBackbuffer& MediaCfg = Node->MediaSettings;
    if (MediaCfg.bEnable)
    {
        UE_LOG(LogTemp, Log, TEXT("Node %s has media enabled"), *NodeId);
        
        // 检查是否有全帧输出或分块输出
        if (MediaCfg.MediaOutputs.Num() > 0)
        {
            UE_LOG(LogTemp, Log, TEXT("  Full-frame media outputs: %d"), MediaCfg.MediaOutputs.Num());
        }
        
        if (MediaCfg.TiledMediaOutputs.Num() > 0)
        {
            UE_LOG(LogTemp, Log, TEXT("  Tiled media outputs: %d"), MediaCfg.TiledMediaOutputs.Num());
            UE_LOG(LogTemp, Log, TEXT("  Split layout: %dx%d"), MediaCfg.TiledSplitLayout.X, MediaCfg.TiledSplitLayout.Y);
        }
    }
}
```

**保存配置并检查版本兼容性：**

```cpp
// 来源：Private/DisplayClusterConfigurationModule.h + Public/DisplayClusterConfigurationVersion.h
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationVersion.h"

IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();

// 检查配置文件版本
EDisplayClusterConfigurationVersion Version = ConfigModule.GetConfigVersion(TEXT("/Game/Configs/MyStage.ndisplay"));
switch (Version)
{
case EDisplayClusterConfigurationVersion::Version_426:
    UE_LOG(LogTemp, Log, TEXT("Config is 4.26 format"));
    break;
case EDisplayClusterConfigurationVersion::Version_427:
    UE_LOG(LogTemp, Log, TEXT("Config is 4.27 format"));
    break;
case EDisplayClusterConfigurationVersion::Version_500:
    UE_LOG(LogTemp, Log, TEXT("Config is 5.0 format"));
    break;
default:
    UE_LOG(LogTemp, Warning, TEXT("Unknown or unsupported config format"));
    break;
}

// 加载后自动升级到最新版本（内部由 UpdateToLatest 处理）
UDisplayClusterConfigurationData* Data = ConfigModule.LoadConfig(TEXT("/Game/Configs/MyStage.ndisplay"));

// 保存配置
FString OutputPath = TEXT("/Game/Configs/MyStage_Copy.ndisplay");
ConfigModule.SaveConfig(Data, OutputPath);

// 导出为 JSON 字符串
FString ConfigString;
if (ConfigModule.ConfigAsString(Data, ConfigString))
{
    UE_LOG(LogTemp, Log, TEXT("Config as string:\n%s"), *ConfigString);
}
```

## Demo 示例

**最小示例：创建一个 nDisplay 配置数据并添加节点和 Viewport：**

```cpp
// MyNDisplayConfigHelper.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterConfigurationTypes_Viewport.h"
#include "IDisplayClusterConfiguration.h"

class FMyNDisplayConfigHelper
{
public:
    /** 创建一个简单的双节点集群配置 */
    static UDisplayClusterConfigurationData* CreateSimpleTwoNodeConfig(UObject* Outer)
    {
        // 创建空配置
        UDisplayClusterConfigurationData* Config = UDisplayClusterConfigurationData::CreateNewConfigData(Outer);
        if (!Config) return nullptr;

        // 设置配置信息
        Config->Info.Description = TEXT("Simple 2-node cluster");

        // 创建主节点（Primary Node）
        UDisplayClusterConfigurationClusterNode* MasterNode = NewObject<UDisplayClusterConfigurationClusterNode>(Config);
        MasterNode->Host = TEXT("192.168.1.100");
        MasterNode->bIsFullscreen = true;
        MasterNode->bIsSoundEnabled = true;

        // 为主节点添加一个 Viewport
        UDisplayClusterConfigurationViewport* MasterViewport = NewObject<UDisplayClusterConfigurationViewport>(MasterNode);
        MasterViewport->Camera = TEXT("camera_icvfx");
        MasterViewport->Region = FDisplayClusterConfigurationRectangle(0, 0, 1920, 1080);
        MasterViewport->RenderSettings.BufferRatio = 1.0f;
        MasterViewport->RenderSettings.StereoMode = EDisplayClusterConfigurationViewport_StereoMode::Default;
        MasterViewport->ProjectionPolicy.Type = TEXT("camera");

        MasterNode->Viewports.Add(TEXT("viewport_main"), MasterViewport);

        // 创建从节点（Secondary Node）
        UDisplayClusterConfigurationClusterNode* SlaveNode = NewObject<UDisplayClusterConfigurationClusterNode>(Config);
        SlaveNode->Host = TEXT("192.168.1.101");
        SlaveNode->bIsFullscreen = true;

        // 为从节点添加一个 Viewport
        UDisplayClusterConfigurationViewport* SlaveViewport = NewObject<UDisplayClusterConfigurationViewport>(SlaveNode);
        SlaveViewport->Camera = TEXT("camera_icvfx");
        SlaveViewport->Region = FDisplayClusterConfigurationRectangle(0, 0, 1920, 1080);
        SlaveViewport->ProjectionPolicy.Type = TEXT("camera");

        SlaveNode->Viewports.Add(TEXT("viewport_secondary"), SlaveViewport);

        // 将节点注册到集群
        Config->Cluster->Nodes.Add(TEXT("node_master"), MasterNode);
        Config->Cluster->Nodes.Add(TEXT("node_slave"), SlaveNode);

        // 设置主节点
        Config->Cluster->PrimaryNode.Id = TEXT("node_master");

        return Config;
    }

    /** 将配置保存到文件 */
    static bool SaveConfigToFile(UDisplayClusterConfigurationData* Config, const FString& FilePath)
    {
        if (!IDisplayClusterConfiguration::IsAvailable()) return false;

        IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
        return ConfigModule.SaveConfig(Config, FilePath);
    }
};
```

## 模块依赖

从各模块的 Build.cs 分析，nDisplay 有以下**独特**依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（SharedMemoryMedia、DisplayClusterMedia 用于 GPU 共享内存传输） |
| `MediaUtils` / `MediaFrameworkUtilities` | Unreal Media Framework 集成（媒体输入/输出管道） |
| `MPCDI` | MPCDI 标准投影映射支持 |
| `OpenColorIO` | OCIO 色彩管理集成 |
| `TextureShare` | 跨进程纹理共享（与外部应用程序交换渲染数据） |
| `ProceduralMeshComponent` | 运行时网格生成（Warp Blend 曲面校正） |

> 大量模块依赖 `UnrealEd`、`EditorWidgets`、`LevelEditor` 等编辑器模块，因为 nDisplay 提供了丰富的编辑器内配置界面。运行时功能依赖标准 Core/Engine/Slate 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 和 nDisplay 支持 EXR 多层渲染 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄影机命名和 MPCDI/ICVFX 着色器不透明度 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护**。nDisplay 是 Epic Games 企业级功能的核心组件，自 2018 年创建以来持续获得高强度更新：

- **更新频率**：每月甚至每周都有实质性提交，最近一周内有 5 次提交
- **维护规模**：28 个子模块、1300+ 源文件，属于 UE5 中最大的 Runtime 插件之一
- **功能演进**：从基础集群渲染 → 4.27 ICVFX → 5.x OCIO/媒体/瓦片渲染/MoviePipeline 集成，功能持续扩展
- **向后兼容**：维护了 4.26、4.27、5.00 三个版本的配置格式解析器，旧配置可自动升级
- **默认禁用**：`EnabledByDefault=false`，需要在插件设置中手动启用，因为该插件仅适用于特定硬件配置场景

**推荐使用**：如果你的项目涉及虚拟制片、多屏投影或沉浸式显示环境，nDisplay 是 UE5 唯一官方的集群渲染方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/in-camera-vfx-in-unreal-engine/)（虚拟制片/nDisplay 综合文档）
- [nDisplay 配置文件格式](https://docs.unrealengine.com/5.8/en-US/ndisplay-configuration-file-reference-in-unreal-engine/)