# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 用于实现多 PC 同步集群渲染的核心插件。它解决的核心问题是：如何让多台计算机（节点）协同工作，将一个 UE 场景拆分并同步渲染到由多块屏幕组成的复杂显示系统上（例如大型 LED 墙、CAVE 洞穴系统、穹顶投影等）。通过该插件，可以实现：
* **单目 (Mono)** 或 **立体 (Stereo)** 渲染。
* **帧同步**：确保所有渲染节点在完全相同的时间点渲染并输出画面，消除撕裂和延迟。
* **视锥体拆分与管理**：根据物理屏幕的布局和投影方式，为每个渲染节点自动计算和应用正确的相机视锥体。
* **复杂的几何与色彩校正**：处理投影仪或屏幕带来的几何变形（Warping）和色彩不均（Blending）问题。

简而言之，它是构建大规模、沉浸式视觉体验的底层技术基础。

## 使用场景

* **虚拟制片 (Virtual Production)**：在配备大型 LED 屏的舞台上，使用 nDisplay 将虚拟环境实时渲染到 LED 墙和天花板上，为演员提供逼真的背景，并实现前景元素的实时合成。
* **沉浸式显示与仿真**：构建 CAVE (Cave Automatic Virtual Environment) 系统、穹顶影院、多通道投影驾驶舱模拟器等，提供环绕式的视觉体验。
* **主题公园与大型活动**：为游乐设施、展览馆、音乐会等打造由数百块屏幕组成的巨型显示墙。
* **专业级可视化**：用于汽车设计、建筑漫游、科学数据可视化等领域，需要高分辨率、高帧率多屏输出的场景。

## 蓝图用法

nDisplay 的核心运行时逻辑和配置主要通过 C++ 和其专用的配置资产 (`UDisplayClusterBlueprint`) 进行管理。**当前分析的模块 `DisplayClusterTests` 是一个内部测试模块，不包含公开的蓝图可调用函数或属性。** 要使用 nDisplay 的功能，通常通过其配置资产和编辑器工具进行设置，而非直接调用蓝图节点。更高级的蓝图集成（如通过 Remote Control 等）可能存在于其他关联模块中。

## C++ 用法

`DisplayClusterTests` 模块提供了一套用于单元测试和功能测试的工具函数，展示了如何以编程方式与 nDisplay 的配置系统交互。虽然这些是测试工具，但它们揭示了操作 nDisplay 配置对象的 C++ API 核心模式。

### 头文件引入

```cpp
#include "DisplayClusterTestUtils.h"
```

### 基本用法

以下代码展示了如何使用测试工具创建一个 nDisplay 配置资产并为其添加集群节点。这反映了通过代码动态构建或修改 nDisplay 配置的基本流程。
**来源文件：`Source/DisplayClusterTests/Private/DisplayClusterTestUtils.h`**

```cpp
// 创建一个新的 nDisplay 配置资产
UDisplayClusterBlueprint* MyClusterAsset = DisplayClusterTestUtils::CreateDisplayClusterAsset();

// 获取资产中的默认集群配置
UDisplayClusterConfigurationCluster* ClusterRoot = MyClusterAsset->GetCluster();

// 向集群中添加一个名为 “Node_01” 的渲染节点
UDisplayClusterConfigurationClusterNode* NewNode = DisplayClusterTestUtils::AddClusterNodeToCluster(MyClusterAsset, ClusterRoot, TEXT(“Node_01”));

// 向这个新节点添加一个视口
UDisplayClusterConfigurationViewport* NewViewport = DisplayClusterTestUtils::AddViewportToClusterNode(MyClusterAsset, NewNode, TEXT(“Viewport_01”));

// ... 进行其他配置或保存资产 ...

// 测试结束后清理资源
DisplayClusterTestUtils::CleanUpAssetAndPackage(MyClusterAsset);
```

### 进阶用法

测试工具还提供了操作配置对象属性的高级模板函数，这些函数模拟了在编辑器属性面板中修改属性的行为。
**来源文件：`Source/DisplayClusterTests/Private/DisplayClusterTestUtils.h`**

```cpp
// 假设我们已经有一个节点配置对象 `NodeConfig`
UDisplayClusterConfigurationClusterNode* NodeConfig = ...;

// 定义要修改的属性路径：一个结构体成员内的字段
TArray<FName> FieldNames;
FieldNames.Add(TEXT(“ScreenInfo”)); // 第一个字段是“ScreenInfo”结构体
FieldNames.Add(TEXT(“Width”));     // 第二个字段是该结构体内的“Width”

// 通过属性系统设置一个浮点值 (例如屏幕宽度)
float NewWidth = 3840.0f;
bool bSuccess = DisplayClusterTestUtils::SetBlueprintPropertyValue(NodeConfig, nullptr, FieldNames, NewWidth);

// 同样，获取一个线性颜色值（需要特殊处理）
TArray<FName> ColorFieldNames;
ColorFieldNames.Add(TEXT(“Color”));
FLinearColor CurrentColor;
if (DisplayClusterTestUtils::GetBlueprintPropertyValue(NodeConfig, ColorFieldNames, CurrentColor))
{
    // 使用 CurrentColor
}
```

## Demo 示例

一个最小化示例，演示如何创建一个简单的 nDisplay 配置，用于单节点单视口的渲染，并最后进行清理。这可以作为编写 nDisplay 自动化测试或工具的起点。

```cpp
// MyNDisplayConfigTool.h
#pragma once

#include “CoreMinimal.h”

class UDisplayClusterBlueprint;

class FMyNDisplayConfigTool
{
public:
    /** 创建并配置一个最基本的单节点 nDisplay 资产 */
    static UDisplayClusterBlueprint* CreateBasicSingleNodeConfig();
};

// MyNDisplayConfigTool.cpp
#include “MyNDisplayConfigTool.h”
#include “DisplayClusterTestUtils.h”

UDisplayClusterBlueprint* FMyNDisplayConfigTool::CreateBasicSingleNodeConfig()
{
    // 1. 创建资产
    UDisplayClusterBlueprint* ConfigAsset = DisplayClusterTestUtils::CreateDisplayClusterAsset();
    if (!ConfigAsset)
    {
        return nullptr;
    }

    // 2. 获取集群根
    UDisplayClusterConfigurationCluster* Cluster = ConfigAsset->GetCluster();
    if (!Cluster)
    {
        DisplayClusterTestUtils::CleanUpAssetAndPackage(ConfigAsset);
        return nullptr;
    }

    // 3. 添加一个节点
    UDisplayClusterConfigurationClusterNode* Node = DisplayClusterTestUtils::AddClusterNodeToCluster(ConfigAsset, Cluster, TEXT(“PrimaryNode”));
    if (!Node)
    {
        DisplayClusterTestUtils::CleanUpAssetAndPackage(ConfigAsset);
        return nullptr;
    }

    // 4. 向该节点添加一个视口
    UDisplayClusterConfigurationViewport* Viewport = DisplayClusterTestUtils::AddViewportToClusterNode(ConfigAsset, Node, TEXT(“MainViewport”));
    if (!Viewport)
    {
        DisplayClusterTestUtils::CleanUpAssetAndPackage(ConfigAsset);
        return nullptr;
    }

    // 5. 配置完成，返回资产。调用者负责后续的保存或清理。
    UE_LOG(LogTemp, Log, TEXT(“Created basic nDisplay config: %s”), *ConfigAsset->GetName());
    return ConfigAsset;
}
```

## 模块依赖

要使用 `DisplayClusterTests` 模块的功能，你的模块需要在 `.Build.cs` 文件中声明以下依赖：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 使用 `FBlueprintEditorUtils` 等编辑器功能来模拟属性修改和蓝图更新 |
| `DisplayClusterConfiguration` | 访问 `UDisplayClusterConfigurationClusterNode`, `UDisplayClusterConfigurationViewport` 等 nDisplay 核心配置类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加了 EXR 多层图像支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 MoviePipeline 中的 WarpBlendAlpha 模式到 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名问题，以及 MPCDI/ICVFX 着色器中不透明 Alpha 的问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时尊重非默认的显示 Gamma 值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 是 Unreal Engine 中一个成熟且活跃维护的大型功能插件。
* **活跃维护**：从近期提交记录看，它持续获得功能增强（如与 MovieGraph 集成）和重要的 Bug 修复，最近一次更新在 2026 年 5 月，表明 Epic Games 团队仍在积极投入。
* **长期存在**：该插件自 2018 年（UE 4.20 时期）引入，经历了多年的迭代，已经成为虚拟制片和大型显示项目的基石。
* **功能全面**：其庞大的模块列表覆盖了从核心渲染、投影校正、媒体输入输出、编辑器工具到多用户协作的完整工作流。
* **注意事项**：作为一项高度专业化的技术，其学习曲线较陡，且对硬件和网络环境有特定要求。默认未启用 (`EnabledByDefault: false`)。
* **推荐使用**：对于任何涉及多机同步渲染、LED 虚拟制片或复杂投影显示的项目，**nDisplay 是首选且推荐使用的官方解决方案**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)