# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多PC集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于**同步集群渲染**的核心系统，它解决了使用多台计算机（PC）驱动多个显示设备（如投影仪、LED墙）进行大规模、高分辨率或沉浸式显示时的渲染同步和内容管理问题。它允许将一个UE场景的渲染负载分布到多个计算机上，同时确保所有屏幕的渲染内容在空间和时间上保持精确同步。

`DisplayClusterColorGrading` 模块是 nDisplay 生态中的一个**编辑器扩展模块**，它专门负责在 nDisplay 操作面板中集成颜色分级（Color Grading）编辑器。它解决了为复杂的多视口/多节点显示系统（例如 LED 墙的多个区域）提供直观、高效的颜色分级工作流的问题。它通过生成数据模型，将 nDisplay 特有的颜色分级设置（如按视口或按ICVFX相机分组）暴露给标准的 UMG 颜色分级面板，使美术师能够精细调整每个显示区域的最终画面效果。

## 使用场景

- **虚拟制作 (Virtual Production) / LED 墙拍摄**: 你使用大型 LED 墙作为背景，需要为屏幕上不同区域（例如天空、地平线、前景）分别调整颜色和曝光，以匹配现场布光和摄影机设置。使用 `DisplayClusterColorGrading` 可以为每个独立的渲染节点或视口创建颜色分级组。
- **大型沉浸式环境 (Immersive Environments)**: 你在搭建一个由多台投影机拼接的穹顶或 CAVE 系统。不同投影区域由于投影仪特性和幕布材质，可能需要单独的颜色校正。此模块允许你针对每个投影区域（对应 nDisplay 中的一个节点或视口）进行独立的 LUT 和色彩调整。
- **复杂多屏展示系统**: 例如主题公园游乐设施、展览馆，需要多台 PC 同步渲染多个显示器上的内容，并需要为每个显示器精细匹配色彩一致性。
- **高级视觉特效 (ICVFX) 工作流**: 当使用 nDisplay 的 In-Camera VFX 功能时，需要为虚拟相机看到的 LED 墙部分（即虚拟背景）进行独立的颜色分级，以完美融入实拍画面。`DisplayClusterColorGradingGenerator_ICVFXCamera` 就是为此设计的。

## 蓝图用法

`DisplayClusterColorGrading` 模块主要作为编辑器扩展工作，其核心功能是通过 C++ 接口和编辑器 UI 暴露，蓝图节点相对较少。主要的交互入口是通过模块接口获取颜色分级抽屉的单例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Color Grading Drawer Singleton` | 获取管理颜色分级抽屉 UI 的单例对象，用于打开或刷新抽屉。 | `IDisplayClusterColorGrading` |
| `Dock Color Grading Drawer` | 将颜色分级抽屉停靠到 nDisplay 操作面板的标签页中。 | `IDisplayClusterColorGradingDrawerSingleton` |
| `Refresh Color Grading Drawers` | 刷新所有已打开的颜色分级抽屉的 UI，使其与当前关卡和活动根 Actor 的状态同步。 | `IDisplayClusterColorGradingDrawerSingleton` |

### 使用示例（蓝图描述）

1.  在任意蓝图（如你的编辑器工具蓝图）中，调用 `IDisplayClusterColorGrading::Get()` 函数（需要先确保 `DisplayClusterColorGrading` 模块可用）。
2.  将返回的接口对象引线连接到 `Get Color Grading Drawer Singleton` 节点，获取 `IDisplayClusterColorGradingDrawerSingleton` 对象。
3.  调用 `Dock Color Grading Drawer` 节点。这将在你的 nDisplay 操作面板界面中创建一个新的标签页，其中包含完整的颜色分级界面。
4.  之后，可以通过 `Refresh Color Grading Drawers` 节点来更新该界面，例如在关卡变化或 Actor 选择变化后。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterColorGrading.h"
#include "IDisplayClusterColorGradingDrawerSingleton.h"
```

### 基本用法

主要通过单例接口控制颜色分级抽屉的显示和刷新。

```cpp
// 来源: Public/IDisplayClusterColorGrading.h, Public/IDisplayClusterColorGradingDrawerSingleton.h
if (IDisplayClusterColorGrading::IsAvailable())
{
    // 获取颜色分级模块接口
    IDisplayClusterColorGrading& ColorGradingModule = IDisplayClusterColorGrading::Get();
    // 获取抽屉管理器单例
    IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = ColorGradingModule.GetColorGradingDrawerSingleton();

    // 将颜色分级抽屉停靠在操作面板中
    DrawerSingleton.DockColorGradingDrawer();

    // 当某些状态改变时，刷新UI
    DrawerSingleton.RefreshColorGradingDrawers();
}
```

### 进阶用法

创建自定义的颜色分级数据模型生成器，以扩展 nDisplay 颜色分级系统，支持新的对象类型。以下示例展示如何注册一个新的生成器来处理 `ADisplayClusterRootActor` 的自定义颜色分级属性。

```cpp
// 来源: Private/DataModelGenerators/DisplayClusterColorGradingGenerator_RootActor.h
// 假设你有一个自定义的根Actor子类，需要特殊的颜色分级处理。
class FMyCustomColorGradingGenerator : public FDisplayClusterColorGradingGenerator_ColorGradingRenderingSettings
{
public:
    static TSharedRef<IColorGradingEditorDataModelGenerator> MakeInstance()
    {
        return MakeShareable(new FMyCustomColorGradingGenerator());
    }

    //~ IColorGradingEditorDataModelGenerator interface
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FColorGradingEditorDataModel& OutColorGradingDataModel) override
    {
        // 1. 在PropertyRowGenerator中查找你的自定义属性句柄
        // 2. 使用基类提供的 CreateColorGradingGroup 或 CreateColorGradingElement 方法构建数据模型
        // 3. 将构建好的组添加到 OutColorGradingDataModel 中
    }
    // ... 其他虚函数实现
};

// 在某个合适的地方（如模块启动时）注册这个生成器
// 注册通常由DisplayClusterColorGrading模块内部管理，但你可以通过扩展接口添加。
```

## Demo 示例

一个最小的编辑器工具，展示如何触发 nDisplay 颜色分级抽屉的停靠操作。

**ColorGradingDrawerControlTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Toolkits/AssetEditorToolkit.h"

class FColorGradingDrawerControlTool : public FAssetEditorToolkit
{
public:
    void InitEditor(const TArray<UObject*>& InObjects);

    // 一个简单的按钮回调，用于打开颜色分级抽屉
    void OnOpenColorGradingDrawerClicked();

    // IToolkit interface
    virtual FName GetToolkitFName() const override;
    virtual FText GetBaseToolkitName() const override;
    virtual FLinearColor GetWorldCentricTabColorScale() const override;
    virtual FString GetWorldCentricTabPrefix() const override;
};
```

**ColorGradingDrawerControlTool.cpp**
```cpp
#include "ColorGradingDrawerControlTool.h"
#include "IDisplayClusterColorGrading.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/SBoxPanel.h"

void FColorGradingDrawerControlTool::InitEditor(const TArray<UObject*>& InObjects)
{
    // 创建一个简单的UI，包含一个按钮
    TSharedRef<SVerticalBox> Widget = SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("停靠 nDisplay 颜色分级面板")))
            .OnClicked_Lambda([this]()
            {
                OnOpenColorGradingDrawerClicked();
                return FReply::Handled();
            })
        ];
}

void FColorGradingDrawerControlTool::OnOpenColorGradingDrawerClicked()
{
    if (IDisplayClusterColorGrading::IsAvailable())
    {
        IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton().DockColorGradingDrawer();
    }
}

FName FColorGradingDrawerControlTool::GetToolkitFName() const
{
    return FName("ColorGradingDrawerControlTool");
}

// ... 其他虚函数实现
```

## 模块依赖

从 `DisplayClusterColorGrading.Build.cs` 分析。依赖了多个与编辑器UI和属性编辑相关的模块。

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | 用于与细节面板和属性行生成器交互，是颜色分级数据模型生成的基础。 |
| `DisplayClusterConfiguration` | 获取 nDisplay 配置数据，例如节点、视口信息，用于构建按视口分组的颜色分级选项。 |
| `DisplayClusterOperator` | 集成到 nDisplay 操作面板，这是颜色分级抽屉的主要宿主界面。 |
| `ColorGradingEditor` | UE 内置的颜色分级编辑器模块，`SColorGradingPanel` 等 UI 控件的来源。 |
| `EditorWidgets` | 提供一些通用的编辑器控件，如 `SInlineEditableTextBlock`，用于重命名颜色分级组。 |
| `WorkspaceMenuStructure` | 用于在编辑器工作区菜单中注册新标签页。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 增加 EXR 多图层支持，提升渲染输出灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 电影管线：将 WarpBlendAlpha 模式合并到 WarpBlend 中，简化配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名问题；修复 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复在输出帧编码回退时未遵循非默认 DisplayGamma 设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**综合评价：活跃维护中，核心企业级功能。**

1.  **创建时间与年龄**：创建于 2018 年，已有 8 年历史，是一个成熟的企业级功能。
2.  **更新频率**：**极其活跃**。提供的 git 历史显示，仅在 2026 年 5 月的最后一周内就有至少 5 次提交，修复 bug 并增加新功能（如 EXR 多图层支持）。
3.  **维护状态**：**持续维护**。Epic Games 仍在积极开发和修复 nDisplay，这从其密集的更新记录可以看出。
4.  **已知问题与限制**：
    *   系统复杂，学习曲线陡峭。
    *   需要专门的硬件（多台 PC、同步设备、投影仪等）才能发挥其作用。
    *   默认禁用 (`EnabledByDefault: false`)，需要用户手动在项目设置中启用。
5.  **推荐使用**：**强烈推荐**用于专业虚拟制作、沉浸式体验或任何需要多 PC 同步高分辨率渲染的项目。它是 Unreal Engine 在该领域的标准解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/)（UE 官方 nDisplay 文档）