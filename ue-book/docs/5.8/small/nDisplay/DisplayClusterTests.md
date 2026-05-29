# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏/集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现**同步集群渲染**的高级框架。它解决的核心问题是：如何让多台计算机（PC）协同工作，将 Unreal Engine 的渲染输出**精确同步**并分发到多个显示器、投影仪或 LED 墙上，从而构建一个统一的、高分辨率的、沉浸式的视觉环境。

其主要应用场景包括：
- **虚拟制片 (Virtual Production)**：驱动 LED 墙（如 The Volume），将 CG 环境实时投射到物理舞台上，供演员和摄影机实时交互。
- **多通道/CAVE 环境**：构建由多个投影平面（如三面墙、地板、天花板）组成的沉浸式房间。
- **大型主题公园景点**：为骑乘设施、球幕影院等提供同步的多视口渲染。
- **专业 AV 与模拟**：用于飞行模拟器、驾驶模拟器、大型指挥控制中心等需要高保真和同步视觉的场合。

它通过一个中心化的**集群配置**来定义整个渲染拓扑，包括哪些节点（PC）负责渲染哪些视口，以及视口之间如何拼接和变形。每个节点运行一个 UE 实例，通过高速网络进行通信和帧同步，确保所有画面在时间上完全一致。

**注意**：此插件默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。

## 使用场景

- 你在为电影拍摄构建一个实时 LED 墙虚拟环境 → 使用 nDisplay 来配置墙的拓扑、投影和色彩管理。
- 你需要为一个科学可视化项目构建一个四面 CAVE 洞穴系统 → 使用 nDisplay 定义四个投影通道及其几何关系。
- 你正在开发一个大型游乐场的 360 度球幕影院体验 → 使用 nDisplay 进行多机同步渲染和边缘融合。
- 你的需求是让多台 PC 同步渲染同一个场景，以支持超高清或超高性能渲染 → 使用 nDisplay 作为底层同步和分发框架。

## 蓝图用法

由于 nDisplay 主要是一个配置和管理系统，其核心蓝图交互围绕**配置资产**和**运行时控制**。基于测试工具和典型用法，可以推断以下核心功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Display Cluster Asset` | 创建一个新的 nDisplay 配置蓝图资产 | `UDisplayClusterBlueprint` (通过工厂) |
| `Add Cluster Node` | 向集群配置中添加一个代表物理 PC 的节点 | `UDisplayClusterConfigurationCluster` |
| `Add Viewport` | 向一个集群节点添加一个渲染视口（对应一个输出显示器） | `UDisplayClusterConfigurationClusterNode` |
| 各种属性设置 | 配置视口的尺寸、投影矩阵、变形网格等 | `UDisplayClusterConfigurationViewport` 及其子对象 |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中右键，选择创建 `Display Cluster` 蓝图资产。
2.  **编辑集群拓扑**：打开该蓝图，进入专用的 nDisplay 配置编辑器。在“集群”面板中，可以添加/删除代表每台渲染 PC 的“集群节点”。
3.  **配置视口**：选中一个集群节点，为其添加“视口”。在视口属性中设置输出显示器、分辨率、投影方式（如平面、圆柱、网格）。
4.  **分配相机**：将场景中的相机（通常是一个 `DisplayClusterRootActor` 或普通 `CameraActor`）分配给特定的视口。
5.  **启动集群**：在编辑器或通过命令行，使用 `-dc_cluster` 等参数启动多个 UE 实例，它们会自动读取配置并开始同步渲染。

## C++ 用法

虽然 nDisplay 的主要使用场景通过编辑器配置和蓝图完成，但其底层 API 可用于程序化控制和扩展。测试模块 `DisplayClusterTests` 展示了如何程序化创建和修改配置资产。

### 头文件引入

```cpp
#include "DisplayClusterConfiguration/Public/DisplayClusterConfigurationTypes.h"
#include "DisplayCluster/Public/DisplayClusterBlueprint.h"
// 注意：对于测试工具，需要引入测试模块的头文件
#include "DisplayClusterTests/Private/DisplayClusterTestUtils.h"
```

### 基本用法（程序化创建配置）

以下示例演示了如何使用测试工具函数创建一个基本的 nDisplay 配置资产。
*来源：基于 `DisplayClusterTestUtils.h` 中的函数说明推导。*

```cpp
// 假设在某个 Editor 模块或自定义工具中
#include "DisplayClusterTestUtils.h"
// 需要链接 DisplayClusterTests 模块 (仅用于开发/测试)

// 1. 创建一个新的 nDisplay 资产
UDisplayClusterBlueprint* MyClusterAsset = DisplayClusterTestUtils::CreateDisplayClusterAsset();
if (!MyClusterAsset)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create nDisplay asset"));
    return;
}

// 2. 获取资产的集群根配置
UDisplayClusterConfigurationCluster* ClusterRoot = MyClusterAsset->GetCluster();
check(ClusterRoot);

// 3. 添加一个集群节点 (代表一台 PC)
const FString NodeName = TEXT("RenderNode01");
UDisplayClusterConfigurationClusterNode* ClusterNode = DisplayClusterTestUtils::AddClusterNodeToCluster(
    MyClusterAsset, ClusterRoot, NodeName
);

// 4. 为该节点添加一个视口
const FString ViewportName = TEXT("MainViewport");
UDisplayClusterConfigurationViewport* Viewport = DisplayClusterTestUtils::AddViewportToClusterNode(
    MyClusterAsset, ClusterNode, ViewportName
);

// 5. (可选) 通过属性接口修改视口参数
TArray<FName> FieldNames = {GET_MEMBER_NAME_CHECKED(UDisplayClusterConfigurationViewport, ViewportRect)};
FIntRect NewRect(0, 0, 1920, 1080);
DisplayClusterTestUtils::SetBlueprintPropertyValue<FIntRect>(Viewport, MyClusterAsset, FieldNames, NewRect);

// 6. 保存资产
FAssetRegistryModule::AssetCreated(MyClusterAsset);
MyClusterAsset->MarkPackageDirty();
```

### 进阶用法

更高级的用法涉及直接操作 `IDisplayClusterClusterManager`、`IDisplayClusterRenderManager` 等运行时接口，通常用于开发自定义的渲染节点、同步逻辑或插件。这些接口需要在运行时获取，通常通过 `IDisplayCluster::Get()` 来访问。

## Demo 示例

下面是一个最小化的 C++ 示例，展示如何在编辑器模块中程序化创建并保存一个简单的 nDisplay 资产。此代码需要放在 Editor 模块中，并且项目已启用 nDisplay 插件。

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "Toolkits/AssetEditorManager.h" // 用于保存资产

class FMyEditorTool
{
public:
    static void CreateSimpleNDisplayConfig();
};
```

```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "DisplayClusterBlueprint.h"
#include "DisplayClusterConfiguration/Public/DisplayClusterConfigurationTypes.h"
#include "DisplayClusterTests/Public/DisplayClusterTestUtils.h" // 引入测试工具
#include "AssetRegistryModule.h"

void FMyEditorTool::CreateSimpleNDisplayConfig()
{
    // 创建资产
    UDisplayClusterBlueprint* Blueprint = DisplayClusterTestUtils::CreateDisplayClusterAsset();
    if (!Blueprint)
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建 nDisplay 资产"));
        return;
    }

    // 获取集群配置
    UDisplayClusterConfigurationCluster* Cluster = Blueprint->GetCluster();
    if (!Cluster)
    {
        UE_LOG(LogTemp, Error, TEXT("资产中没有集群配置"));
        return;
    }

    // 添加两个节点，模拟双机同步
    UDisplayClusterConfigurationClusterNode* Node1 = DisplayClusterTestUtils::AddClusterNodeToCluster(Blueprint, Cluster, TEXT("PC_Left"));
    UDisplayClusterConfigurationClusterNode* Node2 = DisplayClusterTestUtils::AddClusterNodeToCluster(Blueprint, Cluster, TEXT("PC_Right"));

    // 为每个节点添加一个视口
    if (Node1 && Node2)
    {
        DisplayClusterTestUtils::AddViewportToClusterNode(Blueprint, Node1, TEXT("Display_Left"));
        DisplayClusterTestUtils::AddViewportToClusterNode(Blueprint, Node2, TEXT("Display_Right"));
    }

    // 触发蓝图编辑器更新并保存
    FBlueprintEditorUtils::PostEditChangeBlueprintActors(Blueprint);
    FAssetRegistryModule::AssetCreated(Blueprint);
    Blueprint->MarkPackageDirty();

    UE_LOG(LogTemp, Log, TEXT("已创建包含两个节点的 nDisplay 配置资产"));
}
```

## 模块依赖

要使用 nDisplay 的完整功能，你的项目模块可能需要依赖以下一个或多个模块，具体取决于你的使用场景。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 核心运行时框架，提供集群管理、渲染和同步API |
| `DisplayClusterConfiguration` | 处理 `.ndisplay` 配置资产的数据结构和逻辑 |
| `DisplayClusterProjection` | 负责各种投影模式（平面、圆柱、网格等）和变形 |
| `DisplayClusterMedia` | 集成媒体框架，支持从外部源（如摄像机、视频文件）捕获帧 |
| `DisplayClusterWarp` | 处理复杂的几何校正和边缘融合 (Warp & Blend) |
| `DisplayClusterMoviePipeline` | 与影片渲染队列集成，用于离线渲染 nDisplay 场景 |
| `DisplayClusterMultiUser` | 支持多人协作编辑 nDisplay 配置 |
| `DisplayClusterReplication` | 处理集群内部的状态复制和同步 |
| `MovieSceneCapture` | (常见依赖) 用于影片渲染和捕获 |
| `MediaFrameworkUtilities` | (常见依赖) 用于媒体输入输出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的影片渲染管道添加了 EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在影片渲染管道中合并了 WarpBlend 和 WarpBlendAlpha 两种混合模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了媒体渲染图中的相机命名问题，并修复了 MPCDI/ICVFX 着色器的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在备用编码路径下未使用正确显示 Gamma 值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时会导致画面闪烁的 Bug。 |

### 维护评价

- **活跃维护**：根据 Git 日志，nDisplay 在 2026 年 5 月仍有密集的功能性更新和 Bug 修复，表明 Epic Games 将其作为虚拟制片和沉浸式体验的核心技术在**积极维护**。
- **复杂性与成熟度**：这是一个拥有 29 个子模块、超过 1300 个文件的大型插件，架构复杂。它自 2018 年随 UE 4.20 起存在，已经历多年迭代，属于成熟产品。
- **推荐使用**：对于需要同步集群渲染、虚拟制片或多通道投影的项目，**强烈推荐**使用 nDisplay。它是 Epic 官方提供的解决方案，与 UE 引擎深度集成，功能全面且得到持续支持。但请注意其学习曲线较陡，需要对渲染管线和网络同步有一定了解。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) (UE5 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)

**重要提示**：这是一个 **xlarge** 规模的插件。本文档仅提供总览和索引。要深入了解特定子模块（如投影、媒体、影片渲染等），请参阅各子模块的详细文档。