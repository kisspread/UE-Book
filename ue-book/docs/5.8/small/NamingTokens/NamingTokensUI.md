# Naming Tokens UI

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名令牌 UI |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 插件用于定义和解析字符串中的命名令牌（Token），特别适用于文件路径、命名规则等场景。核心功能是让用户在字符串中使用 `{TokenKey}` 格式的占位符，运行时将其替换为实际值。

**NamingTokensUI 模块**是该插件的 UI 层，提供了专门的可编辑文本框控件，支持：
- 语法高亮：自动识别并以不同样式显示 `{token}` 格式的令牌
- 智能补全：输入 `{` 时弹出下拉建议列表，按命名空间分组显示可用令牌
- 实时预览：切换显示原始令牌文本和解析后的实际值
- 警告提示：当令牌未识别或解析为空值时显示警告图标
- 上下文绑定：支持传入 UObject 上下文，为不同对象计算不同的令牌值

## 使用场景

- 你在做一个资产命名工具，需要用户输入模板如 `{Project}_{Sequence}_{Shot}` → 用 NamingTokensEditableText
- 你需要在编辑器 UI 中提供带自动补全的命名规则输入框 → 用 NamingTokensEditableText
- 你需要实时预览令牌替换后的结果 → 用 NamingTokensEditableText 的解析模式

## 蓝图用法

NamingTokensUI 模块暴露的核心 UMG 控件是 `UNamingTokensEditableText`，继承自 `UMultiLineEditableText`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetResolvedText` | 获取令牌解析后的最终文本 | `UNamingTokensEditableText` |
| `GetTokenizedText` | 获取包含 `{token}` 的原始模板文本 | `UNamingTokensEditableText` |
| `SetContexts` | 设置用于令牌求值的 UObject 上下文数组 | `UNamingTokensEditableText` |
| `SetCanDisplayResolvedText` | 设置是否允许显示解析后的文本 | `UNamingTokensEditableText` |
| `SetDisplayTokenIcon` | 设置是否在文本框中显示令牌图标 | `UNamingTokensEditableText` |
| `SetDisplayErrorMessage` | 设置是否显示令牌格式错误消息 | `UNamingTokensEditableText` |
| `SetDisplayBorderImage` | 设置是否显示边框图像 | `UNamingTokensEditableText` |
| `SetShowUnknownTokenWarning` | 设置是否对未识别的令牌显示警告 | `UNamingTokensEditableText` |
| `SetShowUnsetTokenWarning` | 设置是否对解析为空值的令牌显示警告 | `UNamingTokensEditableText` |
| `SetWidgetArgumentStyle` | 设置令牌参数的文本样式 | `UNamingTokensEditableText` |
| `SetBackgroundColor` | 设置背景颜色 | `UNamingTokensEditableText` |

### 蓝图属性

| 属性 | 说明 | 类型 |
|---|---|---|
| `FilterArgs` | 命名令牌过滤参数 | `FNamingTokenFilterArgs` |
| `NamespaceSuggestionPriority` | 命名空间建议优先级排序 | `TArray<FString>` |
| `bEnableSuggestionDropdown` | 是否启用下拉建议框 | `bool` |
| `bFullyQualifyFilteredNamespaces` | 过滤的命名空间是否自动补全完整命名空间 | `bool` |
| `bIsMultiline` | 是否配置为多行文本框 | `bool` |

### 使用示例（蓝图描述）

1. 在 UMG Widget Blueprint 中添加 `Naming Tokens Editable Text Box` 控件
2. 在 Details 面板中配置 `FilterArgs` 限制可用的令牌范围
3. 通过 `SetContexts` 节点传入需要求值的 UObject 上下文
4. 在需要获取结果时，调用 `GetResolvedText` 获取解析后的文本
5. 监听 `OnPreEvaluateNamingTokens` 事件，在求值前执行自定义逻辑

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokensEditableText.h"       // UMG 控件
#include "SNamingTokensEditableTextBox.h"    // 底层 Slate 控件
```

### 基本用法

在 C++ 中创建和配置命名令牌编辑文本框：

```cpp
// 创建 Slate 控件并配置属性
TSharedRef<SNamingTokensEditableTextBox> TokenTextBox = SNew(SNamingTokensEditableTextBox)
    .Text(FText::FromString(TEXT("{Project}_{Sequence}_{Shot}")))
    .AllowMultiLine(false)
    .EnableSuggestionDropdown(true)
    .ShouldEvaluateTokens(true)
    .DisplayTokenIcon(true)
    .DisplayErrorMessage(true);

// 获取解析后的文本
const FText& ResolvedText = TokenTextBox->GetResolvedText();

// 获取原始令牌文本
const FText& TokenizedText = TokenTextBox->GetTokenizedText();

// 手动触发令牌求值
TokenTextBox->EvaluateNamingTokens();
```

### 进阶用法

配置过滤参数和上下文，以及自定义警告行为：

```cpp
// 设置过滤参数，限制可用令牌范围
FNamingTokenFilterArgs FilterArgs;
// 配置 FilterArgs...
TokenTextBox->SetFilterArgs(FilterArgs);

// 设置命名空间优先级
TArray<FString> NamespacePriority = {TEXT("Game"), TEXT("Sequence"), TEXT("Shot")};
TokenTextBox->SetNamespaceSuggestionPriority(NamespacePriority);

// 设置上下文对象
TArray<UObject*> Contexts;
Contexts.Add(MyGameAsset);
TokenTextBox->SetContexts(Contexts);

// 配置警告显示
TokenTextBox->SetShowUnknownTokenWarning(true);   // 未识别令牌警告
TokenTextBox->SetShowUnsetTokenWarning(false);     // 空值令牌警告

// 设置过滤命名空间自动补全
TokenTextBox->SetFullyQualifyFilteredNamespaces(true);

// 监听文本变化
TokenTextBox->SetOnTextChanged(FOnTextChanged::CreateLambda([](const FText& InText)
{
    UE_LOG(LogTemp, Log, TEXT("Token text changed: %s"), *InText.ToString());
}));

// 监听求值前事件
TokenTextBox->SetOnPreEvaluateNamingTokens(FSimpleDelegate::CreateLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("About to evaluate naming tokens"));
}));
```

## Demo 示例

```cpp
// MyTokenWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Components/Widget.h"
#include "SNamingTokensEditableTextBox.h"

class UMyTokenWidget : public UWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Naming Tokens")
    FNamingTokenFilterArgs FilterArgs;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Naming Tokens")
    bool bEnableSuggestions = true;

protected:
    virtual TSharedRef<SWidget> RebuildWidget() override
    {
        MyTokenTextBox = SNew(SNamingTokensEditableTextBox)
            .FilterArgs(FilterArgs)
            .EnableSuggestionDropdown(bEnableSuggestions)
            .ShouldEvaluateTokens(true)
            .DisplayTokenIcon(true)
            .AllowMultiLine(false);

        return MyTokenTextBox.ToSharedRef();
    }

    virtual void SynchronizeProperties() override
    {
        Super::SynchronizeProperties();
        if (MyTokenTextBox.IsValid())
        {
            MyTokenTextBox->SetFilterArgs(FilterArgs);
            MyTokenTextBox->SetEnableSuggestionDropdown(bEnableSuggestions);
        }
    }

    virtual void ReleaseSlateResources(bool bReleaseChildren) override
    {
        Super::ReleaseSlateResources(bReleaseChildren);
        MyTokenTextBox.Reset();
    }

private:
    TSharedPtr<SNamingTokensEditableTextBox> MyTokenTextBox;
};
```

## 模块依赖

本模块的依赖关系基于 NamingTokensUI 模块（命名令牌 UI 组件）。使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 核心命名令牌运行时模块，提供令牌解析和评估逻辑 |
| `NamingTokensUI` | UI 模块本身，提供可编辑文本框和下拉建议控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 未识别令牌在警告提示中用 {} 包裹显示 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动补全菜单单击即提交的问题 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键操作覆盖令牌文本的问题 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i... | 添加编辑器工具命名令牌的工厂和资产定义 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制作资产迁移到不同的资产分类 |

### 维护评价

**活跃维护** — 该插件创建于 2025 年初，距今约 1.3 年。从近期提交记录来看，2026 年 5 月有多次密集的功能改进和 bug 修复，说明该插件仍在积极开发中。

- 实验性状态（IsExperimentalVersion=true）：该插件尚未标记为正式版，API 可能会有变动
- 活跃开发：近期有 UI 交互修复、自动补全改进、资产定义添加等实质性更新
- 虚拟制作整合：正在与虚拟制作工作流整合，扩展了应用场景
- **推荐使用**：虽然仍为实验性，但功能完善且持续维护，适合在项目中试用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [官方文档]()（暂无）