# Naming Tokens UI

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名标记 UI |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 组件） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1.7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

`NamingTokens` 插件的核心功能是提供一套系统，用于在字符串（例如文件路径、资产名称）中定义和评估可被识别的“标记”（Tokens）。`NamingTokensUI` 模块是该系统的**用户界面组件库**，它封装了底层的标记评估逻辑，为编辑器和工具提供开箱即用的 Slate 控件和 UMG 控件，使用户能够直观地编辑包含动态标记的模板字符串，并实时预览其评估结果。

它解决了在资产管线、批量处理或自动化工作流中，需要动态生成具有规律性和可读性名称的痛点，让设计师和美术师无需接触代码即可使用变量来构建复杂的命名规则。

## 使用场景

- **资产命名约定**：你需要为一系列需要导出的模型资产建立一个包含版本号、LOD等级、资产类型的命名模板，例如 `SM_{AssetName}_v{Version}_{LOD}`。
- **关卡序列命名**：在影视虚拟制作中，为镜头序列定义命名规则，自动包含日期、场次、镜头号等信息。
- **自定义工具开发**：你正在开发一个批处理工具，需要一个 UI 让用户输入一个带有变量的文件名模板，并能在界面上预览最终生成的名称。

## 蓝图用法

核心蓝图控件是 `UNamingTokensEditableText`，它提供了丰富的属性和事件来集成到 UMG 界面中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Resolved Text` | 获取已评估（解析后）的最终文本。 | `UNamingTokensEditableText` |
| `Get Tokenized Text` | 获取包含原始标记（如 `{Version}`）的文本。 | `UNamingTokensEditableText` |
| `Set Contexts` | 设置用于评估的上下文对象列表。评估时，系统会从这些对象中查找标记的值。 | `UNamingTokensEditableText` |
| `Set Display Token Icon` | 设置是否在文本框中显示标记图标。 | `UNamingTokensEditableText` |
| `Set Show Unknown Token Warning` | 设置当文本中包含未被识别的标记时，是否显示警告图标。 | `UNamingTokensEditableText` |
| `Set Show Unset Token Warning` | 设置当某个标记评估结果为空值时，是否显示警告。 | `UNamingTokensEditableText` |
| `On Pre Evaluate Naming Tokens` | 在评估标记之前触发的多播委托，可用于预处理或修改评估上下文。 | `UNamingTokensEditableText` |

### 使用示例（蓝图描述）

1.  在 UMG 设计器中，从控制板拖入一个 `Naming Tokens Editable Text Box` 控件。
2.  在控件的“Details”面板中，找到 `Naming Tokens` 分类。
3.  你可以通过蓝图设置 `Contexts`，例如将一个游戏模式对象或数据资产传入，以提供可访问的标记值。
4.  将控件的 `Get Resolved Text` 节点连接到需要最终名称的逻辑（例如，一个 `Rename` 资产的函数）。
5.  调整 `Appearance` 分类下的属性（如 `Display Token Icon`, `Show Unknown Token Warning`）来优化用户体验。
6.  用户在该文本框中输入类似 `SK_{Character}_{Animation}` 的文本时，下拉建议菜单会根据已注册的标记和当前上下文自动弹出，辅助输入。输入框右侧会根据配置显示标记图标或错误/警告状态。

## C++ 用法

### 头文件引入

```cpp
// 使用 UMG 控件
#include "NamingTokensEditableText.h"

// 使用底层 Slate 控件
#include "SNamingTokensEditableTextBox.h"
#include "NamingTokens/Data/NamingTokenData.h" // 需要用于构造 FilterArgs 等
```

### 基本用法 (UMG)

创建并配置一个 `UNamingTokensEditableText` 控件，监听其评估结果。
（来源：基于 `Public/NamingTokensEditableText.h` 中的接口设计）

```cpp
// 假设在某个编辑器工具或自定义 UMG Widget 中
UNamingTokensEditableText* NamingTextWidget = /* 从 UMG 或 C++ 创建的控件 */;

// 设置用于评估的上下文，例如当前关卡或特定资产
TArray<UObject*> Contexts;
Contexts.Add(GetWorld()); // 添加当前世界作为上下文
NamingTextWidget->SetContexts(Contexts);

// 监听文本变化（可选，通常直接读取结果）
// NamingTextWidget->OnPreEvaluateNamingTokens.AddDynamic(this, &UMyClass::HandlePreEvaluation);

// 当需要获取最终名称时
const FText& FinalName = NamingTextWidget->GetResolvedText();
FString FinalNameString = FinalName.ToString();

// 当需要获取包含标记的模板文本时
const FText& TemplateText = NamingTextWidget->GetTokenizedText();
```

### 进阶用法 (Slate)

直接使用 Slate 控件 `SNamingTokensEditableTextBox`，以获得更精细的控制。
（来源：基于 `Public/SNamingTokensEditableTextBox.h` 中的 `SLATE_BEGIN_ARGS`）

```cpp
// 在某个 Slate 面板或窗口的构建函数中
SNew(SNamingTokensEditableTextBox)
    .Text(FText::FromString(TEXT("StaticMesh_{Name}_{LOD}")))
    .ShouldEvaluateTokens(true)
    .AllowMultiLine(false)
    .IsReadOnly(false)
    .CanDisplayResolvedText(true)
    .DisplayTokenIcon(true)
    .ShowUnknownTokenWarning(true)
    // 设置过滤参数，以限制可用的标记
    .FilterArgs_Lambda([this]() -> FNamingTokenFilterArgs {
        FNamingTokenFilterArgs Args;
        Args.NamespacesToInclude.Add(TEXT("Character")); // 只包含 Character 命名空间下的标记
        return Args;
    })
    // 接收评估完成后的事件
    .OnTokenizedTextEvaluated_Lambda([](const FText& EvaluatedText) {
        UE_LOG(LogTemp, Log, TEXT("Evaluated Name: %s"), *EvaluatedText.ToString());
    })
    // 当文本改变时
    .OnTextChanged_Lambda([](const FText& NewText) {
        // 处理标记文本变化
    })
    // 当用户选择了一个建议项后
    .OnSuggestionCommitted_Lambda([](TSharedPtr<FNamingTokenDataTreeItem> SelectedItem) {
        if (SelectedItem.IsValid() && SelectedItem->NamingTokenData.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("User selected token: %s"), *SelectedItem->NamingTokenData->TokenKey);
        }
    });
```

## Demo 示例

以下是一个最小化的编辑器工具窗口示例，展示如何在 C++ 中创建一个包含 `NamingTokensEditableText` 的界面。
```cpp
// MyNamingTokenToolWidget.h
#pragma once
#include "Widgets/SCompoundWidget.h"

class SMyNamingTokenToolWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyNamingTokenToolWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<class UNamingTokensEditableText> NamingTextWidget;
    TSharedPtr<class SWidget> WidgetHost;
};

// MyNamingTokenToolWidget.cpp
#include "MyNamingTokenToolWidget.h"
#include "NamingTokensEditableText.h"
#include "Components/VerticalBox.h"

void SMyNamingTokenToolWidget::Construct(const FArguments& InArgs)
{
    // 创建 UMG 控件的 Slate 宿主
    SAssignNew(WidgetHost, SObjectWidget)
        .ObjectToDisplay(NamingTextWidget);

    // 创建并初始化 UMG 控件
    NamingTextWidget = NewObject<UNamingTokensEditableText>();
    NamingTextWidget->SetFlags(RF_Transient);
    NamingTextWidget->AddToRoot(); // 防止被垃圾回收，示例代码需谨慎管理生命周期

    // 配置控件属性
    NamingTextWidget->SetDisplayTokenIcon(true);
    NamingTextWidget->SetShowUnknownTokenWarning(true);
    NamingTextWidget->SetCanDisplayResolvedText(true);

    // 构建 Slate 布局
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("输入命名模板 (例如: SM_{Name}_LOD{Level})")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            WidgetHost.ToSharedRef()
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("获取最终名称")))
            .OnClicked_Lambda([this]() -> FReply {
                if (NamingTextWidget)
                {
                    const FText& Resolved = NamingTextWidget->GetResolvedText();
                    FMessageDialog::Open(EAppMsgType::Ok, FText::Format(
                        NSLOCTEXT("NamingTool", "Result", "最终名称: {0}"), Resolved));
                }
                return FReply::Handled();
            })
        ]
    ];
}
```

## 模块依赖

从 `NamingTokensUI` 模块的 `Build.cs` 分析，除了标准 Core/Engine/Slate 依赖外，主要需要依赖：

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 核心标记系统逻辑，提供数据结构（如 `FNamingTokenData`）、过滤参数 (`FNamingTokenFilterArgs`) 和评估函数。 |
| `NamingTokensEditor` | 编辑器专用功能，可能包含标记定义资产、工厂类等。 |
| `Slate`, `SlateCore`, `UMG` | 用于构建和渲染 UI 控件。 |
| `PropertyEditor` | 可能用于在细节面板中自定义属性编辑器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 优化警告提示：将未解析的标记键用 {} 包裹显示，更清晰。 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复建议菜单：现在单击即可选中提交，提升交互效率。 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键菜单：右键点击不再意外破坏已输入的标记文本。 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i | 增强资产类型：为编辑器工具添加命名标记资产工厂，使其在资产浏览器中可见。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 分类调整：配合虚拟制作，调整了相关资产在编辑器中的分类位置。 |

### 维护评价

`NamingTokens` 是一个较新的实验性插件（创建于2025年初），但从**最近提交记录看，维护非常活跃**。提交历史集中在2026年5月，且全部是针对 `NamingTokensUI` 模块的**实质性功能改进和 Bug 修复**，例如优化交互细节、增强资产系统集成等。这表明该插件正处于积极的开发和完善阶段。

由于其“实验性”状态（`IsExperimentalVersion=true`）和“默认不启用”（`Installed=false`）的特性，它可能尚未被广泛用于生产环境，API 或行为在后续版本中仍有变化的可能。**推荐**用于编辑器扩展和工具开发中探索使用，但在正式项目集成前需进行充分测试，并做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [官方文档]() （暂无）
- [测试用例]() （用户未提供，可能位于 `Engine/Tests/` 或插件内部）