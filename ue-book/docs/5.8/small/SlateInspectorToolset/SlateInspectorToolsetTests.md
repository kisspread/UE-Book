# Slate Inspector Toolset

> Slate UI automation and inspection tools.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Slate 检查工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途

Slate Inspector Toolset 是一个为 **AI 助手（AI Assistant）** 或 **自动化脚本** 提供程序化操作和检查 Unreal Engine 编辑器内 Slate UI 界面能力的工具集。它解决的核心问题是：让非人类的程序（如大语言模型、测试脚本）能够“看到”并“操作”复杂的编辑器界面元素（如按钮、文本框、滑块）。这是实现编辑器自动化、录制回放、AI 驱动的工具开发等功能的基础。

## 使用场景

- 你正在开发一个由 AI 助手驱动的 Unreal 编辑器扩展，需要让 AI 能够读取输入框的文本、点击特定按钮、或从下拉框中选择选项。
- 你需要编写自动化测试来验证某个编辑器面板或工具窗口的 Slate 控件是否按预期工作（例如，检查一个复选框的状态，或滑块是否能拖到指定值）。
- 你在构建一个宏录制工具，需要记录用户在 Slate UI 上的操作（如点击、输入）以便后续回放。

## 蓝图用法

该插件主要为 C++ 和 AI 工具集提供底层能力，公开的蓝图节点较少。其核心功能通过 `UToolsetDefinition` 和相关的自动化任务暴露给 AI 助手系统。对于蓝图用户，更直接的方式可能是使用其关联的 `ToolsetRegistry` 系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SlateInspectorToolset` 模块提供的命令 | 通过 `UToolsetDefinition` 定义的工具函数，供 AI 助手调用，例如查找控件、读取文本、模拟点击等。 | `USlateInspectorToolset` |

### 使用示例（蓝图描述）

此插件通常不直接在蓝图图表中使用常规节点。其交互流程通常由上层的 AI 助手系统驱动。例如，当 AI 助手需要“在‘内容浏览器’中搜索‘Mesh’”时，它会调用由 `SlateInspectorToolset` 注册的工具函数，该函数内部会查找对应的 Slate 控件并模拟输入。

## C++ 用法

该插件的 API 主要面向 Toolset 开发者，用于扩展 AI 助手对 Slate 的操作能力。测试代码是理解其用法的最佳参考。

### 头文件引入

```cpp
// 主模块
#include "SlateInspectorToolset.h"

// 测试模块（用于查看示例）
#include "SlateInspectorToolsetTestPanel.h"
```

### 基本用法（从测试用例推断）

该插件的核心是提供一套工具函数，这些函数可以查找、查询和操作 Slate 控件。以下是一个基于测试用例逻辑的示例，展示了如何获取一个按钮控件的信息并模拟点击。

```cpp
// 假设在某个 Toolset Definition 的 UFUNCTION 中
// 来源参考：SlateInspectorToolsetTestPanel.h 中的按钮控件

// 1. 通过 Toolset 系统获取对特定 Slate 控件的引用（例如，通过路径或标签）
TSharedPtr<SWidget> FoundButton = UToolsetFunctionLibrary::FindWidgetByTag(TEXT("MyTestButton"));

// 2. 查询控件状态
if (TSharedPtr<SButton> ButtonPtr = StaticCastSharedPtr<SButton>(FoundButton))
{
    bool bIsEnabled = ButtonPtr->IsEnabled();
    // 执行其他查询...
}

// 3. 模拟用户操作（如点击）
// 通常通过 FSlateApplication 或专用的自动化函数来完成。
// 例如，可以调用工具集中定义的 “ClickButton” 函数。
```

### 进阶用法（组合操作）

结合测试面板 `SSlateInspectorToolsetTestPanel` 中的控件类型，可以想象一个更复杂的自动化序列：

```cpp
// 一个自动化脚本的任务：在测试面板中输入文本并选择下拉框选项
// 来源参考：SSlateInspectorToolsetTestPanel 的成员变量

// 步骤1：找到多行文本框并设置文本
TSharedPtr<SMultiLineEditableTextBox> MultiLineBox = /* 通过某种方式找到 */;
if (MultiLineBox)
{
    MultiLineBox->SetText(FText::FromString(TEXT("自动化输入的文本")));
}

// 步骤2：找到组合框并选择一个选项
TSharedPtr<SComboBox<TSharedPtr<FString>>> ComboBox = /* 通过某种方式找到 */;
if (ComboBox)
{
    // 假设有一个包含所有选项的数组
    TArray<TSharedPtr<FString>> AllOptions = /* 获取选项 */;
    // 选择第一个选项
    ComboBox->SetSelectedItem(AllOptions[0]);
}

// 步骤3：找到滑块并设置值
TSharedPtr<SSlider> Slider = /* 通过某种方式找到 */;
if (Slider)
{
    Slider->SetValue(0.75f); // 设置到75%
}
```

## Demo 示例

以下是一个最小化的、展示如何创建一个包含多种可操作控件的 Slate 面板的示例。这个面板本身可以被 Slate Inspector Toolset 检查和操作。

**SlateInspectorToolsetTestPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SCheckBox.h"
#include "Widgets/Input/SComboBox.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Input/SSpinBox.h"

class SSlateInspectorToolsetTestPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SSlateInspectorToolsetTestPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 各种控件指针
    int32 ButtonClickCount = 0;
    TSharedPtr<SEditableTextBox> TextBox;
    TSharedPtr<SCheckBox> CheckBox;
    TSharedPtr<SComboBox<TSharedPtr<FString>>> ComboBox;
    TArray<TSharedPtr<FString>> ComboOptions;
    TSharedPtr<FString> SelectedComboOption;
    TSharedPtr<SSlider> Slider;
    float SliderValue = 0.0f;

    // 回调函数示例
    FReply OnButtonClicked();
    void OnCheckStateChanged(ECheckBoxState NewState);
    void OnComboSelectionChanged(TSharedPtr<FString> NewValue, ESelectInfo::Type SelectInfo);
    void OnSliderValueChanged(float NewValue);
};
```

**SlateInspectorToolsetTestPanel.cpp**
```cpp
#include "SlateInspectorToolsetTestPanel.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Views/SListView.h"

void SSlateInspectorToolsetTestPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight().Padding(5)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("点击按钮")))
            .OnClicked(this, &SSlateInspectorToolsetTestPanel::OnButtonClicked)
            .Tag(FName("TestButtonTag")) // 用于工具集查找
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(5)
        [
            SAssignNew(TextBox, SEditableTextBox)
            .HintText(FText::FromString(TEXT("输入文本...")))
            .Tag(FName("TestTextBox"))
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(5)
        [
            SAssignNew(CheckBox, SCheckBox)
            .OnCheckStateChanged(this, &SSlateInspectorToolsetTestPanel::OnCheckStateChanged)
            .Tag(FName("TestCheckBox"))
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("测试复选框")))
            ]
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(5)
        [
            SAssignNew(ComboBox, SComboBox<TSharedPtr<FString>>)
            .OptionsSource(&ComboOptions)
            .OnSelectionChanged(this, &SSlateInspectorToolsetTestPanel::OnComboSelectionChanged)
            .OnGenerateWidget_Lambda([](TSharedPtr<FString> Item) {
                return SNew(STextBlock).Text(FText::FromString(*Item));
            })
            .Tag(FName("TestComboBox"))
            [
                SNew(STextBlock).Text_Lambda([this]() {
                    return SelectedComboOption ? FText::FromString(*SelectedComboOption) : FText::GetEmpty();
                })
            ]
        ]
        + SVerticalBox::Slot().AutoHeight().Padding(5)
        [
            SAssignNew(Slider, SSlider)
            .Value(this->SliderValue)
            .OnValueChanged(this, &SSlateInspectorToolsetTestPanel::OnSliderValueChanged)
            .Tag(FName("TestSlider"))
        ]
    ];

    // 初始化下拉框选项
    ComboOptions.Add(MakeShared<FString>(TEXT("选项 A")));
    ComboOptions.Add(MakeShared<FString>(TEXT("选项 B")));
    ComboOptions.Add(MakeShared<FString>(TEXT("选项 C")));
    SelectedComboOption = ComboOptions[0];
}

FReply SSlateInspectorToolsetTestPanel::OnButtonClicked()
{
    ButtonClickCount++;
    UE_LOG(LogTemp, Log, TEXT("按钮被点击，次数：%d"), ButtonClickCount);
    return FReply::Handled();
}

void SSlateInspectorToolsetTestPanel::OnCheckStateChanged(ECheckBoxState NewState)
{
    UE_LOG(LogTemp, Log, TEXT("复选框状态改变：%s"), 
        NewState == ECheckBoxState::Checked ? TEXT("选中") : TEXT("未选中"));
}

void SSlateInspectorToolsetTestPanel::OnComboSelectionChanged(TSharedPtr<FString> NewValue, ESelectInfo::Type SelectInfo)
{
    SelectedComboOption = NewValue;
    UE_LOG(LogTemp, Log, TEXT("下拉框选项改变：%s"), *NewValue);
}

void SSlateInspectorToolsetTestPanel::OnSliderValueChanged(float NewValue)
{
    SliderValue = NewValue;
    UE_LOG(LogTemp, Log, TEXT("滑块值改变：%.2f"), NewValue);
}
```

## 模块依赖

从 `SlateInspectorToolset.Build.cs` 和测试模块的依赖推断，使用者通常需要以下非标准依赖：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 核心依赖，用于将功能注册为 AI 助手可调用的工具。 |
| `Slate` / `SlateCore` | 提供基础 Slate 控件和渲染能力。 |
| `InputCore` | 处理输入事件（如模拟点击）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 修改了工具集定义中如何确定哪些 UFunction 可作为工具的逻辑。 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | （与上一条相关）调整工具函数的判定机制。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了 CL52878047 的更改。 |
| 2026-04-13 | `69570138` | [SlateInspectorToolset] Move `SlateInspectorToolset` tests from `Editor` to `AI.Toolsets` category. | 将测试用例从 `Editor` 分类移动到 `AI.Toolsets` 分类。 |
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将所有工具集的加载阶段调整为 PostEngineInit，以简化 Toolset Registry 的注册流程。 |

### 维护评价

- **活跃维护**：插件创建于 **2026年4月2日**，年龄非常新（不到1年）。从近期 git 历史看，更新非常频繁（最近一次在4月18日），且内容集中在核心功能的调整和优化上，表明该插件正处于**积极开发期**。
- **实验性状态**：`.uplugin` 明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这表明 Epic 将其视为前沿技术探索，API 和功能可能会在未来发生重大变更。
- **已知限制**：作为实验性工具，其稳定性和向后兼容性不保证。主要用于内部开发和测试 AI 助手功能。
- **推荐使用**：**仅推荐**给正在基于 Unreal Engine 开发 AI 助手、高级编辑器自动化工具或需要进行深度 Slate UI 自动化测试的**高级开发者**。对于一般的游戏或项目开发，无需也不应启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- [官方文档] (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset/Source/SlateInspectorToolsetTests)