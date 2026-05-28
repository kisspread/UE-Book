# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | 即时模式 UI 工具 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMEngine` (Runtime), `SlateIMInGame` (Runtime), `SlateIMBlueprint` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 插件为 Unreal Engine 的 UI 框架 Slate 提供了一套“即时模式”（Immediate Mode）的封装。在标准的 Slate 开发中，你需要声明式地定义 UI 控件树，管理状态和更新逻辑，这对于构建复杂的、可复用的 UI 组件是必要的。然而，在开发调试工具、快速原型或需要频繁更新、布局简单的诊断界面时，这种模式会显得比较繁琐。

SlateIM 的核心思想是让开发者能够像编写普通代码（如绘制命令）一样，按顺序“立即”构建 UI 元素，而无需预先定义复杂的 Slate 类结构。这极大地简化了临时性、工具性 UI 的编写流程，非常适合用于快速添加调试信息面板、游戏运行状态监视器或编辑器内的即时预览工具。

## 使用场景

- **游戏运行时调试**：你需要在玩家屏幕上实时显示变量、坐标、状态机状态等调试信息，可以快速通过 SlateIM 的 API 构建一个简洁的 HUD。
- **编辑器工具开发**：你在开发一个自定义编辑器窗口或资产预览工具，需要即时、动态地展示数据或控件布局，使用 SlateIM 可以避免编写大量样板代码。
- **独立工具程序**：你在构建一个不依赖完整游戏引擎的独立工具程序（如资源处理器、分析器），但仍需要一个简单的 UI 来显示进度或结果，SlateIM 提供了这种可能性。

## 蓝图用法

SlateIM 主要面向 C++ 开发者。其蓝图模块（`SlateIMBlueprint`）旨在提供蓝图访问接口，但该功能目前可能尚在开发中。详细的蓝图节点将在子模块文档中说明。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `函数名` | 一句话说明 | `UClassName` |

### 使用示例（蓝图描述）

（蓝图用法待子模块文档补充）

## C++ 用法

### 头文件引入

根据创建信息，核心 API 可在 `SlateIM.h` 中找到。

```cpp
#include "SlateIM.h"
```

### 基本用法

SlateIM 的 API 设计旨在简化流程。一个典型的使用模式可能如下（基于模块设计推断）：

```cpp
// 在某个需要更新 UI 的地方（如 UGameplayStatics 的 Tick 或自定义窗口的刷新函数中）
void UMyDebugComponent::UpdateDebugUI()
{
    // 开始一个新的即时模式 UI 构建上下文
    FSlateIMContext Context = FSlateIMContext::Get();

    // 以顺序方式构建 UI
    if (Context.BeginWindow(TEXT("Debug Info")))
    {
        Context.Text(TEXT("Player Position:"));
        Context.Text(PlayerPosition.ToString());

        Context.Text(TEXT("Current State:"));
        Context.Text(StateName);

        // 可能包含简单的交互元素
        if (Context.Button(TEXT("Reset")))
        {
            ResetPlayer();
        }

        Context.EndWindow();
    }
}
```

*注：以上为基于插件用途的示意性代码，具体函数名需参考 `SlateIM.h` 头文件。*

### 进阶用法

SlateIM 模块依赖于 `SlateIMEngine` 模块。`SlateIMInGame` 模块可能提供了在游戏视口或特定 Slate 窗口中直接嵌入即时模式 UI 的便捷方法。更复杂的用法可以结合多个模块，例如使用 `SlateIMEngine` 模块创建更专业的工具窗口，同时在游戏层使用 `SlateIMInGame` 进行快速调试。

## Demo 示例

以下是一个在编辑器中创建按钮，点击后弹出使用 SlateIM 构建的简单调试窗口的示例。

**MyDebugTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyDebugTool : public SCompoundWidget
{
    SLATE_BEGIN_ARGS(SMyDebugTool) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FReply OnShowDebugWindowClicked();

    TSharedPtr<SWindow> DebugWindow;
    FTimerHandle UpdateTimerHandle;
};
```

**MyDebugTool.cpp**
```cpp
#include "MyDebugTool.h"
#include "SlateIM.h" // 引入 SlateIM 核心头文件

void SMyDebugTool::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SButton)
        .Text(FText::FromString(TEXT("Show SlateIM Debug Window")))
        .OnClicked(FOnClicked::CreateSP(this, &SMyDebugTool::OnShowDebugWindowClicked))
    ];
}

FReply SMyDebugTool::OnShowDebugWindowClicked()
{
    if (!DebugWindow.IsValid())
    {
        // 创建一个新的浮动窗口
        DebugWindow = SNew(SWindow)
            .Title(FText::FromString(TEXT("SlateIM Debug")))
            .ClientSize(FVector2D(300, 200))
            .SupportsMinimize(false);

        // 将窗口添加到桌面
        FSlateApplication::Get().AddWindow(DebugWindow.ToSharedRef());

        // 设置一个定时器，定期用 SlateIM 更新窗口内容
        GEditor->GetTimerManager()->SetTimer(UpdateTimerHandle, [this]()
        {
            if (DebugWindow.IsValid())
            {
                // 获取窗口内容区域
                TSharedRef<SVerticalBox> Content = SNew(SVerticalBox);

                // 使用 SlateIM 构建 UI
                // 注意：实际集成方式需参考 SlateIMInGame 或 SlateIMEngine 的特定 API，
                // 可能需要将构建结果挂载到此窗口。
                // 此处为概念演示。
                /*
                FSlateIMContext Context;
                Context.SetContainer(Content);
                Context.Text(FString::Printf(TEXT("Time: %f"), GEditor->GetTimerManager()->GetTimerElapsed(UpdateTimerHandle)));
                */

                DebugWindow->SetContent(Content);
            }
        }, 0.1f, true); // 每0.1秒更新一次
    }
    else
    {
        DebugWindow->BringToFront();
    }

    return FReply::Handled();
}
```

*注：此 Demo 重点展示创建窗口和触发更新的逻辑。SlateIM 的具体内容构建（`Context.Text` 等）需要结合 `SlateIMInGame` 或 `SlateIMEngine` 模块的 API 来将即时模式绘制的命令转换为 Slate 控件并填充到窗口中，具体实现需查阅对应模块的文档。*

## 模块依赖

要使用 SlateIM 插件，你的项目或模块需要根据想要使用的功能进行依赖。

| 模块 | 用途 |
|---|---|
| `SlateIM` | **核心模块**，提供即时模式 UI 的基础 API 和上下文管理。依赖于 `SlateIMEngine`。 |
| `SlateIMEngine` | **引擎集成模块**，提供将即时模式 UI 更深度地集成到引擎（如特定编辑器窗口、控制台）的能力。 |
| `SlateIMInGame` | **游戏内集成模块**，提供在游戏运行时视口或 UI 层中嵌入和管理即时模式 UI 的便捷方法。 |
| `SlateIMBlueprint` | **蓝图支持模块**，旨在为蓝图系统暴露 SlateIM 的功能（当前可能为实验性）。 |

根据你的使用场景选择依赖：
- 只想在 C++ 中构建简单的 UI 用于调试：依赖 `SlateIM`。
- 需要在游戏视口中显示：依赖 `SlateIMInGame`。
- 开发编辑器工具：依赖 `SlateIMEngine`。
- 需要蓝图接口：依赖 `SlateIMBlueprint`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量隐式转换为浮点数导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移为 UE_LOGF，可能是为了适配新的日志系统或格式。 |
| 2026-04-02 | `82179cc5` | Remove parameters from constructor in SlateIM in game widgets and update all existing in widgets | 简化了 SlateIM 游戏内控件的构造函数，并更新了所有现有控件，这是 API 优化。 |
| 2026-04-01 | `097a8aca` | SlateIM: Major changes | SlateIM 进行了重大更新，可能包含新功能或架构调整。 |
| 2026-04-01 | `9016fa55` | [Backout] - CL52349724 | 回滚了之前的提交（CL52349724），表明正在进行迭代开发和问题修复。 |

### 维护评价

SlateIM 是一个于 **2025年初创建** 的 **实验性** 插件。从近期的 Git 历史来看，该插件在 **2026年4月至5月期间有连续、活跃的提交**，内容包括 API 重构（“Major changes”）、编译警告修复和日志系统适配，表明它正处于 **活跃开发和完善阶段**。

**优点**：
1.  **维护活跃**：最近几个月有实质性功能迭代和问题修复。
2.  **目标明确**：针对特定痛点（调试 UI 创建繁琐），有清晰的用途。
3.  **模块化设计**：通过多个运行时模块将功能拆解，允许用户按需引入。

**风险与注意**：
1.  **实验性**：插件被标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，意味着其 API **可能在未来发生重大变更或存在不稳定因素**。
2.  **文档尚缺**：目前官方文档 URL 为空，主要依赖源码和示例学习。
3.  **生态未成**：作为较新的实验性功能，社区资源和成熟用例较少。

**结论**：如果你正在开发 **调试工具或内部编辑器工具**，并且不介意处理潜在的 API 变化，SlateIM 是一个 **值得尝试的现代化、高效的解决方案**。它能显著提升相关 UI 的开发效率。但对于需要长期稳定维护的生产环境核心 UI，建议谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM/Tests) （推测路径，可能存在）