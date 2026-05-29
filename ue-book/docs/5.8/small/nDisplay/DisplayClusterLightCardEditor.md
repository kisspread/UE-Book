# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay分布式渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI与工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的一个核心虚拟制片插件，用于实现**同步的集群渲染**。它允许将单个 Unreal Engine 项目同时渲染到多个显示器或 LED 墙上，并保持所有画面的完美同步。

此文档聚焦于 nDisplay 插件中的一个关键子模块：**DisplayClusterLightCardEditor**。该模块是一个**专用的编辑器工具**，其主要用途是在 LED 墙虚拟制片（ICVFX）工作流中，**以直观的 2D 视图创建、编辑和管理“灯光卡”（Light Cards）**。

**灯光卡**是放置在虚拟场景中用于模拟环境光照的二维元素。它们通常用于为演员或道具提供来自 LED 墙背景的反射和高光。`DisplayClusterLightCardEditor` 提供了一个集成的编辑器面板，让美术和技术美术能够在 nDisplay 的“操作员面板”（Operator Panel）中，直接对灯光卡的形状、位置、缩放和旋转进行可视化编辑，而无需在复杂的 3D 视口中反复调整。

**为什么存在**：在虚拟制片场景中，精确控制 LED 墙上的光照至关重要。直接在 3D 视口中调整灯光卡效率低下且难以对齐。`DisplayClusterLightCardEditor` 通过提供一个类似 2D 平面设计工具的专用界面，极大提升了这一关键任务的工作流程和易用性。

## 使用场景

-   **虚拟制片（ICVFX）灯光调整**：当你在使用 LED 墙拍摄，需要为演员添加一个精确匹配背景建筑窗户的反射光斑时，你可以使用灯光卡编辑器快速在 LED 墙的 2D 平视图上绘制或放置一个灯光卡。
-   **创建可复用的灯光效果**：当你设计好一个特定形状和参数的灯光卡（如模拟车灯效果）后，可以将其保存为模板，并在其他项目或场景中复用。
-   **复杂场景光照**：在一个需要大量环境光照元素的复杂虚拟场景中，使用灯光卡编辑器的 outliner 视图来高效地组织、选择和批量调整所有灯光卡。
-   **导演或美术总监预览**：在拍摄现场，操作员可以快速在编辑器中调整灯光卡，实时预览其在 LED 墙上的效果，而无需修改 3D 场景本身。

## 蓝图用法

`DisplayClusterLightCardEditor` 模块主要是一个编辑器工具，其蓝图接口相对有限，主要用于模块级功能的访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Display Cluster Light Card Editor` | 获取灯光卡编辑器模块的单例实例 | `IDisplayClusterLightCardEditor` |
| `Show Labels` | 根据参数为指定根 Actor 的灯光卡显示标签 | `IDisplayClusterLightCardEditor` |
| `Get Default Light Card Template` | 获取用于创建新灯光卡的默认模板资产 | `IDisplayClusterLightCardEditor` |

### 使用示例（蓝图描述）

1.  **获取编辑器实例**：在任意蓝图函数中，使用“Get Display Cluster Light Card Editor”节点（来自 `IDisplayClusterLightCardEditor` 接口）获取模块单例。
2.  **显示灯光卡标签**：连接上一步的输出，调用 `Show Labels` 节点。你需要传入一个 `FLabelArgs` 结构体，其中包含目标 `DisplayClusterRootActor` 引用和标签显示设置。
3.  **获取默认模板**：调用 `Get Default Light Card Template` 节点，返回一个 `UDisplayClusterStageActorTemplate` 对象，可用于在编辑器中创建新灯光卡时的默认配置。

## C++ 用法

### 头文件引入

```cpp
// 访问模块接口
#include "IDisplayClusterLightCardEditor.h"

// 访问项目设置
#include "Settings/DisplayClusterLightCardEditorSettings.h"

// 访问灯光卡模板资产
#include "LightCardTemplates/DisplayClusterLightCardTemplate.h"
```

### 基本用法

获取模块实例并使用其功能。
```cpp
// 确保模块已加载
if (IDisplayClusterLightCardEditor::IsAvailable())
{
    // 获取模块实例
    IDisplayClusterLightCardEditor& LightCardEditor = IDisplayClusterLightCardEditor::Get();
    
    // 获取默认灯光卡模板
    UDisplayClusterStageActorTemplate* DefaultTemplate = LightCardEditor.GetDefaultLightCardTemplate();
    if (DefaultTemplate)
    {
        UE_LOG(LogTemp, Log, TEXT("Default light card template asset: %s"), *DefaultTemplate->GetName());
    }
    
    // 设置标签显示参数
    IDisplayClusterLightCardEditor::FLabelArgs LabelArgs;
    // ... (配置LabelArgs，例如设置RootActor等)
    LightCardEditor.ShowLabels(LabelArgs);
}
```
*来源：基于 `Public/IDisplayClusterLightCardEditor.h` 中的接口定义。*

### 进阶用法

访问和修改项目设置，以控制编辑器的默认行为。
```cpp
#include "DisplayClusterLightCardEditorSettings.h"

// 获取项目级设置（跨用户）
UDisplayClusterLightCardEditorProjectSettings* ProjectSettings = GetMutableDefault<UDisplayClusterLightCardEditorProjectSettings>();
if (ProjectSettings)
{
    // 修改默认灯光卡模板路径
    ProjectSettings->LightCardTemplateDefaultPath.Path = TEXT("/Game/MyProject/LightCardTemplates");
    
    // 保存设置
    ProjectSettings->SaveConfig();
    
    UE_LOG(LogTemp, Log, TEXT("Light card template default path updated."));
}

// 获取用户级设置
UDisplayClusterLightCardEditorSettings* UserSettings = GetMutableDefault<UDisplayClusterLightCardEditorSettings>();
if (UserSettings)
{
    // 查询用户是否显示图标
    bool bShowIcons = UserSettings->bDisplayIcons;
    UE_LOG(LogTemp, Log, TEXT("Display icons setting: %s"), bShowIcons ? TEXT("true") : TEXT("false"));
}
```
*来源：基于 `Private/Settings/DisplayClusterLightCardEditorSettings.h` 中的设置类定义。*

## Demo 示例

一个演示如何通过 C++ 代码与灯光卡编辑器模块交互的最小示例。
```cpp
// MyLightCardEditorUtils.h
#pragma once

#include "CoreMinimal.h"
#include "IDisplayClusterLightCardEditor.h"

class UDisplayClusterStageActorTemplate;

class FMyLightCardEditorUtils
{
public:
    /** 尝试获取默认灯光卡模板并打印其名称 */
    static void LogDefaultLightCardTemplateInfo();
    
    /** 显示一个简单的消息框，指示模块是否可用 */
    static void CheckEditorModuleAvailability();
};

// MyLightCardEditorUtils.cpp
#include "MyLightCardEditorUtils.h"
#include "DisplayClusterLightCardEditorSettings.h"
#include "Misc/MessageDialog.h"

void FMyLightCardEditorUtils::LogDefaultLightCardTemplateInfo()
{
    if (!IDisplayClusterLightCardEditor::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterLightCardEditor module is not loaded."));
        return;
    }

    UDisplayClusterStageActorTemplate* Template = IDisplayClusterLightCardEditor::Get().GetDefaultLightCardTemplate();
    if (Template)
    {
        UE_LOG(LogTemp, Log, TEXT("Default Light Card Template: '%s' (Path: %s)"),
            *Template->GetName(),
            *Template->GetPathName());
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("No default light card template is set."));
    }
}

void FMyLightCardEditorUtils::CheckEditorModuleAvailability()
{
    FText Message;
    if (IDisplayClusterLightCardEditor::IsAvailable())
    {
        Message = FText::FromString(TEXT("nDisplay Light Card Editor module is loaded and available."));
    }
    else
    {
        Message = FText::FromString(TEXT("nDisplay Light Card Editor module is NOT loaded. Enable the nDisplay plugin first."));
    }
    FMessageDialog::Open(EAppMsgType::Ok, Message);
}
```

## 模块依赖

要使用 `DisplayClusterLightCardEditor` 模块的功能，你的项目或模块需要在 Build.cs 中依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DisplayClusterLightCardEditor` | 提供灯光卡编辑器的核心功能和接口。 |
| `DisplayClusterConfiguration` | 提供 nDisplay 的配置数据结构（如 `UDisplayClusterConfigurationViewport`），编辑器需要这些数据来与场景中的根 Actor 交互。 |
| `DisplayClusterShaders` | 提供用于投影和渲染的自定义着色器，视口客户端可能需要。 |
| `DisplayClusterScenePreview` | 用于在编辑器中预览和管理场景渲染。 |

**注意**：由于此模块深度集成到 nDisplay 的操作员面板（Operator Panel）中，它还隐式依赖了 `DisplayClusterOperator` 和 `DisplayClusterEditor` 等模块。如果你的代码需要操作 3D 视口或 Slate UI，可能还需要 `UnrealEd`、`EditorWidgets`、`LevelEditor` 等编辑器核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay的EXR多层支持，可能影响渲染输出流程。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 简化电影管线的扭曲混合（WarpBlend）模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多个渲染和着色器相关的bug。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 改进了输出帧编码时对Gamma值的处理。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了一个特定尺寸下的GUI闪烁问题。 |

### 维护评价

- **活跃维护**：nDisplay 是 Epic Games 用于虚拟制片（Virtual Production）的核心技术，尤其是 ICVFX（In-Camera VFX）工作流。从提交记录看，它被**持续、活跃地维护和更新**，最近的提交集中在 2026 年 5 月。
- **功能完整**：`DisplayClusterLightCardEditor` 作为其中的重要编辑器组件，提供了专业、完整的灯光卡编辑功能，包括视口、大纲、模板管理和丰富的交互工具。
- **已知限制**：作为一个复杂的编辑器模块，它可能在多用户编辑（Multi-User）场景、特定硬件配置或非标准拓扑结构下存在边缘情况问题。其文档可能不如核心引擎模块详细。
- **推荐使用**：对于从事 **虚拟制片、LED 墙拍摄或 ICVFX 项目**的团队，**强烈推荐启用和使用** nDisplay 插件及其灯光卡编辑器。它是 Unreal Engine 在此领域最成熟的工具集之一。对于不涉及虚拟制片的传统游戏开发项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)