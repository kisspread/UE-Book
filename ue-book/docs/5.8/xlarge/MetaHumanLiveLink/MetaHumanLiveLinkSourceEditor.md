# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 实时流媒体源， 编辑器定制） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件提供了一套完整的工具，用于将实时表演捕捉数据（主要来自 iPhone 的 ARKit 面部追踪）流式传输并应用到虚幻引擎中的 MetaHuman 角色上。它解决了数字人驱动工作流中的核心环节：如何实时、高保真地将演员的面部表情和头部动作映射到高质量的 MetaHuman 模型上。插件通过 Live Link 框架标准化了数据源，使得数据可以灵活地被消费，例如用于虚拟直播、影视预演或实时动画测试。

## 使用场景

- **虚拟直播/VTubing**：主播使用 iPhone 等设备捕捉面部表情，实时驱动一个 MetaHuman 虚拟形象进行直播或录制。
- **实时动画预演**：在电影或游戏制作中，导演和动画师可以在拍摄现场或动画工作室看到演员表演的实时数字替身效果，便于快速决策和迭代。
- **游戏开发与测试**：在开发支持角色面部动画的游戏时，用于实时测试 MetaHuman 角色的动画反应和表情混合效果。

## 蓝图用法

本插件主要通过 Live Link Subject 的细节面板定制化和工作流工具提供功能，其核心逻辑多在 C++ 层面实现。蓝图交互主要通过 Live Link 面板和特定的设置资产进行。

### 核心功能（细节面板定制）

| 功能 | 说明 | 所在类 |
|---|---|---|
| `Configure Subject Settings` | 在 Live Link Subject 的细节面板中，提供定制化界面以设置 MetaHuman 动画流的各项参数，如平滑、骨骼映射等。 | `FMetaHumanLiveLinkSubjectSettingsCustomization` |
| `Apply Smoothing Preset` | 提供一个定制化的属性行，用于快速选择和应用预设的面部动画平滑设置。 | `FMetaHumanSmoothingPreProcessorCustomization` |

### 使用示例（蓝图描述）

1.  **建立连接**：在编辑器中打开 `Live Link` 窗口，点击 `Source`，选择由本插件提供的 `MetaHuman Live Link Source` 或 `Live Link Face Source`。
2.  **配置 Subject**：连接成功后，在 Live Link 窗口的 `Subjects` 列表中会看到你的 MetaHuman 面板（如来自 iPhone 的 Live Link Face 应用）。双击该 Subject 以打开其 `Settings`。
3.  **定制化设置**：在 `Settings` 细节面板中，你会发现插件提供的定制化界面。在这里你可以配置骨骼映射、启用或调整面部动画的平滑效果、设置身体检测阈值等。
4.  **驱动角色**：将配置好的 Live Link Subject 连接到场景中 MetaHuman 角色的 `Animation` 或 `Live Link` 组件上，即可看到角色被实时驱动。

## C++ 用法

本插件的 C++ 用法主要集中在如何扩展或自定义 Live Link 面板的细节视图。

### 头文件引入

```cpp
#include “MetaHumanLiveLinkSubjectSettingsCustomization.h“
#include “MetaHumanSmoothingPreProcessorCustomization.h“
```

### 基本用法：注册自定义细节面板

要为你的 Live Link Subject 设置类注册一个自定义的细节面板，可以在你的编辑器模块中实现。

```cpp
// 来源于 MetaHumanLiveLinkSourceEditorModule.h
#include “IDetailCustomization.h“
#include “PropertyEditorModule.h“
#include “MetaHumanLiveLinkSubjectSettingsCustomization.h“ // 插件提供的定制化类

void FMyEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor“);
    // 假设我们有一个名为 UMyLiveLinkSettings 的类需要定制
    PropertyModule.RegisterCustomClassLayout(
        UMyLiveLinkSettings::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanLiveLinkSubjectSettingsCustomization::MakeInstance)
    );
}
```

### 进阶用法：自定义属性类型

为特定的属性类型（如 `FMetaHumanSmoothingSettings`）提供自定义的编辑界面。

```cpp
// 来源于 MetaHumanSmoothingPreProcessorCustomization.h
#include “IPropertyTypeCustomization.h“
#include “MetaHumanSmoothingPreProcessorCustomization.h“ // 插件提供的定制化类

void FMyEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor“);
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FMetaHumanSmoothingSettings::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMetaHumanSmoothingPreProcessorCustomization::MakeInstance)
    );
}
```

## Demo 示例

本插件的 Demo 主要体现在编辑器工作流中，而非可运行的 C++ 代码。一个最小的可编译编辑器模块示例，展示如何复用插件的定制化功能。

```cpp
// MyMetaHumanEditorModule.h
#pragma once
#include “Modules/ModuleManager.h“

class FMyMetaHumanEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 用于在关闭时注销自定义布局
    FName RegisteredCustomLayout;
};
```

```cpp
// MyMetaHumanEditorModule.cpp
#include “MyMetaHumanEditorModule.h“
#include “PropertyEditorModule.h“
#include “MetaHumanLiveLinkSubjectSettingsCustomization.h“ // 依赖 MetaHumanLiveLinkSourceEditor 模块

void FMyMetaHumanEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(“PropertyEditor“);
    
    // 为特定的 Live Link 设置类（例如来自另一个自定义源）注册 MetaHuman 风格的定制化面板
    RegisteredCustomLayout = UCustomLiveLinkSettings::StaticClass()->GetFName();
    PropertyModule.RegisterCustomClassLayout(
        RegisteredCustomLayout,
        FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanLiveLinkSubjectSettingsCustomization::MakeInstance)
    );
}

void FMyMetaHumanEditorModule::ShutdownModule()
{
    if (FPropertyEditorModule* PropertyModule = FModuleManager::GetModulePtr<FPropertyEditorModule>(“PropertyEditor“))
    {
        PropertyModule->UnregisterCustomClassLayout(RegisteredCustomLayout);
    }
}

IMPLEMENT_MODULE(FMyMetaHumanEditorModule, MyMetaHumanEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorWidgets` | 为 Live Link Subject 设置面板提供特定的编辑器 UI 控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 为身体动画检测暴露可调整的阈值参数，增强了身体驱动控制的灵活性。 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 改进面部动画序列导出，以支持组合求解（Combined Solve）工作流。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在苹果平台上使用 AVFoundation 媒体后端处理文件媒体源束，优化平台兼容性。 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新了 ADA (Animation Data Assets) 模型。 |

### 维护评价

- **创建时间**：插件于 2025 年 2 月创建，相对年轻。
- **更新频率**：从提交历史看，在 2026 年 5 月仍有密集的更新，集中在功能增强（身体阈值暴露、导出改进）和兼容性修复上，表明插件处于**活跃维护**状态。
- **维护状态**：**活跃维护中**。Epic Games 团队显然在持续为其添加新功能并修复问题。
- **已知限制**：作为 MetaHuman 工具链的一部分，其效果高度依赖于输入数据的质量（如 iPhone 面部追踪精度）和网络/连接的稳定性。
- **推荐使用**：对于任何需要实时驱动 MetaHuman 角色的项目，尤其是虚拟制片和直播场景，该插件是官方推荐的核心工具，值得积极采用和关注更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/animation-tools-and-settings/) (动画工具和设置概览， 涵盖 Live Link)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink/Tests) (如果存在)