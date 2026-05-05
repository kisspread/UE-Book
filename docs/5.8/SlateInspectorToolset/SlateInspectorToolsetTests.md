# SlateInspectorToolset

> Slate UI automation and inspection tools.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途

SlateInspectorToolset 是一套面向编辑器的 Slate UI 自动化测试与检查工具集。它解决的核心问题是：**如何对 Slate 控件进行程序化的状态快照、运行时观察和输入模拟**。

在 UE5 的开发过程中，Slate UI 框架本身缺乏内置的自动化测试基础设施。该插件填补了这一空白，提供了：

1. **快照（Snapshot）**：捕获 Slate 控件树的当前状态，用于回归测试和状态比对
2. **观察者（Observer）**：监听控件属性变化，用于验证 UI 行为是否符合预期
3. **输入模拟（Input Simulation）**：程序化地模拟点击、输入、滑动等用户交互，无需人工操作即可驱动 UI 测试

该插件依赖 `ToolsetRegistry` 插件，表明它是 Epic 内部 Toolset 工具体系的一部分，通过注册机制与其他工具集协同工作。

## 使用场景

- 你在开发编辑器扩展，需要对自定义 Slate 面板进行自动化回归测试 → 用 SlateInspectorToolset
- 你需要验证某个 Slate 控件在特定交互后的状态变化（如按钮点击计数、滑块值变化）→ 用观察者和输入模拟功能
- 你在构建 CI 流水线，需要无人值守地测试编辑器 UI → 用输入模拟驱动测试流程
- 你需要调试复杂的 Slate 控件层级问题 → 用快照功能导出控件树结构

## 蓝图用法

该插件为 Editor 模块，主要面向 C++ 自动化测试场景。由于当前可见的源码仅包含测试面板，核心 API 细节需参考主模块 `SlateInspectorToolset` 的完整实现。

### 核心概念

| 概念 | 说明 |
|---|---|
| 快照（Snapshot） | 对 Slate 控件树进行状态捕获，生成可比对的结构化数据 |
| 观察者（Observer） | 注册到指定控件上，监听属性变化并触发回调 |
| 输入模拟 | 程序化生成鼠标/键盘事件，注入到目标控件 |

## C++ 用法

### 头文件引入

```cpp
#include "SlateInspectorToolset.h"
```

### 测试面板构造

测试模块提供了一个标准的测试面板 `SSlateInspectorToolsetTestPanel`，包含所有常见 Slate 控件类型，用于验证工具集的各项功能。

```cpp
// 来源: Private/SlateInspectorToolsetTestPanel.h

// 创建测试面板
TSharedRef<SSlateInspectorToolsetTestPanel> TestPanel =
    SNew(SSlateInspectorToolsetTestPanel);

// 面板内置的控件可用于测试：
// - 按钮点击计数
TestPanel->ButtonClickCount;        // 第一个按钮的点击次数
TestPanel->SecondButtonClickCount;  // 第二个按钮的点击次数

// - 文本输入控件
TestPanel->TextBox;          // 单行文本框 (SEditableTextBox)
TestPanel->MultiLineTextBox; // 多行文本框 (SMultiLineEditableTextBox)
TestPanel->SearchBox;        // 搜索框 (SSearchBox)

// - 开关控件
TestPanel->CheckBox;         // 复选框 (SCheckBox)

// - 下拉选择
TestPanel->ComboBox;         // 下拉框 (SComboBox<FString>)
TestPanel->SelectedComboOption; // 当前选中项

// - 数值控件
TestPanel->Slider;           // 滑块 (SSlider)
TestPanel->SliderValue;      // 滑块当前值
TestPanel->SpinBox;          // 数值输入框 (SSpinBox<float>)
TestPanel->SpinBoxValue;     // 数值输入框当前值
```

### 进阶用法

典型的自动化测试流程如下（基于测试面板推断）：

```cpp
// 1. 构造测试面板
TSharedRef<SSlateInspectorToolsetTestPanel> Panel =
    SNew(SSlateInspectorToolsetTestPanel);

// 2. 使用快照功能捕获初始状态
// （调用 SlateInspectorToolset 主模块的快照 API）

// 3. 使用输入模拟功能执行交互
// - 模拟按钮点击，验证 ButtonClickCount 递增
// - 模拟文本输入，验证 TextBox 内容变化
// - 模拟滑块拖动，验证 SliderValue 更新

// 4. 再次快照，与初始状态比对
// 验证所有控件状态变化符合预期
```

## Demo 示例

```cpp
// SlateInspectorToolsetTestPanel.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "Widgets/Input/SCheckBox.h"
#include "Widgets/Input/SComboBox.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Input/SSpinBox.h"
#include "Widgets/Input/SSearchBox.h"
#include "Widgets/Input/SMultiLineEditableTextBox.h"

class SMyTestPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTestPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        ChildSlot
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight()
            [
                SNew(SButton)
                .Text(FText::FromString(TEXT("Test Button")))
            ]
            + SVerticalBox::Slot().AutoHeight()
            [
                SAssignNew(TextBox, SEditableTextBox)
                .HintText(FText::FromString(TEXT("Type here...")))
            ]
            + SVerticalBox::Slot().AutoHeight()
            [
                SAssignNew(CheckBox, SCheckBox)
            ]
            + SVerticalBox::Slot().AutoHeight()
            [
                SAssignNew(Slider, SSlider)
                .Value(0.5f)
            ]
        ];
    }

    TSharedPtr<SEditableTextBox> TextBox;
    TSharedPtr<SCheckBox> CheckBox;
    TSharedPtr<SSlider> Slider;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 工具集注册框架，用于将 SlateInspectorToolset 注册到统一的工具管理体系中 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-13 `69570138` [SlateInspectorToolset] Move `SlateInspectorToolset` tests from `Editor` to `AI.Toolsets` category.
- 2026-04-03 `7f02bd73` [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，属于实验阶段
- **依赖 ToolsetRegistry**：表明它是 Epic 内部工具链的一部分，可能随工具链整体迭代
- **测试覆盖**：包含独立的测试模块 `SlateInspectorToolsetTests`，说明 Epic 对其质量有一定保障
- **EditorOnly**：仅在编辑器中可用，不影响打包产物
- **建议**：适合在编辑器扩展开发中用于自动化测试，但不建议在生产环境中作为核心依赖。作为实验性功能，API 可能在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)