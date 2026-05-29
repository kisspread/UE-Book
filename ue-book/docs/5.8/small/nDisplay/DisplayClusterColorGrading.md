# Display Cluster Color Grading

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 色彩分级 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterColorGrading` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterColorGrading` 模块是 nDisplay 集群渲染插件的一个子模块，它**为虚拟制作中的 nDisplay 集群渲染系统提供了一个集成的、上下文感知的色彩分级工作流**。

该模块解决的核心问题是：在由多台 PC 驱动多个显示器（如 LED 墙、多通道投影）的复杂虚拟制作场景中，艺术家需要**针对整个显示集群或特定显示节点（Node）** 进行精细的颜色校正（Color Grading）。该模块通过将色彩分级面板集成到 nDisplay 的 Operator 面板中，并与场景中的 `ADisplayClusterRootActor` 和 `UDisplayClusterICVFXCameraComponent`（ICVFX 摄像机组件）深度绑定，实现了这种专业化的色彩管理能力。

## 使用场景

- **虚拟制作/LED 墙拍摄**：在 LED 墙（Volume）拍摄现场，摄影师和调色师需要实时调整整个墙壁不同区域的色温、曝光和颜色，以确保前景演员与 LED 墙背景的无缝融合。此模块允许他们针对整个 nDisplay 集群或特定面板（Panel）进行独立的颜色校正。
- **多通道投影/环幕/穹顶投影安装**：在博物馆、主题公园或沉浸式体验环境中，多个投影仪拼接成一个完整的画面。此模块允许维护人员校准并匹配各个投影仪之间的颜色和亮度，消除视觉上的拼接痕迹。
- **复杂的 ICVFX 工作流**：当使用 nDisplay 控制多个摄像机视角或进行视差校正时，可能需要对特定的 ICVFX 摄像机组件进行独立的颜色分级，以匹配主摄像机的视觉风格。

## 蓝图用法

该模块主要提供编辑器 UI 和内部数据模型，公开的蓝图 API 较少，主要集中在模块接口的访问上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` (静态函数) | 获取 `IDisplayClusterColorGrading` 模块接口的单例实例。 | `IDisplayClusterColorGrading` |
| `GetColorGradingDrawerSingleton` | 获取管理色彩分级抽屉（Drawer）UI 的单例对象。 | `IDisplayClusterColorGrading` |
| `DockColorGradingDrawer` | 将色彩分级面板停靠到 nDisplay Operator 窗口中。 | `IDisplayClusterColorGradingDrawerSingleton` |
| `RefreshColorGradingDrawers` | 刷新所有已打开的色彩分级面板的 UI。 | `IDisplayClusterColorGradingDrawerSingleton` |

### 使用示例（蓝图描述）

1.  打开 nDisplay 的 **Operator 面板**。
2.  在 Operator 面板的状态栏或布局扩展中，点击色彩分级图标或按钮，这会调用 `DockColorGradingDrawer`。
3.  色彩分级面板将出现，显示当前 `ADisplayClusterRootActor` 的色彩分级设置。
4.  艺术家可以直接在面板上调整颜色轮（Color Wheels）和细节参数，这些调整会自动应用到对应的 nDisplay 集群渲染节点上。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterColorGrading.h" // 模块接口
```

### 基本用法

通过模块接口访问色彩分级功能。

```cpp
// 检查模块是否可用
if (IDisplayClusterColorGrading::IsAvailable())
{
    // 获取模块接口
    IDisplayClusterColorGrading& ColorGradingModule = IDisplayClusterColorGrading::Get();

    // 获取管理 UI 的单例
    IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = ColorGradingModule.GetColorGradingDrawerSingleton();

    // 将色彩分级面板停靠到 Operator 窗口
    DrawerSingleton.DockColorGradingDrawer();

    // 在场景或配置更新后，刷新 UI
    DrawerSingleton.RefreshColorGradingDrawers();
}
```

### 进阶用法

该模块的核心复杂性在于其内部数据模型（`FDisplayClusterColorGradingDataModel`）和生成器（`IColorGradingEditorDataModelGenerator`）的设计。以下示例展示了如何为自定义类型创建一个色彩分级数据模型生成器。

```cpp
// 假设你有一个自定义组件，它包含 FColorGradingRenderingSettings 成员。
// 你可以创建一个生成器，将这个结构体暴露给色彩分级 UI。
class FMyCustomComponentColorGradingGenerator : public FDisplayClusterColorGradingGenerator_ColorGradingRenderingSettings
{
public:
    // IColorGradingEditorDataModelGenerator 接口实现
    virtual void Initialize(...) override { /* 初始化逻辑 */ }
    virtual void Destroy(...) override { /* 清理逻辑 */ }
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FColorGradingEditorDataModel& OutColorGradingDataModel) override
    {
        // 1. 使用 PropertyRowGenerator 从你的自定义对象中获取属性句柄。
        // 2. 调用基类的 CreateColorGradingGroup 或 CreateColorGradingElement 方法，
        //    传入你的 FColorGradingRenderingSettings 属性句柄。
        // 3. 将创建好的组和元素添加到 OutColorGradingDataModel 中。
    }
};

// 然后，你需要注册这个生成器，以便在编辑器中选择你的自定义组件时，色彩分级面板能正确显示。
// 这通常在模块的 StartupModule 中或通过编辑器扩展点完成。
```

**注意**：这种进阶用法通常用于扩展 nDisplay 的色彩分级能力，以支持自定义组件。大部分开发者通过现有的 `FDisplayClusterColorGradingGenerator_RootActor` 和 `FDisplayClusterColorGradingGenerator_ICVFXCamera` 来使用功能。

## Demo 示例

以下是一个最小示例，演示如何在游戏模块中访问并使用色彩分级模块来打开抽屉。

```cpp
// MyGameModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void OpenColorGradingPanel();
};

// MyGameModule.cpp
#include "MyGameModule.h"
#include "DisplayClusterColorGrading.h"

void FMyGameModule::StartupModule()
{
}

void FMyGameModule::ShutdownModule()
{
}

void FMyGameModule::OpenColorGradingPanel()
{
    // 确保 nDisplay 和色彩分级模块已加载
    if (IDisplayClusterColorGrading::IsAvailable())
    {
        IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton().DockColorGradingDrawer();
        UE_LOG(LogTemp, Log, TEXT("Requested to dock the nDisplay color grading panel."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterColorGrading module is not available."));
    }
}
```

## 模块依赖

该模块的依赖项主要来自 nDisplay 核心模块和编辑器框架。由于这些依赖在 nDisplay 插件内部已解决，对于**直接使用此模块**的外部项目，其构建依赖（Build.cs）是自包含的。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该模块作为 nDisplay 的子模块，其依赖（如 `DisplayCluster`）在插件内部处理。 |

## 维护状态

该模块作为 nDisplay 这个大型企业级插件的一部分，**仍在 Epic Games 的活跃维护之下**。最近的提交主要集中在功能完善、性能优化和 Bug 修复。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 管线添加了多层 EXR 输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在 nDisplay 的 Movie Pipeline 中合并了两种混合模式，简化工作流。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多渲染图（MRG）中的相机命名和着色器中的不透明度 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 确保在输出帧编码回退时，尊重非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能发生的闪烁问题。 |

### 维护评价

- **维护活跃**：从近期的提交记录可以看出，该模块（及整个 nDisplay 插件）在 **2026 年内持续有功能更新和错误修复**，表明其仍处于**活跃维护**状态。
- **企业级功能**：这是 Epic Games 为虚拟制作和专业可视化领域提供的核心工具链之一，其稳定性和功能性得到持续投资。
- **推荐使用**：对于需要使用多 PC 集群进行同步渲染的专业项目（如虚拟制片、大型可视化、模拟训练等），**强烈推荐使用**。但对于简单的单 PC 项目则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)