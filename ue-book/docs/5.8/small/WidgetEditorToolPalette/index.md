# Widget Editor Tool Palette

> A set of tools to enhance UMG creation UX

| 属性 | 值 |
|---|---|
| 中文名 | UMG编辑器工具板 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `WidgetEditorToolPalette` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2022-03-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WidgetEditorToolPalette) | |

## 用途

此插件为 Unreal Motion Graphics (UMG) 可视化设计器（Widget Blueprint Editor）扩展了一套交互式工具。其核心目的是将 Unreal 的交互式工具框架 (`UInteractiveTool`) 引入到 2D UI 设计流程中，为 UI 设计师提供类似 3D 视口编辑器（如建模工具）的专业、可扩展的工具体验。

它主要解决 UMG 编辑器原生操作方式单一（如仅支持点击选择）的问题，通过提供专业的工具（如框选工具、一键创建控件工具）来提升 UI 布局和元素管理的效率。

## 使用场景

- 你需要在 UMG 编辑器中快速创建特定类型的控件（如按钮、图片），并希望通过快捷键直接激活创建工具，而不是从调色板拖拽。
- 你需要在 UMG 编辑器中同时选中多个控件进行批量移动或编辑，原生点击选择效率低下，需要类似“框选”的专业选择方式。
- 你希望为你的项目或团队自定义 UMG 编辑器的工具集和快捷键。

## 蓝图用法

此插件主要是编辑器扩展，其核心功能（矩形选择、控件创建）通过 C++ 工具类实现，并未直接暴露新的蓝图节点。其使用主要体现在 UMG 编辑器界面上新增的工具栏和交互模式。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图可调用节点） | 工具功能通过编辑器模式激活，不提供蓝图接口 | |

### 使用示例（蓝图描述）

此插件的功能在蓝图编辑器中无法直接使用或调用。它通过向 `FWidgetBlueprintEditor`（Widget 蓝图编辑器）注册一个编辑器模式（`UWidgetEditorToolPaletteMode`）和工具栏（`FWidgetEditorToolPaletteToolkit`）来工作。用户在使用 Widget 蓝图时，可以通过编辑器界面切换到此工具模式，并使用新增的矩形选择工具和创建控件工具。

## C++ 用法

此插件的 C++ 接口主要用于管理工具调色板模式的生命周期和状态查询。

### 头文件引入

```cpp
#include "WidgetEditorToolPaletteModule.h"
```

### 基本用法

通过模块接口可以查询和切换工具调色板模式的激活状态。

```cpp
// 来源：WidgetEditorToolPaletteModule.h
// 获取模块实例
FWidgetEditorToolPaletteModule& Module = FModuleManager::GetModuleChecked<FWidgetEditorToolPaletteModule>(TEXT("WidgetEditorToolPalette"));

// 检查工具调色板模式是否激活（需要传入当前的Widget蓝图编辑器指针）
TWeakPtr<FWidgetBlueprintEditor> Editor = /* ... 获取当前编辑器实例 ... */;
bool bIsActive = Module.IsWidgetEditorToolPaletteModeActive(Editor);

// 切换工具调色板模式的激活状态
Module.OnToggleWidgetEditorToolPaletteMode(Editor);
```

### 进阶用法

插件通过 `UCreateWidgetToolSettings` 提供了可配置的创建工具堆栈。你可以通过修改项目设置（`Config/DefaultWidgetEditorToolPalette.ini`）来添加自定义的控件创建工具及其快捷键。

```cpp
// 来源：Settings/CreateWidgetToolSettings.h
// 在配置文件中定义结构，例如：
// [Startup]
// +CreateWidgetStacks=(DisplayName="UI Controls", WidgetToolInfos=((WidgetClass="/Script/UMGEditor.Widget_Button", DisplayName="Button", WidgetHotkey=(bCtrl=true, Key=B))))
```

## Demo 示例

以下示例展示了一个最小化的自定义编辑器工具，它模拟了 `CreateWidgetTool` 的创建逻辑。

**MyCustomCreateTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Tools/UInteractiveTool.h"
#include "Framework/Commands/UICommandInfo.h"
#include "MyCustomCreateTool.generated.h"

UCLASS()
class UMyCustomCreateTool : public UInteractiveTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override;
    virtual void OnPropertyModified(UObject* PropertySet, FProperty* Property) override;

    // 鼠标点击回调
    void OnClicked(const FGeometry& Geometry, const FPointerEvent& Event);
};
```

**MyCustomCreateTool.cpp**
```cpp
#include "MyCustomCreateTool.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

void UMyCustomCreateTool::Setup()
{
    Super::Setup();
    // 初始化工具属性、注册输入事件等
    // 在实际的 CreateWidgetTool 中，这里会与设计器视图交互
}

void UMyCustomCreateTool::OnPropertyModified(UObject* PropertySet, FProperty* Property)
{
    // 响应属性变化，例如更新工具行为
}

void UMyCustomCreateTool::OnClicked(const FGeometry& Geometry, const FPointerEvent& Event)
{
    // 核心创建逻辑：计算点击位置，在 UMG 画布中创建控件
    // 这是一个模拟，实际需操作 UMG 的 Slate 树和 Widget 树
    UWorld* World = GetWorld();
    if (World)
    {
        FVector Location = /* 从 Event 和 Geometry 计算出的世界位置 */;
        AActor* NewActor = World->SpawnActor<AActor>(AActor::StaticClass(), FTransform(Location));
        // 在真实 UMG 工具中，这里是创建 SNew(SButton) 等操作
    }
    // 通知工具链完成
    RequestDeletion();
}
```

## 模块依赖

从插件模块的 `Build.cs` 文件推断，使用此插件时，你的编辑器模块可能需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `WidgetEditorToolPalette` | 插件的核心模块，提供工具模式和基础框架 |
| `UMGEditor` | UMG 编辑器核心，提供 `FWidgetBlueprintEditor`、`SDesignerView` 等关键类 |
| `InteractiveToolsFramework` | 提供交互式工具的基类和管理器 (`UInteractiveTool`, `UInteractiveToolManager`) |
| `EditorWidgets` | 提供编辑器 UI 控件，如工具板的界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后，进行了第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了某个更改列表 (CL51314860) 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将初始化委托从静态属性改为函数获取，以修复注册缺失问题。 |
| 2026-02-20 | `2ce45174` | [Viewport ITF] Allow editor modes to opt-in to the new gizmos. When editor modes change, the ITF Tra... | 允许编辑器模式选择加入新的 Gizmo 系统，并在模式切换时处理相关事务。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base*.ini` 重命名为 `Default*.ini`，遵循UE新规范。 |

### 维护评价

- **活跃维护**：从 git 记录看，插件在 **2026年2月** 仍有活跃的更新，主要是修复兼容性问题（如 `FCoreDelegates` API 变更）和适配引擎新特性（Viewport ITF）。
- **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认未启用 (`Installed: false`)，表明它仍处于实验阶段，API 和功能可能发生变化。
- **年龄**：创建于 2022 年，约 4 年历史，对于一个实验性功能来说仍在合理维护周期内。
- **推荐度**：**推荐有兴趣的用户试用**，特别是希望深度定制 UMG 编辑器工作流的团队。但由于其 Beta 状态，不建议在生产项目的核心部分强依赖它。建议关注其后续的合并到主分支或功能冻结的公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WidgetEditorToolPalette)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现公开的测试文件)