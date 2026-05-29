# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏显示集群 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、媒体资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的专业级多机集群渲染系统，用于将一个虚拟场景同步渲染到多个物理显示器上，支持单目（mono）和立体（stereo）模式。它解决的核心问题是：**如何用多台 PC 协同工作，把一个 UE 场景拼接渲染到一个由多个屏幕组成的大型显示墙上**。

典型应用场景包括：
- **虚拟制片 LED 墙**（Virtual Production）：使用 ICVFX（In-Camera VFX）技术，在 LED Volume 中实时渲染场景背景
- **CAVE/穹顶投影**：多面投影的沉浸式体验空间
- **多通道模拟器**：驾驶/飞行模拟器的多屏幕环绕显示
- **大规模 LED 显示墙**：舞台演出、主题公园、展览展示

nDisplay 通过 MPCDI（Multi-PC Display Configuration Interface）标准进行投影配置，支持 Warp（几何变形）和 Blend（亮度混合）来实现无缝拼接。它是一个运行时插件，默认不启用，需要用户根据项目需求手动开启。

## 使用场景

- 你在搭建虚拟制片 LED 墙 → 用 nDisplay 配置 ICVFX 摄像机和 LED 面板
- 你需要多台 PC 同步渲染同一场景的不同视角 → 用 nDisplay 的集群同步功能
- 你有一个 CAVE 投影空间（3-6 面） → 用 nDisplay 配置投影和边缘融合
- 你要为驾驶模拟器构建多屏幕环境 → 用 nDisplay 管理多视口
- 你需要将渲染输出发送到外部媒体设备（如 LED 处理器） → 用 nDisplay Media 模块
- 你要用 Movie Render Queue 录制多视口视频 → 用 nDisplay MoviePipeline 集成

## 蓝图用法

nDisplay 主要通过配置资产（UDisplayClusterBlueprint）和运行时组件进行控制，蓝图 API 侧重于运行时操作和监控。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDisplayClusterAsset` | 创建新的 nDisplay 配置资产 | `UDisplayClusterBlueprint` |
| 集群节点/视口管理 | 通过配置对象添加/移除集群节点和视口 | `UDisplayClusterConfigurationCluster` |

### 使用示例（蓝图描述）

nDisplay 的使用流程：
1. 在编辑器中创建 `nDisplay` 配置资产（.ndisplay 文件）
2. 在配置编辑器中添加集群节点（Cluster Nodes），每个节点对应一台渲染 PC
3. 为每个节点添加视口（Viewports），定义屏幕的位置、投影方式和分辨率
4. 配置投影策略（MPCDI、Camera、Mesh 等）和混合（Blend/Warp）参数
5. 在运行时通过 `DisplayCluster` 模块启动集群渲染

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterConfigurationTypes.h"
#include "IDisplayCluster.h"
```

### 基本用法

从测试工具中提取的资产创建和配置模式：

```cpp
// 来源: DisplayClusterTestUtils.h

// 创建 nDisplay 配置资产
UDisplayClusterBlueprint* Asset = DisplayClusterTestUtils::CreateDisplayClusterAsset();

// 获取集群配置
UDisplayClusterConfigurationCluster* Cluster = Asset->GetCluster();

// 添加集群节点
UDisplayClusterConfigurationClusterNode* Node = 
    DisplayClusterTestUtils::AddClusterNodeToCluster(Asset, Cluster, TEXT("RenderNode1"));

// 为节点添加视口
UDisplayClusterConfigurationViewport* Viewport = 
    DisplayClusterTestUtils::AddViewportToClusterNode(Asset, Node, TEXT("Viewport_0"));
```

### 进阶用法

通过属性系统修改配置属性并触发蓝图更新：

```cpp
// 来源: DisplayClusterTestUtils.h - SetBlueprintPropertyValue

// 修改蓝图属性（嵌套字段路径）
TArray<FName> FieldNames = { 
    FName("Cluster"), 
    FName("Nodes"), 
    FName("RenderNode1"), 
    FName("Viewports"),
    FName("Viewport_0"),
    FName("Resolution"),
    FName("X")
};
int32 NewWidth = 1920;

// 设置属性值并触发蓝图构造脚本重新运行
DisplayClusterTestUtils::SetBlueprintPropertyValue<int32>(
    Owner, Blueprint, FieldNames, NewWidth
);

// 读取属性值
int32 CurrentWidth = 0;
DisplayClusterTestUtils::GetBlueprintPropertyValue<int32>(
    Owner, FieldNames, CurrentWidth
);

// 颜色类型需要特殊处理（通过字符串转换）
FLinearColor TestColor = FLinearColor::Red;
DisplayClusterTestUtils::SetBlueprintPropertyValue<FLinearColor>(
    Owner, Blueprint, ColorFieldNames, TestColor
);
```

## Demo 示例

一个最小的 nDisplay 集群配置测试示例：

```cpp
// DisplayClusterMinimalTest.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterTestUtils.h"

class FDisplayClusterMinimalTest
{
public:
    /** 创建一个基本的单节点单视口配置 */
    static bool RunMinimalTest()
    {
        // 1. 创建 nDisplay 配置资产
        UDisplayClusterBlueprint* Asset = DisplayClusterTestUtils::CreateDisplayClusterAsset();
        if (!Asset)
        {
            return false;
        }

        UDisplayClusterConfigurationCluster* Cluster = Asset->GetCluster();
        if (!Cluster)
        {
            DisplayClusterTestUtils::CleanUpAssetAndPackage(Asset);
            return false;
        }

        // 2. 创建渲染节点
        UDisplayClusterConfigurationClusterNode* Node = 
            DisplayClusterTestUtils::AddClusterNodeToCluster(
                Asset, Cluster, TEXT("MainNode")
            );
        if (!Node)
        {
            DisplayClusterTestUtils::CleanUpAssetAndPackage(Asset);
            return false;
        }

        // 3. 创建视口
        UDisplayClusterConfigurationViewport* Viewport = 
            DisplayClusterTestUtils::AddViewportToClusterNode(
                Asset, Node, TEXT("MainViewport")
            );
        if (!Viewport)
        {
            DisplayClusterTestUtils::CleanUpAssetAndPackage(Asset);
            return false;
        }

        // 4. 清理
        DisplayClusterTestUtils::CleanUpAssetAndPackage(Asset);
        return true;
    }
};
```

```cpp
// DisplayClusterMinimalTest.cpp
#include "DisplayClusterMinimalTest.h"

// 实现已在头文件中内联展示
```

## 模块依赖

nDisplay 是一个大型插件，各子模块依赖不同。以下是使用者最可能需要关注的**特有依赖**：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（SharedMemoryMedia、DisplayClusterMedia 模块依赖） |
| `ScalableMPCDI` | 第三方 MPCDI 标准实现，用于投影配置和几何变形 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：nDisplay 包含 29 个子模块，具体依赖请参考各模块的 `Build.cs` 文件。生产环境中通常只需要 `DisplayCluster`（核心运行时）和 `DisplayClusterConfiguration`（配置系统）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成中添加 EXR 多图层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄像机命名和 MPCDI/ICVFX 着色器的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时尊重非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是 **Epic Games 官方积极维护**的专业级插件：

- **活跃维护**：最近更新集中在 2026 年 5 月，更新频率约为每周 1-2 次，均为功能性更新和 bug 修复
- **持续演进**：近期重点在 MovieGraph 集成、ICVFX 着色器改进和 MovieRenderQueue 增强，表明 Epic 持续投入虚拟制片工作流
- **成熟稳定**：自 2018 年创建以来已迭代 8 年，是 Unreal Engine 虚拟制片的核心组件之一
- **规模庞大**：29 个子模块、1351 个源文件，说明功能覆盖面广且经过充分扩展
- **推荐使用**：对于 LED Volume 虚拟制片、多屏集群渲染、沉浸式体验等场景，nDisplay 是官方唯一推荐方案，强烈建议使用

> ⚠️ **注意**：nDisplay 默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。该插件主要用于专业/企业级场景，对硬件和网络环境有较高要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)（Unreal Engine 官方虚拟制片文档）