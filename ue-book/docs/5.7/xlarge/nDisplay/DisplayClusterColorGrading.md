# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterColorGrading` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterColorGrading` 模块是 nDisplay 虚拟制作系统的一部分，专门用于管理颜色分级（Color Grading）功能的用户界面和状态。它解决的核心问题是：在由多台 PC 和多个屏幕组成的 nDisplay 集群渲染环境中，如何为操作员提供一个统一、持久的颜色分级调整界面。该模块通过一个单例（Singleton）模式管理“颜色分级抽屉”（Color Grading Drawer）的生命周期和状态，确保在 nDisplay 操作员窗口中能够便捷地停靠和刷新颜色分级控件，从而实现对整个虚拟场景颜色分级的集中、同步控制。

## 使用场景

- **虚拟制作现场**：在 LED 墙或投影幕组成的虚拟拍摄现场，导演或技术美术需要实时调整整个场景或特定区域的颜色分级（如白平衡、色调映射、LUT 等），以匹配实拍素材或达到特定的艺术效果。
- **多屏幕同步调色**：当使用 nDisplay 驱动多个显示器或投影仪时，确保所有屏幕的颜色表现一致，操作员需要在一个中央控制界面进行调整，而不是逐个屏幕设置。
- **实时预览与调整**：在内容创作或现场直播中，需要快速预览颜色分级效果，并能即时应用到所有渲染节点。

## 蓝图用法

该模块主要提供 C++ 接口，用于管理编辑器内的 UI 控件。在头文件中未发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记，因此**不直接暴露蓝图节点**。其功能通常通过 nDisplay 的操作员窗口（Operator Window）或编辑器工具栏按钮间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterColorGrading.h"
```

### 基本用法

获取模块实例并访问颜色分级抽屉单例，以控制其 UI 状态。

```cpp
// 检查模块是否可用
if (IDisplayClusterColorGrading::IsAvailable())
{
    // 获取模块引用
    IDisplayClusterColorGrading& ColorGradingModule = IDisplayClusterColorGrading::Get();

    // 获取颜色分级抽屉单例
    IDisplayClusterColorGradingDrawerSingleton& DrawerSingleton = ColorGradingModule.GetColorGradingDrawerSingleton();

    // 将颜色分级抽屉停靠到 nDisplay 操作员窗口
    DrawerSingleton.DockColorGradingDrawer();

    // 当颜色分级设置发生变化后，刷新所有已打开的抽屉 UI
    DrawerSingleton.RefreshColorGradingDrawers();
}
```
*来源: `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterColorGrading/Public/IDisplayClusterColorGrading.h`*

### 进阶用法

通常，`DisplayClusterColorGrading` 模块会与 nDisplay 的其他核心模块（如 `DisplayCluster`、`DisplayClusterOperator`）协同工作。例如，在 nDisplay 操作员窗口的初始化流程中，可能会调用 `DockColorGradingDrawer` 来集成颜色分级面板。当通过其他系统（如 Remote Control）修改了颜色分级参数后，需要调用 `RefreshColorGradingDrawers` 来确保 UI 反映最新的设置。

## Demo 示例

以下是一个最小化的示例，展示如何在你的编辑器工具或模块中集成 nDisplay 的颜色分级抽屉。

**1. 头文件 (`MyColorGradingTool.h`)**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyColorGradingTool
{
public:
    void Initialize();
    void OnColorSettingsChanged();

private:
    // 用于缓存单例引用，避免重复查找
    IDisplayClusterColorGradingDrawerSingleton* CachedDrawerSingleton = nullptr;
};
```

**2. 实现文件 (`MyColorGradingTool.cpp`)**
```cpp
#include "MyColorGradingTool.h"
#include "IDisplayClusterColorGrading.h"

void FMyColorGradingTool::Initialize()
{
    if (IDisplayClusterColorGrading::IsAvailable())
    {
        CachedDrawerSingleton = &IDisplayClusterColorGrading::Get().GetColorGradingDrawerSingleton();
        // 在工具初始化时，尝试停靠颜色分级抽屉
        if (CachedDrawerSingleton)
        {
            CachedDrawerSingleton->DockColorGradingDrawer();
        }
    }
}

void FMyColorGradingTool::OnColorSettingsChanged()
{
    // 当你的工具修改了颜色分级设置后，通知 nDisplay 刷新 UI
    if (CachedDrawerSingleton)
    {
        CachedDrawerSingleton->RefreshColorGradingDrawers();
    }
}
```

**3. 模块依赖 (`YourModule.Build.cs`)**
```csharp
using UnrealBuildTool;

public class YourModule : ModuleRules
{
    public YourModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "DisplayClusterColorGrading" // 依赖颜色分级模块
        });
    }
}
```

## 模块依赖

从 `DisplayClusterColorGrading.Build.cs` 分析，该模块依赖以下 nDisplay 内部模块：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供集群渲染的基础框架和 API。 |
| `DisplayClusterOperator` | nDisplay 操作员窗口模块，颜色分级抽屉需要停靠在此窗口中。 |

## 维护状态

### 近期更新

1.  **`a2772a31b52f`** (2024-05-21): `nDisplay: Fixed issue where color grading and white balance settings would reset to zero instead of desirable default values when the color grading or white balace structs were elements of an array.`
    *   **解读**: 修复了一个关键 bug，该 bug 会导致当颜色分级或白平衡结构体是数组元素时，设置会被重置为零而非期望的默认值。这表明该模块仍在积极维护和修复实际使用中的问题。

2.  **`a86e9f4e0f3f`** (2024-05-14): `[nDisplay] [Virtual Production] DLSS plugin integration for nDisplay.`
    *   **解读**: 集成了 NVIDIA DLSS 插件。虽然此提交主要针对 nDisplay 整体，但颜色分级作为画面后处理的一部分，其工作流可能间接受益于 DLSS 带来的性能提升和画质选项。

3.  **`67cb360f496b`** (2024-05-14): `[nDisplay] [Virtual Production] Added global upscaler settings for Outer viewports and Inner Frustum.`
    *   **解读**: 添加了全局升频器设置。这扩展了 nDisplay 的渲染管线配置，颜色分级模块需要确保其 UI 能正确反映或适配这些新的全局设置。

### 维护评价

- **活跃维护**: 该模块在最近 3 个月内有实质性更新，包括 bug 修复和功能集成，表明它仍在 Epic Games 的活跃维护范围内。
- **功能稳定**: 作为 nDisplay 虚拟制作工作流中的一个 UI 组件，其核心功能（停靠、刷新抽屉）相对稳定，近期的更新主要集中在修复边缘情况和集成新特性。
- **推荐使用**: 对于需要在 nDisplay 环境中进行颜色分级的项目，**推荐使用**此模块。它提供了标准化的集成方式，避免了自行开发 UI 集成逻辑的复杂性。但需注意，该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterColorGrading)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (nDisplay 整体测试)