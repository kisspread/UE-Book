# nDisplay Configuration

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机集群渲染配置 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、JSON 模板、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群同步渲染**系统，用于将一个 Unreal 场景分布到多台 PC 上进行同步渲染，支持单目和立体（Stereo）模式。它的核心应用场景是 **虚拟制片（Virtual Production / ICVFX）**——通过 LED Volume 墙幕实时渲染场景背景，让实体摄影机拍摄到的画面与虚拟环境无缝融合。

本模块（DisplayClusterConfiguration）是 nDisplay 的**配置数据层**，定义了整个集群系统的所有数据结构：

- **场景层级**：相机、屏幕、变换节点
- **集群拓扑**：主节点、从节点、网络端口、视口分配
- **ICVFX 相机配置**：内视锥（Inner Frustum）、色度键（Chromakey）、光卡（Light Cards）、OCIO 色彩管理
- **渲染设置**：分辨率、缓冲比例、GPU 分配、Overscan、立体渲染
- **媒体输出**：Media I/O、分块输出（Tiled）、Texture Share
- **后处理**：色度分级、模糊、MIP 生成、输出重映射
- **配置文件版本管理**：支持 4.26、4.27、5.00 三种 JSON 格式的加载和迁移

简单来说：如果你需要搭建一个 LED Volume 摄影棚或 CAVE 系统，nDisplay 就是引擎提供的基础设施，而这个配置模块是它运行的"蓝图图纸"。

## 使用场景

- **LED Volume 虚拟制片**：多台渲染 PC 驱动 LED 墙幕，实体摄影机通过 ICVFX 系统与虚拟场景实时合成
- **CAVE / 洞穴式沉浸显示**：多面投影墙围绕用户，每面墙由独立 PC 渲染
- **多屏拼接显示**：将一个大型场景分布到多个显示器/投影仪上
- **立体 3D 显示**：Side-by-Side 或 Top-Bottom 立体渲染
- **虚拟现实剧场**：同步多台 PC 的渲染输出，保持帧同步
- **线下渲染（Movie Pipeline）**：通过 nDrive MoviePipeline 模块批量渲染集群输出

## 蓝图用法

nDisplay 的配置数据层大量使用 `BlueprintReadWrite`/`BlueprintCallable`，可通过蓝图直接操作集群配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportIds` | 获取集群节点上所有视口 ID 列表 | `UDisplayClusterConfigurationClusterNode` |
| `GetViewport` | 根据视口 ID 获取视口配置对象 | `UDisplayClusterConfigurationClusterNode` |
| `GetReferencedMeshNames` | 获取投影策略引用的所有 Mesh 名称 | `UDisplayClusterConfigurationClusterNode` |
| `GetNodeIds` | 获取集群中所有节点 ID | `UDisplayClusterConfigurationCluster` |
| `GetNode` | 根据节点 ID 获取节点配置对象 | `UDisplayClusterConfigurationCluster` |
| `GetViewportIds` (全局) | 获取集群所有视口 ID | `UDisplayClusterConfigurationData` |
| `GetViewport` (全局) | 根据视口 ID 获取视口对象 | `UDisplayClusterConfigurationData` |
| `GetCameraIds` | 获取所有 ICVFX 相机 ID | `UDisplayClusterConfigurationData` |
| `GetCamera` | 根据 ID 获取 ICVFX 相机配置 | `UDisplayClusterConfigurationData` |
| `GetNodeIds` (全局) | 获取所有集群节点 ID | `UDisplayClusterConfigurationData` |
| `GetNode` (全局) | 根据节点 ID 获取节点对象 | `UDisplayClusterConfigurationData` |
| `AssignPostprocess` | 为节点分配后处理效果 | `UDisplayClusterConfigurationData` |
| `RemovePostprocess` | 移除节点上的后处理效果 | `UDisplayClusterConfigurationData` |
| `GetProjectionPolicy` | 获取视口的投影策略配置 | `UDisplayClusterConfigurationData` |
| `GetReferencedMeshNames` | 获取所有引用的 Mesh 名称 | `UDisplayClusterConfigurationData` |

### 使用示例（蓝图描述）

**遍历集群节点并获取视口信息：**
1. 使用 `UDisplayClusterConfigurationData::GetNodeIds` 获取所有节点 ID 数组
2. 对每个节点 ID 调用 `GetNode` 获取节点对象
3. 在节点对象上调用 `GetViewportIds` 获取视口列表
4. 对每个视口 ID 调用 `GetViewport` 获取视口配置
5. 从视口配置中读取 `ProjectionPolicy`、`Region`、`Camera` 等属性

**动态修改后处理效果：**
1. 获取 `UDisplayClusterConfigurationData` 引用
2. 调用 `AssignPostprocess(NodeId, PostprocessId, Type, Parameters)` 为指定节点添加后处理
3. 使用 `RemovePostprocess(NodeId, PostprocessId)` 移除效果

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterConfigurationTypes_ICVFX.h"
#include "DisplayClusterConfigurationTypes_Viewport.h"
#include "DisplayClusterConfigurationTypes_Postprocess.h"
#include "IDisplayClusterConfiguration.h"
```

### 基本用法：加载 nDisplay 配置文件

```cpp
// 通过模块接口加载 .ndisplay 配置文件
// 来源: Public/IDisplayClusterConfiguration.h

#include "IDisplayClusterConfiguration.h"

void LoadDisplayConfig()
{
    if (IDisplayClusterConfiguration::IsAvailable())
    {
        IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
        
        // 获取配置文件版本
        FString ConfigPath = TEXT("MyConfig.ndisplay");
        EDisplayClusterConfigurationVersion Version = ConfigModule.GetConfigVersion(ConfigPath);
        
        // 加载配置数据
        UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(ConfigPath);
        
        if (ConfigData)
        {
            // 获取集群节点数量
            uint32 NodeCount = ConfigData->GetNumberOfClusterNodes();
            
            // 获取主节点地址
            FString PrimaryAddr = ConfigData->GetPrimaryNodeAddress();
            
            // 遍历所有节点
            TArray<FString> NodeIds;
            ConfigData->GetNodeIds(NodeIds);
            
            for (const FString& NodeId : NodeIds)
            {
                UDisplayClusterConfigurationClusterNode* Node = ConfigData->GetNode(NodeId);
                if (Node)
                {
                    // 获取该节点上的所有视口
                    TArray<FString> ViewportIds;
                    Node->GetViewportIds(ViewportIds);
                    
                    UE_LOG(LogTemp, Log, TEXT("Node %s has %d viewports, host: %s"),
                        *NodeId, ViewportIds.Num(), *Node->Host);
                }
            }
        }
    }
}
```

### 进阶用法：访问 ICVFX 相机与色度键配置

```cpp
// 来源: Public/DisplayClusterConfigurationTypes_ICVFX.h, Public/DisplayClusterConfigurationTypes.h

void ConfigureICVFX(UDisplayClusterConfigurationData* ConfigData)
{
    if (!ConfigData || !ConfigData->Cluster)
        return;
    
    // 获取全局 ICVFX Stage 设置
    const FDisplayClusterConfigurationICVFX_StageSettings& StageSettings = ConfigData->StageSettings;
    
    // 检查内视锥是否启用
    bool bInnerFrustumEnabled = StageSettings.bEnableInnerFrustums;
    
    // 获取默认 ICVFX 帧分辨率
    int32 DefaultWidth = StageSettings.DefaultFrameSize.Width;
    int32 DefaultHeight = StageSettings.DefaultFrameSize.Height;
    
    // 遍历所有相机，检查 OCIO 配置
    TArray<FString> CameraIds;
    // (通过 ConfigData 公开的 API 获取相机列表)
    
    // 获取指定视口的 OCIO 配置
    const FOpenColorIOColorConversionSettings* OCIOConfig =
        StageSettings.FindViewportOCIOConfiguration(TEXT("Viewport_1"));
    
    // 检查全局色度键设置
    const FDisplayClusterConfigurationICVFX_GlobalChromakeySettings& Chromakey = 
        StageSettings.GlobalChromakey;
    
    // 获取视口的渲染设置
    UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(TEXT("Node_1"));
    if (Node)
    {
        UDisplayClusterConfigurationViewport* Viewport = Node->GetViewport(TEXT("Viewport_1"));
        if (Viewport)
        {
            // 检查视口是否启用 ICVFX
            bool bICVFXEnabled = Viewport->ICVFX.bAllowICVFX;
            
            // 获取视口的 ICVFX 标志
            EDisplayClusterViewportICVFXFlags Flags = 
                Viewport->GetViewportICVFXFlags(StageSettings);
            
            // 获取渲染设置
            const FDisplayClusterConfigurationViewport_RenderSettings& RenderSettings = 
                Viewport->RenderSettings;
            float BufferRatio = RenderSettings.BufferRatio;
            int32 GPUIndex = Viewport->GPUIndex;
            
            // 检查立体渲染模式
            EDisplayClusterConfigurationViewport_StereoMode StereoMode = 
                RenderSettings.StereoMode;
            
            // 检查 Overscan 设置
            if (RenderSettings.Overscan.bEnabled)
            {
                float LeftOverscan = RenderSettings.Overscan.Left;
                float RightOverscan = RenderSettings.Overscan.Right;
            }
        }
    }
}
```

### 进阶用法：媒体输出配置

```cpp
// 来源: Public/DisplayClusterConfigurationTypes_Media.h

void CheckMediaOutput(UDisplayClusterConfigurationClusterNode* Node)
{
    if (!Node) return;
    
    // 检查节点级别的媒体设置
    const FDisplayClusterConfigurationMediaNodeBackbuffer& MediaSettings = Node->MediaSettings;
    if (MediaSettings.bEnable)
    {
        // 检查是否有媒体输出绑定
        bool bHasOutput = MediaSettings.IsMediaOutputAssigned();
        
        // 检查分块输出布局
        FIntPoint TileLayout = MediaSettings.TiledSplitLayout;
    }
    
    // 检查视口级别的媒体设置
    UDisplayClusterConfigurationViewport* Viewport = Node->GetViewport(TEXT("Viewport_1"));
    if (Viewport)
    {
        const FDisplayClusterConfigurationMediaViewport& MediaConfig = 
            Viewport->RenderSettings.Media;
        if (MediaConfig.bEnable)
        {
            bool bHasInput = MediaConfig.IsMediaInputAssigned();
            bool bHasOutput = MediaConfig.IsMediaOutputAssigned();
        }
    }
}
```

## Demo 示例

一个可编译的最小示例：在运行时加载 nDisplay 配置并遍历集群拓扑。

### MyDisplayClusterActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationTypes.h"
#include "MyDisplayClusterActor.generated.h"

UCLASS()
class MYGAME_API AMyDisplayClusterActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDisplayClusterActor();

    virtual void BeginPlay() override;

    /** nDisplay 配置文件路径 */
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString ConfigFilePath;

private:
    void PrintClusterTopology(UDisplayClusterConfigurationData* ConfigData);
};
```

### MyDisplayClusterActor.cpp

```cpp
#include "MyDisplayClusterActor.h"
#include "DisplayClusterConfigurationTypes_Viewport.h"
#include "DisplayClusterConfigurationTypes_ICVFX.h"

AMyDisplayClusterActor::AMyDisplayClusterActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDisplayClusterActor::BeginPlay()
{
    Super::BeginPlay();

    if (!IDisplayClusterConfiguration::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterConfiguration module not available"));
        return;
    }

    IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
    UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(ConfigFilePath, this);

    if (ConfigData)
    {
        PrintClusterTopology(ConfigData);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load nDisplay config: %s"), *ConfigFilePath);
    }
}

void AMyDisplayClusterActor::PrintClusterTopology(UDisplayClusterConfigurationData* ConfigData)
{
    if (!ConfigData || !ConfigData->Cluster)
        return;

    UE_LOG(LogTemp, Log, TEXT("=== nDisplay Cluster Topology ==="));
    UE_LOG(LogTemp, Log, TEXT("Description: %s"), *ConfigData->Info.Description);
    UE_LOG(LogTemp, Log, TEXT("Total Nodes: %u"), ConfigData->GetNumberOfClusterNodes());
    UE_LOG(LogTemp, Log, TEXT("Primary Node: %s"), *ConfigData->GetPrimaryNodeAddress());

    // 遍历所有集群节点
    TArray<FString> NodeIds;
    ConfigData->Cluster->GetNodeIds(NodeIds);

    for (const FString& NodeId : NodeIds)
    {
        UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(NodeId);
        if (!Node) continue;

        UE_LOG(LogTemp, Log, TEXT("  Node: %s | Host: %s | Sound: %s | Fullscreen: %s"),
            *NodeId,
            *Node->Host,
            Node->bIsSoundEnabled ? TEXT("Yes") : TEXT("No"),
            Node->bIsFullscreen ? TEXT("Yes") : TEXT("No"));

        // 遍历该节点的视口
        TArray<FString> ViewportIds;
        Node->GetViewportIds(ViewportIds);

        for (const FString& ViewportId : ViewportIds)
        {
            UDisplayClusterConfigurationViewport* Viewport = Node->GetViewport(ViewportId);
            if (!Viewport) continue;

            UE_LOG(LogTemp, Log, TEXT("    Viewport: %s | Camera: %s | Region: (%d,%d %dx%d) | ICVFX: %s"),
                *ViewportId,
                *Viewport->Camera,
                Viewport->Region.X, Viewport->Region.Y,
                Viewport->Region.W, Viewport->Region.H,
                Viewport->ICVFX.bAllowICVFX ? TEXT("Yes") : TEXT("No"));
        }
    }

    // 打印 ICVFX Stage 设置
    const FDisplayClusterConfigurationICVFX_StageSettings& ICVFX = ConfigData->StageSettings;
    UE_LOG(LogTemp, Log, TEXT("ICVFX Settings:"));
    UE_LOG(LogTemp, Log, TEXT("  Inner Frustum: %s"), ICVFX.bEnableInnerFrustums ? TEXT("Enabled") : TEXT("Disabled"));
    UE_LOG(LogTemp, Log, TEXT("  Default Frame: %dx%d"), ICVFX.DefaultFrameSize.Width, ICVFX.DefaultFrameSize.Height);
    UE_LOG(LogTemp, Log, TEXT("  Freeze Outer Viewports: %s"), ICVFX.bFreezeRenderOuterViewports ? TEXT("Yes") : TEXT("No"));
}
```

## 模块依赖

从各模块的 Build.cs 分析，以下是该插件**独特**的、不常见的依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | DisplayClusterMedia、SharedMemoryMedia 模块使用 D3D12 资源共享 |
| `LevelEditor` | DisplayCluster 核心模块的编辑器集成 |
| `EditorWidgets` | DisplayCluster 核心模块的编辑器 UI 组件 |

无其他特殊依赖（其余均为标准 Core/Engine/Slate 等）。使用者的 Build.cs 需要根据具体使用的子模块添加对应依赖，例如：

```cpp
// 仅使用配置数据类型
PublicDependencyModuleNames.Add("DisplayClusterConfiguration");

// 使用完整 nDisplay 功能
PublicDependencyModuleNames.Add("DisplayCluster");
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 到 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名；修复 MPCDI/ICVFX 着色器不透明度 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时尊重非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2018 年 6 月（UE 4.20 企业版功能），至今约 8 年
- **更新频率**：极高，最近提交日期为 2026 年 5 月，每周都有多次功能性更新和 bug 修复
- **维护状态**：由 Epic Games 专人团队持续维护，是 Unreal 虚拟制片（Virtual Production）的核心基础设施
- **代码规模**：28 个模块、1351 个源文件，是引擎最大的插件之一
- **配置版本演进**：支持 4.26→4.27→5.00 三代配置格式的向后兼容和自动迁移
- **已知限制**：需要手动启用（`EnabledByDefault = false`）；仅支持 Win64 和 Linux 平台
- **推荐使用**：如果你的项目涉及虚拟制片、LED Volume、CAVE 显示或多屏拼接，这是**官方唯一推荐**的解决方案，生态成熟，文档和社区支持完善

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/)（Unreal Engine 官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)