# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置数据、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机集群同步渲染**的核心插件，解决在多台 PC 上同步渲染并输出到多个物理显示器（或投影仪）的技术需求。它主要用于：

- **LED 虚拟拍摄**（ICVFX）：在 LED 墙上实时渲染摄像机视口内容，支持 Camera Frustum 追踪
- **CAVE/穹顶投影**：多台投影仪拼接输出到曲面屏幕，支持 MPCDI、EasyBlend、Mesh 等多种变形校正方案
- **多屏同步输出**：将一个 UE 场景渲染到多个物理显示器上，保持帧同步
- **投影策略系统**：支持 Simple、Camera、Mesh、Dome、VIOSO、EasyBlend、MPCDI、Manual、Reference 等多种投影映射方式
- **媒体 IO 集成**：支持 SharedMemoryMedia、Rivermax 等媒体传输协议，支持分块媒体（Tiled Media）配置
- **电影管线集成**：通过 MoviePipeline 模块支持离线渲染 nDisplay 场景为 EXR 序列

插件默认**不启用**（`EnabledByDefault: false`），需要在项目设置中手动开启，因为它是专业级虚拟制作工具，仅在特定硬件集群环境中使用。

## 使用场景

- 你在做**虚拟拍摄（Virtual Production）**，需要 LED 墙实时显示场景 → 用 nDisplay 配置 ICVFX Camera 和 LED Viewport
- 你需要搭建 **CAVE 沉浸式环境**，多台投影仪拼接投影 → 用 nDisplay 配置多 ClusterNode + Mesh/MPCDI 投影策略
- 你有多台 PC 组成渲染集群，需要**帧同步渲染**到多个显示器 → 用 nDisplay 配置 Cluster 拓扑和渲染同步策略
- 你需要将 nDisplay 场景**离线渲染为视频序列帧** → 用 DisplayClusterMoviePipeline 模块
- 你需要通过**媒体流**（SharedMemory 或网络）将渲染结果输出到外部设备 → 用 DisplayClusterMedia + SharedMemoryMedia

## 蓝图用法

nDisplay 的核心配置主要通过 **DisplayClusterBlueprint 资产**和编辑器 UI 完成，而非传统的蓝图节点调用。以下是关键的可操作节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UDisplayClusterBlueprint` | nDisplay 配置蓝图资产，包含 Cluster、Layout、Screen 等所有配置 | `UDisplayClusterBlueprint` |
| `UDisplayClusterConfiguratorEditorSubsystem.ImportAsset` | 从 .cfg/.ndisplay 文件导入配置到蓝图资产 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `UDisplayClusterConfiguratorEditorSubsystem.SaveConfig` | 将配置数据导出为 .cfg 文件 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `UDisplayClusterConfiguratorEditorSubsystem.ReloadConfig` | 从文件重新加载配置数据 | `UDisplayClusterConfiguratorEditorSubsystem` |

### 使用示例（编辑器工作流）

1. **创建 nDisplay 配置**：在 Content Browser 右键 → Miscellaneous → nDisplay Configuration，创建 `UDisplayClusterBlueprint` 资产
2. **双击打开编辑器**：打开 DisplayClusterConfigurator 蓝图编辑器，包含以下面板：
   - **Cluster 面板**：管理集群节点（Host IP、Viewport、ICVFX Camera）
   - **Output Mapping 面板**：可视化编辑多显示器布局映射
   - **SCS 编辑器**：管理组件层级（Screen、Camera、XForm 等）
3. **导入 MPCDI 文件**：通过工具栏 Import → MPCDI，自动创建 Screen 和 Viewport 配置
4. **导出配置**：通过 File → Export 将配置保存为 .cfg 文件，供集群中的各 PC 使用

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfiguratorBlueprintEditor.h"
#include "DisplayClusterConfiguratorModule.h"
#include "DisplayClusterConfigurationClusterUtils.h"
```

### 基本用法

从 `DisplayClusterConfiguratorClusterUtils.h` 提取的集群操作工具函数：

```cpp
// 来源：Public/ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h
#include "DisplayClusterConfigurationClusterUtils.h"

// 创建一个新的集群节点并添加到集群中
UDisplayClusterConfigurationClusterNode* NewNode = UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
    ClusterNode, Cluster, TEXT("MyClusterNode"));

// 将视口添加到集群节点
UDisplayClusterConfigurationViewport* NewViewport = UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
    Viewport, ClusterNode, TEXT("MyViewport"));

// 设置主节点
bool bSuccess = UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(ClusterNode);

// 重命名集群节点（自动去重）
bool bRenamed = UE::DisplayClusterConfiguratorClusterUtils::RenameClusterNode(ClusterNode, TEXT("NewNodeName"));

// 按主机排序集群节点
TMap<FString, TMap<FString, UDisplayClusterConfigurationClusterNode*>> SortedNodes;
UE::DisplayClusterConfiguratorClusterUtils::SortClusterNodesByHost(ClusterNodesMap, SortedNodes);
```

### 进阶用法

通过编辑器子系统进行配置的导入/导出操作：

```cpp
// 来源：Private/DisplayClusterConfiguratorEditorSubsystem.h
#include "DisplayClusterConfiguratorEditorSubsystem.h"

// 获取编辑器子系统
UDisplayClusterConfiguratorEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UDisplayClusterConfiguratorEditorSubsystem>();

// 从文件导入配置
UDisplayClusterBlueprint* Blueprint = Subsystem->ImportAsset(Parent, FName("MyConfig"), TEXT("/Path/to/config.cfg"));

// 重新加载配置
UDisplayClusterConfigurationData* ConfigData = Subsystem->ReloadConfig(Blueprint, TEXT("/Path/to/config.cfg"));

// 将配置导出为字符串
FString ConfigString;
Subsystem->ConfigAsString(ConfigData, ConfigString);

// 保存配置到文件
Subsystem->SaveToFile(ConfigData, TEXT("/Path/to/output.cfg"));
```

使用属性工具操作配置数据中的 Map 属性：

```cpp
// 来源：Private/DisplayClusterConfiguratorPropertyUtils.h
#include "DisplayClusterConfiguratorPropertyUtils.h"

// 获取属性视图
TSharedPtr<ISinglePropertyView> PropView = UE::DisplayClusterConfiguratorPropertyUtils::GetPropertyView(Owner, FName("MyPropertyName"));

// 向 Map 属性添加键值对
UE::DisplayClusterConfiguratorPropertyUtils::AddKeyValueToMap(MapOwner, MapPropertyHandle, TEXT("Key"), TEXT("Value"));

// 从 Map 属性移除键
UE::DisplayClusterConfiguratorPropertyUtils::RemoveKeyFromMap(MapOwner, MapPropertyHandle, TEXT("Key"));
```

## Demo 示例

### 通过 C++ 创建集群节点并添加视口

```cpp
// MyClusterSetup.h
#pragma once

#include "CoreMinimal.h"

class UDisplayClusterConfigurationCluster;
class UDisplayClusterConfigurationClusterNode;
class UDisplayClusterConfigurationViewport;

class FMyClusterSetup
{
public:
    /** 在集群中创建一个主机和两个视口的简单配置 */
    static void SetupBasicCluster(UDisplayClusterConfigurationCluster* Cluster);
};
```

```cpp
// MyClusterSetup.cpp
#include "MyClusterSetup.h"
#include "DisplayClusterConfigurationClusterUtils.h"
#include "DisplayClusterConfigurationData.h"

void FMyClusterSetup::SetupBasicCluster(UDisplayClusterConfigurationCluster* Cluster)
{
    if (!Cluster)
    {
        return;
    }

    // 创建第一个集群节点（主节点）
    UDisplayClusterConfigurationClusterNode* PrimaryNode = 
        UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
            nullptr, Cluster, TEXT("Node_Primary"));
    
    if (PrimaryNode)
    {
        // 设置为主节点
        UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(PrimaryNode);

        // 为主节点添加左视口
        UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
            nullptr, PrimaryNode, TEXT("Viewport_Left"));

        // 为主节点添加右视口
        UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
            nullptr, PrimaryNode, TEXT("Viewport_Right"));
    }

    // 创建第二个集群节点（从节点）
    UDisplayClusterConfigurationClusterNode* SecondaryNode = 
        UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
            nullptr, Cluster, TEXT("Node_Secondary"));

    if (SecondaryNode)
    {
        // 为从节点添加视口
        UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
            nullptr, SecondaryNode, TEXT("Viewport_Center"));
    }

    // 按主机排序，检查配置结果
    TMap<FString, TMap<FString, UDisplayClusterConfigurationClusterNode*>> SortedNodes;
    UE::DisplayClusterConfiguratorClusterUtils::SortClusterNodesByHost(
        Cluster->ClusterNodes, SortedNodes);
}
```

## 模块依赖

nDisplay 是一个大型插件，包含 29 个模块。以下是各模块的独特依赖（省略常见的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 多个编辑器模块（Configurator、Editor、Monitor、Projection 等）依赖 |
| `LevelEditor` | DisplayCluster 主模块依赖，用于关卡编辑器集成 |
| `D3D12RHI` | DisplayClusterMedia 和 SharedMemoryMedia 依赖，用于 DirectX 12 共享内存传输 |
| `ScalableMPCDI` | 第三方 MPCDI 库，用于 MPCDI 投影变形配置 |

使用者无需直接依赖所有模块。在你的 `.Build.cs` 中通常只需添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DisplayCluster",         // 核心运行时功能
    "DisplayClusterConfiguration"  // 配置数据结构
});

// 如需媒体功能
PrivateDependencyModuleNames.AddRange(new string[] {
    "DisplayClusterMedia",
    "SharedMemoryMedia"
});

// 如需编辑器扩展
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("DisplayClusterConfigurator");
}
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 管线支持 EXR 多图层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend，简化混合模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄像机命名和 MPCDI/ICVFX 着色器的不透明 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退时未使用非默认 DisplayGamma 的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是一个**活跃维护**中的大型专业插件：

- ✅ **持续更新**：最近的提交集中在 2026 年 5 月，每周都有功能性修复和增强
- ✅ **功能不断演进**：新增 EXR 多图层支持、MoviePipeline 集成改进、ICVFX 着色器优化等
- ✅ **企业级支持**：由 Epic Games 维护，是 Virtual Production 工作流的核心组件
- ✅ **跨平台支持**：支持 Win64 和 Linux
- ⚠️ **复杂度高**：29 个模块、1351 个源文件，学习曲线较陡
- ⚠️ **需要特定硬件**：正常使用需要多机集群环境，不适合单机开发调试

**推荐使用**：如果你在做虚拟制作（Virtual Production）、LED 虚拟拍摄（ICVFX）或多投影 CAVE 环境，nDisplay 是必不可少的官方方案。对于单显示器开发场景则无需使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)（Unreal Engine 文档中心 - nDisplay 章节）