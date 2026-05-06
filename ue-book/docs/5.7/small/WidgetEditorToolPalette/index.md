# Tool Palette for the Widget Editor

> A set of tools to enhance UMG creation UX

| 属性 | 值 |
|---|---|
| 中文名 | 控件编辑器工具面板 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Slate 样式资源） |
| 模块 | `WidgetEditorToolPalette` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WidgetEditorToolPalette) | |

---

## 用途

该插件为 UMG 编辑器（Widget 蓝图编辑器）提供一套可扩展的工具面板，通过“点击创建控件”（`UCreateWidgetTool`）和“矩形框选”（`URectangleSelectTool`）两种核心工具，增强控件编辑的交互效率。它还允许用户通过项目设置（`UCreateWidgetToolSettings`）自定义工具栈（Tool Stack）和热键，实现快速创建常用控件的便捷操作。

**解决什么问题？** 原生 UMG 编辑器缺少快速创建特定控件的快捷键和工具面板；框选多个控件的操作也不够直观。该插件补足这些功能，让设计师和开发者能更高效地进行界面布局。

---

## 使用场景

- **快速创建常用控件**：在 UMG 编辑器中，通过设置一批常用控件（如按钮、文本块、图像等）并绑定热键，点击即可在指定位置生成控件，省去拖拽控件的步骤。
- **矩形框选多控件**：类似 Photoshop 的选区工具，通过拖拽矩形框来选中多个控件，适用于整体移动、对齐或删除操作。
- **自定义工具布局**：项目团队可以统一配置工具面板的显示名称、热键，甚至重写创建工具的逻辑（通过定制 `UCreateWidgetToolBuilder`），满足不同项目的独特工作流。

---

## 蓝图用法

该插件为编辑器插件，不公开任何 BlueprintCallable 或 BlueprintReadWrite 属性，因此无法在蓝图节点中直接调用。所有配置和工具行为均通过 C++ 实现。

---

## C++ 用法

### 头文件引入

```cpp
#include "WidgetEditorToolPaletteModule.h"
#include "Settings/CreateWidgetToolSettings.h"
#include "DefaultTools/CreateWidgetTool.h"
#include "DefaultTools/RectangleSelectTool.h"
```

### 基本用法

#### 1. 通过项目设置自定义工具栈

在项目设置中（Editor → Plugins → Create Widget Hotkeys）添加工具栈和工具信息。示例设置（保存到 `DefaultEditor.ini` 或通过 C++ 代码修改 `UCreateWidgetToolSettings`）：

```cpp
// 获取设置对象
UCreateWidgetToolSettings* Settings = GetMutableDefault<UCreateWidgetToolSettings>();

// 添加一个工具栈：“常用按钮”
FCreateWidgetStackInfo StackInfo;
StackInfo.DisplayName = TEXT("常用按钮");

// 添加一个创建按钮的工具
FCreateWidgetToolInfo ToolInfo;
ToolInfo.WidgetClass = UButton::StaticClass();     // 创建 UButton
ToolInfo.DisplayName = TEXT("Button");             // 显示名称
ToolInfo.WidgetHotkey = FInputChord(EKeys::B);     // 按 B 键激活
ToolInfo.CreateWidgetToolBuilder = UCreateWidgetToolBuilder::StaticClass(); // 默认 builder
StackInfo.WidgetToolInfos.Add(ToolInfo);

Settings->WidgetToolStacks.Add(StackInfo);
Settings->SaveConfig(); // 保存到配置文件
```

#### 2. 初始化工具面板（编辑器启动时自动完成）

模块启动时（`FWidgetEditorToolPaletteModule::StartupModule`）会注册编辑器模式、工具命令及样式。开发者无需额外调用。

#### 3. 激活/切换工具面板

```cpp
// 获取模块实例
FWidgetEditorToolPaletteModule& Module = FModuleManager::Get().LoadModuleChecked<FWidgetEditorToolPaletteModule>("WidgetEditorToolPalette");

// 通过 Widget 蓝图编辑器实例切换工具面板
TWeakPtr<FWidgetBlueprintEditor> Editor = /* 获取当前编辑器 */;
Module.OnToggleWidgetEditorToolPaletteMode(Editor);
```

### 进阶用法

#### 自定义创建工具 Builder

若要修改点击创建控件时的行为（例如在点击位置自动设置大小），可继承 `UCreateWidgetToolBuilder` 并重写 `BuildTool` 方法：

```cpp
UCLASS()
class UMyCustomCreateWidgetToolBuilder : public UCreateWidgetToolBuilder
{
    GENERATED_BODY()

public:
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override
    {
        UCreateWidgetTool* Tool = NewObject<UCreateWidgetTool>(SceneState.ToolManager);
        // 自定义初始化逻辑
        Tool->WidgetClass = WidgetClass;
        // 例如设置默认尺寸
        // Tool->DefaultSize = FVector2D(200.0f, 50.0f);
        return Tool;
    }
};
```

然后在设置中指定该 Builder 类：

```cpp
ToolInfo.CreateWidgetToolBuilder = UMyCustomCreateWidgetToolBuilder::StaticClass();
```

---

## Demo 示例

以下是一个完整的 C++ 模块，用于在项目启动时注册一个自定义工具栈。

### MyWidgetTools.cpp

```cpp
#include "MyWidgetTools.h"
#include "Settings/CreateWidgetToolSettings.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"

void FMyWidgetToolsModule::StartupModule()
{
    // 在模块启动时添加自定义工具
    UCreateWidgetToolSettings* Settings = GetMutableDefault<UCreateWidgetToolSettings>();
    if (Settings)
    {
        // 工具栈1：基础控件
        FCreateWidgetStackInfo Stack1;
        Stack1.DisplayName = TEXT("基础控件");

        FCreateWidgetToolInfo BtnInfo;
        BtnInfo.WidgetClass = UButton::StaticClass();
        BtnInfo.DisplayName = TEXT("按钮");
        BtnInfo.WidgetHotkey = FInputChord(EKeys::B);
        Stack1.WidgetToolInfos.Add(BtnInfo);

        FCreateWidgetToolInfo TextInfo;
        TextInfo.WidgetClass = UTextBlock::StaticClass();
        TextInfo.DisplayName = TEXT("文本块");
        TextInfo.WidgetHotkey = FInputChord(EKeys::T);
        Stack1.WidgetToolInfos.Add(TextInfo);

        Settings->WidgetToolStacks.Add(Stack1);
        Settings->SaveConfig();
    }
}

void FMyWidgetToolsModule::ShutdownModule()
{
    // 清理（如果需要）
}

IMPLEMENT_MODULE(FMyWidgetToolsModule, MyWidgetTools);
```

### MyWidgetTools.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyWidgetToolsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

> **注意**：上述示例假设你的模块已依赖 `WidgetEditorToolPalette`。在 `Build.cs` 中添加 `PublicDependencyModuleNames.AddRange(new string[] { "WidgetEditorToolPalette" });`

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WidgetEditorToolPalette` | 本插件自身（运行时/编辑器模块） |

**其他自动依赖**（通常由编辑器插件隐式包含，无需手动添加）：  
- `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore`
- `UnrealEd`, `EditorStyle`, `PropertyEditor`, `EditorInteractiveToolsFramework`

本插件不引入非常规的独立外部依赖。

---

## 维护状态

### 近期更新

- 2025-03-25 `91c92132` [Truncation Warnings] Graph Editor Module - update MarqueeOperation to Vector2f  
- 2025-03-05 `7ab43c2f` Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd  
- 2024-11-15 `a2c3875d` Cleanup of FSlateFontInfo constructor across the solution that uses font paths  
- 2023-01-10 `4ff7bab1` Slate: Initial phase of FVector2D deprecation  
- 2022-10-26 `ed85af77` Non unity/pch compile fixes  

### 维护评价

- **创建时间**：2022-10-26（约 2.5 年）  
- **最近更新**：2025-03-25（修复）和 2025-03-05（适配 UE 5.5+ API 变化），表明依然在跟随引擎版本演进而更新。  
- **活跃度**：虽然更新频率不高（约 1 次/年），但每次 UE 大版本中出现 API 弃用时都有对应修复，属于“维护中”而非完全废弃。  
- **稳定性**：插件标记为实验性（IsBetaVersion=true），API 可能在未来发生变化，但核心功能已可使用。  
- **推荐使用**：适合希望扩展 UMG 编辑器工作流的团队。如果不需要自定义工具面板，可使用原生的控件拖拽；如果需要快速创建和框选，该插件是官方提供的解决方案。

**警告**：作为实验性插件，不保证向后兼容，升级引擎版本时需检查 API 变更。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/WidgetEditorToolPalette)  
- 官方文档：暂未提供（`.uplugin` 中 `DocsURL` 为空）  
- 测试用例：未找到公开的自动化测试文件（该插件规模较小）