# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的专业级分布式渲染系统。其核心功能是让多台联网的 PC（集群）协同工作，共同渲染一个统一的虚拟场景，并将输出分配到多个物理显示器、投影仪或 LED 墙幕上。它解决的核心问题是通过空间计算和硬件同步，实现超大视场角（FOV）、立体（Stereoscopic 3D）或高分辨率的沉浸式视觉体验，广泛应用于电影虚拟制作（ICVFX）、大型模拟器、主题公园和可视化演示。

## 使用场景

-   **电影虚拟制作 (ICVFX)**：你在使用 LED 墙幕拍摄时，需要多台渲染主机精确同步地生成墙幕上不同区域的画面，同时还要处理摄影机内部的“内嵌”画面。→ 使用 nDisplay 配置集群、投影策略和 ICVFX 摄像机。
-   **多投影仪 CAVE 系统**：你需要构建一个由多台投影仪拼接成的环绕式显示环境。→ 使用 nDisplay 管理每个投影仪对应的视口（Viewport）及其投影校正（Projection）。
-   **立体渲染**：你的多屏显示器需要输出左眼和右眼画面以实现 3D 效果。→ 在 nDisplay 配置中设置立体模式（Stereo）和瞳距（Interpupillary Distance）。
-   **大型可视化**：你需要将一个高精度的工程模型或科学数据分布到多个显示器上展示。→ 使用 nDisplay 将单一场景分割渲染到多个节点上。
-   **媒体输入输出集成**：你需要将外部视频源（如摄影机实拍画面）输入到 LED 墙幕，或从渲染集群输出视频流。→ 使用 nDisplay 的 Media 模块进行配置。

## 蓝图用法

nDisplay 插件的运行时蓝图节点主要集中在对已加载配置的查询和运行时状态控制上。配置资产本身是一个复杂的 UObject 结构体（`UDisplayClusterConfigurationData`），通常通过编辑器或 C++ 代码加载。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNodeIds` | 获取当前集群配置中所有节点（PC）的ID列表 | `UDisplayClusterConfigurationCluster` |
| `GetNode` | 根据节点ID获取特定集群节点的配置对象 | `UDisplayClusterConfigurationCluster` |
| `GetViewportIds` | 获取指定集群节点上所有视口的ID列表 | `UDisplayClusterConfigurationClusterNode` |
| `GetViewport` | 根据视口ID获取特定视口的配置对象 | `UDisplayClusterConfigurationClusterNode` |
| `GetProjectionPolicy` | 获取指定视口的投影策略配置 | `UDisplayClusterConfigurationData` |
| `GetReferencedMeshNames` | 获取配置中引用的所有网格体名称（用于投影校正） | `UDisplayClusterConfigurationData` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接创建 `UDisplayClusterConfigurationData`。你的工作流可能是：
1.  通过 C++ 或自定义蓝图函数加载一个 `.ndisplay` 配置文件，获得一个 `UDisplayClusterConfigurationData` 对象引用。
2.  使用 `GetNodeIds` 节点获取所有节点列表。
3.  遍历节点列表，使用 `GetNode` 和 `GetViewportIds` 获取每个节点的视口信息。
4.  根据需要，使用 `GetProjectionPolicy` 等节点检查具体配置。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterConfiguration/Public/IDisplayClusterConfiguration.h"
```

### 基本用法

以下示例展示了如何通过接口加载 nDisplay 配置文件并访问其基础数据。

```cpp
// 来源: 基于 IDisplayClusterConfiguration 接口和 UDisplayClusterConfigurationData 类型
void LoadAndQueryConfig()
{
    // 1. 获取配置模块接口
    IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
    
    // 2. 加载配置文件
    FString ConfigFilePath = TEXT("/Game/MyProject/MyClusterSetup");
    UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(ConfigFilePath);
    
    if (ConfigData)
    {
        // 3. 访问全局信息
        UE_LOG(LogTemp, Log, TEXT("Config Description: %s"), *ConfigData->Info.Description);
        
        // 4. 访问集群节点
        TArray<FString> NodeIds;
        ConfigData->Cluster->GetNodeIds(NodeIds);
        
        for (const FString& NodeId : NodeIds)
        {
            UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(NodeId);
            if (Node)
            {
                UE_LOG(LogTemp, Log, TEXT("Node '%s' Host: %s, Viewports:"), *NodeId, *Node->Host);
                
                // 5. 访问节点下的视口
                TArray<FString> ViewportIds;
                Node->GetViewportIds(ViewportIds);
                // ... 进一步查询视口细节
            }
        }
        
        // 6. 访问场景设置（用于 ICVFX）
        const FDisplayClusterConfigurationICVFX_StageSettings& StageSettings = ConfigData->StageSettings;
        UE_LOG(LogTemp, Log, TEXT("Default Frame Resolution: %d x %d"), StageSettings.DefaultFrameSize.Width, StageSettings.DefaultFrameSize.Height);
    }
}
```

### 进阶用法

保存和修改配置是一个更高级的操作，通常在编辑器工具或自动化流程中使用。

```cpp
// 来源: 基于 IDisplayClusterConfiguration 接口
void ModifyAndSaveConfig()
{
    IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
    UDisplayClusterConfigurationData* ConfigData = ConfigModule.LoadConfig(TEXT("/Game/Config/Test"));
    
    if (ConfigData)
    {
        // 修改一些配置
        ConfigData->bFollowLocalPlayerCamera = true;
        ConfigData->Diagnostics.bSimulateLag = false;
        
        // 查找并修改特定节点的窗口设置
        UDisplayClusterConfigurationClusterNode* Node = ConfigData->Cluster->GetNode(TEXT("RenderNode_1"));
        if (Node)
        {
            Node->bIsFullscreen = true;
        }
        
        // 保存修改后的配置
        bool bSaved = ConfigModule.SaveConfig(ConfigData, TEXT("/Game/Config/Test_Modified"));
        if (bSaved)
        {
            UE_LOG(LogTemp, Log, TEXT("Config saved successfully."));
        }
    }
}
```

## Demo 示例

一个展示如何读取配置并遍历其结构的最小 C++ 示例。

**文件: `MyNDisplayConfigReader.h`**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterConfigurationTypes.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayConfigReader.generated.h"

UCLASS()
class AMyNDisplayConfigReader : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString ConfigAssetPath = TEXT("/Game/MyNDisplayConfig");

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "nDisplay")
    void ReadConfig();

protected:
    UPROPERTY()
    TObjectPtr<UDisplayClusterConfigurationData> LoadedConfig;
};
```

**文件: `MyNDisplayConfigReader.cpp`**
```cpp
#include "MyNDisplayConfigReader.h"
#include "DisplayClusterConfiguration/Public/IDisplayClusterConfiguration.h"

void AMyNDisplayConfigReader::ReadConfig()
{
    if (!IDisplayClusterConfiguration::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("nDisplay Configuration module is not loaded."));
        return;
    }

    IDisplayClusterConfiguration& ConfigModule = IDisplayClusterConfiguration::Get();
    LoadedConfig = ConfigModule.LoadConfig(ConfigAssetPath, this);

    if (!LoadedConfig)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load nDisplay config from: %s"), *ConfigAssetPath);
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("--- nDisplay Config Summary ---"));
    UE_LOG(LogTemp, Log, TEXT("Version: %s"), *LoadedConfig->Info.Version);
    UE_LOG(LogTemp, Log, TEXT("Description: %s"), *LoadedConfig->Info.Description);
    UE_LOG(LogTemp, Log, TEXT("Primary Node: %s"), *LoadedConfig->Cluster->PrimaryNode.Id);

    TArray<FString> NodeIds;
    LoadedConfig->Cluster->GetNodeIds(NodeIds);
    UE_LOG(LogTemp, Log, TEXT("Total Cluster Nodes: %d"), NodeIds.Num());

    for (const FString& NodeId : NodeIds)
    {
        UDisplayClusterConfigurationClusterNode* Node = LoadedConfig->Cluster->GetNode(NodeId);
        if (Node)
        {
            UE_LOG(LogTemp, Log, TEXT("  Node: %s | Host: %s | Viewports: %d"),
                *NodeId, *Node->Host, Node->Viewports.Num());
        }
    }

    UE_LOG(LogTemp, Log, TEXT("ICVFX Stage Enabled Inner Frustums: %s"),
        LoadedConfig->StageSettings.bEnableInnerFrustums ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("--- End Summary ---"));
}
```

## 模块依赖

对于核心的运行时功能，你的模块通常需要依赖 `DisplayClusterConfiguration` 来操作配置数据。如果涉及更高级的渲染或媒体功能，则需要依赖其他特定模块。`DisplayCluster` 是主运行时模块，包含了集群同步和渲染的核心逻辑。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 主运行时模块，包含集群管理、同步和渲染逻辑 |
| `DisplayClusterConfiguration` | nDisplay 配置数据的加载、保存、版本管理和类型定义 |
| `DisplayClusterProjection` | 投影策略（如平面、圆柱、网格）的实现 |
| `DisplayClusterMedia` | 处理外部媒体（视频）输入和输出 |
| `DisplayClusterWarp` | 几何变形（Warp）和混合（Blend）功能的实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染图添加 EXR 多图层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线合并透明通道处理模式，简化配置 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复渲染图中拓扑感知相机命名及着色器不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码时未考虑非默认显示伽马值的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

-   **活跃维护**：nDisplay 是 Epic Games 虚拟制作技术栈的核心组件之一。从 git 记录来看，它持续获得功能更新（如 EXR 多图层、电影管线优化）和重要的 bug 修复，维护非常活跃。
-   **技术复杂度高**：这是一个大型、复杂的插件，包含近30个子模块，覆盖配置、渲染、同步、媒体、投影等所有方面。
-   **推荐使用**：对于有明确分布式渲染或多屏显示需求的项目（尤其是电影虚拟制作领域），nDisplay 是官方推荐且功能完备的解决方案。虽然学习曲线陡峭，但它是该领域的行业标准工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/Overview/)