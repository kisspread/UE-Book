# UMG Widget Preview

> Quickly preview and debug UMG widgets without running PIE.

| 属性 | 值 |
|---|---|
| 中文名 | UMG小部件预览 |
| 分类 | UI |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UMGWidgetPreview` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-31 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UMGWidgetPreview) | |

## 用途

该插件是一个编辑器工具，旨在解决 UMG (Unreal Motion Graphics) UI 开发中的常见痛点：**快速预览与调试**。在传统流程中，开发者必须启动“在编辑器中运行” (PIE) 会话才能看到 UI 的最终运行效果，这非常耗时，尤其在调整布局、样式或调试交互时。此插件通过提供一个独立的编辑器窗口，允许开发者直接在编辑器中即时预览和交互测试 UMG Widget，从而极大地加速了 UI 开发和迭代过程。

其核心功能包括：
1.  **即时预览**：无需启动 PIE，直接在编辑器视口内渲染和交互 UI。
2.  **结构化预览**：支持预览带有插槽 (Slot) 的复合 Widget，允许为每个插槽指定不同的子 Widget。
3.  **调试辅助**：能够检查 Widget 是否具备 `bCanCallInitializedWithoutPlayerContext` 属性，这对在无玩家上下文的编辑器环境中预览至关重要，并提供修复建议。
4.  **状态管理**：工具包具有状态机（如 Running， Paused， Background， Unsupported），能智能地根据编辑器焦点、蓝图编译等事件自动切换预览状态。
5.  **ViewModel 集成**：支持在预览时自动构造缺失的 ViewModel，便于测试数据绑定。

## 使用场景

- **UI 布局调整**：你在编辑一个复杂的 UMG Widget 布局，希望快速查看对齐、边距等修改效果，无需等待 PIE 启动。
- **复合 Widget 预览**：你设计了一个主菜单 Widget，其中包含多个可替换的插槽（如内容区域、广告栏），需要测试不同插槽内容的组合效果。
- **蓝图调试**：你的 Widget 依赖于 ViewModel 数据绑定，希望在不运行完整游戏逻辑的情况下，验证数据如何反映在 UI 上。
- **兼容性检查**：你正在开发一个通用的 UI 组件，需要确认它是否能在没有玩家控制器的环境下初始化（例如用于游戏内嵌套的菜单）。

## 蓝图用法

该插件主要通过 C++ 暴露 API，但核心类 `UWidgetPreview` 包含一些可用于蓝图的属性和函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWidgetSlotNames` | 获取当前预览 Widget 中所有可用的插槽名称列表。 | `UWidgetPreview` |
| `GetOrCreateWidgetInstance` | 获取或创建用于预览的 Widget 实例。可用于触发重建。 | `UWidgetPreview` |
| `GetWidgetInstance` | 获取当前已创建的 Widget 实例（若存在）。 | `UWidgetPreview` |
| `ClearWidgetInstance` | 清除当前 Widget 实例，将其存入 Previous 并准备重建。 | `UWidgetPreview` |
| `SetWidgetType` | 设置要预览的主 Widget 类型（可指向 UUserWidget 蓝图或 WidgetPreview 资产）。 | `UWidgetPreview` |
| `SetSlotWidgetTypes` | 设置插槽 Widget 类型映射，为指定名称的插槽分配不同的子 Widget。 | `UWidgetPreview` |
| `SetbShouldOverrideWidgetSize` | 启用或禁用覆盖预览 Widget 的尺寸。 | `UWidgetPreview` |
| `SetOverriddenWidgetSize` | 设置覆盖的预览 Widget 尺寸（在覆盖启用时生效）。 | `UWidgetPreview` |
| `SetDefaultConstructViewmodels` | 设置是否在预览打开时自动构造缺失的 ViewModel。 | `UWidgetPreview` |

### 使用示例（蓝图描述）

虽然主要以资产编辑器形式使用，但可以通过蓝图脚本化地创建和操控预览：
1.  从内容浏览器创建或打开一个 `WidgetPreview` 资产。
2.  在资产编辑器的详情面板中，通过“Widget”属性选择一个要预览的 UUserWidget 蓝图。
3.  如果主 Widget 有插槽，“Slot Widgets”属性会列出可用插槽，可为每个插槽指定不同的 UUserWidget 蓝图。
4.  勾选“Override Widget Size”可以指定预览窗口的固定分辨率。
5.  点击工具栏的“预览”按钮即可在视口内看到实时渲染效果，并可以与之交互。

## C++ 用法

该插件主要作为编辑器工具使用，但其核心类 `UWidgetPreview` 和接口 `IWidgetPreviewToolkit` 也可以通过 C++ 进行编程扩展或集成。

### 头文件引入

```cpp
#include "WidgetPreview.h"
// 如果要访问模块事件，可包含公共接口
#include "IUMGWidgetPreviewModule.h"
```

### 基本用法

创建并配置一个 `UWidgetPreview` 对象，用于在自定义工具或测试中预览 Widget。
*来源: `WidgetPreview.h`*

```cpp
// 获取或创建一个 UWidgetPreview 实例
UWidgetPreview* MyPreview = NewObject<UWidgetPreview>();

// 定义要预览的 Widget 蓝图
FPreviewableWidgetVariant MainWidgetType;
MainWidgetType.ObjectPath = FSoftObjectPath(TEXT("/Game/UI/WBP_MainMenu.WBP_MainMenu"));
MyPreview->SetWidgetType(MainWidgetType);

// 定义插槽 Widget (如果主 Widget 有插槽)
TMap<FName, FPreviewableWidgetVariant> SlotWidgets;
FPreviewableWidgetVariant SlotWidgetVariant;
SlotWidgetVariant.ObjectPath = FSoftObjectPath(TEXT("/Game/UI/WBP_ContentPanel.WBP_ContentPanel"));
SlotWidgets.Add(FName("ContentSlot"), SlotWidgetVariant);
MyPreview->SetSlotWidgetTypes(SlotWidgets);

// 可选：覆盖预览尺寸
MyPreview->SetbShouldOverrideWidgetSize(true);
MyPreview->SetOverriddenWidgetSize(FVector2D(1920.f, 1080.f));

// 在一个可用的 UWorld (通常是编辑器预览世界) 中生成实例
UWorld* EditorPreviewWorld = GEditor->GetEditorWorldContext().World();
UUserWidget* PreviewInstance = MyPreview->GetOrCreateWidgetInstance(EditorPreviewWorld);
if (PreviewInstance)
{
    // 预览实例已创建，可以获取其 Slate 控件进行进一步操作
    TSharedPtr<SWidget> SlateWidget = MyPreview->GetSlateWidgetInstance();
}
```

### 进阶用法

监听 `UWidgetPreview` 的状态变化，以在自定义 UI 中同步更新。
*来源: `WidgetPreview.h`, `IWidgetPreviewToolkit.h`*

```cpp
// 绑定到 Widget 变化事件
MyPreview->OnWidgetChanged().AddLambda([](EWidgetPreviewWidgetChangeType ChangeType)
{
    // 响应主 Widget 或插槽 Widget 的变化
    // ChangeType 枚举可以区分变化类型
    UE_LOG(LogTemp, Log, TEXT("Preview Widget changed!"));
});

// 如果您有访问 Toolkit (IWidgetPreviewToolkit) 的指针，可以监听对象选择变化
// (这通常在扩展编辑器插件时更常见)
FOnSelectedObjectsChanged& SelectionDelegate = Toolkit->OnSelectedObjectsChanged();
SelectionDelegate.AddLambda([](const TConstArrayView<TWeakObjectPtr<UObject>>& SelectedObjects)
{
    // 当预览器中选择的对象变化时，例如在详情面板中查看不同 Widget 的属性
});
```

## Demo 示例

一个在编辑器工具中创建并显示 Widget 预览的最小 C++ 示例片段。

**WidgetPreviewDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UWidgetPreview;
class SWidget;

class FWidgetPreviewDemo
{
public:
    void InitPreview();
    void ShowPreviewInWindow();

private:
    UWidgetPreview* WidgetPreviewAsset = nullptr;
    TSharedPtr<SWidget> PreviewSlateWidget;
};
```

**WidgetPreviewDemo.cpp**
```cpp
#include "WidgetPreviewDemo.h"
#include "WidgetPreview.h"
#include "Widgets/SBoxPanel.h"
#include "Framework/Application/SlateApplication.h"
#include "Engine/Engine.h"

void FWidgetPreviewDemo::InitPreview()
{
    // 创建 WidgetPreview 资产
    WidgetPreviewAsset = NewObject<UWidgetPreview>();
    
    // 配置要预览的 Widget
    FPreviewableWidgetVariant WidgetToPreview;
    WidgetToPreview.ObjectPath = FSoftObjectPath(TEXT("/Game/Widgets/WBP_TestUI.WBP_TestUI"));
    WidgetPreviewAsset->SetWidgetType(WidgetToPreview);
    
    // 在编辑器世界中实例化
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (UUserWidget* Instance = WidgetPreviewAsset->GetOrCreateWidgetInstance(World))
    {
        PreviewSlateWidget = WidgetPreviewAsset->GetSlateWidgetInstance();
    }
}

void FWidgetPreviewDemo::ShowPreviewInWindow()
{
    if (!PreviewSlateWidget.IsValid()) return;

    // 创建一个简单的 Slate 窗口来承载预览控件
    TSharedRef<SWindow> PreviewWindow = SNew(SWindow)
        .Title(FText::FromString(TEXT("Widget Preview Demo")))
        .ClientSize(FVector2D(800, 600))
        [
            SNew(SOverlay)
            + SOverlay::Slot()
            [
                SNew(SBorder).Padding(10.f)
                [
                    PreviewSlateWidget.ToSharedRef()
                ]
            ]
        ];

    // 将窗口添加到 Slate 应用
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().AddWindow(PreviewWindow);
    }
}
```

## 模块依赖

您的模块若要使用 `UWidgetPreview` 类进行扩展开发，需要在 `.Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `UMGWidgetPreview` | 插件核心运行时模块，包含 `UWidgetPreview` 等核心类 |
| `UMGEditor` | UMG 编辑器模块，用于处理 Widget 蓝图相关操作 |
| `WidgetBlueprint` | Widget 蓝图模块，提供 `UWidgetBlueprint` 等类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `8fdf43d3` | [ContentBrowser] New Add Menu UserInterface Menu | 在内容浏览器的“添加”菜单中增加了“用户界面”分类菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF（可能指代特定的日志宏）。 |
| 2026-03-10 | `4f5c7fa3` | MVVM Widget Preview: Fixed status message lagging behind state when changing source widgets. | 修复了在 MVVM 小部件预览中切换源小部件时，状态消息更新滞后的问题。 |
| 2025-12-23 | `b3775500` | UMG MVVM Previewer: There's now an option to default construct missing viewmodels when the preview i | UMG MVVM 预览器新增选项：可在预览时默认构造缺失的 ViewModel。 |
| 2025-08-28 | `e6f47d77` | Minor fix to a potential nullptr access in UMG Widget Preview Editor Plugin | 修复了 UMG 小部件预览编辑器插件中一个潜在的空指针访问问题。 |

### 维护评价

该插件自2024年5月创建以来，仍在**持续维护和功能增强中**。
- **活跃度**：最近一次更新在2026年4月，显示仍在积极开发，包括新功能集成（菜单改进、MVVM增强）和稳定性修复。
- **状态**：虽然 `.uplugin` 中标记为 `IsExperimentalVersion: true`，但 `EnabledByDefault: true` 且持续更新，表明其核心功能已相对稳定，处于“实验性后期”或“积极完善”阶段。
- **推荐**：对于需要快速迭代 UMG UI 的开发者，这是一个非常实用的编辑器工具，**强烈推荐尝试**。它能显著提升UI开发效率。使用时需注意其实验性标签，可能会在未来版本中有API调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UMGWidgetPreview)
- [官方文档]() (`.uplugin` 中未提供 DocsURL)
- [测试用例]() (未在给定信息中发现明确的测试文件路径)