# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 远不止于基础的“多 PC 集群同步渲染”。它是 Epic Games 为应对高端虚拟制片（Virtual Production）、沉浸式展览、大型 LED 墙渲染及复杂的多投影仪系统（如 CAVE）而打造的**企业级渲染集群管理与控制框架**。其核心解决以下问题：
1.  **精准的几何与色彩管理**：通过 MPCDI、Warp/Blend 等技术，实现多台投影仪或 LED 面板间像素级对齐、色彩统一和边缘融合。
2.  **同步与锁定**：确保所有集群节点在极低延迟下渲染同一帧，避免撕裂和卡顿，支持 NVIDIA Quadro Sync 和 DWM（桌面窗口管理器）等硬件/软件同步方案。
3.  **虚拟制片流水线集成**：与 nCamera（虚拟摄像机）、LED 墙渲染、Remote Control 等深度集成，提供从现场拍摄到后期合成的全流程工具。
4.  **现场监控与运维**：提供实时监控节点状态、同步质量、性能指标以及自动故障检测（Hitch Detection）的工具，保障现场拍摄的稳定性。

## 使用场景

- 你正在为电影或广告拍摄搭建 **LED 墙虚拟制片现场**，需要多台渲染 PC 驱动巨幅 LED 面板，并保证所有屏幕画面与摄像机移动完美同步。
- 你需要为博物馆或展厅构建一个 **多投影仪的 CAVE（洞穴自动虚拟环境）或圆顶投影系统**，并进行复杂的几何校正和色彩校准。
- 你的项目需要 **多用户（如导演、灯光师、视觉特效总监）在各自的工作站上实时协作**，调整虚拟场景、灯光和摄像机，并将这些更改同步到整个渲染集群。
- 你需要在大型活动中进行 **实时渲染和现场视觉特效（ICVFX）**，并需要高可靠性的远程控制和监控能力。

## 蓝图用法

**注意**：用户提供的文件分析以 `Private` 头文件为主，未包含公开的 `BlueprintCallable` API。根据插件复杂性，其公共蓝图 API 主要集中在配置、场景预览、远程控制接口等模块。以下为根据功能推断的典型节点：

### 核心节点（推断）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node` | 获取当前集群节点的信息。 | `UDisplayCluster` |
| `Execute Cluster Event` | 在集群的所有节点或特定节点上执行蓝图事件。 | `UDisplayClusterClusterEvent` |
| `Get nDisplay Configuration` | 加载并获取 nDisplay 的配置资产。 | `UDisplayClusterConfiguration` |
| `Control Stage Actor` | 通过 Remote Control 接口控制舞台上的灯光卡、摄像机等演员。 | `UDisplayClusterRemoteControlInterceptor` |

### 使用示例（蓝图描述）

由于信息有限，无法提供精确的蓝图节点连接图。典型的使用流程是：
1.  在编辑器中创建一个 **DisplayCluster Configuration Asset**。
2.  打开该资产，在专用的 nDisplay 配置编辑器中设置集群节点、视口、投影类型（投影仪/LED 墙）、几何校正数据（.MPCDI/.icvfx 文件）等。
3.  在关卡蓝图中，通过 `Get nDisplay Configuration` 节点加载配置。
4.  使用 `Execute Cluster Event` 节点，在特定事件（如开始拍摄）时向所有集群节点发送同步指令。

## C++ 用法

由于用户提供的代码片段为私有类（`FNvidiaSyncWatchdog`、`UDisplayClusterStageMonitoringSettings`），无法直接用于外部开发。但其 **`DisplayClusterConfiguration`** 模块是用户进行底层开发时最常交互的模块之一，用于程序化创建或修改配置。

### 头文件引入

```cpp
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationTypes.h"
```

### 基本用法

**示例：程序化创建一个简单的 nDisplay 配置**
（此示例基于 `UDisplayClusterConfiguration` 模块的典型用法模式推断）

```cpp
// 1. 创建配置对象
UDisplayClusterConfiguration* Config = NewObject<UDisplayClusterConfiguration>();

// 2. 配置集群节点 (Cluster)
FDisplayClusterConfigurationCluster ClusterConfig;
ClusterConfig.Address = TEXT("192.168.1.10");
ClusterConfig.Port = 41001;
ClusterConfig.Role = EDisplayClusterConfigurationClusterRole::Primary;
Config->Cluster.Nodes.Add(TEXT("PrimaryNode"), ClusterConfig);

// 3. 配置视口 (Viewport)
FDisplayClusterConfigurationViewport ViewportConfig;
ViewportConfig.ViewportRect = FIntRect(0, 0, 1920, 1080);
// 设置几何校正数据 (例如加载一个 .MPCDI 文件)
ViewportConfig.WarpRef.GeometryType = EDisplayClusterWarpGeometryType::MPCDI;
ViewportConfig.WarpRef.MPCDIFile.FilePath = TEXT("/Game/MPCDI/MySetup.mpcdi");
Config->Cluster.PrimaryNode.Viewports.Add(TEXT("MyViewport"), ViewportConfig);

// 4. 保存资产 (需要在编辑器环境中)
// FAssetRegistryModule::AssetCreated(Config);
// Config->MarkPackageDirty();
```

### 进阶用法

进阶开发通常涉及编写自定义的 **`DisplayClusterStageMonitor`** 提供程序，以集成特定硬件设备的状态监控，或者编写 **`ProjectionPolicy`** 插件以支持新型显示硬件。这些开发需要深入理解 nDisplay 的模块化架构和回调接口。

## Demo 示例

**功能**：加载一个已有的 nDisplay 配置资产并获取其集群节点信息。

```cpp
// NDdisplayMinimalDemo.h
#pragma once
#include "CoreMinimal.h"

class UNDdisplayMinimalDemo
{
public:
    void RunDemo();
};
```

```cpp
// NDdisplayMinimalDemo.cpp
#include "NDdisplayMinimalDemo.h"
#include "IDisplayClusterConfiguration.h"
#include "DisplayClusterConfigurationTypes.h"
#include "Misc/PackageName.h"

void UNDdisplayMinimalDemo::RunDemo()
{
    // 假设我们有一个已保存的 nDisplay 配置资产路径
    const FString ConfigAssetPath = TEXT("/Game/Config/MyClusterConfig.MyClusterConfig");
    
    // 加载配置资产
    UObject* LoadedObject = LoadObject<UObject>(nullptr, *ConfigAssetPath);
    if (UDisplayClusterConfiguration* Config = Cast<UDisplayClusterConfiguration>(LoadedObject))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded nDisplay configuration: %s"), *Config->GetName());

        // 遍历集群节点
        for (const auto& NodePair : Config->Cluster.Nodes)
        {
            const FString& NodeName = NodePair.Key;
            const FDisplayClusterConfigurationCluster& NodeInfo = NodePair.Value;
            UE_LOG(LogTemp, Log, TEXT("Cluster Node: %s, Address: %s, Role: %s"),
                *NodeName,
                *NodeInfo.Address,
                *UEnum::GetValueAsString(NodeInfo.Role));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load nDisplay configuration from: %s"), *ConfigAssetPath);
    }
}
```

## 模块依赖

从 `Build.cs` 分析，nDisplay 插件具有复杂且广泛的依赖，以下列出其**独特且不常见**的依赖模块。

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 用于 D3D12 渲染硬件接口，支持高级同步和共享内存功能。 |
| `ScalableMPCDI` | 第三方 MPCDI（多投影仪校准数据交换）格式支持库。 |
| `UnrealEd`, `EditorWidgets`, `LevelEditor`, `PropertyEditor` 等 | 大量编辑器模块依赖，用于构建专用的 nDisplay 配置器、场景预览、细节面板等编辑器工具。 |

**重要提示**：由于大量依赖编辑器模块（`UnrealEd` 等），此插件主要用于开发阶段和运行在专用渲染 PC 上的打包程序。对于需要深度编辑器集成的虚拟制片现场工作站，这是必需的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 集成添加了 EXR 多层渲染支持，增强后期合成能力。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 简化了 Movie Pipeline 中的 WarpBlend 模式，将 Alpha 模式合并。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中摄像机命名问题和 MPCDI/ICVFX 着色器的不透明度 Bug。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在回退编码输出帧时，未尊重非默认 DisplayGamma 设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

**活跃维护**。nDisplay 是 Epic Games 虚拟制片战略的核心组件之一。
- **更新频率**：近期更新非常密集（2026 年 5 月有多次提交），且更新内容围绕**新功能**（EXR 多层）、**工作流简化**（MoviePipeline 模式合并）和 **Bug 修复**（着色器、同步、渲染问题），表明该插件处于积极开发和优化中。
- **成熟度**：插件已历经 8 年发展，功能完整且深度集成引擎，是成熟的企业级解决方案。
- **推荐使用**：对于任何涉及多机同步渲染、虚拟制片、沉浸式投影的项目，nDisplay 是**官方唯一且推荐的解决方案**。需注意其**较高的配置复杂性和硬件要求**，以及对编辑器模块的强依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)