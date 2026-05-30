# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置蓝图资产、着色器、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多台 PC 同步集群渲染**的核心插件，专门解决以下问题：

- **多屏/多视口同步渲染**：将一个场景的渲染结果同步分发到多台 PC 上，每台 PC 负责驱动一块或多个物理显示（如 LED 墙、投影仪、多屏 CAVE 系统）
- **虚拟制片 (Virtual Production)**：在 LED Volume 摄影棚中，实时渲染虚拟背景并投射到 LED 墙上，配合摄像机跟踪实现沉浸式拍摄
- **投影几何校正 (Warp & Blend)**：支持 MPCDI、EasyBlend、MPCDI 等多种投影校正格式，处理多台投影仪之间的边缘融合和几何变形
- **同步策略**：提供渲染同步 (Render Sync)、输入同步 (Input Sync) 等策略，确保集群中所有 PC 的渲染帧一致
- **媒体输入/输出**：支持全帧和分片 (Tiled) 媒体流，包括共享内存 (SharedMemory)、Rivermax 等媒体协议

简而言之：当你需要**多台电脑协同渲染同一个虚拟世界**并输出到复杂物理显示矩阵时，就需要 nDisplay。

## 使用场景

- 你在搭建 **LED Volume 虚拟制片摄影棚** → 使用 nDisplay 配置 LED 墙的渲染视口和 ICVFX 相机
- 你需要将渲染输出分发到 **CAVE 系统**（多面投影沉浸式环境） → 用 nDisplay 管理多台投影仪的几何校正和边缘融合
- 你有 **多屏监控墙**（如安保控制室、交易大厅） → 用 nDisplay 将不同视角分发到不同显示屏
- 你需要 **立体 3D 渲染**（如 VR 眼镜的左右眼） → nDisplay 支持 mono 和 stereo 模式
- 你在使用 **NVIDIA SwapGroup/Barrier** 进行帧同步 → nDisplay 内置 NVIDIA 渲染同步策略
- 你需要通过 **Movie Pipeline** 录制多视口合成视频 → nDisplay 提供 MoviePipeline 集成模块

## 蓝图用法

nDisplay 主要通过**配置蓝图 (UDisplayClusterBlueprint)** 进行配置，而非直接在游戏蓝图中调用运行时函数。其核心工作流程是编辑器中的配置流程。

### 核心配置对象

| 对象 | 说明 | 所在模块 |
|---|---|---|
| `ADisplayClusterRootActor` | 集群显示的根 Actor，承载所有配置和组件 | `DisplayCluster` |
| `UDisplayClusterBlueprint` | nDisplay 的配置蓝图资产，存储集群配置数据 | `DisplayClusterConfiguration` |
| `UDisplayClusterConfigurationData` | 配置数据容器，包含集群、视口、投影策略等 | `DisplayClusterConfiguration` |
| `UDisplayClusterConfigurationCluster` | 集群定义，包含主机节点列表和同步策略 | `DisplayClusterConfiguration` |
| `UDisplayClusterConfigurationClusterNode` | 集群节点定义，代表一台 PC 及其视口列表 | `DisplayClusterConfiguration` |
| `UDisplayClusterConfigurationViewport` | 视口配置，包含区域、投影策略、相机绑定等 | `DisplayClusterConfiguration` |

### 编辑器工作流

nDisplay 提供了一个专用的**蓝图编辑器 (DisplayClusterConfigurator)**，包含以下视图：

- **Output Mapping（输出映射）**：可视化编辑各视口在物理空间中的布局，支持拖拽、对齐、缩放
- **Cluster（集群）**：树形视图管理集群节点、主机、视口的层级关系
- **Details（细节面板）**：编辑选中对象的属性，包含投影策略选择、色彩分级、媒体配置等

### 集群工具函数（Cluster Utils）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `AddClusterNodeToCluster()` | 将集群节点添加到集群 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `RemoveClusterNodeFromCluster()` | 从集群移除节点 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `AddViewportToClusterNode()` | 将视口添加到集群节点 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `RemoveViewportFromClusterNode()` | 从集群节点移除视口 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `SetClusterNodeAsPrimary()` | 设置主节点 | `UE::DisplayClusterConfiguratorClusterUtils` |
| `FindOrCreateHostDisplayData()` | 查找或创建主机显示数据 | `UE::DisplayClusterConfiguratorClusterUtils` |

### 属性工具函数（Property Utils）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `GetPropertyView()` | 为属性创建临时 PropertyHandle | `UE::DisplayClusterConfiguratorPropertyUtils` |
| `SetPropertyHandleValue()` | 设置属性值 | `UE::DisplayClusterConfiguratorPropertyUtils` |
| `AddKeyValueToMap()` | 向 Map 属性添加键值对 | `UE::DisplayClusterConfiguratorPropertyUtils` |
| `RemoveKeyFromMap()` | 从 Map 属性移除键 | `UE::DisplayClusterConfiguratorPropertyUtils` |

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterConfiguratorModule.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationData.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationCluster.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationClusterNode.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationViewport.h"
```

### 基本用法：配置集群节点

```cpp
// 创建集群节点并添加到集群
#include "DisplayClusterConfiguratorClusterUtils.h"

UDisplayClusterConfigurationCluster* Cluster = /* 获取集群配置 */;
UDisplayClusterConfigurationClusterNode* NewNode = nullptr;

// 使用集群工具函数添加节点
NewNode = UE::DisplayClusterConfiguratorClusterUtils::AddClusterNodeToCluster(
    nullptr,                      // 新创建的节点
    Cluster,
    TEXT("Node_PC1")              // 节点名称
);

// 添加视口到集群节点
UDisplayClusterConfigurationViewport* Viewport = 
    UE::DisplayClusterConfiguratorClusterUtils::AddViewportToClusterNode(
        nullptr,
        NewNode,
        TEXT("Viewport_Left")
    );

// 设置主节点
UE::DisplayClusterConfiguratorClusterUtils::SetClusterNodeAsPrimary(NewNode);
```

### 基本用法：MPCDI 导入

```cpp
#include "DisplayClusterConfiguratorMPCDIImporter.h"

UDisplayClusterBlueprint* Blueprint = /* 获取蓝图 */;
FDisplayClusterConfiguratorMPCDIImporterParams Params;
Params.ParentComponentName = FName("MPCDIParent");
Params.ViewPointComponentName = FName("DefaultViewPoint");
Params.OriginComponentName = NAME_None;  // 使用根组件
Params.HostStartingIPAddress = FIPv4Address::InternalLoopback;
Params.bIncrementHostIPAddress = true;
Params.bCreateStageGeometryComponents = true;

bool bSuccess = FDisplayClusterConfiguratorMPCDIImporter::ImportMPCDIIntoBlueprint(
    TEXT("/Path/to/config.mpcdi"),
    Blueprint,
    Params
);
```

### 进阶用法：属性操作

```cpp
#include "DisplayClusterConfiguratorPropertyUtils.h"

// 读取属性视图
TSharedPtr<ISinglePropertyView> PropView = 
    UE::DisplayClusterConfiguratorPropertyUtils::GetPropertyView(
        MyObject, FName("PropertyName")
    );

// 向 Map 属性添加条目
UE::DisplayClusterConfiguratorPropertyUtils::AddKeyValueToMap(
    MapOwner,
    MapPropertyHandle,
    TEXT("NewKey"),
    TEXT("NewValue")
);

// 从 Map 属性移除条目
UE::DisplayClusterConfiguratorPropertyUtils::RemoveKeyFromMap(
    MapOwner,
    MapPropertyHandle,
    TEXT("KeyToRemove")
);
```

### 进阶用法：编辑器子系统

```cpp
#include "DisplayClusterConfiguratorEditorSubsystem.h"

// 通过编辑器子系统导入 nDisplay 配置
UDisplayClusterConfiguratorEditorSubsystem* Subsystem = 
    GEditor->GetEditorSubsystem<UDisplayClusterConfiguratorEditorSubsystem>();

// 从文件导入
UDisplayClusterBlueprint* Blueprint = Subsystem->ImportAsset(
    ParentPackage,
    FName("MyDisplayCluster"),
    TEXT("/Path/to/config.cfg")
);

// 重新导入
bool bSuccess = Subsystem->ReimportAsset(Blueprint);

// 保存配置
Subsystem->SaveConfig(ConfigData, TEXT("/Path/to/output.cfg"));

// 获取配置字符串
FString ConfigString;
Subsystem->ConfigAsString(ConfigData, ConfigString);
```

## Demo 示例

### 最小示例：创建集群配置并在编辑器中打开

```cpp
// DisplayClusterDemoModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FDisplayClusterDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// DisplayClusterDemoModule.cpp
#include "DisplayClusterDemoModule.h"
#include "DisplayClusterConfiguratorModule.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationData.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationCluster.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationClusterNode.h"
#include "DisplayClusterConfiguration/DisplayClusterConfigurationViewport.h"
#include "DisplayClusterConfiguratorClusterUtils.h"
#include "DisplayClusterConfiguratorEditorSubsystem.h"

void FDisplayClusterDemoModule::StartupModule()
{
    // 确保 nDisplay 模块已加载
    if (FModuleManager::Get().IsModuleLoaded("DisplayClusterConfigurator"))
    {
        UE_LOG(LogTemp, Log, TEXT("DisplayClusterConfigurator module is loaded"));
    }
}

void FDisplayClusterDemoModule::ShutdownModule()
{
    // 清理
}

IMPLEMENT_MODULE(FDisplayClusterDemoModule, DisplayClusterDemo)
```

> **注意**：由于 nDisplay 主要通过编辑器 UI 进行配置，大部分交互需要在编辑器的 Display Cluster Configurator 蓝图编辑器中完成。C++ API 主要用于**程序化配置**和**编辑器扩展**。

## 模块依赖

nDisplay 涉及大量模块，以下是使用者需要关注的**非标准依赖**：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | nDisplay 配置数据模型（集群、视口、投影策略等核心数据结构） |
| `DisplayClusterProjection` | 投影策略实现（MPCDI、EasyBlend、Camera 等几何校正） |
| `DisplayClusterWarp` | Warping/Blending 几何变形和边缘融合 |
| `DisplayClusterShaders` | nDisplay 专用着色器（后处理、合成、ICVFX 等） |
| `DisplayClusterMedia` | 媒体输入输出（全帧、分片媒体流） |
| `SharedMemoryMedia` | 共享内存媒体传输（PC 间低延迟帧传输） |
| `DisplayClusterColorGrading` | 多视口色彩分级 |
| `DisplayClusterMoviePipeline` | Movie Pipeline 集成（录制多视口视频） |
| `DisplayClusterReplication` | 集群间状态复制 |
| `DisplayClusterMultiUser` | 多用户编辑支持 |
| `DisplayClusterRemoteControlInterceptor` | Remote Control API 集成 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 解析库 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（媒体模块需要） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名及着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**🟢 活跃维护中**

nDisplay 是 Unreal Engine 虚拟制片（Virtual Production）管线的核心组件，由 Epic Games 专职团队持续维护。

- **创建时间**：2018 年（UE 4.20 时期），约 8 年历史
- **更新频率**：近期（2026 年 5 月）仍有多次功能性更新，涉及 MovieGraph 集成、着色器修复、输出编码改进
- **代码规模**：1351 个源文件，29 个模块 + 1 个外部库，属于大型专业插件
- **模块类型注意**：所有模块均标记为 Runtime，但多个模块实际依赖 `UnrealEd`、`EditorWidgets`、`LevelEditor` 等编辑器模块，说明这些模块在打包时会被裁剪，仅在编辑器环境中完整可用
- **默认未启用**：`EnabledByDefault: false`，需要在项目设置中手动启用
- **平台支持**：Win64 和 Linux
- **已知限制**：主要面向专业虚拟制片场景，配置复杂度较高；集群同步依赖网络延迟和硬件同步能力

**推荐使用**：如果你的项目涉及虚拟制片、LED Volume、多屏显示或集群渲染，nDisplay 是必选方案。对于普通游戏项目则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplayOverview/)