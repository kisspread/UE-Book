# DisplayClusterColorGrading

> 支持使用多台 PC 在单眼或立体模式下进行同步的集群渲染

| 属性 | 值 |
|---|---|
| 中文名 | 颜色分级模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterColorGrading` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterColorGrading` 是 nDisplay 集群渲染插件中的一个核心编辑器/运行时模块。它解决的主要问题是：**在虚拟制作（如 LED 墙拍摄）和多通道渲染等场景中，为艺术家和操作员提供一个统一的、直观的颜色分级界面，以管理集群中所有渲染节点（PC）的颜色校正设置。**

在传统的单一工作站工作流中，调色通常在一个应用窗口内完成。但在 nDisplay 集群渲染中，一个完整的画面被切分并分布在多台机器的多个显示器或投影仪上输出。此模块的作用是抽象底层的复杂性，提供一个单一的 UI（颜色分级面板），允许用户同时控制集群中多个视口（Viewports）或节点（Nodes）的全局颜色设置，确保所有输出在颜色上保持一致和艺术可控。它特别针对 `ADisplayClusterRootActor` 和 `UDisplayClusterICVFXCameraComponent` 等 nDisplay 核心资产设计了数据模型生成器。

## 使用场景

- 你正在使用 nDisplay 设置一个由多台 PC 驱动的大型 LED 墙进行虚拟拍摄 → 需要使用此模块为整个 LED 墙的各个部分进行统一的颜色分级。
- 你的项目需要将一个场景渲染到多个显示器（例如环幕、CAVE）上，且需要在编辑器中精确控制每个显示器的输出色调、饱和度等。
- 你作为虚拟制作的技术美术或现场操作员，需要在 nDisplay Operator 面板内快速调整整个集群渲染效果的颜色外观。
- 你正在开发基于 nDisplay 的多通道渲染流程，并需要集成专业的颜色校正工具链。

## 蓝图用法

此模块主要提供编辑器 UI 和运行时数据模型管理，其公开的蓝图接口相对有限，主要用于模块访问和面板控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 `DisplayClusterColorGrading` 模块的单例接口。在模块可用后调用。 | `IDisplayClusterColorGrading` |
| `IsAvailable` | 检查颜色分级模块是否已加载并准备就绪。 | `IDisplayClusterColorGrading` |
| `GetColorGradingDrawerSingleton` | 获取用于管理颜色分级抽屉面板的单例对象。 | `IDisplayClusterColorGrading` |
| `DockColorGradingDrawer` | 将颜色分级面板永久停靠到 nDisplay Operator 窗口的标签页中。 | `IDisplayClusterColorGradingDrawerSingleton` |
| `RefreshColorGradingDrawers` | 强制刷新所有已打开的颜色分级面板的 UI，以匹配当前关卡和激活的根 Actor 状态。 | `IDisplayClusterColorGradingDrawerSingleton` |

### 使用示例（蓝图描述）

在自定义的编辑器工具蓝图或编辑器 Utility Widget 中，你可以按以下逻辑使用：
1. 首先，调用 `IDisplayClusterColorGrading::IsAvailable()` 确认模块已加载。
2. 如果可用，调用 `IDisplayClusterColorGrading::Get()` 获取模块实例。
3. 通过实例调用 `GetColorGradingDrawerSingleton()` 获取面板管理器。
4. 使用管理器的 `DockColorGradingDrawer()` 或 `RefreshColorGradingDrawers()` 来控制颜色分级面板的显示和更新。

## C++ 用法

该模块的 C++ 接口主要用于与 nDisplay 编辑器框架深度集成，自定义颜色分级数据源或扩展面板功能。

### 头文件引入

```cpp
#include "IDisplayClusterColorGrading.h"
#include "IDisplayClusterColorGradingDrawerSingleton.h"
```

### 基本用法

获取模块单例并访问其管理的对象。
```cpp
// 检查模块是否就绪
if (IDisplayClusterColorGrading::IsAvailable())
{
    // 获取模块接口
    IDisplayClusterColorGrading& ColorGradingModule = IDisplayClusterColorGrading::Get();
    
    // 获取颜色分级面板管理器
    IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = ColorGradingModule.GetColorGradingDrawerSingleton();
    
    // 刷新面板以反映最新的关卡数据变化
    DrawerSingleton.RefreshColorGradingDrawers();
}
```

### 进阶用法：自定义颜色分级数据模型生成器

你可以通过继承 `IColorGradingEditorDataModelGenerator` 接口并使用模块提供的基类，为自定义的 nDisplay 相关组件创建颜色分级数据源。这允许你将自己的组件属性暴露到标准的颜色分级面板中。

```cpp
// 假设你有一个自定义的摄像机后处理组件 UMyPostProcessComponent
// 1. 创建一个数据模型生成器类
class FMyComponentColorGradingGenerator : public FDisplayClusterColorGradingGenerator_ColorGradingRenderingSettings
{
public:
    static TSharedRef<IColorGradingEditorDataModelGenerator> MakeInstance();
    
    virtual void Initialize(const TSharedRef<FColorGradingEditorDataModel>& InDataModel, const TSharedRef<IPropertyRowGenerator>& InPropertyRowGenerator) override;
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FColorGradingEditorDataModel& OutDataModel) override;

    // ... 实现其他必要的虚函数
    // 使用基类提供的辅助函数如 CreateColorGradingGroup, FindPropertyHandle 等来构建数据模型
};

// 2. 在某个编辑器初始化点（如模块的 StartupModule 中）注册你的生成器
// 需要查找 nDisplay 颜色分级系统注册自定义生成器的具体接口或流程。
```

## Demo 示例

一个最小化的、演示如何与 `DisplayClusterColorGrading` 模块交互的 C++ 类示例。

**MyColorGradingHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyColorGradingHelper
{
public:
    // 刷新颜色分级面板
    static void RefreshColorGradingPanel();
    
    // 将颜色分级面板停靠到Operator窗口
    static void DockColorGradingPanel();
};
```

**MyColorGradingHelper.cpp**
```cpp
#include "MyColorGradingHelper.h"
#include "IDisplayClusterColorGrading.h"
#include "IDisplayClusterColorGradingDrawerSingleton.h"

void FMyColorGradingHelper::RefreshColorGradingPanel()
{
    if (IDisplayClusterColorGrading::IsAvailable())
    {
        IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton().RefreshColorGradingDrawers();
    }
}

void FMyColorGradingHelper::DockColorGradingPanel()
{
    if (IDisplayClusterColorGrading::IsAvailable())
    {
        IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton().DockColorGradingDrawer();
    }
}
```

## 模块依赖

此模块为 `DisplayClusterColorGrading` (Runtime)，但它深度集成于编辑器。其构建依赖中包含了多个编辑器相关模块，用于创建 UI 和与编辑器选择系统交互。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 访问编辑器核心功能，如属性行生成器 (`IPropertyRowGenerator`)、细节面板节点等。 |
| `EditorWidgets` | 提供编辑器通用的 UI 控件。 |
| `LevelEditor` | 与关卡编辑器集成，监听选择变化等事件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加了 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 MoviePipeline 中的 WarpBlendAlpha 模式到 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知的摄像机命名问题，以及 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码的回退路径中遵守非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

该模块属于 **活跃维护** 状态。
- **年龄**：创建于 2018 年，已有 8 年历史，是 nDisplay 功能集的成熟组成部分。
- **近期更新**：最近的提交（2026年5月）集中在功能增强（如 EXR 多层）、渲染管线优化（WarpBlend 模式合并）和关键 bug 修复（如着色器、闪烁问题）。这些更新表明模块仍在积极开发，以支持更复杂的虚拟制作流程（如 MovieGraph）。
- **是否活跃**：非常活跃。更新频繁且与当前的虚拟制作技术演进同步。
- **已知限制**：作为复杂的集群渲染工具链的一部分，其使用和调试需要一定的 nDisplay 配置知识。模块本身不直接暴露高级蓝图 API，更侧重于提供编辑器内工具。
- **推荐使用**：**强烈推荐**。对于任何涉及 nDisplay 多机渲染和专业调色的项目，此模块是必不可少的核心工具。它由 Epic Games 直接维护，与引擎其他部分的集成度高，稳定性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：无（.uplugin 中 DocsURL 为空）