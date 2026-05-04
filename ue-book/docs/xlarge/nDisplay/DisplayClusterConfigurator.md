# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、着色器、媒体资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机集群同步渲染**的核心插件，解决的是单台 PC 无法满足超大分辨率或多屏幕输出的场景。它允许多台 PC（集群节点）各自渲染画面的一部分，通过精确的帧同步和投影校正，将多个输出拼接成一个完整的、无缝的视觉画面。

核心能力包括：

- **集群同步渲染**：多台 PC 通过网络同步渲染同一场景，支持主从架构（Primary/Secondary）
- **多视口投影**：每个集群节点可拥有多个视口（Viewport），支持平面、圆柱、球面等多种投影方式
- **几何校正（Warp）**：支持 MPCDI 格式的几何校正数据，用于投影仪边缘融合和曲面校正
- **色彩校正（Color Grading）**：对每个视口/节点进行独立的色彩管理
- **媒体输入/输出**：通过共享内存（SharedMemoryMedia）实现低延迟的视频帧传输
- **虚拟制片支持**：与 Movie Pipeline 集成，支持 LED 墙虚拟制片工作流
- **多用户协作**：支持 Multi-User 编辑，多人同时操作集群配置
- **远程控制**：通过 Remote Control API 远程调整集群参数
- **舞台监控**：实时监控集群运行状态

nDisplay 不仅仅是"把画面分到多台电脑上"，它是 Epic 为虚拟制片（Virtual Production）、LED 墙（LED Volume）、CAVE 系统、穹顶投影等专业场景打造的完整解决方案。

## 使用场景

- 你在搭建 **LED 墙虚拟制片片场**，需要多台渲染 PC 驱动 LED 屏幕的不同区域 → 用 nDisplay
- 你在做 **CAVE 洞穴式 VR 系统**，需要多面投影墙同步渲染 → 用 nDisplay
- 你需要 **穹顶投影** 或 **环幕投影**，单台 PC 性能不够 → 用 nDisplay
- 你在搭建 **多显示器赛车/飞行模拟器**，需要无缝拼接多个输出 → 用 nDisplay
- 你需要对投影仪做 **边缘融合和几何校正** → 用 nDisplay 的 Warp/MPCDI 功能
- 你要用 **Movie Pipeline 录制** LED 墙上的虚拟场景 → 用 nDisplay 的 MoviePipeline 集成

## 蓝图用法

nDisplay 的运行时核心通过 `ADisplayClusterRootActor` 暴露蓝图接口。配置器模块（DisplayClusterConfigurator）主要面向编辑器，不直接暴露蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClusterNodeId` | 获取当前集群节点的名称 | `UDisplayClusterBlueprintAPI` |
| `GetPrimaryNodeId` | 获取主节点名称 | `UDisplayClusterBlueprintAPI` |
| `IsPrimary` | 判断当前节点是否为主节点 | `UDisplayClusterBlueprintAPI` |
| `GetViewportId` | 获取当前视口 ID | `UDisplayClusterBlueprintAPI` |
| `SetViewportCameraRotation` | 设置指定视口的相机旋转 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1. **创建 nDisplay 配置资产**：在 Content Browser 右键 → Miscellaneous → nDisplay Config，这会创建一个 `UDisplayClusterBlueprint` 资产
2. **在场景中放置 Root Actor**：将 `ADisplayClusterRootActor` 拖入场景，关联配置资产
3. **配置集群节点**：在 nDisplay Configurator 编辑器中定义 Host（主机）、ClusterNode（集群节点）、Viewport（视口）
4. **运行时判断节点身份**：使用 `IsPrimary` 节点判断当前 PC 是否为主节点，据此执行不同的逻辑

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfiguration.h"
#include "DisplayClusterConfiguratorClusterUtils.h"
```

### 基本用法：集群节点管理

从 `DisplayClusterConfiguratorClusterUtils` 提供的工具函数，用于程序化管理集群配置：

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterConfigurator/Public/ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h

#include "ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h"
#include "DisplayClusterConfigurationCluster.h"
#include "DisplayClusterConfigurationClusterNode.h"
#include "DisplayClusterConfigurationViewport.h"

// 添加集群节点到集群
UDisplayClusterConfigurationClusterNode* NewNode = UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
    ClusterNode,           // 要添加的节点
    Cluster,               // 目标集群
    TEXT("RenderNode_01")  // 新名称（可选）
);

// 设置为主节点
bool bSuccess = UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(NewNode);

// 检查是否为主节点
bool bIsPrimary = UE::DisplayClusterConfiguratorClusterUtils::IsClusterNodePrimary(NewNode);

// 重命名集群节点
UE::DisplayClusterConfiguratorClusterUtils::RenameClusterNode(NewNode, TEXT("RenderNode_New"));

// 添加视口到集群节点
UDisplayClusterConfigurationViewport* Viewport = UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
    MyViewport,            // 要添加的视口
    NewNode,               // 目标集群节点
    TEXT("Viewport_01")    // 新名称（可选）
);

// 移除视口
UE::DisplayClusterConfiguratorClusterUtils::RemoveViewportFromClusterNode(Viewport);

// 移除集群节点
UE::DisplayClusterConfiguratorClusterUtils::RemoveClusterNodeFromCluster(NewNode);
```

### 进阶用法：编辑器配置器扩展

nDisplay Configurator 模块提供了完整的 MVC 架构用于编辑器扩展：

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterConfigurator/Public/IDisplayClusterConfigurator.h

#include "IDisplayClusterConfigurator.h"

// 获取配置器模块实例
if (IDisplayClusterConfigurator::IsAvailable())
{
    IDisplayClusterConfigurator& Configurator = IDisplayClusterConfigurator::Get();
    
    // 获取命令集
    const FDisplayClusterConfiguratorCommands& Commands = Configurator.GetCommands();
    
    // 获取菜单扩展管理器（用于添加自定义菜单项）
    TSharedPtr<FExtensibilityManager> MenuManager = Configurator.GetMenuExtensibilityManager();
    
    // 获取工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> ToolBarManager = Configurator.GetToolBarExtensibilityManager();
}
```

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterConfigurator/Public/IDisplayClusterConfiguratorBlueprintEditor.h

// 监听配置重载事件
IDisplayClusterConfiguratorBlueprintEditor& Editor = /* 获取编辑器实例 */;
Editor.FOnConfigReloaded.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("nDisplay config reloaded"));
});

// 监听对象选择事件
Editor.FOnObjectSelected.AddLambda([]()
{
    TArray<UObject*> SelectedObjects = Editor.GetSelectedObjects();
    // 处理选中对象...
});
```

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterConfigurator/Public/Views/OutputMapping/IDisplayClusterConfiguratorViewOutputMapping.h

// 配置输出映射视图的显示设置
FOutputMappingSettings& Settings = OutputMappingView->GetOutputMappingSettings();
Settings.bShowRuler = true;                    // 显示标尺
Settings.bShowWindowInfo = true;               // 显示窗口信息
Settings.bShowOutsideViewports = false;        // 隐藏外部视口
Settings.bAllowClusterItemOverlap = false;     // 不允许集群项重叠
Settings.bKeepClusterNodesInHosts = true;      // 保持集群节点在主机内
Settings.ViewScale = 1.5f;                     // 设置视图缩放

// 配置主机排列方式
FHostNodeArrangementSettings& ArrangementSettings = OutputMappingView->GetHostArrangementSettings();
ArrangementSettings.ArrangementType = EHostArrangementType::Grid;  // 网格排列
ArrangementSettings.GridSize = 4;                                   // 4x4 网格

// 配置节点对齐
FNodeAlignmentSettings& AlignmentSettings = OutputMappingView->GetNodeAlignmentSettings();
AlignmentSettings.SnapProximity = 25;           // 吸附距离
AlignmentSettings.bSnapAdjacentEdges = true;    // 吸附相邻边
AlignmentSettings.bSnapSameEdges = true;        // 吸附相同边
```

## Demo 示例

以下展示如何程序化创建一个简单的 nDisplay 集群配置：

```cpp
// MyNDisplaySetup.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyNDisplaySetup.generated.h"

UCLASS()
class UMyNDisplaySetup : public UEditorSubsystem
{
    GENERATED_BODY()
    
public:
    /** 创建一个双节点集群配置 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void CreateDualNodeCluster();
};
```

```cpp
// MyNDisplaySetup.cpp
#include "MyNDisplaySetup.h"
#include "ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h"
#include "DisplayClusterConfigurationCluster.h"
#include "DisplayClusterConfigurationClusterNode.h"
#include "DisplayClusterConfigurationViewport.h"
#include "DisplayClusterConfigurationData.h"

void UMyNDisplaySetup::CreateDualNodeCluster()
{
    // 创建集群配置数据
    UDisplayClusterConfigurationData* ConfigData = NewObject<UDisplayClusterConfigurationData>();
    UDisplayClusterConfigurationCluster* Cluster = ConfigData->Cluster;
    
    // 创建主节点（左侧屏幕）
    UDisplayClusterConfigurationClusterNode* PrimaryNode = NewObject<UDisplayClusterConfigurationClusterNode>(Cluster);
    UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
        PrimaryNode, Cluster, TEXT("PrimaryNode"));
    UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(PrimaryNode);
    
    // 为主节点添加视口
    UDisplayClusterConfigurationViewport* PrimaryViewport = NewObject<UDisplayClusterConfigurationViewport>(PrimaryNode);
    UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
        PrimaryViewport, PrimaryNode, TEXT("LeftScreen"));
    
    // 创建从节点（右侧屏幕）
    UDisplayClusterConfigurationClusterNode* SecondaryNode = NewObject<UDisplayClusterConfigurationClusterNode>(Cluster);
    UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
        SecondaryNode, Cluster, TEXT("SecondaryNode"));
    
    // 为从节点添加视口
    UDisplayClusterConfigurationViewport* SecondaryViewport = NewObject<UDisplayClusterConfigurationViewport>(SecondaryNode);
    UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
        SecondaryViewport, SecondaryNode, TEXT("RightScreen"));
    
    UE_LOG(LogTemp, Log, TEXT("Dual node cluster configuration created successfully"));
}
```

**Build.cs 依赖**：

```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "DisplayClusterConfiguration",
    "DisplayClusterConfigurator"
});
```

## 模块依赖

nDisplay 是一个庞大的插件，各子模块之间的依赖关系复杂。以下是使用者最可能需要关注的模块依赖：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 集群配置数据模型（运行时必选） |
| `DisplayCluster` | 核心运行时逻辑，集群同步、渲染管线 |
| `DisplayClusterProjection` | 投影计算（平面/圆柱/球面投影） |
| `DisplayClusterWarp` | 几何校正（Warp/Mesh） |
| `DisplayClusterColorGrading` | 色彩校正 |
| `DisplayClusterMedia` | 媒体输入/输出（依赖 D3D12RHI） |
| `SharedMemoryMedia` | 共享内存帧传输（依赖 D3D12RHI） |
| `DisplayClusterConfigurator` | 编辑器配置工具（蓝图编辑器扩展） |
| `DisplayClusterMoviePipeline` | Movie Pipeline 集成 |
| `DisplayClusterMultiUser` | 多用户编辑支持 |
| `DisplayClusterReplication` | 网络复制 |
| `DisplayClusterRemoteControlInterceptor` | 远程控制拦截 |
| `DisplayClusterStageMonitoring` | 舞台运行状态监控 |
| `ScalableMPCDI` | 第三方 MPCDI 库（几何校正数据格式） |

**注意**：多个模块依赖 `UnrealEd`、`D3D12RHI` 等，这意味着完整的 nDisplay 功能需要编辑器环境和 DirectX 12 支持。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `b677450f7a65` | [nDisplay] Fixed crash while importing an nDisplay config in the nD configurator | 修复了在 nDisplay 配置器中导入配置时的崩溃问题，属于关键 bug 修复 |
| 近期 | `08567a026e09` | [UnrealEd] Added cvar for percentage-based scaling snap | 通用编辑器改动，非 nDisplay 专属更新 |
| 近期 | `865186bfe3c7` | Refactor camera speed to be based on a single float value | 相机速度重构，可能影响 nDisplay 视口预览中的相机操作 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

nDisplay 是 Epic Games 虚拟制片（Virtual Production）战略的核心组件之一，持续受到积极维护：

- **创建于 2018 年**，至今约 7 年，是 UE 中较为成熟的大型插件
- **持续更新**：作为虚拟制片工作流的关键部分，每个 UE 版本都会收到功能更新和 bug 修复
- **模块化架构**：27 个子模块覆盖了从配置、渲染、投影、校正到媒体、协作的完整链路
- **生产环境验证**：被大量虚拟制片片场、LED 墙项目在生产中使用
- **EnabledByDefault=false**：需要手动启用，因为这是一个专业功能，不是所有项目都需要

**注意事项**：
- 插件规模庞大（1600+ 源文件），学习曲线较陡
- 部分功能依赖 D3D12RHI，Linux 平台支持可能有限制
- 需要多台 PC 和网络环境才能发挥完整价值
- 配置复杂，建议先从官方的 nDisplay 示例项目开始学习

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/ndisplay-in-unreal-engine/)