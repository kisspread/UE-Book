# AvalancheMaskEditor

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动效遮罩编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、用户界面） |
| 模块 | `AvalancheMaskEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaskEditor) | |

## 用途

`AvalancheMaskEditor` 是 **Motion Design（动效设计）** 插件的核心编辑器扩展模块。它为用户在虚拟制播（Virtual Production）环境中创建复杂的动态图形和合成效果提供了可视化的遮罩（Mask）编辑能力。

这个模块的主要职责是：
1.  **提供专用的编辑器模式** (`UAvaMaskEditorMode`)：用户可以进入此模式，通过直观的视口交互（如选择、操作）来为场景中的Actor应用几何遮罩（Geometry Mask）。
2.  **扩展编辑器界面**：在状态栏、菜单中集成了快速切换遮罩显示、隔离视图等控件，方便艺术家和设计师进行实时效果预览和调整。
3.  **集成场景视图扩展** (`FAvaMaskSceneViewExtension`)：在渲染层面支持遮罩效果的可视化预览，确保所见即所得。
4.  **管理编辑器状态** (`UAvaMaskEditorSubsystem`)：集中管理如“显示所有遮罩”、“隔离选中遮罩”等编辑器级开关状态。

简单来说，它让原本可能需要手动配置的复杂几何遮罩效果，变成了一个可视化、可交互的编辑过程，是Motion Design流程中实现精准视觉控制的关键工具。

## 使用场景

-   **你正在为电视节目或直播制作动态图形（Lower Thirds、Logo动画、背景元素）** → 使用Motion Design插件进行设计，然后通过 `AvalancheMaskEditor` 为不同图形元素添加遮罩，实现精确的裁剪、显露和过渡效果。
-   **你需要在虚拟演播室中合成实景与CG元素** → 使用此编辑器为CG元素创建基于几何形状的遮罩，使其与实景的透视、遮挡关系正确匹配。
-   **你正在设计一套复杂的粒子或克隆效果** → 通过遮罩控制效果影响的区域范围，实现更艺术化的视觉效果。
-   **团队协作中，需要快速预览和调试场景中的遮罩效果** → 使用编辑器提供的“显示所有遮罩”、“隔离视图”等选项，专注于检查特定部分的遮罩逻辑。

## 蓝图用法

此模块的蓝图交互主要集中在编辑器UI控件和子系统功能调用上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleShowAllMasks` | 切换是否在视口中显示所有几何遮罩的边界/可视化信息 | `UAvaMaskEditorSubsystem` |
| `ToggleIsolateSelectedMask` | 切换是否在视口中只隔离显示当前选中的遮罩，方便调试 | `UAvaMaskEditorSubsystem` |
| `ToggleEnableSelectedMask` | 切换是否启用（显示效果）当前选中的遮罩 | `UAvaMaskEditorSubsystem` |
| `Enter` / `Exit` | 进入或退出 Motion Design Mask 编辑器模式 | `UAvaMaskEditorMode` |

### 使用示例（蓝图描述）

你无法直接在运行时蓝图中使用这些节点，因为它们主要用于**编辑器扩展**。其典型使用场景是在C++或编辑器Utility Widget中：

1.  **在编辑器工具中添加一个按钮**：
    -   创建一个编辑器Utility Widget蓝图。
    -   在蓝图中，获取 `UAvaMaskEditorSubsystem` 的实例。
    -   为按钮的点击事件绑定 `ToggleShowAllMasks` 函数。这样，点击按钮就能控制视口中所有遮罩的可见性。

2.  **自定义编辑器菜单项**：
    -   通过 `FAvaMaskEditorModule::RegisterMenus` 在编辑器菜单中注册命令（如 `ToggleMaskMode`）。
    -   这些命令会自动关联到 `UAvaMaskEditorSubsystem` 中对应的Toggle函数。

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheMaskEditorSubsystem.h"
#include "AvaMaskEditorMode.h"
```

### 基本用法

获取子系统并控制编辑器状态。

```cpp
// 假设在编辑器工具或另一个EditorSubsystem中
#include "AvalancheMaskEditorSubsystem.h"

void MyEditorTool::ToggleMaskVisibility()
{
    // 获取编辑器子系统
    if (UAvaMaskEditorSubsystem* MaskSubsystem = GEditor->GetEditorSubsystem<UAvaMaskEditorSubsystem>())
    {
        // 切换“显示所有遮罩”状态
        MaskSubsystem->ToggleShowAllMasks();

        // 检查当前状态
        bool bIsShowing = MaskSubsystem->IsShowingAllMasks();
        UE_LOG(LogTemp, Log, TEXT("Show All Masks: %s"), bIsShowing ? TEXT("ON") : TEXT("OFF"));
    }
}
```
*代码逻辑参考自 `UAvaMaskEditorSubsystem` 的公开接口。*

### 进阶用法

进入自定义的遮罩编辑器模式。

```cpp
#include "AvaMaskEditorMode.h"
#include "EditorModeManager.h"

void MyEditorTool::EnterMaskEditMode()
{
    // 获取当前世界的编辑器模式管理器
    if (UWorld* World = GEditor->GetEditorWorldContext().World())
    {
        if (FEditorModeTools* ModeTools = GLevelEditorModeTools())
        {
            // 进入 Motion Design Mask 编辑器模式
            ModeTools->ActivateMode(UAvaMaskEditorMode::EM_MotionDesignMaskEditorModeId);
        }
    }
}

void MyEditorTool::ExitMaskEditMode()
{
    if (FEditorModeTools* ModeTools = GLevelEditorModeTools())
    {
        // 退出该编辑器模式
        ModeTools->DeactivateMode(UAvaMaskEditorMode::EM_MotionDesignMaskEditorModeId);
    }
}
```
*代码逻辑参考自 `UAvaMaskEditorMode` 的模式ID定义和编辑器模式管理器的通用用法。*

## Demo 示例

一个最小化的编辑器工具类，用于控制遮罩编辑器子系统的显示状态。

**MyMaskControlTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyMaskControlTool.generated.h"

class UButton;
class UAvaMaskEditorSubsystem;

UCLASS()
class UMyMaskControlTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "Mask Control")
    void ToggleAllMasksVisibility();

private:
    UPROPERTY(meta = (BindWidget))
    UButton* ToggleButton = nullptr;

    TWeakObjectPtr<UAvaMaskEditorSubsystem> CachedMaskSubsystem;
};
```

**MyMaskControlTool.cpp**
```cpp
#include "MyMaskControlTool.h"
#include "AvalancheMaskEditorSubsystem.h"
#include "Components/Button.h"
#include "Editor.h"

void UMyMaskControlTool::NativeConstruct()
{
    Super::NativeConstruct();

    // 缓存子系统指针
    CachedMaskSubsystem = GEditor->GetEditorSubsystem<UAvaMaskEditorSubsystem>();

    if (ToggleButton)
    {
        ToggleButton->OnClicked.AddDynamic(this, &UMyMaskControlTool::ToggleAllMasksVisibility);
    }
}

void UMyMaskControlTool::ToggleAllMasksVisibility()
{
    if (UAvaMaskEditorSubsystem* MaskSubsystem = CachedMaskSubsystem.Get())
    {
        MaskSubsystem->ToggleShowAllMasks();

        // 可选：更新按钮文本以反映状态
        const bool bIsShowing = MaskSubsystem->IsShowingAllMasks();
        const FText ButtonText = bIsShowing ? NSLOCTEXT("MaskTool", "HideAll", "Hide All Masks") : NSLOCTEXT("MaskTool", "ShowAll", "Show All Masks");
        if (ToggleButton)
        {
            ToggleButton->SetToolTipText(ButtonText);
        }
    }
}
```

## 模块依赖

要使用 `AvalancheMaskEditor` 模块的功能（例如在自己的编辑器扩展中调用其子系统），你的模块需要在 `Build.cs` 中添加以下不常见的依赖：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 核心的几何遮罩功能库，被编辑器用来操作和预览遮罩 |
| `GeometryScript` | 提供几何脚本操作，用于在编辑器中处理遮罩的几何数据 |
| `MotionDesignCore` | Motion Design插件的核心运行时模块，提供基础类型和功能 |
| `PropertyAnimatorCore` | 属性动画核心，遮罩效果可能与属性动画系统集成 |
| `ActorModifierCore` | Actor修改器核心，遮罩功能可能作为Actor修改器实现 |
| `Text3D` | 3D文本功能，遮罩常用于文本动画效果 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将动效设计的场景设置和大纲视图选项卡移至编辑器专属分组，优化界面组织 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用“节目单页面”设置时增加了MRQ（影片渲染队列）分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 在节目控制工具栏中添加了页面加载选项（全部、下一个、选中项），增强了节目编排控制能力 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目级设置，可强制禁用3D文本和形状的碰撞，简化动效设计流程 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口通信逻辑，当客户端关联或断开关联时发送通知，减少冗余代码 |

### 维护评价

**积极维护中**。`AvalancheMaskEditor` 是 Motion Design（Avalanche）插件的一部分，该插件于2025年5月从实验性目录迁移到正式的Virtual Production目录，表明其已进入稳定期。从最近的提交记录看，开发团队在持续进行功能增强、UI优化和集成工作（如MRQ分析、节目控制改进）。最后一次提交在2026年5月，更新非常频繁。作为Epic Games官方维护的核心虚拟制播工具，其可靠性和未来更新是有保障的。**推荐用于正式的虚拟制播和动态图形项目**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaskEditor)
-   [官方文档](https://docs.unrealengine.com)（虚幻引擎文档站，搜索“Motion Design”或“Geometry Mask”）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)（相关功能测试可能位于此模块）