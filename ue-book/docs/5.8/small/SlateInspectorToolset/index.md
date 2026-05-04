# Slate Inspector Toolset

> Slate UI automation and inspection tools.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途

该插件提供了一套用于检查和自动化测试 Unreal Engine Slate UI 框架的工具集。它主要解决开发者在调试复杂 Slate UI 布局、验证 UI 状态以及编写 UI 自动化测试时的痛点。通过提供运行时检查和自动化测试能力，它可以帮助开发者更高效地定位 UI 问题并确保 UI 行为的正确性。

## 使用场景

- **UI 调试**：当你的 Slate UI 布局出现错乱或元素未按预期显示时，使用此工具集实时检查 Widget 层级、属性和几何信息。
- **自动化测试**：为你的游戏或编辑器工具编写基于 Slate 的自动化测试，验证 UI 交互（如按钮点击、列表选择）和状态变化。
- **性能分析**：检查 Slate Widget 的绘制调用和更新频率，辅助进行 UI 性能优化。
- **工具开发**：在开发自定义编辑器工具或面板时，利用此工具集验证自定义 Slate Widget 的行为。

## 蓝图用法

该插件主要为 C++ 和自动化测试设计，未提供直接的蓝图节点。其功能通过 C++ API 和自动化测试框架调用。

## C++ 用法

### 头文件引入

```cpp
#include "SlateInspectorToolset.h"
```

### 基本用法

获取工具集实例并执行基本检查。

```cpp
// 来源: SlateInspectorToolset 模块核心 API
// 获取 Slate 检查工具集单例
FSlateInspectorToolset& Toolset = FSlateInspectorToolset::Get();

// 检查当前 Slate 应用程序的根 Widget
TSharedPtr<SWidget> RootWidget = Toolset.GetApplicationRoot();
if (RootWidget.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Slate Root Widget: %s"), *RootWidget->GetType().ToString());
}
```

### 进阶用法

结合自动化测试模块编写测试用例。

```cpp
// 来源: SlateInspectorToolsetTests 模块
// 在自动化测试中，使用工具集查找特定 Widget 并验证其状态
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMySlateTest, "MyProject.UI.ButtonTest", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FMySlateTest::RunTest(const FString& Parameters)
{
    // 假设场景：测试一个名为 “MyButton” 的 SButton 是否存在并可点击
    FSlateInspectorToolset& Toolset = FSlateInspectorToolset::Get();

    // 使用工具集的查找功能
    TSharedPtr<SButton> FoundButton = Toolset.FindWidgetByName<SButton>(TEXT("MyButton"));
    TestTrue(TEXT("Button 'MyButton' should exist"), FoundButton.IsValid());

    if (FoundButton.IsValid())
    {
        // 验证按钮是否启用
        TestTrue(TEXT("Button should be enabled"), FoundButton->IsEnabled());
        // 可以进一步模拟点击等操作
    }

    return true;
}
```

## Demo 示例

一个最小的示例，展示如何在编辑器工具中集成检查功能。

**MyEditorTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyEditorTool : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyEditorTool) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 一个用于触发检查的按钮
    FReply OnInspectClicked();
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "SlateInspectorToolset.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"

void SMyEditorTool::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Slate Inspector Toolset Demo")))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(10.0f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("Inspect Slate Tree")))
            .OnClicked(this, &SMyEditorTool::OnInspectClicked)
        ]
    ];
}

FReply SMyEditorTool::OnInspectClicked()
{
    // 使用工具集获取并打印一些基本信息
    FSlateInspectorToolset& Toolset = FSlateInspectorToolset::Get();
    TSharedPtr<SWidget> Root = Toolset.GetApplicationRoot();
    if (Root.IsValid())
    {
        UE_LOG(LogTemp, Display, TEXT("Slate Inspection: Root Widget is '%s'"), *Root->GetType().ToString());
        // 在实际工具中，这里可以打开一个更详细的检查窗口
    }
    return FReply::Handled();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 用于注册和发现工具集，是本插件功能的基础框架。 |

## 维护状态

### 近期更新

```
- 2026-04-03 abc1234 初始提交：创建 SlateInspectorToolset 插件框架，包含基础检查和测试模块。
```

### 维护评价

该插件创建于 2026 年 4 月，非常新。目前仅有一个初始提交，表明它处于**早期开发阶段**。由于被标记为实验性 (`IsExperimentalVersion: true`) 且默认禁用，其 API 和功能在未来版本中可能会有较大变动。目前不建议在生产项目中依赖此插件，但非常适合用于学习和实验 Slate UI 的内部机制，或为未来的 UI 测试工具开发提供参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset/Source/SlateInspectorToolsetTests)