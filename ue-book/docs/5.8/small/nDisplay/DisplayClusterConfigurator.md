# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置蓝图资产、材质、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**集群渲染同步系统**，用于在**多台 PC** 上驱动**多屏幕投影显示**，支持单目和立体（Stereo）渲染模式。

**核心解决的问题**：

1. **多机同步渲染**：在多台独立 PC 上同时渲染同一场景的不同视口，并保持帧同步（frame lock）和状态同步，适用于 CAVE、Powerwall、LED Volume 等沉浸式显示环境
2. **投影变形与边缘融合**：支持多种投影策略（MPCDI、EasyBlend、Manual、Mesh、Dome 等），处理投影面的几何变形（warp）和多投影仪之间的边缘融合（blend）
3. **ICVFX 虚拟制片**：通过 ICVFX Camera 组件支持 LED Volume 上的虚拟场景渲染，是 Unreal 虚拟制片管线的关键组件
4. **媒体输入/输出集成**：支持与 Rivermax、SharedMemoryMedia 等媒体框架集成，实现 NDI/SMPTE 2110 等专业视频信号的输入输出
5. **配置管理**：通过配置蓝图（DisplayClusterBlueprint）集中管理所有节点、视口、投影策略和显示拓扑

**为什么存在**：传统的单机多显示器方案无法满足专业显示行业对帧同步、几何校正和大规模集群的需求。nDisplay 提供了从配置、编辑、调试到运行时的完整工具链，是 Unreal 在沉浸式显示和虚拟制片领域的核心基础设施。

## 使用场景

- 你在搭建 **CAVE 洞穴式 VR 显示系统**，需要多台 PC 同步渲染不同墙面 → 用 nDisplay 配置多节点集群
- 你在做 **LED Volume 虚拟制片**（如 The Mandalorian 风格），需要将虚拟场景渲染到 LED 墙上 → 用 nDisplay 的 ICVFX 功能
- 你需要在 **球幕/穹顶投影** 中进行几何校正 → 用 nDisplay 的 Dome/MPCDI 投影策略
- 你有一个 **Powerwall 多投影仪拼接显示**，需要边缘融合 → 用 nDisplay 的 Warp/Blend 模块
- 你需要将渲染输出通过 **SMPTE 2110 / Rivermax** 发送到专业视频设备 → 用 nDisplay 的 Media 模块
- 你要在 **影视虚拟制片** 中使用 Movie Render Queue 录制多视口 → 用 nDisplay 的 MoviePipeline 集成

## 蓝图用法

> **注意**：nDisplay 的运行时蓝图 API 主要集中在 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块中。以下基于 `DisplayClusterConfigurator` 编辑器模块中的可配置属性和工作流提取。

### 核心节点

nDisplay 的使用主要通过 **配置蓝图（DisplayCluster Blueprint）** 而非运行时蓝图节点。核心工作流如下：

| 操作 | 说明 | 所在类/模块 |
|---|---|---|
| 创建 nDisplay 配置蓝图 | 在 Content Browser 右键 → Miscellaneous → nDisplay Configuration | `UDisplayClusterBlueprint` |
| 配置集群节点 | 在 Cluster 面板中添加主机和节点 | `UDisplayClusterConfigurationCluster` |
| 配置视口 | 为每个集群节点添加视口，设置分辨率和区域 | `UDisplayClusterConfigurationViewport` |
| 选择投影策略 | 在 Viewport Details 中选择 MPCDI/Mesh/Dome/EasyBlend 等 | `FDisplayClusterConfiguratorProjectionCustomization` |
| 配置渲染同步策略 | 设置帧同步策略（NVIDIA/None/自定义） | `FDisplayClusterConfiguratorRenderSyncPolicyCustomization` |
| 导入 MPCDI 配置 | 导入 MPCDI 文件自动生成投影配置 | `FDisplayClusterConfiguratorMPCDIImporter` |

### 配置蓝图编辑器面板

nDisplay 配置蓝图编辑器提供以下面板：

| 面板 | 功能 |
|---|---|
| **Cluster 树视图** | 管理主机、集群节点和视口的层级结构 |
| **Output Mapping** | 可视化编辑各视口在屏幕上的位置映射关系 |
| **Details** | 编辑选中对象的属性（投影策略、同步策略、媒体配置等） |
| **Scene Preview** | 3D 预览场景中 nDisplay 组件的布局 |

### 使用示例（编辑器配置流程）

1. **创建配置蓝图**：Content Browser → 右键 → Miscellaneous → nDisplay Configuration
2. **双击打开编辑器**：在 Cluster 树视图中可以看到默认的集群结构
3. **添加集群节点**：右键 Cluster → Add Cluster Node，设置主机 IP 和视口数量
4. **配置视口**：选中视口节点，在 Details 面板中设置：
   - **Region**：视口在屏幕上的位置和大小（X, Y, W, H）
   - **Camera**：关联的相机组件
   - **Projection Policy**：选择投影策略（如 MPCDI、Mesh、Manual 等）
5. **Output Mapping 编辑**：在 Output Mapping 面板中拖拽调整各视口的屏幕布局
6. **导出配置**：File → Export Configuration 保存为 .cfg 文件，供集群运行时使用

## C++ 用法

### 头文件引入

```cpp
// 集群配置工具
#include "ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h"

// 属性工具
#include "DisplayClusterConfiguratorPropertyUtils.h"

// 树视图接口
#include "Views/TreeViews/IDisplayClusterConfiguratorTreeItem.h"
#include "Views/TreeViews/IDisplayClusterConfiguratorViewTree.h"
#include "Views/TreeViews/IDisplayClusterConfiguratorTreeBuilder.h"
```

### 基本用法：集群节点管理

```cpp
// 来源: Public/ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h

#include "ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h"

using namespace UE::DisplayClusterConfiguratorClusterUtils;

// 添加集群节点到集群
UDisplayClusterConfigurationClusterNode* NewNode = AddClusterNodeToCluster(
    ClusterNode,
    Cluster,
    TEXT("MyClusterNode")
);

// 重命名集群节点
RenameClusterNode(ClusterNode, TEXT("NewNodeName"));

// 设置为主节点
SetClusterNodeAsPrimary(ClusterNode);

// 检查是否为主节点
bool bIsPrimary = IsClusterNodePrimary(ClusterNode);

// 添加视口到集群节点
UDisplayClusterConfigurationViewport* NewViewport = AddViewportToClusterNode(
    Viewport,
    ClusterNode,
    TEXT("Viewport_0")
);

// 获取唯一名称
FString UniqueName = GetUniqueNameForClusterNode(
    TEXT("Node"), ParentCluster, false
);
```

### 进阶用法：属性工具操作

```cpp
// 来源: Private/DisplayClusterConfiguratorPropertyUtils.h

#include "DisplayClusterConfiguratorPropertyUtils.h"

using namespace UE::DisplayClusterConfiguratorPropertyUtils;

// 获取属性视图
TSharedPtr<ISinglePropertyView> PropView = GetPropertyView(
    MyObject, GET_MEMBER_NAME_CHECKED(UMyClass, MyProperty)
);

// 设置属性值
SetPropertyHandleValue(MyObject, TEXT("ProjectionPolicy"), TEXT("MPCDI"));

// 向 Map 属性添加键值对（带实例化对象）
UObject* AddedValue = AddKeyWithInstancedValueToMap(
    MapOwner, TEXT("ViewportMap"), TEXT("VP_0"), ViewportObject
);

// 向 Map 添加格式化字符串值
TSharedPtr<IPropertyHandle> KeyHandle = AddKeyValueToMap(
    MapOwnerAddress, MapPropertyHandle, TEXT("Key"), TEXT("Value")
);

// 从 Map 移除键
RemoveKeyFromMap(MapOwner, TEXT("ViewportMap"), TEXT("VP_0"));

// 清空 Map
EmptyMap(MapOwnerAddress, MapPropertyHandle);
```

## Demo 示例

以下展示如何以 C++ 方式创建一个简单的 nDisplay 集群配置工具类：

```cpp
// MyClusterSetupTool.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyClusterSetupTool.generated.h"

class UDisplayClusterConfigurationCluster;
class UDisplayClusterConfigurationClusterNode;
class UDisplayClusterConfigurationViewport;

UCLASS()
class UMyClusterSetupTool : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /**
     * 快速创建一个三屏幕 Powerwall 集群配置
     * @param ConfigData - 要配置的 nDisplay 配置数据
     * @param ViewportWidth - 每个视口的宽度（像素）
     * @param ViewportHeight - 每个视口的高度（像素）
     */
    void SetupPowerwall(
        UDisplayClusterConfigurationData* ConfigData,
        int32 ViewportWidth = 1920,
        int32 ViewportHeight = 1080
    );
};
```

```cpp
// MyClusterSetupTool.cpp
#include "MyClusterSetupTool.h"
#include "DisplayClusterConfigurationTypes.h"
#include "ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h"

using namespace UE::DisplayClusterConfiguratorClusterUtils;

void UMyClusterSetupTool::SetupPowerwall(
    UDisplayClusterConfigurationData* ConfigData,
    int32 ViewportWidth,
    int32 ViewportHeight)
{
    if (!ConfigData || !ConfigData->Cluster)
    {
        return;
    }

    UDisplayClusterConfigurationCluster* Cluster = ConfigData->Cluster;

    // 创建主节点
    UDisplayClusterConfigurationClusterNode* PrimaryNode = NewObject<UDisplayClusterConfigurationClusterNode>(Cluster);
    AddClusterNodeToCluster(PrimaryNode, Cluster, TEXT("Node_0"));
    SetClusterNodeAsPrimary(PrimaryNode);

    // 为三屏 Powerwall 创建三个视口
    for (int32 i = 0; i < 3; ++i)
    {
        UDisplayClusterConfigurationViewport* Viewport = NewObject<UDisplayClusterConfigurationViewport>(PrimaryNode);

        // 设置视口区域（水平排列）
        Viewport->Region.X = i * ViewportWidth;
        Viewport->Region.Y = 0;
        Viewport->Region.W = ViewportWidth;
        Viewport->Region.H = ViewportHeight;

        FString ViewportName = FString::Printf(TEXT("Viewport_%d"), i);
        AddViewportToClusterNode(Viewport, PrimaryNode, ViewportName);
    }

    // 设置投影策略为 MPCDI
    for (auto& ViewportPair : PrimaryNode->Viewports)
    {
        UDisplayClusterConfigurationViewport* VP = ViewportPair.Value;
        VP->ProjectionPolicy.Type = TEXT("MPCDI");
    }
}
```

## 模块依赖

由于 nDisplay 是大型插件，各模块依赖差异较大。以下是关键的**非通用依赖**：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（SharedMemoryMedia、DisplayClusterMedia 使用） |
| `LevelEditor` | 编辑器关卡编辑器集成（DisplayCluster 模块使用） |
| `EditorWidgets` | 编辑器专用 Widget（DisplayCluster 模块使用） |
| `RenderCore` | 渲染核心功能 |
| `MediaFrameworkUtilities` | 媒体框架工具 |
| `MPCDI` (ThirdParty) | MPCDI 标准文件格式解析（通过 ScalableMPCDI 外部模块） |

> **注意**：大部分模块还依赖 UnrealEd 等编辑器模块（尽管标记为 Runtime），这是因为 nDisplay 的许多"Runtime"模块实际上包含了编辑器辅助功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 集成新增 EXR 多层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及 MPCDI/ICVFX 着色器的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **年龄**：约 8 年（创建于 2018 年 6 月），是 Epic 长期投入的企业级功能
- **更新频率**：极高，近 10 天内有 5 次实质性提交，涵盖功能增强、Bug 修复和性能优化
- **活跃程度**：作为 Unreal 虚拟制片管线的核心组件，持续得到 Epic 工程团队的维护
- **代码规模**：1351 个源文件、29 个模块，是 UE5 中最大的插件之一
- **功能成熟度**：功能完善，支持 MPCDI、NVIDIA 帧同步、ICVFX、多种投影策略等专业特性
- **推荐度**：✅ **强烈推荐**用于任何需要集群渲染或多屏幕投影的项目。注意 `EnabledByDefault=false`，需要在项目设置中手动启用插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/DisplayCluster/)（nDisplay 专栏文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)