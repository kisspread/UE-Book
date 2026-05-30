# nDisplay - DisplayClusterColorGrading

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 颜色分级模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterColorGrading` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterColorGrading) | |

## 用途

`DisplayClusterColorGrading` 模块是 nDisplay 集群渲染系统中的一个**编辑器扩展模块**。它并非运行时渲染的核心组件，而是为虚拟制片（Virtual Production）和大型 LED 墙项目提供专用的颜色分级（Color Grading）工作流。

其核心目标是解决在复杂多节点显示集群中，为每个独立的显示节点（Viewport）或 ICVFX（电影虚拟效果）相机定制化颜色校正的需求。传统的后处理颜色分级难以按屏幕/视口维度进行精细控制，而此模块通过生成一个交互式的数据模型（Data Model），将颜色分级属性（如色轮、偏移等）暴露给一个专门的 UI 面板（抽屉或标签页），让艺术家能够在 nDisplay 操作员面板中直观地为每个根演员（Root Actor）和 ICVFX 相机创建、编辑和管理独立的颜色分级组。这极大地提升了在实时渲染环境下对集群输出进行艺术化调色的效率和控制力。

## 使用场景

- 你在使用 nDisplay 搭建大型 LED 墙进行虚拟制片，需要为不同的物理显示面板（对应不同的 nDisplay 视口）独立调整亮度、色调和饱和度。
- 你正在制作一个包含多个 ICVFX 相机的复杂拍摄场景，每个相机的输出需要不同的色彩风格，你需要在操作员面板中快速切换和调整这些风格。
- 你希望将颜色分级设置与特定的显示节点或相机组件绑定，并能够方便地创建预设和复制设置。

## 蓝图用法

本模块主要提供编辑器扩展功能，其核心逻辑通过 C++ 类实现，并未暴露大量 `BlueprintCallable` 节点。其主要交互界面是 nDisplay 操作员面板中集成的“颜色分级抽屉（Color Grading Drawer）”。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DockColorGradingDrawer` | 在 nDisplay 操作员窗口中固定（停靠）颜色分级面板 | `FDisplayClusterColorGradingDrawerSingleton` |
| `RefreshColorGradingDrawers` | 刷新所有已打开的颜色分级抽屉的 UI，使其与当前场景状态同步 | `FDisplayClusterColorGradingDrawerSingleton` |

**获取单例**：通过 `IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton()` 访问上述功能。

### 使用示例（蓝图描述）

由于此功能深度集成于编辑器操作面板，直接蓝图调用较少。主要的用户交互发生在编辑器中：
1.  在关卡编辑器中选择一个 `ADisplayClusterRootActor`。
2.  通过 nDisplay 操作员面板的工具栏或右下角状态栏，打开“颜色分级”抽屉。
3.  在抽屉中，你可以为该根演员创建新的颜色分级组，通过下拉菜单将组分配给特定的视口或节点。
4.  使用色轮和参数滑块调整该组的颜色分级设置，更改会实时反映在对应的显示输出上。
5.  可以将抽屉固定为操作员面板的一个标签页，以便长期使用。

## C++ 用法

本模块的 API 主要供 nDisplay 自身的其他编辑器模块（如 `DisplayClusterOperator`）内部使用，用于扩展操作员面板。普通开发者通常不直接调用，而是通过上述编辑器 UI 使用。以下为概念性用法。

### 头文件引入

```cpp
#include "IDisplayClusterColorGrading.h"
#include "IDisplayClusterColorGradingDrawerSingleton.h"
```

### 基本用法

访问颜色分级抽屉管理单例。
```cpp
// 检查模块是否可用
if (IDisplayClusterColorGrading::IsAvailable())
{
    // 获取抽屉管理单例
    IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton();

    // 以编程方式将颜色分级抽屉固定到操作员面板
    DrawerSingleton.DockColorGradingDrawer();
}
```

### 进阶用法

该模块更复杂的用法体现在其内部实现的颜色分级数据模型生成器（`IColorGradingEditorDataModelGenerator`）。这些生成器负责将 `ADisplayClusterRootActor` 和 `UDisplayClusterICVFXCameraComponent` 的属性转换为 UI 可交互的数据模型。以下为概念性代码，展示如何为一个根演员创建数据模型生成器：

```cpp
#include "DataModelGenerators/DisplayClusterColorGradingGenerator_RootActor.h"

// 创建一个针对根演员的颜色分级数据模型生成器实例
TSharedRef<IColorGradingEditorDataModelGenerator> RootActorGenerator = FDisplayClusterColorGradingGenerator_RootActor::MakeInstance();

// 假设已有 PropertyRowGenerator 和 ColorGradingDataModel (由编辑器框架提供)
// 初始化生成器，绑定到属性行生成器和数据模型
RootActorGenerator->Initialize(ColorGradingDataModel, PropertyRowGenerator);

// 当选择的根演员变化时，调用此方法重新生成数据模型
RootActorGenerator->GenerateDataModel(*PropertyRowGenerator, *ColorGradingDataModel);

// 不再使用时销毁
RootActorGenerator->Destroy(ColorGradingDataModel, PropertyRowGenerator);
```

## Demo 示例

本模块作为编辑器扩展，不提供独立的运行时演示。其“演示”即为在编辑器中使用 nDisplay 操作员面板中的颜色分级功能。以下是一个最小化的 C++ 模块接口使用示例，展示了如何检查和获取此模块。

**DisplayClusterColorGradingMinimalDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FDisplayClusterColorGradingMinimalDemo
{
public:
    static void DemoAccess();
};
```

**DisplayClusterColorGradingMinimalDemo.cpp**
```cpp
#include "DisplayClusterColorGradingMinimalDemo.h"

#include "IDisplayClusterColorGrading.h"
#include "IDisplayClusterColorGradingDrawerSingleton.h"
#include "Modules/ModuleManager.h"

void FDisplayClusterColorGradingMinimalDemo::DemoAccess()
{
    // 确保 nDisplay 主模块已加载
    if (FModuleManager::Get().IsModuleLoaded("DisplayCluster"))
    {
        // 检查颜色分级模块是否可用（通常随 nDisplay 一起加载）
        if (IDisplayClusterColorGrading::IsAvailable())
        {
            UE_LOG(LogTemp, Log, TEXT("DisplayClusterColorGrading module is available."));

            // 获取并调用管理单例的方法
            IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton();
            UE_LOG(LogTemp, Log, TEXT("Successfully obtained the Color Grading Drawer Singleton."));

            // 注意：直接调用 DockColorGradingDrawer 需要操作员面板上下文，在此独立示例中可能无法正常工作
            // DrawerSingleton.DockColorGradingDrawer();
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("DisplayClusterColorGrading module is not loaded."));
        }
    }
}
```

## 模块依赖

该模块的 `Build.cs` 文件未在提供信息中完整列出，但根据其功能和文件分析，它依赖于 nDisplay 的核心模块及一些编辑器模块。以下是其主要的独特依赖：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供根演员、节点等基础类 |
| `DisplayClusterOperator` | nDisplay 操作员面板模块，颜色分级抽屉需要集成其中 |
| `Slate`, `SlateCore`, `EditorWidgets` | 用于构建用户界面 |
| `PropertyEditor`, `UnrealEd` | 用于属性行生成器、细节面板和编辑器集成 |

（注：标准依赖如 `Core`, `CoreUObject`, `Engine` 等已省略）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay 支持多图层 EXR 文件输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了电影渲染管线中的一种 Alpha 混合模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了相机命名和着色器中的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码时未尊重非默认显示伽马值的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理小于视口尺寸时可能出现的闪烁问题 |

### 维护评价

**活跃维护中**。`DisplayClusterColorGrading` 作为 nDisplay 这一大型商业级插件的组成部分，与 nDisplay 核心共同维护。从最近的提交记录看，nDisplay 在 2026 年 5 月仍有密集的功能更新和 bug 修复，表明 Epic Games 仍在积极维护此插件，主要用于支持其虚拟制片解决方案。

该模块创建时间较早（2018年），但作为 nDisplay 功能迭代的一部分，它也在持续演进。鉴于其服务于虚拟制片这一核心业务场景，且最近更新频繁，推荐在需要 nDisplay 颜色分级功能的项目中使用。需要注意的是，此插件默认**未启用**，需要在项目中手动激活。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterColorGrading)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) （位于 nDisplay 主测试模块中）