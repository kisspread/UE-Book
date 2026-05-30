# Avalanche Level Viewport

> Compositing, designer and broadcasting tool.
Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计视口 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（视口相关资产、样式等） |
| 模块 | `AvalancheLevelViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

AvalancheLevelViewport 是 Motion Design 插件的核心视口模块，为虚拟制片中的运动设计、图形布局和广播图形制作提供了一个专用的2D编辑环境。它扩展了标准的 Unreal Engine 关卡视口，增加了针对运动设计的特有功能，如虚拟尺寸、安全框、网格、参考线、对齐工具、相机控制以及自定义的后处理显示模式。

该模块解决的核心问题是：在传统的3D关卡编辑器中，难以精确地进行2D图形布局和运动设计。它提供了一个类似 After Effects 或 DaVinci Resolve 的2D画布环境，同时保持与 Unreal Engine 场景的实时同步，让设计师可以直观地构建、排列和动画化 UI 元素、文本、形状和媒体内容。

## 使用场景

- 你正在为电视广播、现场活动或数字标牌创建动态图形模板 → 使用该视口进行2D布局和设计。
- 你需要精确地将UI元素对齐到屏幕网格或安全框内 → 使用该视口的网格、安全框和参考线功能。
- 你需要预览媒体合成效果，并控制相机的平移、缩放 → 使用该视口的相机控制和虚拟尺寸功能。
- 你需要将多个演员对齐或分布 → 使用该视口的状态栏中的演员对齐工具。

## 蓝图用法

此模块主要为编辑器扩展，提供的 UI 功能主要通过编辑器菜单和快捷键访问，未发现可供蓝图直接调用的 `BlueprintCallable` 函数。

## C++ 用法

### 头文件引入

```cpp
#include "AvaLevelViewportModule.h"
```

### 基本用法

访问和操作视口客户端。

```cpp
// 来源：Private/ViewportClient/AvaLevelViewportClient.h
#include "ViewportClient/AvaLevelViewportClient.h"

// 检查一个编辑器视口客户端是否是 Motion Design 视口
bool bIsAvaViewport = FAvaLevelViewportClient::IsAvaLevelViewportClient(MyEditorViewportClient);

// 获取 Motion Design 视口客户端的共享指针
TSharedPtr<FAvaLevelViewportClient> AvaClient = StaticCastSharedPtr<FAvaLevelViewportClient>(MyEditorViewportClient->AsSharedPtr());

// 获取视口的虚拟尺寸
FIntPoint VirtualSize = AvaClient->GetVirtualViewportSize();

// 获取视口的可见区域
FAvaVisibleArea VisibleArea = AvaClient->GetVisibleArea();
```

### 进阶用法

控制视口的网格、安全框和参考线显示。

```cpp
// 来源：Private/SAvaLevelViewport.h
#include "SAvaLevelViewport.h"

// 假设你拥有一个指向 SAvaLevelViewport 的指针
TSharedPtr<SAvaLevelViewport> AvaViewport = ...;

// 切换网格显示
if (AvaViewport->CanToggleGrid())
{
    AvaViewport->ExecuteToggleGrid();
}

// 切换安全框显示
if (AvaViewport->CanToggleSafeFrames())
{
    AvaViewport->ExecuteToggleSafeFrames();
}

// 添加一条垂直参考线
if (AvaViewport->CanAddVerticalGuide())
{
    AvaViewport->ExecuteAddVerticalGuide();
}
```

## Demo 示例

以下示例展示了如何创建一个自定义的编辑器模块，监听视口设置的变化。

```cpp
// MyViewportObserver.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyViewportObserverModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle OnSettingsChangedHandle;
};

// MyViewportObserver.cpp
#include "MyViewportObserver.h"
#include "AvaViewportSettings.h"

void FMyViewportObserverModule::StartupModule()
{
    // 监听 Motion Design 视口设置的变化
    OnSettingsChangedHandle = UAvaViewportSettings::OnSettingsChanged.AddLambda(
        [](const UAvaViewportSettings* Settings, FName PropertyName)
        {
            if (PropertyName == GET_MEMBER_NAME_CHECKED(UAvaViewportSettings, VirtualSize))
            {
                UE_LOG(LogTemp, Log, TEXT("Motion Design virtual size changed to: %s"), *Settings->VirtualSize.ToString());
            }
        });
}

void FMyViewportObserverModule::ShutdownModule()
{
    UAvaViewportSettings::OnSettingsChanged.Remove(OnSettingsChangedHandle);
}

IMPLEMENT_MODULE(FMyViewportObserverModule, MyViewportObserver)
```

## 模块依赖

此模块依赖于 Motion Design 插件的其他核心模块以及一些外部依赖。

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 插件的核心运行时模块 |
| `AvalancheEditorCore` | Motion Design 编辑器核心功能 |
| `AvalancheViewport` | 视口相关的核心类型和接口 |
| `AvalancheShapes` | 2D形状绘制支持 |
| `AvalancheText` | 文本渲染支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计的两个标签页（场景设置、大纲）移动到了关卡编辑器自己的分组中 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用节目单页面设置时，添加了电影渲染队列的分析数据 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用3D文本和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口代码，通过在客户端关联或解关联时发送通知来减少冗余代码 |

### 维护评价

Avalanche 插件（及其核心的 AvalancheLevelViewport 模块）是 Epic Games 用于虚拟制片和运动设计的 **前沿活跃项目**。

- **活跃维护**：从提交历史看，该插件在过去一周内有多次实质性功能更新和改进，表明它正处于非常活跃的开发阶段。
- **功能全面且不断进化**：模块提供了从基础视口操作（网格、参考线）到高级广播功能（节目单页面管理）的全套工具，且近期更新集中在增强广播控制和提升工作流效率上。
- **代码健康**：近期的提交包括代码重构（`cfb610df`），这表明开发团队在积极优化代码质量，而不仅仅是添加新功能。
- **推荐使用**：对于从事虚拟制片、动态图形、广播或任何需要2D精确布局工作的 Unreal Engine 用户，强烈推荐使用此模块。它是 Motion Design 工作流的基石。

**总体评价**：这是一个 **成熟且快速发展的核心功能模块**，是 Epic Games 官方支持的专业解决方案，可以放心用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)