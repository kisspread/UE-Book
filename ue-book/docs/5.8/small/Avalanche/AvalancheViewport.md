# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 插件为 UE5 提供了完整的动态图形（Motion Graphics）创作环境。它从实验性插件迁移而来，整合了演员修改器、克隆器/效果器、材质设计器、几何遮罩等工具。`AvalancheViewport` 模块是其核心，为动态设计专用视口提供增强功能，包括：

1.  **专用的 2D/3D 视口操作**：支持平移、缩放（类似于 2D 软件）、虚拟尺寸和相机绑定。
2.  **精确的视觉辅助工具**：提供屏幕网格、像素网格、安全框、参考线（Guides）和贴靠（Snapping）系统。
3.  **实时后处理可视化**：支持在视口内叠加背景、棋盘格、RGB 通道分离等效果。
4.  **场景对齐与分布**：提供强大的屏幕空间对齐、分布和尺寸调整工具。

它解决了在 UE5 中高效创建广播级图形、UI 动画和虚拟制片内容的需求，将传统图形软件的工作流（如 After Effects）带入 3D 引擎。

## 使用场景

*   **广播与虚拟制片**：为电视节目、新闻包装、电竞直播创建实时的、数据驱动的 2D/3D 图形元素。
*   **UI/UX 动画制作**：设计和动画化复杂的游戏或应用界面。
*   **舞台视觉设计**：为演唱会、展览设计动态视觉效果。
*   **需要精确布局的场景**：任何需要元素相对于屏幕、相机或其他元素精确对齐和分布的 3D 场景。

## 蓝图用法

该插件的核心功能主要通过 C++ API 提供，但提供了通过 `UAvaViewportSettings` 类访问和修改视口设置的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Snap State` | 获取当前视口的贴靠状态位掩码 | `UAvaViewportSettings` |
| `Has Snap State` | 检查是否启用了特定的贴靠模式 | `UAvaViewportSettings` |
| `Set Snap State` | 设置视口的贴靠状态 | `UAvaViewportSettings` |

### 使用示例（蓝图描述）

1.  **配置视口设置**：在项目设置中找到 “Motion Design - Viewport”，可以设置网格、安全框、贴靠、参考线等。
2.  **在运行时调整贴靠**：通过蓝图获取 `UAvaViewportSettings` 的实例，然后使用 `Set Snap State` 节点，结合 `EAvaViewportSnapState` 枚举（如 `Screen`, `Grid`, `Actor`）的位掩码，动态启用或禁用贴靠功能。

## C++ 用法

### 头文件引入

```cpp
#include "AvaViewportSettings.h"
#include "AvaScreenAlignmentUtils.h"
#include "IAvaViewportClient.h"
```

### 基本用法

**获取和修改视口设置**（来源：`Public/AvaViewportSettings.h`）

```cpp
// 获取视口设置单例
UAvaViewportSettings* ViewportSettings = GetMutableDefault<UAvaViewportSettings>();
if (ViewportSettings)
{
    // 启用网格
    ViewportSettings->bGridEnabled = true;
    // 设置网格颜色
    ViewportSettings->GridColor = FLinearColor::Green;
    // 启用并设置贴靠模式
    ViewportSettings->SetSnapState(EAvaViewportSnapState::Screen | EAvaViewportSnapState::Grid);
    // 保存更改
    ViewportSettings->TryUpdateDefaultConfigFile();
}
```

**使用屏幕对齐工具**（来源：`Public/AvaScreenAlignmentUtils.h`）

```cpp
// 假设你有一个 IAvaViewportWorldCoordinateConverter 的共享指针（通常来自当前视口）
TSharedRef<IAvaViewportWorldCoordinateConverter> CoordinateConverter = ...; 
TArray<AActor*> ActorsToAlign = {Actor1, Actor2, Actor3};

// 将选中的演员水平居中对齐
FAvaScreenAlignmentUtils::AlignActorsHorizontal(
    CoordinateConverter,
    ActorsToAlign,
    EAvaHorizontalAlignment::Center,
    EAvaAlignmentSizeMode::Self,
    EAvaAlignmentContext::SelectedActors
);
```

### 进阶用法

**执行自定义贴靠操作**（来源：`Public/Interaction/AvaSnapOperation.h`）

```cpp
// 假设你正在处理一个拖拽操作，并且有一个有效的 IAvaViewportClient
TSharedPtr<IAvaViewportClient> AvaViewportClient = ...;
TSharedPtr<FAvaSnapOperation> SnapOp = AvaViewportClient->StartSnapOperation();
if (SnapOp.IsValid())
{
    // 生成屏幕和参考线的贴靠点
    SnapOp->GenerateScreenSnapPoints();
    // 为正在拖拽的演员生成贴靠点（排除自身）
    TArray<TWeakObjectPtr<AActor>> SelectedActors = {DraggedActor};
    TArray<TWeakObjectPtr<AActor>> ExcludedActors;
    SnapOp->GenerateActorSnapPoints(SelectedActors, ExcludedActors);
    // 最终化贴靠点（排序）
    SnapOp->FinaliseSnapPoints();

    // 在拖拽更新时，尝试将位置对齐到最近的贴靠点
    FVector2f CurrentMousePosition = ...; // 从视口获取
    SnapOp->SnapScreenLocation(CurrentMousePosition);

    if (SnapOp->WasSnappedTo())
    {
        // 应用贴靠后的位置
        FVector2f SnappedLocation = SnapOp->GetSnappedToLocation();
        // ... 更新演员位置 ...
    }

    // 操作结束后，结束贴靠
    AvaViewportClient->EndSnapOperation(SnapOp.Get());
}
```

## Demo 示例

以下是一个在 C++ 中监听并响应视口设置变化的简单示例。

```cpp
// MyViewportObserver.h
#pragma once
#include "CoreMinimal.h"
#include "AvaViewportSettings.h"

class FMyViewportObserver
{
public:
    void StartObserving();
    void StopObserving();

private:
    void OnViewportSettingsChanged(const UAvaViewportSettings* Settings, FName SettingName);
    FDelegateHandle SettingsChangedHandle;
};
```

```cpp
// MyViewportObserver.cpp
#include "MyViewportObserver.h"

void FMyViewportObserver::StartObserving()
{
    if (UAvaViewportSettings* Settings = GetMutableDefault<UAvaViewportSettings>())
    {
        SettingsChangedHandle = Settings->OnChange.AddRaw(this, &FMyViewportObserver::OnViewportSettingsChanged);
    }
}

void FMyViewportObserver::StopObserving()
{
    if (UAvaViewportSettings* Settings = GetMutableDefault<UAvaViewportSettings>())
    {
        Settings->OnChange.Remove(SettingsChangedHandle);
        SettingsChangedHandle.Reset();
    }
}

void FMyViewportObserver::OnViewportSettingsChanged(const UAvaViewportSettings* Settings, FName SettingName)
{
    // 监听特定设置的变化
    if (SettingName == GET_MEMBER_NAME_CHECKED(UAvaViewportSettings, bGridEnabled))
    {
        UE_LOG(LogTemp, Log, TEXT("视口网格已 %s"), Settings->bGridEnabled ? TEXT("启用") : TEXT("禁用"));
    }
    else if (SettingName == GET_MEMBER_NAME_CHECKED(UAvaViewportSettings, SnapState))
    {
        UE_LOG(LogTemp, Log, TEXT("视口贴靠状态已更新。"));
    }
}
```

## 模块依赖

要使用 `AvalancheViewport` 模块，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `AvalancheViewport` | 核心视口功能 |
| `Avalanche` | 插件主模块，提供基础框架 |
| `AvalancheCore` | Motion Design 的核心功能和类型系统 |
| `AvalancheSequencer` | 与 Sequencer 的深度集成，用于时间轴控制 |
| `AvalancheOutliner` | 专用的场景大纲 |
| `AvalancheCamera` | 增强的相机控制 |
| `AvalancheShapes` | 形状创建与编辑工具 |
| `AvalancheText` | 3D 文本工具 |
| `AvalancheModifiers` | 网格修改器 |

*注意：这是一个大型插件，包含数十个子模块。实际依赖取决于你具体使用哪些功能。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲标签页移至独立分组，优化编辑器布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在播出单页面设置中添加了 Movie Render Queue 的分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加了页面加载选项（全部、下一个、选中项） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/取消关联的通知，减少重复代码 |

### 维护评价

该插件处于 **活跃维护** 状态。
*   **创建时间**：2025年5月，虽然作为独立插件较新，但其功能源自长期的实验性开发。
*   **近期更新**：最近的更新（截至2026年5月）频繁且具有实质性功能增强（如 UI 布局优化、新分析工具、新项目设置），表明 Epic 团队正在积极开发和迭代。
*   **维护状态**：非常活跃。作为 Epic 官方虚拟制片工作流的核心部分，其长期支持有保障。
*   **推荐使用**：**强烈推荐**。对于任何需要专业广播图形或高级视口控制的 UE5 项目，这都是首选工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-motion-design-in-unreal-engine/)