# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、Shader 资产、MPCDI 资产等） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中实现**多台 PC 集群同步渲染**的核心插件。它解决的核心问题是：如何让多台联网的计算机各自渲染同一场景的不同部分（或不同视角），并将输出精确同步地投射到多个物理显示器上，形成一个无缝的大画面。

典型硬件架构包括：

- **CAVE 系统**：多面投影沉浸式环境（如 3-6 面投影房）
- **LED 墙（LED Volume）**：虚拟制作中使用的弧形 LED 显示屏
- **多显示器设置**：如驾驶模拟器的多屏幕环绕显示
- **投影融合**：多台投影仪拼接一个大画面

插件提供了完整的端到端解决方案：
- **配置系统**：通过蓝图资产（`UDisplayClusterBlueprint`）定义集群拓扑、主机、节点、视口和投影策略
- **投影映射**：支持 MPCDI、EasyBlend、VIOSO 等工业标准投影校准格式
- **输出映射编辑器**：可视化的 2D 编辑器，用于规划视口在物理屏幕上的布局
- **媒体集成**：支持 SharedMemory、NVIDIA Rivermax 等媒体输入/输出，用于视频采集和传输
- **ICVFX（LED 虚拟拍摄）**：专用的相机内视效支持，包括 Light Card、色彩分级等
- **电影管线集成**：与 Movie Render Queue 配合，支持多 PC 离线渲染
- **远程控制**：通过 Remote Control API 远程调整运行时参数

**注意**：`EnabledByDefault` 为 `false`，需要在项目设置中手动启用此插件。

## 使用场景

- 你在构建一个 **CAVE 虚拟现实环境**，需要多台 PC 同步渲染不同墙面 → 用 nDisplay 定义集群拓扑和投影策略
- 你在做 **虚拟制作**，需要将 UE5 画面实时输出到 LED Volume 的不同区域 → 用 nDisplay + 共享内存/网络媒体传输
- 你需要为 **驾驶模拟器** 配置多屏环绕显示 → 用 nDisplay 管理每个屏幕的视口和投影
- 你需要 **高质量离线渲染**，利用多台 PC 并行渲染电影序列的不同帧 → 用 nDisplay + Movie Render Queue
- 你需要将 **投影仪融合校正文件**（MPCDI/EasyBlend/VIOSO）导入 UE5 → 用 nDisplay 的 MPCDI 导入功能
- 你需要在运行时 **远程控制** 集群显示参数 → 用 nDisplay 的 Remote Control Interceptor

## 蓝图用法

nDisplay 的运行时 API 主要通过 `UDisplayClusterBlueprint` 资产和 `ADisplayClusterRootActor` 组件暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddClusterNodeToCluster` | 将集群节点添加到集群中，自动处理重名和迁移 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `RemoveClusterNodeFromCluster` | 从集群中移除指定集群节点 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `AddViewportToClusterNode` | 将视口添加到集群节点中 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `RemoveViewportFromClusterNode` | 从集群节点中移除视口 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `RenameClusterNode` | 重命名集群节点（自动唯一化） | `UE::DisplayClusterConfiguratorClusterUtils` |
| `SetClusterNodeAsPrimary` | 设置指定集群节点为主节点 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `CreateNewClusterNodeFromDialog` | 通过对话框创建新集群节点（带配置 UI） | `UE::DisplayClusterConfiguratorClusterEditorUtils` |
| `CreateNewViewportFromDialog` | 通过对话框创建新视口（带配置 UI） | `UE::DisplayClusterConfiguratorClusterEditorUtils` |
| `CopyClusterItemsToClipboard` | 将集群项复制到剪贴板 | `UE::DisplayClusterConfiguratorClusterEditorUtils` |
| `PasteClusterItemsFromClipboard` | 从剪贴板粘贴集群项 | `UE::DisplayClusterConfiguratorClusterEditorUtils` |

### 编辑器子系统接口

| 方法 | 说明 | 所在类 |
|---|---|---|
| `ImportAsset` | 导入 nDisplay 配置文件为蓝图资产 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `ReimportAsset` | 重新导入已有的 nDisplay 蓝图 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `ReloadConfig` | 从指定路径重新加载配置数据 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `SaveConfig` | 将配置数据保存到指定路径 | `UDisplayClusterConfiguratorEditorSubsystem` |
| `ConfigAsString` | 将配置数据序列化为字符串 | `UDisplayClusterConfiguratorEditorSubsystem` |

### 使用示例（蓝图描述）

在编辑器中，nDisplay 主要通过以下流程使用：

1. **创建配置**：在 Content Browser 中右键 → Miscellaneous → nDisplay Configuration Blueprint，双击打开专用编辑器
2. **配置集群**：在 Cluster 面板中添加主机（Host）、集群节点（Cluster Node）和视口（Viewport）
3. **输出映射**：在 Output Mapping 面板中以 2D 可视化方式拖拽布局视口
4. **投影策略**：在 Details 面板中为每个视口选择投影策略（Simple/Camera/Mesh/Dome/MPCDI 等）
5. **放置到场景**：将 nDisplay 蓝图拖入场景，自动生成 `ADisplayClusterRootActor`
6. **运行**：各节点 PC 启动后自动同步渲染

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "DisplayClusterModule.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterBlueprint.h"

// 配置数据
#include "DisplayClusterConfigurationData.h"
#include "DisplayClusterConfigurationCluster.h"
#include "DisplayClusterConfigurationClusterNode.h"
#include "DisplayClusterConfigurationViewport.h"

// 配置器工具
#include "DisplayClusterConfiguratorClusterUtils.h"
#include "DisplayClusterConfiguratorEditorSubsystem.h"
```

### 基本用法：集群配置操作

```cpp
// 来源: Public/ClusterConfiguration/DisplayClusterConfiguratorClusterUtils.h
#include "DisplayClusterConfiguratorClusterUtils.h"

// 添加一个集群节点到集群
UDisplayClusterConfigurationClusterNode* NewNode = 
    UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
        ClusterNode, 
        Cluster, 
        TEXT("RenderNode_01"));

// 设置为主节点
UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(NewNode);

// 添加视口到集群节点
UDisplayClusterConfigurationViewport* NewViewport = 
    UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
        Viewport, 
        ClusterNode, 
        TEXT("Viewport_Main"));

// 获取主机显示数据
UDisplayClusterConfigurationHostDisplayData* HostData = 
    UE::DisplayClusterConfiguratorClusterUtils::GetHostDisplayDataForClusterNode(ClusterNode);
```

### 基本用法：编辑器子系统操作

```cpp
// 来源: Private/DisplayClusterConfiguratorEditorSubsystem.h
#include "DisplayClusterConfiguratorEditorSubsystem.h"

// 获取编辑器子系统
UDisplayClusterConfiguratorEditorSubsystem* Subsystem = 
    GEditor->GetEditorSubsystem<UDisplayClusterConfiguratorEditorSubsystem>();

// 从文件导入 nDisplay 配置
UDisplayClusterBlueprint* Blueprint = Subsystem->ImportAsset(
    ParentPackage, 
    FName("MyDisplayConfig"), 
    TEXT("C:/Config/display_cluster.cfg"));

// 重新导入
Subsystem->ReimportAsset(Blueprint);

// 保存配置到文件
Subsystem->SaveConfig(ConfigData, TEXT("C:/Config/exported.cfg"));
```

### 进阶用法：MPCDI 导入

```cpp
// 来源: Private/MPCDI/DisplayClusterConfiguratorMPCDIImporter.h
#include "DisplayClusterConfiguratorMPCDIImporter.h"

// 配置导入参数
FDisplayClusterConfiguratorMPCDIImporterParams Params;
Params.ParentComponentName = FName("Origin");
Params.ViewPointComponentName = FName("DefaultViewPoint");
Params.bCreateStageGeometryComponents = true;
Params.bIncrementHostIPAddress = true;

// 将 MPCDI 文件导入到 nDisplay 蓝图
bool bSuccess = FDisplayClusterConfiguratorMPCDIImporter::ImportMPCDIIntoBlueprint(
    TEXT("C:/MPCDI/profile.mpcdi"),
    DisplayClusterBlueprint,
    Params);
```

### 进阶用法：属性工具

```cpp
// 来源: Private/DisplayClusterConfiguratorPropertyUtils.h
#include "DisplayClusterConfiguratorPropertyUtils.h"

// 获取临时属性视图
TSharedPtr<ISinglePropertyView> PropView = 
    UE::DisplayClusterConfiguratorPropertyUtils::GetPropertyView(
        OwnerObject, 
        FName("RenderSyncPolicy"));

// 向 Map 属性添加键值对
TSharedPtr<IPropertyHandle> PropHandle = /* ... */;
UE::DisplayClusterConfiguratorPropertyUtils::AddKeyValueToMap(
    MapOwnerAddress, PropHandle, 
    TEXT("ViewportName"), TEXT("ParameterValue"));

// 向 Map 添加实例化对象（深拷贝）
UObject* ClonedValue = 
    UE::DisplayClusterConfiguratorPropertyUtils::AddKeyWithInstancedValueToMap(
        MapOwnerObject, 
        FName("ViewportSettings"), 
        TEXT("Viewport_01"), 
        SourceValue);
```

### 进阶用法：输出映射对齐系统

```cpp
// 来源: Private/Views/OutputMapping/Alignment/DisplayClusterConfiguratorNodeAlignmentHelper.h
// 对齐参数配置
FNodeAlignmentParams AlignParams;
AlignParams.SnapProximity = 10.0f;
AlignParams.MaxSnapRadius = 500.0f;
AlignParams.SnapAdjacentEdgesPadding = 5.0f;
AlignParams.bCanSnapAdjacentEdges = true;
AlignParams.bCanSnapSameEdges = true;

// 获取节点锚点
FNodeAlignmentAnchors Anchors = Node->GetNodeAlignmentAnchors();

// 创建对齐辅助器
FDisplayClusterConfiguratorNodeAlignmentHelper AlignHelper(
    NodeToAlign, Anchors, AlignParams);

// 添加目标节点的对齐关系
AlignHelper.AddAlignmentsToNode(TargetNode);
AlignHelper.AddAlignmentsToParent(ParentNode);

// 获取最终对齐结果
FNodeAlignmentPair Alignments = AlignHelper.GetAlignments();
if (Alignments.HasAlignments())
{
    FVector2D Offset = Alignments.GetOffset();
    // 应用偏移
}
```

## 模块依赖

从各模块的 Build.cs 中提取的独特依赖（排除 Core/CoreUObject/Engine/Slate/SlateCore/UMG/InputCore 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能（多个模块依赖，用于蓝图编辑器、Details 面板定制等） |
| `D3D12RHI` | DirectX 12 渲染硬件接口（用于 SharedMemory 媒体和媒体编辑器） |
| `LevelEditor` | 关卡编辑器集成（DisplayCluster 核心模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 的 nDisplay 输出添加 EXR 多图层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 中的 WarpBlendAlpha 模式合并到 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名及 MPCDI/ICVFX 着色器中的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时正确处理非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

- **年龄**：约 8 年，属于成熟插件
- **活跃度**：**非常活跃**。最近更新在 2026 年 5 月，近 2 周内有 5 次提交，涉及 MovieGraph、着色器修复、媒体管线等多个子系统
- **维护质量**：由 Epic Games 官方团队维护，代码结构清晰，29 个模块划分合理，覆盖了从配置、编辑器、运行时到媒体、电影管线的完整链路
- **规模**：xlarge 级别（1351 个源文件），是 UE5 中最复杂的插件之一
- **推荐度**：**强烈推荐**用于所有需要多 PC 集群同步渲染的项目。作为 UE5 官方虚拟制作管线的核心组件，持续获得 Epic 的投入和更新。唯一限制是需要手动启用，且仅支持 Win64 和 Linux 平台。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：无（DocsURL 为空）